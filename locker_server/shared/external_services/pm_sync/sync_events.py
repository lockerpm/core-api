SYNC_EVENT_CIPHER_UPDATE = "cipher_update"
SYNC_EVENT_CIPHER = "cipher"
SYNC_EVENT_CIPHER_DELETE = "cipher_delete"
SYNC_EVENT_CIPHER_RESTORE = "cipher_restore"
SYNC_EVENT_CIPHER_DELETE_PERMANENT = "cipher_delete_permanent"
SYNC_EVENT_CIPHER_SHARE = "cipher_share"
SYNC_EVENT_CIPHER_INVITATION = "cipher_invitation"

SYNC_EVENT_FOLDER_UPDATE = "folder_update"
SYNC_EVENT_FOLDER_DELETE = "folder_delete"

SYNC_EVENT_COLLECTION_UPDATE = "collection_update"
SYNC_EVENT_COLLECTION_DELETE = "collection_delete"

SYNC_EVENT_VAULT = "sync_vault"

SYNC_EVENT_ORG_KEY = "sync_org_key"

SYNC_SETTINGS = "sync_settings"

SYNC_EMERGENCY_ACCESS = "emergency_access"

SYNC_QUICK_SHARE = "quick_share"

SYNC_EVENT_GROUP_CREATE = "group_create"
SYNC_EVENT_GROUP_UPDATE = "group_update"
SYNC_EVENT_GROUP_DELETE = "group_delete"

SYNC_EVENT_MEMBER_INVITATION = "member_invitation"
SYNC_EVENT_MEMBER_ACCEPTED = "member_accepted"
SYNC_EVENT_MEMBER_CONFIRMED = "member_confirmed"
SYNC_EVENT_MEMBER_REJECT = "member_rejected"
SYNC_EVENT_MEMBER_REMOVE = "member_removed"
SYNC_EVENT_MEMBER_UPDATE = "member_updated"

SYNC_EVENT_ENTERPRISE_POLICY_UPDATE = "enterprise_policy_update"

SYNC_EVENT_PLAN_UPDATE = "user_update_plan"

LIST_DELETE_SYNC_CACHE_EVENTS = [
    SYNC_EVENT_CIPHER_UPDATE, SYNC_EVENT_CIPHER, SYNC_EVENT_CIPHER_DELETE, SYNC_EVENT_CIPHER_RESTORE,
    SYNC_EVENT_CIPHER_DELETE_PERMANENT, SYNC_EVENT_CIPHER_SHARE,
    SYNC_EVENT_FOLDER_UPDATE, SYNC_EVENT_FOLDER_DELETE,
    SYNC_EVENT_COLLECTION_UPDATE, SYNC_EVENT_COLLECTION_DELETE,
    SYNC_EVENT_VAULT, SYNC_EVENT_ORG_KEY,
    SYNC_SETTINGS, SYNC_EMERGENCY_ACCESS,
    SYNC_QUICK_SHARE,
]


SYNC_ACTION_DELETE = "delete"
