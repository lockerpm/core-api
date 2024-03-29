TOKEN_PREFIX = "cs."
TOKEN_TYPE_AUTHENTICATION = "authentication_locker"
TOKEN_TYPE_INVITE_MEMBER = "invite_member"
TOKEN_TYPE_TRIAL_ENTERPRISE = "trial_enterprise"
TOKEN_TYPE_QUICK_SHARE_ACCESS = "quick_share_access"
TOKEN_TYPE_EDUCATION_CLAIM = "education_claim"
TOKEN_TYPE_RESET_PASSWORD = "reset_password"

TOKEN_EXPIRED_TIME_AUTHENTICATION = 30 * 24  # Base on hours
TOKEN_EXPIRED_TIME_INVITE_MEMBER = 24
TOKEN_EXPIRED_TIME_TRIAL_ENTERPRISE = 20 * 60  # 20 minutes
TOKEN_EXPIRED_TIME_EDUCATION_CLAIM = 24 * 60 * 60  # 24 hour
TOKEN_EXPIRED_TIME_RESET_PASSWORD = 7 * 24  # Base on hours
