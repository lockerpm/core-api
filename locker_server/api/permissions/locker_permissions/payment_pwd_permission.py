from locker_server.api.permissions.app import APIPermission


class PaymentPwdPermission(APIPermission):
    def has_permission(self, request, view):
        if view.action in ["webhook_create", "webhook_set_status",
                           "webhook_unpaid_subscription", "webhook_cancel_subscription",
                           "upgrade_trial_enterprise_by_code", "calc_lifetime_public", "calc_subscription_public"]:
            return True
        elif view.action in ["list", "set_invoice_status", "user_invoices", "admin_upgrade_plan", "statistic_income",
                             "statistic_amount", "create_refund", "statistic_net"]:
            return self.is_admin(request)
        return self.is_auth(request)

    def has_object_permission(self, request, view, obj):
        if view.action in ["webhook_create", "webhook_set_status",
                           "webhook_unpaid_subscription", "webhook_cancel_subscription"]:
            return True
        return super(PaymentPwdPermission, self).has_object_permission(request, view, obj)
