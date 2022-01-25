from datetime import datetime, timedelta

from flask import Blueprint
from sqlalchemy import select

from server.app import video_shows, video_categories
from server.app.flask_helpers import ok, json_data, api_key_required
from server.gb_api import GBAPI, SortDirection, ResourceSelect
from config import config
from server.database import Session, SystemState, from_api, Video
from server.requester import RequestPriority

bp = Blueprint('system', config.SERVER_NAME, url_prefix='/api/system')


__defaults = {
    'id': 'SystemState',
    'db__version': '1.0',
    'first_time_setup__initiated': False,
    'first_time_setup__complete': False
}


def get_state(session: Session):
    """
    Get the system state. If the system state has not yet been initialized, it will be initialized.

    :param session: A SQLAlchemy session
    :return: The system state
    """
    state = session.execute(
        select(SystemState)
        .filter_by(id=__defaults.get('id'))
    ).scalars().first()

    if state is None:
        state = initialize_state(session)

    return state


def initialize_state(session: Session):
    """
    Initialize the system state to default values.

    :param session: A SQLAlchemy session
    :return: The system state
    """
    state = SystemState(
        id=__defaults.get('id'),
        db__version=__defaults.get('db__version'),
        first_time_setup__initiated=__defaults.get('first_time_setup__initiated'),
        first_time_setup__complete=__defaults.get('first_time_setup__complete')
    )
    session.add(state)
    return state


@bp.route('/first-time-setup-state', methods=('GET',))
def get_first_time_setup_state():
    """
    Returns information about the state of first time setup tasks.

    :return: An object representing relevant system state.
    """
    api_key = config.get('api.key')

    with Session.begin() as session:
        state = get_state(session)
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
        state = get_state(session)
        state.first_time_setup__initiated = True
        shows_result = video_shows.refresh_shows(session)
        categories_result = video_categories.refresh_categories(session)
        state.first_time_setup__complete = True
        return ok()


@bp.route('/update-index', methods=('POST',))
def update_index():
    data = json_data()
    t = data.get('updateType', str)

    with Session.begin() as session:
        state = get_state(session)
        state.indexer__in_progress = True
        state.indexer__in_progress_type = t
        if state.indexer__total_results is None:
            state.indexer__total_results = 0
        if state.indexer__processed_results is None:
            state.indexer__processed_results = 0
        r: ResourceSelect

        if t == 'quick':
            # Index videos published since the last index update time.
            # Add a margin of error to the last update time to prevent race conditions between indexing and
            # new video posting times. An extra day of lookback should not hurt performance much.
            start_time = state.indexer__last_update + timedelta(days=-1)
            start_time.replace(microsecond=0).isoformat()
            end_time = datetime.now()
            filter_string = f'{start_time}|{end_time}'
            r = GBAPI.select('video') \
                .filter(publish_date=filter_string) \
                .sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)

        else:  # 'full'
            # Loop over all videos available on the Giant Bomb website and add their info to the local database.
            r = GBAPI.select('video').sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)

    while not r.is_last_page:
        with Session.begin() as session:
            r.next()
            state = get_state(session)
            state.indexer__total_results = r.total_results
            state.indexer__processed_results += r.page_results
            for video in from_api(session, Video, r.results):
                session.add(video)

    with Session.begin() as session:
        state.indexer__in_progress = False
        state.indexer__in_progress_type = None
        state.indexer__last_update = datetime.now()
