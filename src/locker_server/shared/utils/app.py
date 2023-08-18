import random
import string
import time
# import pyotp
from typing import List
from user_agents import parse


def now(return_float=False):
    """
    Get time now (UNIX timestamp)
    :return: timestamp
    """
    time_now = time.time()
    return time_now if return_float else int(time_now)


def diff_list(in_list: List, not_in_list: List) -> List:
    """
    This function gets all elment in `in_list` without not in `not_in_list`
    :param in_list: (list)
    :param not_in_list: (list)
    :return:
    """
    return [x for x in in_list if x not in not_in_list]


def random_n_digit(n: int, allow_uppercase: bool = False) -> str:
    """
    Generating new random string
    :param n: (int) Number characters
    :param allow_uppercase: (bool) Allow upper case
    :return: A random string contains number and ascii lower
    """
    valid_digits = string.digits + string.ascii_lowercase
    if allow_uppercase is True:
        valid_digits += string.ascii_uppercase
    return ''.join([random.choice(valid_digits) for _ in range(n)])


def get_ip_location(ip):
    """
    This function to get {location, ip} from the request
    :param ip: The IP address
    :return: (dict) {location, ip}
    """
    from django.contrib.gis.geoip2 import GeoIP2
    location = dict()
    try:
        g = GeoIP2()
        location = g.city(ip) or {}
        city = location.get("city", "")
        country = location.get("country_name", "")
        city_country = []
        if city is not None and city != "":
            city_country.append(city)
        if country is not None and country != "":
            city_country.append(country)
        city_country_str = ", ".join(city_country)
        location.update({"city_country": city_country_str})
    except Exception as e:
        location.update({"city_country": ''})
    return {
        "location": location,
        "ip": ip
    }


# def get_otp_uri(otp_secret: str, username: str = None):
#     totp = pyotp.TOTP(otp_secret)
#     uri = totp.provisioning_uri(name=username, issuer_name="Secrets")
#     return uri


def get_factor2_expired_date(method: str) -> float:
    """
    Return expired time from current time by otp method
    :param method: (str) OTP method
    :return:
    """
    return 0


def get_user_agent(request):
    """
    Return user agent info from request
    """
    user_agent_str = request.META['HTTP_USER_AGENT']
    if not isinstance(user_agent_str, str):
        user_agent_str = user_agent_str.decode('utf-8')
    user_agent = parse(user_agent_string=user_agent_str)
    return user_agent


def secure_random_string(length: int, alpha: bool = True, upper: bool = True, lower: bool = True,
                         numeric: bool = True, special: bool = False):
    return secure_random_string_generator(
        length=length,
        characters=random_string_characters(alpha, upper, lower, numeric, special)
    )


def secure_random_string_generator(length: int, characters: str):
    if length < 0:
        raise Exception("Length cannot be less than zero")
    if not characters:
        raise Exception("Character is not valid")
    random_str = "".join([random.choice(characters) for _ in range(length)])
    return random_str


def random_string_characters(alpha: bool, upper: bool, lower: bool, numeric: bool, special: bool):
    characters = ""
    if alpha:
        if upper:
            characters += string.ascii_uppercase
        if lower:
            characters += string.ascii_lowercase
    if numeric:
        characters += string.digits
    if special:
        characters += "!@#$%^*&"
    return characters
