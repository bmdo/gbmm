from flask import Blueprint, redirect, url_for
from sqlalchemy import select, or_, asc
from config import config
from server.database import SessionMaker, Download, Video, from_api, from_api_generator
from server.app.flask_helpers import bad_request, json_data, FilterHelper, dump, ListResultMetadata, api_key_required
from server.downloader import downloader
from server.gb_api import GBAPI
from server.serialization import DownloadSchema

bp = Blueprint('downloads', config.SERVER_NAME, url_prefix='/api/downloads')


class DownloadRequestData:
    def __init__(self):
        json = json_data()

        try:
            self.object_type = str(json.get('obj_item_name'))
        except ValueError or TypeError:
            raise ValueError(f'Invalid object type {self.object_type}')

        self.validate_object_type()

        try:
            self.id = int(json.get('obj_id'))
        except ValueError or TypeError:
            raise ValueError(f'Invalid ID {self.id}')

    def validate_object_type(self):
        if self.object_type not in ['video']:
            raise ValueError(f'Unsupported object type "{self.object_type}"')


def filter_downloads(session):
    """
    Expected data members:
    id: int or list[int]
    obj_item_name: str or list[str]
    obj_id: str or list[str]
    status: int or list[int]
    limit: int
    page: int
    :return: List of Downloads as JSON
    """
    json = json_data(required=True)

    limit = 20
    page = 1
    offset = 0
    if 'limit' in json:
        if json['limit'] > 0:
            limit = json['limit']
    if 'page' in json:
        if json['page'] > 0:
            page = json['page']
            offset = json['page'] * limit - limit

    filters = FilterHelper()
    if 'id' in json:
        filters.eq_or_in(Download.id, json['id'])
    if 'obj_item_name' in json:
        filters.eq_or_in(Download.obj_item_name, json['obj_item_name'])
    if 'obj_id' in json:
        filters.eq_or_in(Download.obj_id, json['obj_id'])
    if 'status' in json:
        filters.eq_or_in(Download.status, json['status'])

    count = session.query(Download).filter(filters.to_and()).count()
    total_pages = int(count / limit)

    results = session.execute(
        select(Download)
        .filter(filters.to_and())
        .order_by(Download.finish_time.desc())
        .slice(offset, offset + limit)
    ).scalars()
    metadata = ListResultMetadata(limit, offset, page, total_pages, count)
    return results, metadata


@bp.route('/get', methods=('POST',))
@api_key_required
def get():
    try:
        with SessionMaker.begin() as session:
            results, metadata = filter_downloads(session)
            return dump(results.all(), metadata)

    except ValueError as e:
        return bad_request(exception=e)


@bp.route('/get-one', methods=('POST',))
@api_key_required
def get_one():
    try:
        with SessionMaker.begin() as session:
            results, metadata = filter_downloads(session)
            return dump(results.first())

    except ValueError as e:
        return bad_request(exception=e)


def get_for_objects(session, objects: list[tuple[str, int]]) -> list[Download]:
    """
    :param session: A SQLAlchemy session.
    :param objects: A list of 2-value tuples. Tuple index 0 represents the obj_item_name. Tuple index 1 represents the
    object ID.
    :return: A list of downloads for the given objects.
    """
    downloads = []
    for obj in objects:
        download = session.execute(
            select(Download)
            .filter_by(obj_item_name=obj[0], obj_id=obj[1])
            .order_by(Download.finish_time.desc())
        ).scalars().first()
        if download is not None:
            downloads.append(download)
    return downloads


@bp.route('/enqueue', methods=('POST',))
@api_key_required
def enqueue():
    try:
        with SessionMaker.begin() as session:
            # noinspection PyTypeChecker
            data = DownloadRequestData()
            # TODO accept more than videos?
            video = session.get(Video, data.id)
            if video is None:
                video_data = GBAPI.get_one('video', data.id)
                if video_data is None:
                    raise ValueError()
                else:
                    video = next(from_api_generator(session, Video, video_data))

            video_download = download_video_with_images(session, video)
            session.add(video_download)

            return DownloadSchema().dump(video_download)

    except ValueError as e:
        return bad_request(exception=e)


def download_video_with_images(session, video: Video, preferred_quality_field: str = None):
    image_fields = [
        'original_url',
        'screen_large_url',
        'super_url',
        'screen_url',
        'medium_url',
        'small_url',
        'thumb_url',
        'icon_url',
        'tiny_url'
    ]

    video_fields = [
        'hd_url',
        'high_url',
        'low_url'
    ]

    video_image = video.image

    field = None
    if preferred_quality_field is None:
        for f in video_fields:
            val = getattr(video, f, None)
            if val is not None and val != '':
                field = f
                break
    else:
        field = preferred_quality_field

    if field is None:
        raise ValueError('Could not determine video download URL.')

    video_download = downloader.enqueue(session, video, field)

    for field in image_fields:
        downloader.enqueue(session, video_image, field)

    return video_download



# @bp.route('/queue', methods=('GET',))
# def downloads_queue():
#     with Session(engine) as session:
#         downloads = session.execute(
#             select(Download)
#             .where(
#                 or_(
#                     Download.status == Download.DownloadStatus.QUEUED.value,
#                     Download.status == Download.DownloadStatus.IN_PROGRESS.value,
#                     Download.status == Download.DownloadStatus.PAUSED.value
#                 )
#             )
#             .order_by(Download.created_time.asc())
#         ).scalars().all()
#         return render_template('downloads/queue.html', downloads=downloads)


# @bp.route('/history', methods=('GET',))
# def downloads_history():
#     with Session(engine) as session:
#         downloads = session.execute(
#             select(Download)
#             .order_by(Download.created_time.desc())
#         ).scalars().all()
#         return render_template('downloads/history.html', downloads=downloads)

