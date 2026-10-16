UPLOAD_ACTION_ATTACHMENT = "attachment"


# -------------- Limit size ------------- #
LIMIT_SIZE_ATTACHMENT = 52428800        # 50 MB

LIMIT_TOTAL_SIZE_ATTACHMENT = 1073741824    # 1GB

DEFAULT_ATTACHMENT_EXPIRED = 3600

# The expiration of the upload form (presigned PUT url). The quota is reserved for this duration
UPLOAD_FORM_EXPIRED = 600

# The oversize attachments cron only checks the files which are modified in this window (seconds)
OVERSIZE_ATTACHMENT_CHECK_WINDOW = 3 * 3600
