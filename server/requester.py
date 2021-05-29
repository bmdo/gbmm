from config import config
import time
import threading
import requests
import logging
from lxml import objectify


class Request:
    __next_request_id = 0
    headers = config.HEADERS

    def __init__(self, url):
        self.url = url
        self.request_id = self.__get_request_id()
        self.condition = threading.Condition()
        self.created_time = time.time()
        self.enqueued_time = None
        self.requested_time = None
        self.response_time = None
        self.result = None

    def __get_request_id(self):
        i = self.__next_request_id
        self.__next_request_id += 1
        return i


class Requester:
    def __init__(self):
        self.logger = logging.getLogger('gbmm').getChild('requester')
        self.__queue: [Request] = []
        self.__queue_lock = threading.Lock()
        self.__queue_pushed_condition = threading.Condition(self.__queue_lock)
        self.logger.debug('Starting requester daemon')
        self.__daemon = threading.Thread(target=self.__processor, daemon=True).start()

    def __processor(self):
        daemon_logger = self.logger.getChild('daemon')
        daemon_logger.debug('Requester daemon processor thread started')
        min_sleep_time = 1.1
        last_request_sent = 0
        while True:
            self.__queue_lock.acquire()
            if len(self.__queue):
                r: Request = self.__queue.pop()
                daemon_logger.debug(f'Processing request {r.request_id}. '
                                    f'Was waiting in queue for {time.time() - r.enqueued_time} seconds.')
                self.__queue_lock.release()

                r.requested_time = time.time()
                daemon_logger.debug(f'Sending request {r.request_id} to {r.url}')
                last_request_sent = r.requested_time
                xml = requests.get(r.url, headers=r.headers).text.encode('utf-8')
                r.response_time = time.time()
                daemon_logger.debug(f'Request {r.request_id} responded. '
                                    f'Total response time {r.response_time - r.requested_time} seconds.')

                parser = objectify.makeparser(encoding='utf-8')
                r.result = objectify.fromstring(xml, parser)
                with r.condition:
                    r.condition.notify_all()

            else:
                self.__queue_lock.release()

            sleep_time = max([min_sleep_time - (time.time() - last_request_sent), 0])
            daemon_logger.debug(f'Requester daemon sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)
            with self.__queue_pushed_condition:
                while len(self.__queue) == 0:
                    daemon_logger.debug(f"Requester daemon awaiting notification.")
                    self.__queue_pushed_condition.wait()
                    daemon_logger.debug(f"Requester daemon received notification.")

    def request(self, url: str):
        new_request = Request(url)
        self.logger.debug(f"Created request {new_request.request_id}.")
        with self.__queue_lock:
            self.__queue.append(new_request)
            new_request.enqueued_time = time.time()
            self.logger.debug(f"Request {new_request.request_id} enqueued.")
            self.__queue_pushed_condition.notify_all()
            self.logger.debug(f"Request queue condition notified")
        with new_request.condition:
            while new_request.result is None:
                self.logger.debug(f"Waiting for the condition for request {new_request.request_id} to be notified")
                new_request.condition.wait()

        return new_request.result


requester = Requester()
