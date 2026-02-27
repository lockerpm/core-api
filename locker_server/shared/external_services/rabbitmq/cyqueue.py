import json
import time
import traceback
from urllib.parse import urlparse
from amqpstorm import Connection, Message
from django.conf import settings

from locker_server.shared.log.cylog import CyLog


class CyQueue:
    def __init__(self, queue_address):
        self.queue_address = urlparse(queue_address)
        self.hostname = str(self.queue_address.hostname)
        self.username = str(self.queue_address.username)
        self.password = str(self.queue_address.password)
        self.vhost = self.queue_address.path.strip('/')

    def send(self, data, queue_name, retries=5, retry_timeout=5):
        """
        Send the message to RabbitMQ queue
        """
        message = json.dumps(data)
        properties = {
            'content_type': 'text/plain'
        }

        retry = 1
        while retry < retries:
            try:
                with Connection(
                    hostname=self.hostname, username=self.username, password=self.password, virtual_host=self.vhost
                ) as connection:
                    with connection.channel() as channel:
                        channel.queue.declare(queue_name, durable=True)
                        m = Message.create(channel=channel, body=message, properties=properties)
                        m.publish(queue_name)
                        CyLog.debug(**{"message": f"[+] Sending job to queue OK::: {queue_name} - {data}",})
                        return True
            except Exception as e:
                tb = traceback.format_exc()
                CyLog.error(**{"message": f"[!] Sending job to queue error: {queue_name} - {data}. Traceback\n{tb}"})
                time.sleep(retry_timeout)
                retry += 1
        return None


class RelayQueue(CyQueue):
    def __init__(self, queue_address=settings.RELAY_QUEUE_URL):
        super().__init__(queue_address)

    def send(self, data, queue_name=settings.RELAY_QUEUE, retries=5, retry_timeout=5):
        return super().send(data, queue_name, retries, retry_timeout)
