from webauthn.helpers.structs import AuthenticatorTransport


BACKUP_CREDENTIAL_MAX = 6
CREDENTIAL_TYPE_HMAC = "hmac"
CREDENTIAL_TYPE_PRF = "prf"
LIST_CREDENTIAL_TYPE = [CREDENTIAL_TYPE_PRF, CREDENTIAL_TYPE_HMAC]


WEBAUTHN_VALID_TRANSPORTS = [
    AuthenticatorTransport.USB,
    AuthenticatorTransport.NFC,
    AuthenticatorTransport.BLE,
    AuthenticatorTransport.HYBRID,
    AuthenticatorTransport.INTERNAL,
]
