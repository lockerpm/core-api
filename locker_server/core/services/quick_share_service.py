from typing import Dict, List, Optional, Tuple

from locker_server.core.entities.cipher.cipher import Cipher
from locker_server.core.entities.quick_share.quick_share import QuickShare
from locker_server.core.exceptions.cipher_exception import CipherDoesNotExistException
from locker_server.core.exceptions.quick_share_exception import QuickShareDoesNotExistException, \
    QuickShareNotValidAccessException, QuickShareRequireOTPException, QuickShareAttachmentNotValidException
from locker_server.core.repositories.cipher_repository import CipherRepository
from locker_server.core.repositories.enterprise_repository import EnterpriseRepository
from locker_server.core.repositories.quick_share_repository import QuickShareRepository
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.shared.constants.ciphers import MAP_CIPHER_TYPE_STR
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.constants.event import EVENT_ITEM_QUICK_SHARE_CREATED
from locker_server.shared.external_services.locker_background.background_factory import BackgroundFactory
from locker_server.shared.external_services.locker_background.constants import BG_EVENT
from locker_server.shared.external_services.pm_sync import PwdSync, SYNC_QUICK_SHARE
from locker_server.shared.utils.app import now
from locker_server.shared.utils.attachments import normalize_attachment_key, parse_attachment_key


class QuickShareService:
    """
    This class represents Use Cases related QuickShare
    """
    def __init__(self,
                 quick_share_repository: QuickShareRepository,
                 cipher_repository: CipherRepository,
                 user_repository: UserRepository,
                 enterprise_repository: EnterpriseRepository):
        self.quick_share_repository = quick_share_repository
        self.cipher_repository = cipher_repository
        self.user_repository = user_repository
        self.enterprise_repository = enterprise_repository

    def get_by_id(self, quick_share_id: str) -> Optional[QuickShare]:
        quick_share = self.quick_share_repository.get_by_id(quick_share_id=quick_share_id)
        if not quick_share:
            raise QuickShareDoesNotExistException
        return quick_share

    def get_by_access_id(self, access_id: str) -> Optional[QuickShare]:
        quick_share = self.quick_share_repository.get_by_access_id(access_id=access_id)
        if not quick_share:
            raise QuickShareDoesNotExistException
        return quick_share

    def list_user_quick_shares(self, user_id: int):
        cipher_ids = self.cipher_repository.get_cipher_ids_created_by_user(user_id=user_id)
        quick_shares = self.quick_share_repository.list_quick_shares(**{
            "cipher_ids": cipher_ids
        })
        return quick_shares

    @staticmethod
    def _list_attachments(data) -> List[Dict]:
        if not isinstance(data, dict):
            return []
        return [attachment for attachment in (data.get("attachments") or []) if isinstance(attachment, dict)]

    @classmethod
    def _list_attachment_keys(cls, data) -> List[str]:
        """
        The normalized storage keys of the attachments in the data of a cipher (or a quick share)
        """
        keys = [normalize_attachment_key(attachment.get("url")) for attachment in cls._list_attachments(data)]
        return [key for key in keys if key]

    @classmethod
    def _normalize_attachments(cls, cipher: Cipher, attachments: List[Dict]) -> List[Dict]:
        """
        The quick share only refers the attachments of its cipher. The urls are normalized to the storage keys
        :raise QuickShareAttachmentNotValidException: The attachment does not belong to the cipher
        """
        cipher_attachment_keys = set(cls._list_attachment_keys(cipher.data))
        attachment_ids = set()
        normalized_attachments = []
        for attachment in attachments:
            parsed_key = parse_attachment_key(attachment.get("url"))
            if not parsed_key:
                raise QuickShareAttachmentNotValidException
            key, attachment_cipher_id = parsed_key
            if attachment_cipher_id != cipher.cipher_id or key not in cipher_attachment_keys:
                raise QuickShareAttachmentNotValidException
            attachment_id = attachment.get("id")
            if not attachment_id or attachment_id in attachment_ids:
                raise QuickShareAttachmentNotValidException
            attachment_ids.add(attachment_id)
            normalized_attachments.append({**attachment, "url": key})
        return normalized_attachments

    def _validate_quick_share_attachments(self, user_id: int, quick_share_data: Dict) -> Dict:
        detail_data = quick_share_data.get("data")
        attachments = self._list_attachments(detail_data)
        if not attachments:
            return quick_share_data
        cipher_id = quick_share_data.get("cipher_id")
        # The user must still be able to view the cipher in the vault (the same scope as the attachment urls).
        # E.g. a member created this cipher in a sharing folder, then left the sharing team
        if not self.cipher_repository.get_multiple_by_user(user_id=user_id, filter_ids=[cipher_id]):
            raise CipherDoesNotExistException
        cipher = self.cipher_repository.get_by_id(cipher_id=cipher_id)
        if not cipher:
            raise CipherDoesNotExistException
        detail_data["attachments"] = self._normalize_attachments(cipher=cipher, attachments=attachments)
        return quick_share_data

    def create_user_quick_share(self, user_id: int, ip=None, **quick_share_data):
        """
        :raise CipherDoesNotExistException: The user can not view the cipher of the shared attachments
        :raise QuickShareAttachmentNotValidException: The shared attachments do not belong to the cipher
        """
        quick_share_data = self._validate_quick_share_attachments(user_id=user_id, quick_share_data=quick_share_data)
        quick_share = self.quick_share_repository.create_quick_share(**quick_share_data)
        self.user_repository.delete_sync_cache_data(user_id=user_id)
        PwdSync(event=SYNC_QUICK_SHARE, user_ids=[user_id]).send(
            data={"id": str(quick_share.quick_share_id)}
        )
        # Update activity logs:
        user_enterprise_ids = self.enterprise_repository.list_user_enterprise_ids(user_id=user_id, **{
            "status": E_MEMBER_STATUS_CONFIRMED
        })
        if user_enterprise_ids:
            cipher_id = quick_share_data.get("cipher_id")
            emails = [m.get("email") for m in quick_share_data.get("emails")]
            item_type = MAP_CIPHER_TYPE_STR.get(quick_share.cipher.cipher_type)
            BackgroundFactory.get_background(bg_name=BG_EVENT).run(func_name="create_by_enterprise_ids", **{
                "enterprise_ids": user_enterprise_ids, "user_id": user_id, "acting_user_id": user_id,
                "type": EVENT_ITEM_QUICK_SHARE_CREATED, "ip_address": ip, "cipher_id": cipher_id,
                "metadata": {"item_type": item_type, "emails": emails}
            })

        return quick_share

    def update_user_quick_share(self, quick_share: QuickShare, **quick_share_data):
        quick_share = self.quick_share_repository.update_quick_share(
            quick_share_id=quick_share.quick_share_id, **quick_share_data
        )
        if not quick_share:
            raise QuickShareDoesNotExistException
        return quick_share

    def delete_user_quick_share(self, user_id: int, quick_share: QuickShare):
        self.quick_share_repository.delete_quick_share(quick_share_id=quick_share.quick_share_id)
        self.user_repository.delete_sync_cache_data(user_id=user_id)
        PwdSync(event=SYNC_QUICK_SHARE, user_ids=[user_id]).send(
            data={"id": str(quick_share.quick_share_id)}
        )

    def public_quick_share(self, quick_share: QuickShare,
                           email: str = None, code: str = None, token: str = None) -> Tuple:
        if not self.quick_share_repository.check_valid_access(
            quick_share=quick_share, email=email, code=code, token=token
        ):
            raise QuickShareNotValidAccessException
        quick_share = self.quick_share_repository.update_access_count(
            quick_share_id=quick_share.quick_share_id, email=email
        )

        token = None
        expired_time = None
        if email and code and quick_share.is_public is False:
            token, expired_time = self.quick_share_repository.generate_public_access_token(
                quick_share=quick_share, email=email
            )
        if quick_share.cipher.created_by:
            self.user_repository.delete_sync_cache_data(user_id=quick_share.cipher.created_by.user_id)
        PwdSync(event=SYNC_QUICK_SHARE, user_ids=[quick_share.cipher.created_by.user_id]).send(
            data={"id": str(quick_share.quick_share_id)}
        )

        return quick_share, token, expired_time

    def check_access(self, quick_share: QuickShare, email: str) -> bool:
        return self.quick_share_repository.check_email_access(quick_share=quick_share, email=email)

    def get_email_access(self, quick_share: QuickShare) -> QuickShare:
        # Check the disabled status first, so a disabled quick share does not reveal anything (even require_otp)
        if quick_share.disabled:
            raise QuickShareNotValidAccessException
        if quick_share.max_access_count and quick_share.access_count >= quick_share.max_access_count:
            raise QuickShareNotValidAccessException
        if quick_share.expiration_date and quick_share.expiration_date < now():
            raise QuickShareNotValidAccessException
        if quick_share.is_public is False:
            raise QuickShareRequireOTPException

        # Return data - Update access count
        quick_share = self.quick_share_repository.update_access_count(quick_share_id=quick_share.quick_share_id)
        if quick_share.cipher.created_by:
            self.user_repository.delete_sync_cache_data(user_id=quick_share.cipher.created_by.user_id)
            PwdSync(event=SYNC_QUICK_SHARE, user_ids=[quick_share.cipher.created_by.user_id]).send(
                data={"id": str(quick_share.quick_share_id)}
            )
        return quick_share

    def set_email_otp(self, quick_share: QuickShare, email: str) -> QuickShare:
        code = self.quick_share_repository.set_email_otp(quick_share_id=quick_share.quick_share_id, email=email)
        if not code:
            raise QuickShareDoesNotExistException
        return code

    # ------------------------ QuickShare attachments --------------------- #
    def issue_attachment_token(self, quick_share: QuickShare, email: str = None) -> Optional[Tuple]:
        """
        Issue the token to download the attachments, after the quick share is accessed successfully
        :return: (tuple) (token, expired_time) or None if the quick share does not have any attachments
        """
        if not self._list_attachments(quick_share.data):
            return None
        return self.quick_share_repository.generate_attachment_access_token(quick_share=quick_share, email=email)

    def get_attachment_path(self, quick_share: QuickShare, attachment_id: str, attachment_token: str) -> str:
        """
        Get the storage key of a quick share attachment. The access count is not increased: the access is counted when
        the quick share is accessed (the token is issued)
        :raise QuickShareNotValidAccessException: The token is not valid or the quick share is not available anymore
        :raise QuickShareAttachmentNotValidException: The attachment does not belong to the quick share (or its cipher)
        """
        payload = self.quick_share_repository.validate_attachment_access_token(
            quick_share=quick_share, token=attachment_token
        )
        if not payload:
            raise QuickShareNotValidAccessException
        if quick_share.disabled:
            raise QuickShareNotValidAccessException
        if quick_share.expiration_date and quick_share.expiration_date < now():
            raise QuickShareNotValidAccessException
        if not quick_share.is_public:
            email = payload.get("email")
            share_emails = [share_email.get("email") for share_email in quick_share.emails]
            if not email or email not in share_emails:
                raise QuickShareNotValidAccessException

        attachment = next(
            (a for a in self._list_attachments(quick_share.data) if a.get("id") == attachment_id), None
        )
        if not attachment:
            raise QuickShareAttachmentNotValidException
        key = normalize_attachment_key(attachment.get("url"))
        # The owner can remove the attachment from the cipher after sharing it
        if not key or key not in self._list_attachment_keys(quick_share.cipher.data):
            raise QuickShareAttachmentNotValidException
        return key
