import flask
from flask import Blueprint

from server.app.flask_helpers import json_data, bad_request, dump, FilterHelper, api_key_required
from server.gb_api import GBAPI, SortDirection
from server.database import Session, Video, from_api
from . import downloads
from config import config

bp = Blueprint('videos', config.SERVER_NAME, url_prefix='/api/videos')


def filter_videos():
    json = json_data(required=True)

    limit = 20
    page = 1
    offset = 0
    if 'limit' in json:
        if 0 < json['limit'] <= 100:
            limit = json['limit']
    if 'page' in json:
        if json['page'] > 0:
            page = json['page']
            offset = json['page'] * limit - limit

    filters = FilterHelper()


@bp.route('/browse', methods=('POST',))
@api_key_required
def browse():
    """
    Expected data members:
    id: int or list[int]
    video_show: int
    video_categories: int
    limit: int
    page: int
    :return: List of Downloads as JSON
    """
    try:
        json = json_data(required=True)
    except ValueError as e:
        return bad_request(exception=e)

    limit = 20
    page = 1
    offset = 0
    sort_field = 'date'
    sort_direction = SortDirection.DESC

    if 'limit' in json:
        if 0 < json['limit'] <= 100:
            limit = json['limit']
    if 'page' in json:
        if json['page'] > 0:
            page = json['page']
            offset = json['page'] * limit - limit
    if 'sort_field' in json:
        sort_field = json['sort_field']
    if 'sort_direction' in json:
        if json['sort_direction'] == 'asc':
            sort_direction = SortDirection.ASC
        elif json['sort_direction'] == 'desc':
            sort_direction = SortDirection.DESC

    f = []
    if 'id' in json:
        if isinstance(json['id'], list):
            val = ','.join(json['id'])
        else:
            val = json['id']
        f.append(f'id:{val}')
    if 'video_show' in json:
        val = json['video_show']
        f.append(f'video_show:{val}')
    if 'video_categories' in json:
        val = json['video_categories']
        f.append(f'video_categories:{val}')

    session_data = flask.session.get('videos_browse_metadata', None)
    if session_data is not None:
        videos_select = GBAPI.from_session_data(session_data)
    else:
        videos_select = GBAPI.select('videos')

    videos_select.field_list('id', 'name', 'deck', 'image')
    videos_select.limit(limit)
    videos_select.filter(filter=':'.join(f))
    videos_select.sort(sort_field, sort_direction)
    page = videos_select.page(page)
    flask.session['videos_browse_metadata'] = videos_select.to_session_data()

    with Session.begin() as session:
        videos = from_api(session, Video, page)

        video_tuples = [('video', v.id) for v in videos]
        downloads_list = downloads.get_for_objects(session, video_tuples)

        return dump({
            'videos': videos,
            'downloads': downloads_list
        })


@bp.route('/get', methods=('POST',))
@api_key_required
def get():
    try:
        json = json_data(required=True)
    except ValueError as e:
        return bad_request(exception=e)

    s = GBAPI.select('video')
    if 'id' in json:
        s.filter(id=json['id'])

    videos = s.next()

    with Session.begin() as session:
        return dump(from_api(session, Video, videos))


@bp.route('/get-one', methods=('POST',))
@api_key_required
def get_one():
    try:
        json = json_data(required=True)
    except ValueError as e:
        return bad_request(exception=e)

    video = None

    if 'id' in json:
        video = GBAPI.get_one('video', json['id'])

    if video is None:
        raise ValueError('Bad JSON.')

    with Session.begin() as session:
        return dump(from_api(session, Video, video))
