import ipaddress
import os
import re

import tldextract
from user_agents import parse


def get_ip_by_request(request):
    ip_address = ''

    # Look up: HTTP_X_ORIGINAL_FORWARDED_FOR
    x_original_forwarded_for = request.META.get("HTTP_X_ORIGINAL_FORWARDED_FOR", "")
    if x_original_forwarded_for:
        ips = [ip.strip() for ip in x_original_forwarded_for.split(",")]
        for ip in ips:
            if is_valid_ip(ip):
                ip_address = ip
                break

    # Look up: HTTP_X_FORWARDED_FOR
    if not ip_address:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            ips = [ip.strip() for ip in x_forwarded_for.split(',')]
            for ip in ips:
                if is_valid_ip(ip):
                    ip_address = ip
                    break

    # Look up: HTTP_X_REAL_IP
    if not ip_address:
        x_real_ip = request.META.get('HTTP_X_REAL_IP', '')
        if x_real_ip and is_valid_ip(x_real_ip):
            ip_address = x_real_ip.strip()

    # Look up: REMOTE_ADDR
    if not ip_address:
        remote_addr = request.META.get('REMOTE_ADDR', '')
        if remote_addr and is_valid_ip(remote_addr):
            ip_address = remote_addr.strip()

    if not ip_address:
        ip_address = '127.0.0.1'
    return ip_address


def is_valid_ip(ip_address: str) -> bool:
    """
    Check if a string matches an ipv4 or ipv6 address
    :param ip_address: (str) A string needs check
    :return:
    """
    return is_valid_ipv4_address(ip_address=ip_address) or is_valid_ipv6_address(ip_address=ip_address)


def is_valid_ipv4_address(ip_address: str) -> bool:
    """
    Check if a string matches an IPv4 address
    :param ip_address: (str) a string needs check
    :return True if this string matches an IPv4 address
    """
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.version == 4
    except ValueError:
        return False
    except:
        return False


def is_valid_ipv6_address(ip_address: str) -> bool:
    """
    Check if a string matches an IPv6 address
    :param ip_address: (str) A string needs check
    :return:
    """
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.version == 6
    except ValueError:
        return False
    except:
        return False


def is_valid_domain(domain: str):
    """
    Check a string is a domain or not
    :param domain:
    :return:
    """
    pattern = re.compile(
        r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    return True if pattern.match(domain) else False


def extract_root_domain(domain: str) -> str:
    """
    Get root domain of domain
    :param domain:
    :return:
    """
    extracted = tldextract.extract(domain)
    return "{}.{}".format(extracted.domain, extracted.suffix)


def extract_full_domain(domain: str) -> str:
    extracted = tldextract.extract(domain)
    full_domain = "{}.{}".format(extracted.domain, extracted.suffix)
    if extracted.subdomain:
        full_domain = "{}.{}".format(extracted.subdomain, full_domain)
    return full_domain


def detect_device(ua_string: str):
    """
    Detect device information from request
    :param ua_string: (str) User Agent string
    :return:
    """
    if not ua_string:
        return {}

    device_information = dict()
    user_agent = parse(ua_string)
    # Accessing user agent to retrieve browser attributes
    device_information["browser"] = {
        "family": user_agent.browser.family,
        "version": user_agent.browser.version_string
    }

    # Accessing user agent to retrieve operating system properties
    device_information["os"] = {
        "family": user_agent.os.family,
        "version": user_agent.os.version_string
    }

    # Accessing user agent to retrieve device properties
    device_information["device"] = {
        "family": user_agent.device.family,
        "brand": user_agent.device.brand,
        "model": user_agent.device.model,
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
        "is_bot": user_agent.is_bot
    }
    return device_information
