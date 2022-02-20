import uuid as uuid
from enum import Enum

from flask import Blueprint
from sqlalchemy import select

from server import messenger
from server.app.flask_helpers import ok, json_data, api_key_required, dump
from config import config
from server.messenger import Interest, MessageEventType

bp = Blueprint('subscriptions', config.SERVER_NAME, url_prefix='/api/subscriptions')


def convert_event_types_from_id(event_type_ids: list[int]) -> set[MessageEventType]:
    return set([MessageEventType(t) for t in event_type_ids])


@bp.route('/subscribe', methods=('POST',))
def subscribe():
    return {'uuid': str(messenger.new_subscriber().uuid)}


@bp.route('/<uuid:subscriber_uuid>/unsubscribe', methods=('POST',))
def unsubscribe(subscriber_uuid: uuid.UUID):
    messenger.remove_subscriber(subscriber_uuid)
    return ok()


@bp.route('/<uuid:subscriber_uuid>/get', methods=('POST',))
def get(subscriber_uuid: uuid.UUID):
    out = {
        'subscription_valid': False
    }
    try:
        subscriber = messenger.get_subscriber(subscriber_uuid)
        out['messages'] = subscriber.get_messages()
        out['subscription_valid'] = True
        return subscriber.get_messages()
    except messenger.SubscriberNotFoundException:
        out['messages'] = []
    finally:
        return dump(out)


@bp.route('/<uuid:subscriber_uuid>/add-interests', methods=('POST',))
def add_interests(subscriber_uuid: uuid.UUID):
    data = json_data(required=True)
    interests = data.get('interests', list)
    for interest in interests:
        subject_type = interest.get('subjectType', str)
        event_types = interest.get('eventTypes', set)
        # TODO
    return ok()


@bp.route('/<uuid:subscriber_uuid>/remove-interests', methods=('POST',))
def remove_interests(subscriber_uuid: uuid.UUID):
    data = json_data(required=True)
    interests = data.get('interests', list)
    for interest in interests:
        subject_type = interest.get('subjectType', str)
        event_types = interest.get('eventTypes', set)
        # TODO
    return ok()


@bp.route('/<uuid:subscriber_uuid>/set-interests', methods=('POST',))
def set_interests(subscriber_uuid: uuid.UUID):
    data = json_data(required=True)
    interests: list[Interest] = []
    for i in data.get('interests', list):
        subject_type = i.get('subjectType')
        event_types = convert_event_types_from_id(i.get('eventType'))
        interests.append(Interest(subject_type, event_types))
    subscriber = messenger.get_subscriber(subscriber_uuid)
    subscriber.set_interests(interests)
    return ok()