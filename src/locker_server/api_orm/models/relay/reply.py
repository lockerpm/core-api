from locker_server.api_orm.abstracts.relay.reply import AbstractReplyORM


class ReplyORM(AbstractReplyORM):
    class Meta(AbstractReplyORM.Meta):
        swappable = 'LS_RELAY_REPLY_MODEL'
        db_table = 'cs_reply'
