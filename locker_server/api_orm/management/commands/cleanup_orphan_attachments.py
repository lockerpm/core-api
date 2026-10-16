from django.core.management import BaseCommand

from locker_server.api_orm.models.wrapper import get_cipher_model
from locker_server.api_orm.utils.attachments import ATTACHMENT_KEY_PATTERN
from locker_server.settings import locker_server_settings
from locker_server.shared.external_services.attachments.attachment_factory import AttachmentStorageFactory
from locker_server.shared.utils.app import now


CipherORM = get_cipher_model()


class Command(BaseCommand):
    help = "Find (and delete with --execute) the attachment files whose ciphers do not exist anymore"

    def add_arguments(self, parser):
        parser.add_argument("--execute", action="store_true", help="Delete the orphan files. Default: dry-run")
        parser.add_argument("--prefix", default="attachments/", help="The storage prefix to scan")
        parser.add_argument("--batch-size", type=int, default=1000)
        parser.add_argument(
            "--min-age-hours", type=float, default=24, help="Skip files which are modified in the last N hours"
        )

    def handle(self, *args, **options):
        execute = options["execute"]
        batch_size = options["batch_size"]
        max_last_modified = now() - options["min_age_hours"] * 3600
        attachment_storage = AttachmentStorageFactory.get_attachment_service(
            service_name=locker_server_settings.DEFAULT_CLOUD_STORAGE
        )
        self.stdout.write(
            f"Scanning {options['prefix']} on {locker_server_settings.DEFAULT_CLOUD_STORAGE} "
            f"({'EXECUTE' if execute else 'DRY-RUN'})"
        )

        stats = {"scanned": 0, "skipped": 0, "orphans": 0, "orphan_size": 0, "deleted": 0}
        batch = []
        for key, size, last_modified in attachment_storage.iter_keys(prefix=options["prefix"]):
            stats["scanned"] += 1
            match = ATTACHMENT_KEY_PATTERN.fullmatch(key)
            if not match or last_modified > max_last_modified:
                stats["skipped"] += 1
                continue
            batch.append((key, size or 0, match.group("cipher_id")))
            if len(batch) >= batch_size:
                self._handle_batch(attachment_storage, batch, stats, execute)
                batch = []
        if batch:
            self._handle_batch(attachment_storage, batch, stats, execute)

        self.stdout.write(
            f"Scanned: {stats['scanned']} - Skipped: {stats['skipped']} - "
            f"Orphans: {stats['orphans']} ({stats['orphan_size']} bytes) - Deleted: {stats['deleted']}"
        )

    def _handle_batch(self, attachment_storage, batch, stats, execute: bool):
        cipher_ids = {cipher_id for _, _, cipher_id in batch}
        # Soft-deleted ciphers (in the trash) still exist => their files are kept
        existed_cipher_ids = set(
            str(cipher_id) for cipher_id in CipherORM.objects.filter(id__in=cipher_ids).values_list('id', flat=True)
        )
        orphan_keys = []
        for key, size, cipher_id in batch:
            if cipher_id in existed_cipher_ids:
                continue
            orphan_keys.append(key)
            stats["orphans"] += 1
            stats["orphan_size"] += size
            self.stdout.write(f"[orphan] {key} ({size} bytes)")
        if execute and orphan_keys:
            if attachment_storage.delete_files(file_paths=orphan_keys):
                stats["deleted"] += len(orphan_keys)
            else:
                self.stderr.write(f"Delete orphan files error. See the error logs. Keys: {orphan_keys}")
