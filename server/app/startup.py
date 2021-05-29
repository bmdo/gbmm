from flask import Blueprint
from config import config
from . import video_shows, video_categories
from server.app.flask_helpers import ok, is_ok, unavailable
from ..database import Session, Setting

bp = Blueprint('startup', config.SERVER_NAME, url_prefix='/api/startup')


@bp.route('/run', methods=('POST',))
def run():
    with Session.begin() as session:
        Setting.set(session, 'startup_initiated', 'True')
        shows_result = video_shows.refresh_shows(session)
        categories_result = video_categories.refresh_categories(session)
        Setting.set(session, 'startup_complete', 'True')
        return ok()
