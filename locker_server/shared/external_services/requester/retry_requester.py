import json
import os
import traceback

import urllib3
import requests
from django.conf import settings
from requests import Response
import time


from locker_server.shared.error_responses.error import refer_error, gen_error
from locker_server.shared.log.cylog import CyLog

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def requester(method, url, headers=None, data_send=None, is_json=True, retry=False, max_retries=3, timeout=10,
              proxies=None):
    if data_send is None:
        data_send = dict()
    if headers is None:
        headers = {}

    env = os.getenv("PROD_ENV", "dev")
    if env == "staging":
        headers.update({
            "CF-Access-Client-Id": settings.CF_ACCESS_CLIENT_ID,
            "CF-Access-Client-Secret": settings.CF_ACCESS_CLIENT_SECRET
        })

    if isinstance(data_send, dict) is False and isinstance(data_send, list) is False:
        # Invalid Json data
        res = Response()
        res.status_code = 400
        res._content = json.dumps(refer_error(gen_error("0004"))).encode('utf-8')
        return res

    number_retries = 0
    while True:
        try:
            res = None
            if method.lower() == "get":
                res = requests.get(headers=headers, url=url, verify=False, timeout=timeout, proxies=proxies)
            elif method.lower() == "post":
                if is_json is True:
                    res = requests.post(
                        headers=headers, url=url, json=data_send, verify=False, timeout=timeout, proxies=proxies
                    )
                else:
                    res = requests.post(
                        headers=headers, url=url, data=data_send, verify=False, timeout=timeout, proxies=proxies
                    )
            elif method.lower() == "put":
                if is_json:
                    res = requests.put(
                        headers=headers, url=url, json=data_send, verify=False, timeout=timeout, proxies=proxies
                    )
                else:
                    res = requests.put(
                        headers=headers, url=url, data=data_send, verify=False, timeout=timeout, proxies=proxies
                    )
            elif method.lower() == "delete":
                if is_json is True:
                    res = requests.delete(
                        headers=headers, url=url, json=data_send, verify=False, timeout=timeout, proxies=proxies
                    )
                else:
                    res = requests.delete(
                        headers=headers, url=url, data=data_send, verify=False, timeout=timeout, proxies=proxies
                    )
            if res is None:
                res = Response()
                res.status_code = 400
                res._content = json.dumps(refer_error(gen_error("0008"))).encode('utf-8')
                return res
            return res
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            number_retries += 1
            if retry:
                if number_retries <= max_retries:
                    time.sleep(3)
                    continue
                else:
                    res = Response()
                    res.status_code = 400
                    res._content = json.dumps(refer_error(gen_error("0009"))).encode('utf-8')
                    return res
            else:
                tb = traceback.format_exc()
                CyLog.debug(**{"message": f"[!] Call to {url} by method {method} with config:::"
                                          f"{data_send} {is_json} {retry} {max_retries} {proxies} timeout:::\n{tb}"})
                res = Response()
                res.status_code = 400
                res._content = json.dumps(refer_error(gen_error("0009"))).encode('utf-8')
                return res
