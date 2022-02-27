from flask import Blueprint
from sqlalchemy import select

from server.app.flask_helpers import dump, ok, api_key_required
from server.gb_api import GBAPI
from server.database import SessionMaker, from_api, VideoCategory, from_api_generator
from config import config

bp = Blueprint('video_categories', config.SERVER_NAME, url_prefix='/api/video-categories')


def refresh_categories(session):
    s = GBAPI.select('video_category')
    categories_results = s.next()
    while not s.is_last_page:
        categories_results += s.next()

    categories = from_api_generator(session, VideoCategory, categories_results)
    for category in categories:
        session.add(category)


@bp.route('/refresh-all', methods=('GET',))
@api_key_required
def refresh_all():
    with SessionMaker.begin() as session:
        refresh_categories(session)
        return ok()


@bp.route('/get-all', methods=('GET',))
@api_key_required
def get_all():
    with SessionMaker.begin() as session:
        categories_results = session.execute(
            select(VideoCategory)
            .order_by(VideoCategory.name.asc())
        ).scalars().all()

        return dump(categories_results)
