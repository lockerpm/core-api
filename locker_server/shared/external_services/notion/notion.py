import itertools
import time
import requests
import json
import httpx
from notion_client import Client
from notion_client.errors import APIResponseError, HTTPResponseError, RequestTimeoutError

from django.conf import settings

from locker_server.shared.log.cylog import CyLog

TIMEOUT = 5
RATE_LIMIT_STATUS_CODES = [429, 409]
NOTION_TOKENS = itertools.cycle([settings.NOTION_CUSTOMER_SUCCESS_TOKEN])


class NotionClient:
    def __init__(self, token=None):
        if not token:
            token = self.token
        self.notion_inst = Client(auth=token)

    @property
    def token(self):
        return next(NOTION_TOKENS)

    def request(self, instance, method, *args, **kwargs):
        max_retries = 3
        retry = 1
        while retry <= max_retries:
            try:
                return getattr(instance, method)(*args, **kwargs)
            except APIResponseError as e:
                if e.status in RATE_LIMIT_STATUS_CODES:
                    self.notion_inst = Client(auth=self.token)
                    time.sleep(TIMEOUT)
                else:
                    if e.status != 404:
                        CyLog.info(**{"message": f'[-] Error: {e.body}'})
                    else:
                        raise
                retry += 1
            except (HTTPResponseError, httpx.ConnectError, RequestTimeoutError, httpx.RemoteProtocolError):
                time.sleep(TIMEOUT)
                retry += 1
            except:
                CyLog.error()
                raise

    def create_page(self, parent, properties, icon):
        return self.request(self.notion_inst.pages, 'create', parent=parent, properties=properties, icon=icon)

    def create_database(self, parent, title, properties, icon):
        return self.request(self.notion_inst.databases, 'create', parent=parent, title=title, properties=properties,
                            icon=icon)

    def list_children_blocks(self, root_block_id):
        return self.request(self.notion_inst.blocks.children, 'list', block_id=root_block_id)['results']

    def update_page(self, page_id, payload):
        return self.request(self.notion_inst.pages, 'update', page_id=page_id, **payload)

    def delete_block(self, block_id):
        return self.request(self.notion_inst.blocks, 'delete', block_id=block_id)

    def clear_blocks(self, page_id):
        blocks = self.list_children_blocks(page_id)
        for block in blocks:
            self.delete_block(block['id'])

    def query_database(self, db_id):
        return self.request(self.notion_inst.databases, 'query', database_id=db_id)['results']

    def retrieve_page(self, page_id):
        return self.request(self.notion_inst.pages, 'retrieve', page_id=page_id)

    def retrieve_database(self, db_id):
        return self.request(self.notion_inst.databases, 'retrieve', database_id=db_id)

    def retrieve_block(self, block_id):
        return self.request(self.notion_inst.blocks, 'retrieve', block_id=block_id)

    def retrieve_page_or_block(self, block_id):
        try:
            return self.retrieve_page(block_id)
        except APIResponseError as e:
            if e.status == 404:
                try:
                    return self.retrieve_block(block_id)
                except APIResponseError as e:
                    if e.status == 404:
                        return None

    # def list_users(self):
    #     return self.request(self.notion_inst.users, 'list')

    @staticmethod
    def get_page_content(page_id):
        url = 'https://www.notion.so/api/v3/loadPageChunk'
        payload = {
            "page": {"id": page_id},
            "limit": 100,
            "cursor": {"stack": []},
            "chunkNumber": 0,
            "verticalColumns": False
        }
        while True:
            try:
                r = requests.post(url, json=payload)
                return json.dumps(r.json()['recordMap']['block'])
            except:
                time.sleep(TIMEOUT)


notion_customer_success = NotionClient(token=settings.NOTION_CUSTOMER_SUCCESS_TOKEN)
