from flask import Blueprint
from sqlalchemy import select

from server.app.flask_helpers import ok, json_data, api_key_required
from config import config
from server.database import Session
import server.system

bp = Blueprint('system', config.SERVER_NAME, url_prefix='/api/system')


@bp.route('/update-index', methods=('POST',))
def update_index():
    data = json_data()
    out = {}
    t = data.get('type', str)
    if t == 'quick':
        server.system.update_video_index(server.system.IndexUpdateType.quick)
    else: # 'full'
        server.system.update_video_index(server.system.IndexUpdateType.full)
    return out