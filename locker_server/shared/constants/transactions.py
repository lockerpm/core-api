TRIAL_PERSONAL_PLAN = 14 * 86400  # 14 days
TRIAL_PERSONAL_DURATION_TEXT = "14 days"
TRIAL_PROMOTION = 6 * 30 * 86400  # 6 months
TRIAL_PROMOTION_DURATION_TEXT = "6 months"

TRIAL_BETA_EXPIRED = 1654016400  # 1/6/2022 00:00:00
TRIAL_TEAM_PLAN = 14 * 86400  # 14 days
TRIAL_TEAM_MEMBERS = 10

REFERRAL_EXTRA_TIME = 86400 * 30  # 30 days
REFERRAL_LIMIT = 3

APPSUMO_PRICE_LIFETIME = 19
APPSUMO_PRICE_LIFETIME_FAMILY = 59

# -------------------- Max attempts ------------------------------ #
MAX_ATTEMPTS = 3

# -------------------- UTM Source Promotion ------------------------ #
UTM_SOURCE_PROMOTIONS = "plans-promotion"
LIST_UTM_SOURCE_PROMOTIONS = [UTM_SOURCE_PROMOTIONS]

# ------------------- Currency ------------------------------------- #
CURRENCY_VND = "VND"
CURRENCY_USD = "USD"
CURRENCY_WHC = "WHC"

LIST_CURRENCY = [CURRENCY_VND, CURRENCY_USD]

# ------------------- Transaction type ------------------------------ #
TRANSACTION_TYPE_PAYMENT = "Payment"
TRANSACTION_TYPE_REFUND = "Refund"
TRANSACTION_TYPE_TRIAL = "Trial"

# ------------------- Payment method -------------------------------- #
PAYMENT_METHOD_CARD = "card"
PAYMENT_METHOD_BANKING = "banking"
PAYMENT_METHOD_WALLET = "wallet"
PAYMENT_METHOD_MOBILE = "mobile"


# ------------------- Payment status -------------------------------- #
PAYMENT_STATUS_FAILED = "failed"  # Failed
PAYMENT_STATUS_PAID = "paid"  # Successful
PAYMENT_STATUS_PENDING = "pending"  # Contact pending
PAYMENT_STATUS_PROCESSING = "processing"  # CyStack banking processing
PAYMENT_STATUS_PAST_DUE = "past_due"  # Subscription failed

LIST_PAYMENT_STATUS = [
    PAYMENT_STATUS_FAILED, PAYMENT_STATUS_PAID, PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_PROCESSING, PAYMENT_STATUS_PAST_DUE
]
# ------------------- Duration types -------------------------------- #
DURATION_MONTHLY = "monthly"
DURATION_HALF_YEARLY = "half_yearly"
DURATION_YEARLY = "yearly"

LIST_DURATION = [DURATION_MONTHLY, DURATION_YEARLY]

# ------------------- Promo code types ------------------------------ #
PROMO_AMOUNT = "amount_off"
PROMO_PERCENTAGE = "percentage_off"

# ------------------- Promo code prefix ---------------------- #
MISSION_REWARD_PROMO_PREFIX = "LKMR-"
EDUCATION_PROMO_PREFIX = "EDU-"

# ------------------- Plan type constants --------------------------- #
PLAN_TYPE_PM_FREE = "pm_free"
PLAN_TYPE_PM_PREMIUM = "pm_premium"
PLAN_TYPE_PM_FAMILY = "pm_family"

PLAN_TYPE_PM_ENTERPRISE = "pm_enterprise"
PLAN_TYPE_PM_ENTERPRISE_STARTUP = "pm_enterprise_startup"

PLAN_TYPE_PM_LIFETIME = "pm_lifetime_premium"
PLAN_TYPE_PM_LIFETIME_FAMILY = "pm_lifetime_family"
PLAN_TYPE_PM_LIFETIME_TEAM = "pm_lifetime_team"

LIST_FAMILY_PLAN = [PLAN_TYPE_PM_FAMILY, PLAN_TYPE_PM_LIFETIME_FAMILY, PLAN_TYPE_PM_LIFETIME_TEAM]

LIST_LIFETIME_PLAN = [PLAN_TYPE_PM_LIFETIME, PLAN_TYPE_PM_LIFETIME_FAMILY, PLAN_TYPE_PM_LIFETIME_TEAM]

LIST_ENTERPRISE_PLAN = [PLAN_TYPE_PM_ENTERPRISE, PLAN_TYPE_PM_ENTERPRISE_STARTUP]

LIST_PLAN_TYPE = [PLAN_TYPE_PM_FREE, PLAN_TYPE_PM_PREMIUM, PLAN_TYPE_PM_FAMILY,
                  PLAN_TYPE_PM_ENTERPRISE, PLAN_TYPE_PM_ENTERPRISE_STARTUP,
                  PLAN_TYPE_PM_LIFETIME, PLAN_TYPE_PM_LIFETIME_FAMILY]

FAMILY_MAX_MEMBER = 6

# ------------- Banking code ----------------------------- #
BANKING_ID_PWD_MANAGER = "LK"
BANKING_ID_WEB_SECURITY = "CW"

# ------------ Saas market ------------------------------- #
SAAS_MARKET_STACK_SOCIAL = "StackSocial"
SAAS_MARKET_DEAL_FUEL = "DealFuel"
SAAS_MARKET_DEAL_MIRROR = "DealMirror"
SAAS_MARKET_PITCH_GROUND = "PitchGround"
LIST_PAYMENT_SOURCE = [SAAS_MARKET_STACK_SOCIAL, SAAS_MARKET_DEAL_FUEL, SAAS_MARKET_PITCH_GROUND]

# ---------- Payment Channel -------------------------- #
PAYMENT_CHANNEL_ORGANIC = "organic"
PAYMENT_CHANNEL_ADS = "ads"
PAYMENT_CHANNEL_AFFILIATE = "affiliate"
