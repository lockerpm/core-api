from django.urls import re_path, include
from rest_framework.routers import DefaultRouter

from locker_server.api.v1_0 import views
from locker_server.shared.caching.api_cache_page import LONG_TIME_CACHE

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    re_path(r'^', include(router.urls))
]

# ------------------------------- Management Command ----------------------------- #
urlpatterns += [

]

# ----------------------------------- Resources ----------------------------- #
urlpatterns += [
    re_path(r'^resources/plans$', LONG_TIME_CACHE(views.ResourcePwdViewSet.as_view({'get': 'plans'}))),
    re_path(r'^resources/enterprise/plans$',
        LONG_TIME_CACHE(views.ResourcePwdViewSet.as_view({'get': 'enterprise_plans'}))),
    re_path(r'^resources/mail_providers$', views.ResourcePwdViewSet.as_view({'get': 'mail_providers'})),
    re_path(r'^resources/market_banners$', views.ResourcePwdViewSet.as_view({'get': 'market_banners'})),
    re_path(r'^resources/banner_data', views.ResourcePwdViewSet.as_view({'get': 'banner_data'})),
]

# ----------------------------------- Tools ----------------------------- #
urlpatterns += [
    re_path(r'^tools/breach$', views.ToolPwdViewSet.as_view({'post': 'breach'})),
    re_path(r'^tools/public/breach$', views.ToolPwdViewSet.as_view({'post': 'public_breach'})),
]

# ----------------------------------- Exclude domains ----------------------------- #
urlpatterns += [
    re_path(r'^exclude_domains$', views.ExcludeDomainPwdViewSet.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^exclude_domains/(?P<pk>[a-z0-9\-]+)$',
        views.ExcludeDomainPwdViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),
]

# ----------------------------------- Users ----------------------------- #
urlpatterns += [
    re_path(r'^users/me$', views.UserPwdViewSet.as_view({'get': 'me', 'put': 'me'})),
    re_path(r'^users/me/prelogin$', views.UserPwdViewSet.as_view({'get': 'prelogin_me'})),
    re_path(r'^users/me/revision_date$', views.UserPwdViewSet.as_view({'get': 'revision_date'})),
    re_path(r'^users/me/onboarding_process$',
        views.UserPwdViewSet.as_view({'get': 'onboarding_process', 'put': 'onboarding_process'})),
    re_path(r'^users/me/block_by_2fa$', views.UserPwdViewSet.as_view({'get': 'block_by_2fa_policy'})),
    re_path(r'^users/me/login_method$', views.UserPwdViewSet.as_view({'get': 'login_method_me'})),
    re_path(r'^users/me/block_policy$', views.UserPwdViewSet.as_view({'get': 'block_policy_me'})),
    re_path(r'^users/me/passwordless_require$', views.UserPwdViewSet.as_view({'get': 'passwordless_require'})),
    re_path(r'^users/me/violation$', views.UserPwdViewSet.as_view({'get': 'violation_me'})),
    re_path(r'^users/me/family', views.UserPwdViewSet.as_view({'get': 'family'})),
    re_path(r'^users/me/delete$', views.UserPwdViewSet.as_view({'post': 'delete_me'})),
    re_path(r'^users/me/purge$', views.UserPwdViewSet.as_view({'post': 'purge_me'})),
    re_path(r'^users/me/password$', views.UserPwdViewSet.as_view({'post': 'password'})),
    re_path(r'^users/me/new_password$', views.UserPwdViewSet.as_view({'post': 'new_password'})),
    re_path(r'^users/me/check_password$', views.UserPwdViewSet.as_view({'post': 'check_password'})),
    re_path(r'^users/me/fcm_id$', views.UserPwdViewSet.as_view({'post': 'fcm_id'})),
    re_path(r'^users/me/devices$', views.UserPwdViewSet.as_view({'get': 'devices'})),
    re_path(r'^users/password_hint$', views.UserPwdViewSet.as_view({'post': 'password_hint'})),
    re_path(r'^users/register$', views.UserPwdViewSet.as_view({'post': 'register'})),
    re_path(r'^users/session$', views.UserPwdViewSet.as_view({'post': 'session'})),
    re_path(r'^users/session/otp$', views.UserPwdViewSet.as_view({'post': 'session_by_otp'})),
    re_path(r'^users/session/revoke_all$', views.UserPwdViewSet.as_view({'post': 'revoke_all_sessions'})),
    re_path(r'^users/invitations/confirmation$', views.UserPwdViewSet.as_view({'get': 'invitation_confirmation'})),
    re_path(r'^users/invitations$', views.UserPwdViewSet.as_view({'get': 'invitations'})),
    re_path(r'^users/invitations/(?P<pk>[a-z0-9\-]+)$', views.UserPwdViewSet.as_view({'put': 'invitation_update'})),
    re_path(r'^users/exist$', views.UserPwdViewSet.as_view({'get': 'exist'})),
    re_path(r'^users/prelogin$', views.UserPwdViewSet.as_view({'post': 'prelogin'})),
    re_path(r'^users/reset_password$', views.UserPwdViewSet.as_view({'post': 'reset_password'})),
    re_path(r'^users/access_token$', views.UserPwdViewSet.as_view({'post': 'access_token'})),
    re_path(r'^users/backup_credentials$', views.BackupCredentialPwdViewSet.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^users/backup_credentials/(?P<pk>[a-zA-Z0-9\-]+)$',
        views.BackupCredentialPwdViewSet.as_view({'get': 'retrieve', 'delete': "destroy"})),

]

# ----------------------------------- Passwordless ----------------------------- #
urlpatterns += [
    re_path(r'^passwordless/credential$',
        views.PasswordlessPwdViewSet.as_view({'get': 'credential', 'post': 'credential', 'delete': 'credential'})),
]

# -------------------------------- Notification Settings ------------------ #
urlpatterns += [
    re_path(r'^notification/settings$', views.NotificationSettingPwdViewSet.as_view({'get': 'list'})),
    re_path(r'^notification/settings/(?P<category_id>[a-z_]+)$',
        views.NotificationSettingPwdViewSet.as_view({'put': 'update'})),
    # TODO: Remove them later
    re_path(r'^notifcation/settings$', views.NotificationSettingPwdViewSet.as_view({'get': 'list'})),
    re_path(r'^notifcation/settings/(?P<category_id>[a-z_]+)$',
        views.NotificationSettingPwdViewSet.as_view({'put': 'update'})),
]

# -------------------------------- Sync ----------------------------------- #
urlpatterns += [
    re_path(r'^sync$', views.SyncPwdViewSet.as_view({'get': 'sync'})),
    re_path(r'^sync/count$', views.SyncPwdViewSet.as_view({'get': 'sync_count'})),
    re_path(r'^sync/ciphers$', views.SyncPwdViewSet.as_view({'get': 'sync_ciphers'})),
    re_path(r'^sync/ciphers/(?P<pk>[0-9a-z\-]+)$', views.SyncPwdViewSet.as_view({'get': 'sync_cipher_detail'})),
    re_path(r'^sync/folders$', views.SyncPwdViewSet.as_view({'get': 'sync_folders'})),
    re_path(r'^sync/folders/(?P<pk>[0-9a-z\-]+)$', views.SyncPwdViewSet.as_view({'get': 'sync_folder_detail'})),
    re_path(r'^sync/collections$', views.SyncPwdViewSet.as_view({'get': 'sync_collections'})),
    re_path(r'^sync/collections/(?P<pk>[0-9a-z\-]+)$', views.SyncPwdViewSet.as_view({'get': 'sync_collection_detail'})),
    re_path(r'^sync/profile$', views.SyncPwdViewSet.as_view({'get': 'sync_profile_detail'})),
    re_path(r'^sync/organizations/(?P<pk>[0-9a-z\-]+)$', views.SyncPwdViewSet.as_view({'get': 'sync_org_detail'})),
    re_path(r'^sync/policies$', views.SyncPwdViewSet.as_view({'get': 'sync_policies'})),
]

# -------------------------------- Ciphers ------------------------------- #
urlpatterns += [
    re_path(r'^ciphers/vaults$', views.CipherPwdViewSet.as_view({'post': 'vaults'})),
    re_path(r'^ciphers/permanent_delete$', views.CipherPwdViewSet.as_view({'put': 'multiple_permanent_delete'})),
    re_path(r'^ciphers/delete$', views.CipherPwdViewSet.as_view({'put': 'multiple_delete'})),
    re_path(r'^ciphers/restore$', views.CipherPwdViewSet.as_view({'put': 'multiple_restore'})),
    re_path(r'^ciphers/move$', views.CipherPwdViewSet.as_view({'put': 'multiple_move'})),
    re_path(r'^ciphers/import$', views.CipherPwdViewSet.as_view({'post': 'import_data'})),
    re_path(r'^ciphers/sync/offline$', views.CipherPwdViewSet.as_view({'post': 'sync_offline'})),
    re_path(r'^ciphers/(?P<pk>[0-9a-z\-]+)$', views.CipherPwdViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
    re_path(r'^ciphers/(?P<pk>[0-9a-z\-]+)/use$', views.CipherPwdViewSet.as_view({'put': 'cipher_use'})),
]

# -------------------------------- Cipher Sharing ------------------------------- #
urlpatterns += [
    re_path(r'^sharing/public_key$', views.SharingPwdViewSet.as_view({'post': 'public_key'})),
    re_path(r'^sharing/invitations$', views.SharingPwdViewSet.as_view({'get': 'invitations'})),
    re_path(r'^sharing/invitations/(?P<pk>[a-z0-9\-]+)$',
        views.SharingPwdViewSet.as_view({'put': 'invitation_update'})),
    re_path(r'^sharing$', views.SharingPwdViewSet.as_view({'put': 'share'})),
    re_path(r'^sharing/multiple$', views.SharingPwdViewSet.as_view({'put': 'multiple_share'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/members/(?P<member_id>[0-9a-z\-]+)$',
        views.SharingPwdViewSet.as_view({'post': 'invitation_confirm', 'put': 'update_role'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/groups/(?P<group_id>[0-9a-z\-]+)$',
        views.SharingPwdViewSet.as_view({'post': 'invitation_group_confirm', 'put': 'update_group_role'})),

    re_path(r'^sharing/(?P<pk>[0-9]+)/members/(?P<member_id>[0-9a-z\-]+)/stop$',
        views.SharingPwdViewSet.as_view({'post': 'stop_share'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/groups/(?P<group_id>[0-9a-z\-]+)/stop$',
        views.SharingPwdViewSet.as_view({'post': 'stop_share'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/leave$', views.SharingPwdViewSet.as_view({'post': 'leave'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/stop$',
        views.SharingPwdViewSet.as_view({'post': 'stop_share_cipher_folder'})),

    re_path(r'^sharing/(?P<pk>[0-9]+)/members$', views.SharingPwdViewSet.as_view({'post': 'add_member'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/folders/(?P<folder_id>[0-9a-z\-]+)$',
        views.SharingPwdViewSet.as_view({'put': 'update_share_folder'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/folders/(?P<folder_id>[0-9a-z\-]+)/delete$',
        views.SharingPwdViewSet.as_view({'post': 'delete_share_folder'})),
    re_path(r'^sharing/(?P<pk>[0-9]+)/folders/(?P<folder_id>[0-9a-z\-]+)/stop$',
        views.SharingPwdViewSet.as_view({'post': 'stop_share_folder'})),

    re_path(r'^sharing/(?P<pk>[0-9]+)/folders/(?P<folder_id>[0-9a-z\-]+)/items$',
        views.SharingPwdViewSet.as_view({'post': 'add_item_share_folder', 'put': 'remove_item_share_folder'})),
    re_path(r'^sharing/my_share$', views.SharingPwdViewSet.as_view({'get': 'my_share'})),

]

# ------------------------------ Quick Shares --------------------------------- #
urlpatterns += [
    re_path(r'^quick_shares$', views.QuickSharePwdViewSet.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^quick_shares/(?P<pk>[0-9a-z-]+)$',
        views.QuickSharePwdViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    re_path(r'^quick_shares/(?P<pk>[0-9A-Z]+)/public$', views.QuickSharePwdViewSet.as_view({'post': 'public'})),
    re_path(r'^quick_shares/(?P<pk>[0-9A-Z]+)/access$',
        views.QuickSharePwdViewSet.as_view({'get': 'access', 'post': 'access'})),
    re_path(r'^quick_shares/(?P<pk>[0-9A-Z]+)/otp$', views.QuickSharePwdViewSet.as_view({'post': 'otp'})),
]

# -------------------------------- Folders ------------------------------- #
urlpatterns += [
    re_path(r'^folders$', views.FolderPwdViewSet.as_view({'post': 'create'})),
    re_path(r'^folders/(?P<pk>[0-9a-z\-]+)$',
        views.FolderPwdViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]

# -------------------------------- Import ------------------------------- #
urlpatterns += [
    re_path(r'^import/folders$', views.ImportDataPwdViewSet.as_view({'post': 'import_folders'})),
    re_path(r'^import/ciphers$', views.ImportDataPwdViewSet.as_view({'post': 'import_ciphers'})),
]

# -------------------------------- Emergency Access ------------------------------- #
urlpatterns += [
    re_path(r'^emergency_access/trusted$', views.EmergencyAccessPwdViewSet.as_view({'get': 'trusted'})),
    re_path(r'^emergency_access/granted$', views.EmergencyAccessPwdViewSet.as_view({'get': 'granted'})),
    re_path(r'^emergency_access/invite$', views.EmergencyAccessPwdViewSet.as_view({'post': 'invite'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)$', views.EmergencyAccessPwdViewSet.as_view({'delete': 'destroy'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/reinvite$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'reinvite'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/public_key$',
        views.EmergencyAccessPwdViewSet.as_view({'get': 'public_key'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/accept$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'accept'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/confirm$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'confirm'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/initiate$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'initiate'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/approve$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'approve'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/reject$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'reject'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/view$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'view'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/takeover$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'takeover'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/password$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'password'})),
    re_path(r'^emergency_access/(?P<pk>[0-9a-z\-]+)/id_password$',
        views.EmergencyAccessPwdViewSet.as_view({'post': 'id_password'})),
]

# ------------------------------- Payment ------------------------------------- #
urlpatterns += [
    re_path(r'^payments/calc$', views.PaymentPwdViewSet.as_view({'post': 'calc'})),
    re_path(r'^payments/trial$', views.PaymentPwdViewSet.as_view({'get': 'check_trial', 'post': 'upgrade_trial'})),
    re_path(r'^payments/trial/enterprise$', views.PaymentPwdViewSet.as_view({
        'post': 'upgrade_trial_enterprise_by_code', 'put': 'generate_trial_enterprise_code'
    })),
    re_path(r'^payments/plan$', views.PaymentPwdViewSet.as_view({'get': 'current_plan', 'post': 'upgrade_plan'})),
    re_path(r'^payments/next_attempt$', views.PaymentPwdViewSet.as_view({'get': 'next_attempt'})),
    re_path(r'^payments/plan/limit$', views.PaymentPwdViewSet.as_view({'get': 'plan_limit'})),
    re_path(r'^payments/plan/cancel$', views.PaymentPwdViewSet.as_view({'post': 'cancel_plan'})),

    re_path(r'^payments/invoices$', views.PaymentPwdViewSet.as_view({'get': 'invoices'})),
    re_path(r'^payments/invoices/(?P<pk>[A-Z0-9]+)$',
        views.PaymentPwdViewSet.as_view({'get': 'retrieve_invoice', 'post': 'retry_invoice'})),
]

# -------------------------------- Family Plan members  ------------------------------------- #
urlpatterns += [
    re_path(r'^family/members$', views.FamilyPwdViewSet.as_view({'get': 'member_list', 'post': 'member_create'})),
    re_path(r'^family/members/(?P<member_id>[0-9]+)$', views.FamilyPwdViewSet.as_view({'delete': 'member_destroy'})),
]

# -------------------------------- Releases  ------------------------------------- #
urlpatterns += [
    re_path(r'^releases$', views.ReleasePwdViewSet.as_view({'get': 'list'})),
    re_path(r'^releases/(?P<client_id>[0-9a-zA-Z_-]+)/(?P<version>[0-9.]+)$',
        LONG_TIME_CACHE(views.ReleasePwdViewSet.as_view({'get': 'retrieve'}))),
    re_path(r'^releases/current$', views.ReleasePwdViewSet.as_view({'get': 'current', 'post': 'current'})),
    re_path(r'^releases/current_version$', views.ReleasePwdViewSet.as_view({'get': 'current_version'})),
    re_path(r'^releases/new$', views.ReleasePwdViewSet.as_view({'post': 'new'}))
]

# --------------------------------- Form submission ---------------------------- #
urlpatterns += [
    re_path(r'^affiliate_submissions$', views.AffiliateSubmissionPwdViewSet.as_view({'post': 'create'})),
]

# ----------------------------------- Admin --------------------------------- #
urlpatterns += [
    re_path(r'^admin/payments/invoices$', views.PaymentPwdViewSet.as_view({'get': 'list'})),
    re_path(r'^admin/payments/refund$', views.PaymentPwdViewSet.as_view({'post': 'create_refund'})),
    re_path(r'^admin/payments/statistic/income$', views.PaymentPwdViewSet.as_view({'get': 'statistic_income'})),
    re_path(r'^admin/payments/statistic/amount$', views.PaymentPwdViewSet.as_view({'get': 'statistic_amount'})),
    re_path(r'^admin/payments/statistic/net$', views.PaymentPwdViewSet.as_view({'get': 'statistic_net'})),

    re_path(r'^admin/payments/invoices/(?P<pk>[A-Z0-9]+)$',
        views.PaymentPwdViewSet.as_view({'put': 'set_invoice_status', 'get': 'retrieve_invoice'})),

    re_path(r'^admin/users/ids$', views.UserPwdViewSet.as_view({'get': 'list_user_ids'})),
    re_path(r'^admin/users$', views.UserPwdViewSet.as_view({'get': 'list_users'})),
    re_path(r'^admin/users/dashboard$', views.UserPwdViewSet.as_view({'get': 'dashboard'})),
    re_path(r'^admin/users/(?P<pk>[0-9]+)$', views.UserPwdViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),
    re_path(r'^admin/users/(?P<pk>[0-9]+)/invoices$', views.PaymentPwdViewSet.as_view({'get': 'user_invoices'})),
    re_path(r'^admin/users/(?P<pk>[0-9]+)/plan$', views.PaymentPwdViewSet.as_view({'post': 'admin_upgrade_plan'})),

    re_path(r'^admin/affiliate_submissions$', views.AffiliateSubmissionPwdViewSet.as_view({'get': 'list'})),
    re_path(r'^admin/affiliate_submissions/(?P<pk>[0-9]+)$',
        views.AffiliateSubmissionPwdViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]

# ------------------------------- Management Command ----------------------------- #
urlpatterns += [
    re_path(r'^managements/commands/(?P<pk>[a-z_]+)$', views.ManagementCommandPwdViewSet.as_view({'post': 'commands'})),
    re_path(r'^managements/statistics/users$', views.ManagementCommandPwdViewSet.as_view({'get': 'users'})),
]

# ----------------------------------- User Reward missions ----------------- ------------ #
urlpatterns += [
    re_path(r'^reward/claim$', views.UserRewardMissionPwdViewSet.as_view({'get': 'claim'})),
    re_path(r'^reward/claim/promo_codes$',
        views.UserRewardMissionPwdViewSet.as_view({'get': 'list_promo_codes', 'post': 'claim_promo_code'})),
    re_path(r'^reward/missions$', views.UserRewardMissionPwdViewSet.as_view({'get': 'list'})),
    re_path(r'^reward/missions/(?P<pk>[a-z0-9_]+)/completed$',
        views.UserRewardMissionPwdViewSet.as_view({'post': 'completed'})),
]

# ----------------------------------- Cipher Attachments ----------------- ------------ #
urlpatterns += [
    re_path(r'^attachments$', views.AttachmentPwdViewSet.as_view({'post': 'create'})),
    re_path(r'^attachments/url$', views.AttachmentPwdViewSet.as_view({'post': 'url'})),
    re_path(r'^attachments/multiple_delete$', views.AttachmentPwdViewSet.as_view({'post': 'multiple_delete'})),
]

# -------------------------------- Scam setting  ------------------------------------- #
urlpatterns += [
    re_path(r'^scam_settings$', views.ScamSettingPwdViewSet.as_view({'get': 'list', 'put': 'update'})),
    re_path(r'^scam_settings/whitelist_urls$',
        views.ScamSettingPwdViewSet.as_view({'get': 'list_wl_urls', 'post': 'create_wl_url'})),
    re_path(r'^scam_settings/whitelist_urls/(?P<wl_url_id>[a-zA-Z0-9_-]+)$',
        views.ScamSettingPwdViewSet.as_view(
            {'get': 'retrieve_wl_url', 'put': 'update_wl_url', "delete": "destroy_wl_url"})),
]
