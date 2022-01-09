from flask import Blueprint
from sqlalchemy import select

from server.app.flask_helpers import ok, json_data, api_key_required
from config import config
from server.database import Session, Setting

bp = Blueprint('system', config.SERVER_NAME, url_prefix='/api/system')


@bp.route('/refresh-available-videos', methods=('POST',))
def refresh_video_index():
    with Session.begin() as session:
        return {}
