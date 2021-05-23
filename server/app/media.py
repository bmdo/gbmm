import re

from flask import Blueprint, send_file, Response, request
from sqlalchemy import select

from server.app.flask_helpers import ok, not_found, dump
from server.gb_api import GBAPI
from server.database import Session, Video, File, VideoShow, VideoCategory
from config import config

bp = Blueprint('media', config.SERVER_NAME, url_prefix='/media')


@bp.route('/recent', methods=('GET',))
def recent():
    with Session.begin() as session:
        shows = session.execute(
            select(Video)
            .order_by(Video.publish_date.desc())
            .slice(0, 40)
        ).scalars().all()
        return dump(shows)


@bp.route('/show/list', methods=('GET',))
def show_list():
    with Session.begin() as session:
        shows = session.execute(
            select(VideoShow)
        ).scalars().all()
        return dump(shows)


@bp.route('/show/<int:show_id>/videos', methods=('GET',))
def show_videos(show_id: int):
    with Session.begin() as session:
        videos = session.execute(
            select(Video)
            .filter_by(video_show_id=show_id)
            .order_by(Video.publish_date.desc())
        ).scalars().all()
        return dump(videos)


@bp.route('/show/<int:show_id>/info', methods=('GET',))
def show_info(show_id: int):
    with Session.begin() as session:
        show = session.get(VideoShow, show_id)
        if show is None:
            return not_found(f'Show with ID {show_id} not found.')
        return dump(show)


@bp.route('/category/list', methods=('GET',))
def category_list():
    with Session.begin() as session:
        shows = session.execute(
            select(VideoCategory)
        ).scalars().all()
        return dump(shows)


@bp.route('/category/<int:category_id>/videos', methods=('GET',))
def category_videos(category_id: int):
    with Session.begin() as session:
        videos = session.execute(
            select(Video)
            .filter_by(video_categories_id=category_id)
            .order_by(Video.publish_date.desc())
        ).scalars().all()
        return dump(videos)


@bp.route('/category/<int:category_id>/info', methods=('GET',))
def category_info(category_id: int):
    with Session.begin() as session:
        category = session.get(VideoCategory, category_id)
        if category is None:
            return not_found(f'Show with ID {category_id} not found.')
        return dump(category)


@bp.route('/video/<int:video_id>/file', methods=('GET',))
def video_file(video_id: int):
    with Session.begin() as session:
        video = session.get(Video, video_id)
        if video is None:
            return not_found(f'Video with ID {video_id} not found.')
        if video.file is None:
            return not_found(f'File for video with ID {video_id} not found.')

        return send_file(video.file.path, mimetype=video.file.content_type, conditional=True)


@bp.route('/video/<int:video_id>/info', methods=('GET',))
def video_info(video_id: int):
    with Session.begin() as session:
        video = session.get(Video, video_id)
        if video is None:
            return not_found(f'Video with ID {video_id} not found.')
        return dump(video)


@bp.route('/image/<int:image_id>', methods=('GET',))
def image(image_id: int):
    return not_found()
