from locker_server.api_orm.abstracts.notifications.notification_settings import AbstractNotificationSettingORM


class NotificationSettingORM(AbstractNotificationSettingORM):
    class Meta(AbstractNotificationSettingORM.Meta):
        swappable = 'LS_NOTIFICATION_SETTING_MODEL'
        db_table = 'cs_notification_settings'
