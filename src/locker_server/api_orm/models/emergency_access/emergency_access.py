from locker_server.api_orm.abstracts.emergency_access.emergency_access import AbstractEmergencyAccessORM


class EmergencyAccessORM(AbstractEmergencyAccessORM):
    class Meta:
        swappable = 'LS_EMERGENCY_ACCESS_MODEL'
        db_table = 'cs_emergency_access'
