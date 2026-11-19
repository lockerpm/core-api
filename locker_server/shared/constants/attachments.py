UPLOAD_ACTION_ATTACHMENT = "attachment"

# The attachments are encrypted by the clients, so they are always binary data. This content type is signed in the
# upload form, so the files can not be served as HTML/SVG... from the attachment domain
ATTACHMENT_CONTENT_TYPE = "application/octet-stream"

# -------------- Limit size ------------- #
LIMIT_SIZE_ATTACHMENT = 52428800        # 50 MB

LIMIT_TOTAL_SIZE_ATTACHMENT = 1073741824    # 1GB

DEFAULT_ATTACHMENT_EXPIRED = 3600

# The download url of a quick share attachment is short-lived (the clients download the file right after getting it),
# so the url does not outlive the access of the quick share
QUICK_SHARE_ATTACHMENT_URL_EXPIRED = 300

# The expiration of the upload form (presigned PUT url). The quota is reserved for this duration
UPLOAD_FORM_EXPIRED = 600

# The oversize attachments cron only checks the files which are modified in this window (seconds)
OVERSIZE_ATTACHMENT_CHECK_WINDOW = 3 * 3600
