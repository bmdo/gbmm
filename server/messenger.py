import datetime
import time
import uuid
from enum import Enum
from threading import Lock


class SubscriberNotFoundException(RuntimeError):
    pass


class InboxFullException(RuntimeError):
    pass


class MessageEventType(Enum):
    created = 0
    modified = 1
    deleted = 2

    @staticmethod
    def all():
        return {
            MessageEventType.created,
            MessageEventType.modified,
            MessageEventType.deleted
        }


class Message:
    def __init__(self, event_type: MessageEventType, subject_type: type, subject: any):
        self.event_type = event_type
        self.subject_type = subject_type
        self.subject_id = subject.id
        self.data = subject


class Interest:
    def __init__(self, subject_type: type, event_types: set[MessageEventType] = None):
        if event_types is None:
            event_types = MessageEventType.all()
        self.subject_type = subject_type
        self.event_types = event_types


class Subscriber:
    def __init__(self, messenger: 'Messenger'):
        self.uuid = uuid.uuid1()
        self.interests: list[Interest] = []
        self.__messenger = messenger

    def add_interest(self, subject_type: type, event_types: set[MessageEventType] = None):
        interest = Interest(subject_type, event_types)
        existing = next((i for i in self.interests if i.subject_type is interest.subject_type), None)
        if existing is not None:
            existing.event_types |= interest.event_types
        else:
            self.interests.append(interest)

    def remove_interest(self, subject_type: type, event_types: set[MessageEventType] = None):
        interest = Interest(subject_type, event_types)
        existing = next((i for i in self.interests if i.subject_type is interest.subject_type), None)
        if existing is not None:
            existing.event_types ^= interest.event_types
            if len(existing.event_types) == 0:
                self.interests.remove(existing)

    def set_interests(self, interests: list[Interest]):
        self.interests = interests

    def interested(self, subject_type: type, event_type: MessageEventType):
        return len([
            i for i in self.interests
            if i.subject_type is subject_type
            and event_type in i.event_types
        ]) > 0

    def get_messages(self):
        return self.__messenger.receive_all(self)

    def end(self):
        self.__messenger.remove_subscriber(self)


class Inbox:
    MESSAGE_LIMIT = 1000
    EXPIRATION_TIMEOUT = 300  # 5 minutes

    def __init__(self, subscriber: Subscriber):
        super().__init__()
        self.lock = Lock()
        self.messages: list[Message] = []
        self.subscriber = subscriber
        self.__last_checked = int(time.time())

    @property
    def expired(self):
        return int(time.time()) - self.__last_checked > Inbox.EXPIRATION_TIMEOUT

    def put(self, msg: Message):
        if len(self.messages) > Inbox.MESSAGE_LIMIT:
            raise InboxFullException()

        with self.lock:
            self.messages.append(msg)

    def pop_all(self):
        self.__last_checked = int(time.time())
        with self.lock:
            out = self.messages.copy()
            self.messages.clear()
            return out


class Messenger:
    def __init__(self):
        self.__inboxes: list[Inbox] = []

    def send(self, msg: Message):
        for inbox in self.__inboxes:
            # This is a good time to check if a subscriber's subscription has expired.
            if inbox.expired:
                # If the inbox has expired, remove the subscriber
                self.remove_subscriber(inbox.subscriber)
                continue
            if inbox.subscriber.interested(msg.subject_type, msg.event_type):
                try:
                    inbox.put(msg)
                except InboxFullException:
                    # If this subscriber's inbox has too many messages, assume it is no longer receiving messages and
                    # remove it.
                    self.remove_subscriber(inbox.subscriber)

    def receive_all(self, subscriber: Subscriber):
        inbox = next((s for s in self.__inboxes if s.subscriber is subscriber), None)
        if inbox is not None:
            return inbox.pop_all()
        else:
            raise SubscriberNotFoundException()

    def add_subscriber(self, subscriber: Subscriber):
        self.__inboxes.append(Inbox(subscriber))

    def get_subscriber(self, subscriber_uuid: uuid.UUID):
        return next((s.subscriber for s in self.__inboxes if s.subscriber.uuid == subscriber_uuid), None)

    def remove_subscriber(self, subscriber: Subscriber):
        for inbox in self.__inboxes:
            if inbox.subscriber is subscriber:
                self.__inboxes.remove(inbox)
                return


__messenger = Messenger()


def new_subscriber():
    subscriber = Subscriber(__messenger)
    __messenger.add_subscriber(subscriber)
    return subscriber


def get_subscriber(subscriber_uuid: uuid.UUID):
    return __messenger.get_subscriber(subscriber_uuid)


def remove_subscriber(subscriber_uuid: uuid.UUID):
    return __messenger.remove_subscriber(__messenger.get_subscriber(subscriber_uuid))


def publish(event_type: MessageEventType, subject_type: type, subject: any):
    __messenger.send(Message(event_type, subject_type, subject))
