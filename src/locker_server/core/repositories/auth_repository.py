from typing import Union, Dict
from abc import ABC, abstractmethod


class AuthRepository(ABC):
    @abstractmethod
    def decode_token(self, value: str, secret: str) -> Dict:
        pass

    @abstractmethod
    def get_expired_type(self, token_type_name: str) -> Union[int, float]:
        pass
