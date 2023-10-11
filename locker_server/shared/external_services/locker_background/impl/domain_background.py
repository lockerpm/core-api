from django.conf import settings
from django.db import connection

from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_MEMBER, E_MEMBER_STATUS_INVITED
from locker_server.shared.external_services.locker_background.background import LockerBackground
from locker_server.shared.external_services.requester.retry_requester import requester
from locker_server.shared.external_services.user_notification.list_jobs import PWD_VERIFY_DOMAIN_SUCCESS, \
    PWD_JOIN_YOUR_ORG
from locker_server.shared.external_services.user_notification.notification_sender import NotificationSender, \
    SENDING_SERVICE_MAIL
from locker_server.shared.utils.app import diff_list, now

API_NOTIFY_DOMAIN = "{}/micro_services/cystack_platform/pm/domains".format(settings.GATEWAY_API)
HEADERS = {
    'User-agent': 'Locker Password Manager API',
    "Authorization": settings.MICRO_SERVICE_USER_AUTH
}


class DomainBackground(LockerBackground):
    def domain_verified(self, owner_user_id: int, domain):
        from locker_server.containers.containers import user_service, enterprise_member_service
        try:
            enterprise = domain.enterprise
            member_user_ids = enterprise_member_service.list_enterprise_member_user_ids(
                **{"enterprise_id": enterprise.enterprise_id}
            )
            existed_user_ids = [e for e in member_user_ids if e is not None]

            if not settings.SELF_HOSTED:
                url = API_NOTIFY_DOMAIN + "/verified"
                notification_data = {
                    "owner": owner_user_id,
                    "domain": domain.domain,
                    "existed_user_ids": list(existed_user_ids),
                    "enterprise_name": enterprise.name,
                }
                res = requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
                if res.status_code != 200:
                    self.log_error(
                        func_name="domain_verified",
                        tb=f"Cannot get list locker users with this domain: {domain.domain}\n"
                           f"{url} {res.status_code} {res.status_code}"
                    )
                    return
                else:
                    member_user_ids = res.json().get("member_user_ids", [])
            else:
                domain_address = domain.domain
                org_name = enterprise.name
                existed_user_ids = [e for e in existed_user_ids if e is not None]
                # Sending mail
                NotificationSender(
                    job=PWD_VERIFY_DOMAIN_SUCCESS, scope=settings.SCOPE_PWD_MANAGER, services=[SENDING_SERVICE_MAIL]
                ).send(**{"user_ids": [owner_user_id], "domain": domain_address, "cc": []})

                # Finding all locker users who have domain mail
                if domain_address in settings.LOCKER_TEST_DOMAINS:
                    locker_user_ids = user_service.list_user_ids(**{
                        "exclude_user_ids": existed_user_ids,
                        "emails": [settings.LOCKER_TEST_DOMAIN_MEMBERS]
                    })

                else:
                    locker_user_ids = user_service.list_user_ids(**{
                        "exclude_user_ids": existed_user_ids,
                        "email_endswith": "@{}".format(domain)
                    })
                NotificationSender(
                    job=PWD_JOIN_YOUR_ORG, scope=settings.SCOPE_PWD_MANAGER, services=[SENDING_SERVICE_MAIL]
                ).send(**{"user_ids": list(locker_user_ids), "org_name": org_name})
                member_user_ids = list(set(locker_user_ids))

            existed_member_user_ids = enterprise_member_service.list_enterprise_member_user_ids(**{
                "user_ids": member_user_ids
            })
            non_existed_member_user_ids = diff_list(member_user_ids, existed_member_user_ids)

            user_ids = user_service.list_user_ids(**{"user_ids": non_existed_member_user_ids})

            members = []
            for user_id in user_ids:
                members.append({
                    "enterprise_id": enterprise.enterprise_id,
                    "user_id": user_id,
                    "role_id": E_MEMBER_ROLE_MEMBER,
                    "domain_id": domain.domain_id,
                    "status": E_MEMBER_STATUS_INVITED,
                    "is_default": False,
                    "is_primary": False,
                    "access_time": now()
                })
            return enterprise_member_service.create_multiple_members(members_data=members)
        except Exception as e:
            self.log_error(func_name="domain_verified")
        finally:
            if self.background:
                connection.close()

    def domain_unverified(self, owner_user_id: int, domain):
        try:
            url = API_NOTIFY_DOMAIN + "/unverified"
            enterprise = domain.enterprise
            existed_user_ids = enterprise.enterprise_members.exclude(
                user_id__isnull=True
            ).values_list('user_id', flat=True)
            admins = list(enterprise.enterprise_members.filter(
                role_id=E_MEMBER_ROLE_ADMIN, status=E_MEMBER_STATUS_CONFIRMED, is_activated=True
            ).values_list('user_id', flat=True))

            notification_data = {
                "owner": owner_user_id,
                "domain": domain.domain,
                "existed_user_ids": list(existed_user_ids),
                "enterprise_name": enterprise.name,
                "cc": admins
            }
            res = requester(method="POST", url=url, headers=HEADERS, data_send=notification_data)
            if res.status_code != 200:
                self.log_error(
                    func_name="domain_unverified",
                    tb=f"Cannot send notify domain verification failed: {domain.domain}\n"
                       f"{url} {res.status_code} {res.status_code}"
                )
        except Exception as e:
            self.log_error(func_name="domain_unverified")
        finally:
            if self.background:
                connection.close()

    def domain_auto_approve(self, user_id_update_domain, domain, ip_address: str = None):
        try:
            enterprise = domain.enterprise
            # Get the number of billing members
            members = domain.enterprise_members.filter(status__in=[E_MEMBER_STATUS_REQUESTED])
            member_events_data = []
            billing_members = members.count()
            for member in members:
                member_events_data.append({
                    "acting_user_id": user_id_update_domain,
                    "user_id": member.user_id,
                    "team_id": enterprise.id,
                    "team_member_id": member.id,
                    "type": EVENT_E_MEMBER_CONFIRMED,
                    "ip_address": ip_address
                })

            # Update the Stripe subscription
            if billing_members > 0:
                from cystack_models.factory.payment_method.payment_method_factory import PaymentMethodFactory
                from cystack_models.factory.payment_method.payment_method_factory import \
                    PaymentMethodNotSupportException
                try:
                    PaymentMethodFactory.get_method(
                        user=enterprise.get_primary_admin_user(), scope=settings.SCOPE_PWD_MANAGER,
                        payment_method=PAYMENT_METHOD_CARD
                    ).update_quantity_subscription(amount=billing_members)
                except (PaymentMethodNotSupportException, ObjectDoesNotExist):
                    pass
            # Auto accept all requested members
            members.update(status=E_MEMBER_STATUS_CONFIRMED)
            # Log events
            Event.create_multiple_by_enterprise_members(member_events_data)
        except Exception as e:
            self.log_error(func_name="domain_auto_approve")
        finally:
            if self.background:
                connection.close()
