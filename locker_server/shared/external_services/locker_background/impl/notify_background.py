from datetime import datetime

import requests

from django.conf import settings
from django.db import connection

from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.shared.constants.transactions import PAYMENT_STATUS_PAID
from locker_server.shared.external_services.locker_background.background import LockerBackground
from locker_server.shared.external_services.requester.retry_requester import requester
from locker_server.shared.utils.app import now


API_NOTIFY_PAYMENT = "{}/micro_services/cystack_platform/payments".format(settings.GATEWAY_API)
API_NOTIFY_LOCKER = "{}/micro_services/cystack_platform/pm/notify".format(settings.GATEWAY_API)
HEADERS = {
    'User-agent': 'Locker Password Manager API',
    "Authorization": settings.MICRO_SERVICE_USER_AUTH
}


class NotifyBackground(LockerBackground):
    def downgrade_plan(self, user_id, old_plan, downgrade_time, scope, **metadata):
        from locker_server.containers.containers import user_service
        try:
            try:
                user_plan = user_service.get_current_plan(user=user_service.retrieve_by_id(user_id=user_id))
                current_plan = f"{user_plan.pm_plan.name} Plan"
                # Don't notify if the current plan is the same old plan
                if user_plan.pm_plan.name == old_plan or current_plan == old_plan:
                    return
            except UserDoesNotExistException:
                current_plan = "Free Plan"
            url = API_NOTIFY_PAYMENT + "/notify_downgrade"
            notification_data = {
                "user_id": user_id,
                "old_plan": old_plan,
                "current_plan": current_plan,
                "downgrade_time": downgrade_time,
                "payment_data": metadata.get("payment_data"),
                "scope": scope
            }
            requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
        except requests.ConnectionError:
            self.log_error(func_name="downgrade_plan")
        finally:
            if self.background:
                connection.close()

    def cancel_plan(self, user_id, old_plan, expired_date=None, scope=settings.SCOPE_PWD_MANAGER):
        try:
            url = API_NOTIFY_PAYMENT + "/notify_cancel"
            notification_data = {
                "user_id": user_id,
                "old_plan": old_plan,
                "expired_date": expired_date,
                "scope": scope
            }
            requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
        except requests.ConnectionError:
            self.log_error(func_name="cancel_plan")
        finally:
            if self.background:
                connection.close()

    def banking_expiring(self, user_id, current_plan, start_period, end_period, payment_method, scope,
                         payment_url=None):
        try:
            url = API_NOTIFY_PAYMENT + "/notify_expiring"
            notification_data = {
                "user_id": user_id,
                "current_plan": current_plan,
                "start_period": start_period,
                "end_period": end_period,
                "payment_method": payment_method,
                "scope": scope,
                "payment_url": payment_url,
                "demo": False
            }
            requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
        except requests.ConnectionError:
            self.log_error(func_name="banking_expiring")
        finally:
            if self.background:
                connection.close()

    def trial_successfully(self, user_id: int, plan: str, payment_method: str, duration: str):
        url = API_NOTIFY_PAYMENT + "/notify_trial"
        try:
            notification_data = {
                "user_id": user_id,
                "scope": settings.SCOPE_PWD_MANAGER,
                "plan": plan,
                "payment_method": payment_method,
                "duration": duration
            }
            requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
        except requests.ConnectionError:
            self.log_error(func_name="trial_successfully")
        finally:
            if self.background:
                connection.close()

    def trial_enterprise_successfully(self, user_id: int, scope: str = None):
        url = API_NOTIFY_PAYMENT + "/notify_trial_enterprise"
        try:
            notification_data = {"user_id": user_id, "scope": scope or settings.SCOPE_PWD_MANAGER}
            requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
        except requests.ConnectionError:
            self.log_error(func_name="trial_enterprise_successfully")
        finally:
            if self.background:
                connection.close()

    def pay_successfully(self, payment, payment_platform="Stripe"):
        """
        Notify when a payment invoice was paid
        :param payment: (obj) Payment invoice
        :param payment_platform: (str)
        :return:
        """
        url = API_NOTIFY_PAYMENT + "/notify_payment_success"

        try:
            scope = payment.scope
            metadata = payment.metadata
            number_members = metadata.get("number_members") or 1
            user = payment.user

            from locker_server.containers.containers import user_service
            current_plan = user_service.get_current_plan(user=user)
            enterprise = user_service.get_default_enterprise(user_id=user.user_id)
            payment_data = {
                "enterprise_id": enterprise.id if enterprise else None,
                "enterprise_name": enterprise.name if enterprise else None,
                "stripe_invoice_id": payment.stripe_invoice_id,
                "plan_name": current_plan.pm_plan.name,
                "plan_price": current_plan.pm_plan.get_price(currency=payment.currency, duration=payment.duration),
                "number_members": int(number_members),
                "start_period": current_plan.start_period,
                "end_period": current_plan.end_period
            }
            subtotal = payment.total_price + payment.discount
            notification_data = {
                "user_id": payment.user.user_id,
                "status": payment.status,
                "paid": True if payment.status == PAYMENT_STATUS_PAID else False,
                "scope": payment.scope,
                "payment_id": payment.payment_id,
                "order_date": payment.get_created_time_str(),
                "total": payment.total_price,
                "subtotal": subtotal,
                "discount": payment.discount,
                "currency": payment.currency,
                "duration": payment.duration,
                "plan": payment.plan,
                "customer": payment.get_customer_dict(),
                "payment_method": payment.payment_method,
                "payment_data": payment_data,
                "payment_platform": payment_platform
            }
            requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
        except Exception:
            self.log_error(func_name="notify_pay_successfully")
        finally:
            if self.background:
                connection.close()

    def pay_failed(self, **data):
        url = API_NOTIFY_PAYMENT + "/notify_payment_failed"
        try:
            notification_data = {
                "scope": data.get("scope"),
                "user_id": data.get("user_id"),
                "check_time": "{} (UTC)".format(
                    datetime.utcfromtimestamp(now()).strftime('%H:%M:%S %d-%m-%Y')
                ),
                "current_attempt": data.get("current_attempt"),
                "next_attempt": data.get("next_attempt"),
            }
            requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
        except Exception:
            self.log_error(func_name="notify_pay_failed")
        finally:
            if self.background:
                connection.close()

    def notify_tutorial(self, job, user_ids):
        url = API_NOTIFY_LOCKER + "/tutorial"
        try:
            notification_data = {"job": job, "user_ids": user_ids}
            requester(
                method="POST", url=url, headers=HEADERS, data_send=notification_data,
                retry=True, max_retries=3, timeout=5
            )
        except Exception:
            self.log_error(func_name="notify_tutorial")
        finally:
            if self.background:
                connection.close()

    def notify_add_group_member_to_share(self, data):
        url = API_NOTIFY_LOCKER + "/group_member_to_share"
        try:
            requester(
                method="POST", url=url, headers=HEADERS, data_send=data,
                retry=True, max_retries=3, timeout=5
            )
        except Exception:
            self.log_error(func_name="notify_tutorial")
        finally:
            if self.background:
                connection.close()

    def notify_enterprise_next_cycle(self, data):
        url = API_NOTIFY_LOCKER + "/enterprise_next_cycle"
        try:
            requester(
                method="POST", url=url, headers=HEADERS, data_send=data,
                retry=True, max_retries=3, timeout=5
            )
        except Exception:
            self.log_error(func_name="notify_enterprise_next_cycle")
        finally:
            if self.background:
                connection.close()

    def notify_enterprise_export(self, data):
        url = API_NOTIFY_LOCKER + "/enterprise_export"
        try:
            requester(
                method="POST", url=url, headers=HEADERS, data_send=data,
                retry=True, max_retries=3, timeout=5
            )
        except Exception:
            self.log_error(func_name="notify_enterprise_export")
        finally:
            if self.background:
                connection.close()

    def notify_locker_mail(self, **data):
        url = API_NOTIFY_LOCKER + "/mail"
        try:
            if "scope" not in data:
                data.update({"scope": settings.SCOPE_PWD_MANAGER})
            requester(method="POST", url=url, headers=HEADERS, data_send=data, retry=True, max_retries=3, timeout=5)
        except Exception:
            self.log_error(func_name="notify_locker_mail")
        finally:
            if self.background:
                connection.close()
