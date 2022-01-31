from datetime import datetime, timedelta

from flask import Blueprint
from sqlalchemy import select

from server.app import video_shows, video_categories
from server.app.flask_helpers import ok, json_data, api_key_required
from server.gb_api import GBAPI, SortDirection, ResourceSelect
from config import config
from server.database import Session, SystemStateStorage, from_api, Video
from server.indexer import Indexer
from server.requester import RequestPriority
from server.system_state import SystemState

bp = Blueprint('system', config.SERVER_NAME, url_prefix='/api/system')


def start():
    """
    Run startup tasks.
    """

    with Session.begin() as session:
        state = SystemState.get(session)
        # Resume the full indexer if it was in progress during last shutdown
        Indexer.resume_full_indexer(session)
        # Clear quick indexer "in progress" flag if it was running during last shutdown
        state.indexer_quick__in_progress = False

@bp.route('/first-time-setup-state', methods=('GET',))
def get_first_time_setup_state():
    """
    Returns information about the state of first time setup tasks.

    :return: An object representing relevant system state.
    """
    api_key = config.get('api.key')

    with Session.begin() as session:
        state = SystemState.get(session)
        setup_initiated = \
            state.first_time_setup__initiated is not None and state.first_time_setup__initiated is True

        setup_complete = \
            state.first_time_setup__complete is not None and state.first_time_setup__complete is True

        return {
            'api_key': api_key.value,
            'setup_initiated': setup_initiated,
            'setup_complete': setup_complete
        }


@bp.route('/run-first-time-setup', methods=('POST',))
def run_first_time_setup():
    with Session.begin() as session:
        state = SystemState.get(session)
        state.first_time_setup__initiated = True
        shows_result = video_shows.refresh_shows(session)
        categories_result = video_categories.refresh_categories(session)
        # Index refresh runs asynchronously
        Indexer.start_full_indexer(session)
        state.first_time_setup__complete = True
        return ok()


@bp.route('/update-index', methods=('POST',))
def update_index():
    data = json_data()
    t = data.get('updateType', str)
    with Session.begin() as session:
        if t == 'quick':
            Indexer.start_quick_indexer(session)
        else:
            Indexer.start_full_indexer(session)
    return ok()
