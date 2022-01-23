from flask import Blueprint
from sqlalchemy import select

from server.app.flask_helpers import ok, json_data, api_key_required
from config import config
from server.database import Session, Setting

bp = Blueprint('settings', config.SERVER_NAME, url_prefix='/api/settings')


@bp.route('/get-all', methods=('GET',))
def get_all():
    settings = config.dump_ui()
    return settings


@bp.route('/modify', methods=('POST',))
def modify():
    data = json_data()
    out = {}
    for setting in data.get('settings', []):
        config.modify(setting['address'], setting['value'])
        value = config.get(setting['address']).value
        out[setting['address']] = value
    return out


@bp.route('/startup', methods=('GET',))
def startup():
    api_key = config.get('api.key')

    with Session.begin() as session:
        setting = Setting.get(session, 'startup_initiated')
        startup_initiated = setting is not None and setting.value == 'True'

        setting = Setting.get(session, 'startup_complete')
        startup_complete = setting is not None and setting.value == 'True'

        return {
            'api_key': api_key.value,
            'startup_initiated': startup_initiated,
            'startup_complete': startup_complete
        }
