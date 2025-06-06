# ------------------------------ General code ----------------------------------- #
APP_CODE = [
    {
        "code": "0000",
        "message": "The authentication token is invalid",
        "vi_message": "Token đăng nhập không hợp lệ, gộp chung các trường hợp như token hết hạn, không decode được...v"
    },
    {
        "code": "0002",
        "message": "The account does not have enough permission to execute this operation",
        "vi_message": "Không đủ quyền để thực hiện chức năng này"
    },
    {
        "code": "0004",
        "message": "Invalid data",
        "vi_message": "Dữ liệu không hợp lệ"
    },
    {
        "code": "0005",
        "message": "Method Not Allowed",
        "vi_message": "Phương thức truy cập không hợp lệ"
    },
    {
        "code": "0008",
        "message": "Unknown Error",
        "vi_message": "Khong biet loi"
    },
    {
        "code": "0009",
        "message": "Service temporarily unavailable, try again later.",
        "vi_message": "Service temporarily unavailable, try again later."
    }
]

# ------------------------------ User error code ----------------------------------- #
APP_CODE += [
    {
        "code": "1001",
        "message": "The email address or password is not valid",
        "description": "Đăng nhập thất bại"
    },
    {
        "code": "1002",
        "message": "The authorization code is not valid",
        "description": "Mã OTP không hợp lệ"
    },
    {
        "code": "1003",
        "message": "The account is not activated yet",
        "description": "Tài khoản chưa được kích hoạt"
    },
    {
        "code": "1004",
        "message": "There’s no account associated with this email or username. Try another or create a new account",
        "description": "Tài khoản không tồn tại"
    },
    {
        "code": "1005",
        "message": "This user is not an admin account",
        "description": "Tài khoản này không phải là admin"
    },
    {
        "code": "1006",
        "message": "This group is a base group. So, you can not delete it",
        "description": "Group này là một base group nên bạn không thể xóa"
    },
    {
        "code": "1007",
        "message": "Cannot delete this user because he/she is the sole owner of at least one organization. "
                   "Please delete these organizations",
        "description": "Không thể xóa account này thì account là owner của ít nhất một chương trình. "
                       "Hãy xóa các chương trình mà bạn đã tạo."
    },
    {
        "code": "1008",
        "message": "Login locked due to the enterprise's policy",
        "description": "Bạn đéo thể đăng nhập vì đăng nhập quá số lần quy định của team policy"
    },
    {
        "code": "1009",
        "message": "The account is locked by the enterprise. Please contact your enterprise admin to unblock account",
        "description": "Tài khoản đã bị khóa bởi doanh nghiệp. Vui lòng liên hệ quản trị viên của bạn để mở khóa tài khoản"
    },
    {
        "code": "1010",
        "message": "The account is locked because the Enterprise plan is expired. Please contact your enterprise admin to unblock account",
        "description": "Tài khoản đã bị khóa bởi gói doanh nghiệp đã hết hạn. Vui lòng liên hệ quản trị viên của bạn để mở khóa tài khoản"
    },
    {
        "code": "1011",
        "message": "Your account belongs to Enterprise. Please request or contact your enterprise admin to continue using Locker",
        "description": "Tài khoản của bạn đã thuộc về Doanh nghiệp. Vui lòng yêu cầu tham gia hoặc liên hệ Admin của bạn để tiếp tục sử dụng Locker"
    },
    {
        "code": "1012",
        "message": "The enterprise requires you to enable 2-Step Verification",
        "description": "Doanh nghiệp yêu cầu phải bật xác thực 2 bước"
    }
]

# ----------------------------- Team error code ----------------------------------#
APP_CODE += [
    {
        "code": "3000",
        "message": "You have reached the limit for the number of teams you can create at this time",
        "vi_message": "Bạn đã tạo tối đa số lượng team ở thời điểm này"
    },
    {
        "code": "3001",
        "message": "Can not create a team at this time. Something went wrong, try again later.",
        "vi_message": "Không thể tạo team tại thời điểm hiện tại. Vui lòng thử lại sau"
    },
    {
        "code": "3002",
        "message": "The maximum number of members is reached. Please upgrade your plan",
        "vi_message": "Số lượng thành viên vượt quá giới hạn cho phép. Vui lòng nâng cấp gói của bạn"
    },
    {
        "code": "3003",
        "message": "This team was locked. Please upgrade your plan",
        "vi_message": "Team này đã bị khóa. Vui lòng nâng cấp gói của bạn để tiếp tục sử dụng"
    },
    {
        "code": "3004",
        "message": "The invitation is expired. Please contact admin to re-invite",
        "vi_message": "Lời mời đã hết hạn. Vui lòng liên hệ admin để được mời lại"
    },
    {
        "code": "3005",
        "message": "The domain ownership is not verified",
        "vi_message": "Domain chưa được xác thực"
    },

]

# ----------------------------- PM Folder error code ----------------------------------#
APP_CODE += [
    {
        "code": "4000",
        "message": "You can not delete the default folder of the team",
        "vi_message": "Bạn không thể xóa thư mực mặc định của teams"
    },
]

# ---------------------------- Cipher ------------------------------------------- #
APP_CODE += [
    {
        "code": "5000",
        "message": "This item already belongs to an organization",
        "vi_message": "Bản ghi đã thuộc về một team"
    },
    {
        "code": "5001",
        "message": "You can only select up to 10000 items at a time",
        "vi_message": "Bạn chỉ có thể chọn tối đa 10000 items trong một lần"
    },
    {
        "code": "5002",
        "message": "The maximum number of items is reached. Please check your trash if any",
        "vi_message": "Giới hạn số lượng item đã đạt giới hạn. Vui lòng kiểm tra thùng rác"
    },
    {
        "code": "5003",
        "message": "The maximum size of attachments is reached. Please check your trash if any",
        "vi_message": "Giới hạn kích thước file đính kèm đã đạt giới hạn. Vui lòng kiểm tra thùng rác"
    }
]

# ------------------------------ TRANSACTION --------------------------------#
APP_CODE += [
    {
        "code": "7002",
        "message": "You need to upgrade your plan to execute this operator",
        "vi_message": "Bạn cần nâng cấp gói để thực hiện hạn động này"
    },
    {
        "code": "7003",
        "message": "You don't need to pay to execute this operator",
        "vi_message": "Bạn không cần trả tiền để thực hiện hành động này"
    },
    {
        "code": "7004",
        "message": "You can not cancel the default plan",
        "vi_message": "Bạn không thể hủy gói mặc định"
    },
    {
        "code": "7005",
        "message": "An unexpected error has occurred when connecting to Stripe",
        "vi_message": "Kết nối tới Stripe đã xảy ra lỗi"
    },
    {
        "code": "7006",
        "message": "This card existed",
        "vi_message": "Thẻ đã tồn tại"
    },
    {
        "code": "7007",
        "message": "This user doesn't have any card",
        "vi_message": "User chưa có thẻ nào"
    },
    {
        "code": "7008",
        "message": "This user doesn't have any subscription",
        "vi_message": "User chưa đăng ký gói nào"
    },
    {
        "code": "7009",
        "message": "Your card was declined (insufficient funds, etc...) or your balance is not enough",
    },
    {
        "code": "7010",
        "message": "Your current plan is a subscription plan and does not support this operator"
    },
    {
        "code": "7011",
        "message": "This account's original transaction id is registered. Please use another account or use the family plan",
        "vi_message": "Mobile Transaction đã được sử dụng. Vui lòng dùng tài khoản khác hoặc dùng gói family"
    },
    {
        "code": "7012",
        "message": "The number of members including you has exceeded the limit of the subscription plan allowed",
        "vi_message": "Số lượng thành viên bao gồm cả bạn đã vượt quá giới hạn gói đăng ký cho phép"
    },
    {
        "code": "7013",
        "message": "The trial plan is applied",
        "vi_message": "Gói dùng thử đã được áp dụng"
    },
    {
        "code": "7014",
        "message": "You need to cancel the current plan to upgrade new plan",
        "vi_message": "Bạn cần hủy gói hiện tại để nâng lên gói mới"
    },
    {
        "code": "7015",
        "message": "You are in an Enterprise. Please leave the enterprise to execute this operator",
        "vi_message": "Bạn hiện tại đang ở trong một doanh nghiệp. Vui lòng rời doanh nghiệp để thực hiện hành động này."
    },
    {
        "code": "7016",
        "message": "You are in a Family plan. Please leave the family plan to execute this operator",
        "vi_message": "Bạn hiện tại đang ở trong một gói Family. Vui lòng rời gói để thực hiện hành động này."
    },
    {
        "code": "7017",
        "message": "Your current plan is Lifetime Premium, so you can not execute this operator",
        "vi_message": "Gói của bạn là Lifetime Premium nên bạn không thể thực hiện hành động này"
    },
    {
        "code": "7018",
        "message": "The email you provided was not a valid school email",
        "vi_message": "Email bạn cung cấp không phải là email sinh viên"
    },
    {
        "code": "7019",
        "message": "The school email was claimed",
        "vi_message": "Email sinh viên này đã được nhận gói ưu đãi"
    },
    {
        "code": "7020",
        "message": "The saas license key is not valid",
        "vi_message": "Saas License không hợp lệ"
    },
    {
        "code": "7021",
        "message": "Number of Enterprise members exceeds plan limit",
        "vi_message": "Số lượng thành viên của Enterprise vượt quá giới hạn của gói"
    }
]

# ------------------------------- RELAY ------------------------------------- #
APP_CODE += [
    {
        "code": "8000",
        "message": "The number of relay addresses is reached",
        "vi_message": "Số lượng địa chỉ relay đã đạt tối đa"
    },
    {
        "code": "8001",
        "message": "The number of relay subdomain is reached",
        "vi_message": "Số lượng tên miền phụ đã đạt tối đa"
    },
]

# ------------------------------- Quick Share ------------------------------------- #
APP_CODE += [
    {
        "code": "9000",
        "message": "The quick share is not valid because the email is not valid or the code is not valid",
        "vi_message": "Số lượng địa chỉ relay đã đạt tối đa"
    }
]

# ------------------------------- Backup Credential ------------------------------------- #
APP_CODE += [
    {
        "code": "10000",
        "message": "The number of backup credential is reached",
        "vi_message": "Số lượng backup password đã đạt tối đa"
    }
]


def get_app_code_content(code):
    try:
        return [content for content in APP_CODE if content["code"] == code][0]['message']
    except (IndexError, KeyError):
        raise Exception("Does not have this app_code")
