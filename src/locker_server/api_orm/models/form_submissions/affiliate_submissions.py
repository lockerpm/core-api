from locker_server.api_orm.abstracts.form_submissions.affiliate_submissions import AbstractAffiliateSubmissionORM
from locker_server.shared.utils.app import now


class AffiliateSubmissionORM(AbstractAffiliateSubmissionORM):
    class Meta(AbstractAffiliateSubmissionORM.Meta):
        db_table = 'cs_affiliate_submissions'

    @classmethod
    def create(cls, **data):
        new_affiliate_submission_orm = AffiliateSubmissionORM(
            created_time=data.get("created_time", now()),
            full_name=data.get("full_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            company=data.get("company"),
            country=data.get("country"),
            status=data.get("status"),
        )
        new_affiliate_submission_orm.save()
        return new_affiliate_submission_orm
