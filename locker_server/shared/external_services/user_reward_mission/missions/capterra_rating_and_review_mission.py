import requests
from datetime import datetime
from typing import Dict

from locker_server.shared.constants.missions import REWARD_TYPE_PROMO_CODE
from locker_server.shared.external_services.requester.retry_requester import requester
from locker_server.shared.external_services.user_reward_mission.mission import Mission, MAX_REVIEW_DURATION_TIME
from locker_server.shared.log.cylog import CyLog
from locker_server.shared.utils.app import now


class CapterraRatingAndReviewMission(Mission):
    def __init__(self, mission_type: str, extra_requirements=None):
        super().__init__(mission_type=mission_type, extra_requirements=extra_requirements)
        self.reward_type = REWARD_TYPE_PROMO_CODE
        self.reward_value = 5

    def check_mission_completion(self, input_data: Dict):
        # Remove capterra mission
        return False
        user_identifier = input_data.get("user_identifier")
        product_id = "265084"
        url = f"https://www.capterra.com/spotlight/rest/reviews?apiVersion=2&productId={product_id}&from=0&sort=lastestReview&size=50"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"
        }
        # TODO: Paging later
        try:
            res = requester(method="GET", url=url, headers=headers, timeout=10)
            if res.status_code != 200:
                CyLog.warning(**{"message": "[!] CapterraRatingAndReviewMission.check_mission_completion request error"
                                            " {} {}".format(res.status_code, res.text)})
                return False
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
            return False

        reviews = res.json().get("hits")
        for review in reviews:
            try:
                created_time = datetime.strptime(review.get("@timestamp"), "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except TypeError:
                continue
            if created_time < now() - MAX_REVIEW_DURATION_TIME:
                continue
            if review.get("reviewer").get("fullName") == user_identifier:
                return True
        return False
