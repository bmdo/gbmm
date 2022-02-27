from flask import Blueprint
from sqlalchemy import select

from server.app.flask_helpers import dump, ok, api_key_required
from server.gb_api import GBAPI
from server.database import SessionMaker, from_api, VideoShow, from_api_generator
from config import config

bp = Blueprint('video_shows', config.SERVER_NAME, url_prefix='/api/video-shows')


def refresh_shows(session):
    s = GBAPI.select('video_show')
    show_results = s.next()
    while not s.is_last_page:
        show_results += s.next()

    shows = from_api_generator(session, VideoShow, show_results)
    for show in shows:
        session.add(show)


@bp.route('/refresh-all', methods=('GET',))
@api_key_required
def refresh_all():
    with SessionMaker.begin() as session:
        refresh_shows(session)
        return ok()


@bp.route('/get-all', methods=('GET',))
@api_key_required
def get_all():
    with SessionMaker.begin() as session:
        shows_results = session.execute(
            select(VideoShow)
            .order_by(VideoShow.title.asc())
        ).scalars().all()

        return dump(shows_results)
