FCM_TYPE_NOTIFICATION = "notification"

FCM_TYPE_NEW_SHARE = "new_share_item"
FCM_TYPE_CONFIRM_SHARE = "confirm_share_item"
FCM_TYPE_ACCEPT_SHARE = "accept_share_item"
FCM_TYPE_REJECT_SHARE = "reject_share_item"
FCM_TYPE_NEW_SHARE_GROUP_MEMBER = "new_share_group_member"
FCM_TYPE_CONFIRM_SHARE_GROUP_MEMBER_ADDED = "confirm_share_group_member_added"
FCM_TYPE_NEW_SHARE_AFTER_OWNER_CONFIRMED = "new_share_item_after_owner_confirmed"

FCM_TYPE_EMERGENCY_INVITE = "emergency_invite"
FCM_TYPE_EMERGENCY_ACCEPT_INVITATION = "emergency_accept_invitation"
FCM_TYPE_EMERGENCY_REJECT_INVITATION = "emergency_reject_invitation"
FCM_TYPE_EMERGENCY_INITIATE = "emergency_access_initiate"
FCM_TYPE_EMERGENCY_APPROVE_REQUEST = "emergency_access_approve_request"
FCM_TYPE_EMERGENCY_REJECT_REQUEST = "emergency_access_reject_request"


FCM_TYPE_PWD_TIP_TRICK = "password_tip_trick"


FCM_NOTIFICATIONS = {
    FCM_TYPE_NEW_SHARE: {
        "vi": {
            "title": "Locker",
            "body": "Bạn đã được chia sẻ một {type_name}"
        },
        "en": {
            "title": "Locker",
            "body": "You have a new shared {type_name}"
        }
    },
    FCM_TYPE_CONFIRM_SHARE: {
        "vi": {
            "title": "Locker",
            "body": "Vui lòng xác nhận yêu cầu chia sẻ của bạn"
        },
        "en": {
            "title": "Locker",
            "body": "Please confirm your sharing request"
        }
    },
    FCM_TYPE_ACCEPT_SHARE: {
        "vi": {
            "title": "Locker",
            "body": "{recipient_name} đã chấp nhận {type_name} bạn chia sẻ"
        },
        "en": {
            "title": "Locker",
            "body": "{recipient_name} has accepted the {type_name} you share"
        }
    },
    FCM_TYPE_REJECT_SHARE: {
        "vi": {
            "title": "Locker",
            "body": "{recipient_name} đã từ chối {type_name} bạn chia sẻ"
        },
        "en": {
            "title": "Locker",
            "body": "{recipient_name} has rejected the {type_name} you share"
        }
    },
    FCM_TYPE_EMERGENCY_INVITE: {
        "vi": {
            "title": "Locker",
            "body": "{grantor_name} đã thêm bạn làm Liên hệ khẩn cấp"
        },
        "en": {
            "title": "Locker",
            "body": "{grantor_name} has invited you to be emergency access contact"
        }
    },
    FCM_TYPE_EMERGENCY_ACCEPT_INVITATION: {
        "vi": {
            "title": "Locker",
            "body": "{grantee_name} đã chấp nhận trở thành Liên hệ khẩn cấp của bạn"
        },
        "en": {
            "title": "Locker",
            "body": "{grantee_name} has accepted your emergency access invitation"
        }
    },
    FCM_TYPE_EMERGENCY_REJECT_INVITATION: {
        "vi": {
            "title": "Locker",
            "body": "{grantee_name} đã từ chối trở thành Liên hệ khẩn cấp của bạn"
        },
        "en": {
            "title": "Locker",
            "body": "{grantee_name} has rejected your emergency access invitation"
        }
    },
    FCM_TYPE_EMERGENCY_INITIATE: {
        "vi": {
            "title": "Locker",
            "body": "{grantee_name} đã yêu cầu {type} tài khoản Locker của bạn"
        },
        "en": {
            "title": "Locker",
            "body": "{grantee_name} has requested to {type} your Locker account"
        }
    },
    FCM_TYPE_EMERGENCY_APPROVE_REQUEST: {
        "vi": {
            "title": "Locker",
            "body": "{grantor_name} đã chấp nhận yêu cầu {type} tài khoản Locker của bạn"
        },
        "en": {
            "title": "Locker",
            "body": "{grantor_name} approved your request to {type} their Locker account"
        }
    },
    FCM_TYPE_EMERGENCY_REJECT_REQUEST: {
        "vi": {
            "title": "Locker",
            "body": "{grantor_name} đã từ chối yêu cầu {type} tài khoản Locker của bạn"
        },
        "en": {
            "title": "Locker",
            "body": "{grantor_name} has rejected your request to {type} their Locker account"
        }
    },
    FCM_TYPE_PWD_TIP_TRICK: {
        "vi": {
            "title": "Locker",
            "body": "{title}"
        },
        "en": {
            "title": "Locker",
            "body": "{title}"
        }
    }
}
