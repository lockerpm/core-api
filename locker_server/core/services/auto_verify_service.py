import base64
from typing import Optional, Dict

from cryptography.hazmat.primitives.asymmetric import ed25519, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_public_key

from locker_server.core.entities.user.device import Device
from locker_server.core.exceptions.device_exception import DeviceDoesNotExistException
from locker_server.core.exceptions.user_exception import UserAuthFailedException
from locker_server.core.repositories.device_repository import DeviceRepository
from locker_server.shared.utils.app import now


class AutoVerifyService:
    """
    This class represents Use Cases related Auto verify
    """

    def __init__(self, device_repository: DeviceRepository, ):
        self.device_repository = device_repository

    def update_auto_verify(self, user_id: int, device_identifier: str, h: str, p: str) -> Optional[Device]:
        device = self.device_repository.update_auto_verify(
            user_id=user_id, device_identifier=device_identifier, h=h, p=p,
        )
        if not device:
            raise DeviceDoesNotExistException
        return device

    def get_auto_verify(self, user_id: int, device_identifier: str, ts: float, s: str, pk: str) -> Dict:
        """
        :param user_id:
        :param device_identifier:
        :param ts:
        :param s: Sig
        :param pk: Public Key
        :return:
        """
        device = self.device_repository.get_device_by_identifier(user_id=user_id, device_identifier=device_identifier)
        if not device:
            raise DeviceDoesNotExistException
        if ts + 20000 <= now() * 1000:
            raise UserAuthFailedException
        if not device.p:
            raise UserAuthFailedException

        public_key = base64.b64decode(device.p)
        signature = base64.b64decode(s)
        m = f"{ts}.{pk}".encode("utf-8")
        try:
            verify_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
            verify_key.verify(signature, m)
        except Exception:
            raise UserAuthFailedException
        return {
            "h": self.encrypt_h(device.h, pk),
        }

    @staticmethod
    def encrypt_h(message, public_key_string):
        # Convert the base64 encoded public key to binary
        public_key_bytes = base64.b64decode(public_key_string)

        # Load the public key
        public_key = load_der_public_key(public_key_bytes)

        # Convert the message to bytes
        message_bytes = message.encode('utf-8')

        # Encrypt the message
        encrypted = public_key.encrypt(
            message_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Return the encrypted message as base64
        return base64.b64encode(encrypted).decode('utf-8')
