import requests
from typing import Dict
from bs4 import BeautifulSoup

from locker_server.shared.constants.missions import REWARD_TYPE_PROMO_CODE
from locker_server.shared.external_services.user_reward_mission.mission import Mission


class ClutchRatingAndReviewMission(Mission):
    def __init__(self, mission_type: str, extra_requirements=None):
        super().__init__(mission_type=mission_type, extra_requirements=extra_requirements)
        self.reward_type = REWARD_TYPE_PROMO_CODE
        self.reward_value = 5

    def check_mission_completion(self, input_data: Dict):
        return False
        url = f"https://clutch.co/profile/locker-password-manager?sort_by=date_desc#reviews"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
        }
        res = requests.get(url=url, headers=headers)
        if res.status_code != 200:
            return False
        content = res.text
        soup = BeautifulSoup(content, features="html.parser")

