from django.core.management import BaseCommand

from locker_server.containers.containers import attachment_service
from locker_server.shared.constants.attachments import ATTACHMENT_CONTENT_TYPE
from locker_server.shared.utils.app import now


class Command(BaseCommand):
    help = f"Find (and replace with --execute) the attachment files whose content type is not {ATTACHMENT_CONTENT_TYPE}"

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute", action="store_true", help="Replace the content types. Default: dry-run"
        )
        parser.add_argument(
            "--modified-after-hours", type=float, default=None,
            help="Only check the files which are modified in the last N hours. Default: all files"
        )

    def handle(self, *args, **options):
        execute = options["execute"]
        modified_after_hours = options["modified_after_hours"]
        modified_after = now() - modified_after_hours * 3600 if modified_after_hours is not None else None
        self.stdout.write(
            f"Scanning the attachments whose content type is not {ATTACHMENT_CONTENT_TYPE} "
            f"({'EXECUTE' if execute else 'DRY-RUN'})"
        )
        result = attachment_service.fix_attachment_content_types(modified_after=modified_after, execute=execute)
        for key in result["keys"]:
            self.stdout.write(f"[invalid] {key} ({result['content_types'][key]})")
        self.stdout.write(
            f"Scanned: {result['scanned']} - Invalid: {result['invalid']} - "
            f"{'Fixed: ' + str(result['fixed']) if execute else 'Not fixed'}"
        )
