from django.core.management import BaseCommand

from locker_server.containers.containers import attachment_service
from locker_server.shared.constants.attachments import LIMIT_SIZE_ATTACHMENT
from locker_server.shared.utils.app import now


class Command(BaseCommand):
    help = "Find (and delete with --execute) the attachment files which are larger than the limit size"

    def add_arguments(self, parser):
        parser.add_argument("--execute", action="store_true", help="Delete the oversize files. Default: dry-run")
        parser.add_argument("--max-size", type=int, default=LIMIT_SIZE_ATTACHMENT, help="The max file size (bytes)")
        parser.add_argument(
            "--modified-after-hours", type=float, default=None,
            help="Only check the files which are modified in the last N hours. Default: all files"
        )

    def handle(self, *args, **options):
        execute = options["execute"]
        modified_after_hours = options["modified_after_hours"]
        modified_after = now() - modified_after_hours * 3600 if modified_after_hours is not None else None
        self.stdout.write(
            f"Scanning the attachments larger than {options['max_size']} bytes ({'EXECUTE' if execute else 'DRY-RUN'})"
        )
        result = attachment_service.delete_oversize_attachments(
            max_size=options["max_size"], modified_after=modified_after, execute=execute
        )
        for key in result["keys"]:
            self.stdout.write(f"[oversize] {key} ({result['sizes'][key]} bytes)")
        self.stdout.write(
            f"Scanned: {result['scanned']} - Oversize: {result['oversize']} ({result['oversize_size']} bytes) - "
            f"{'Deleted' if execute else 'Not deleted'}"
        )
