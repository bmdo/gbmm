from flask import Blueprint
from sqlalchemy import select

from server.app import video_shows, video_categories
from server.app.flask_helpers import ok, json_data, api_key_required
from server.gb_api import GBAPI, SortDirection
from config import config
from server.database import Session, SystemState
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
            state.first_time_setup__initiated is not None and state.first_time_setup__initiated == 'True'

        setup_complete = \
            state.first_time_setup__complete is not None and state.first_time_setup__complete == 'True'

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

    if t == 'quick':
        return
    else:  # 'full'
        # Loop over all videos available on the Giant Bomb website and add their info to the local database.
        s = GBAPI.select('video').sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)
        while not s.is_last_page:
            s.next()
            with Session.begin() as session:
                state = session.execute(
                    select(SystemState)
                ).scalars().all()
                repr(state)
                # for k, v, t in db_setting_defaults:
                #    setting = Setting.get(session, k)
                #    if setting is None:
                #        setting = Setting(key=k, value=v, type=t)
                #        session.add(setting)

                # session.add()
            # s.total_results
            # s.total_pages
            # TODO
            # Look at the metadata in the result in order to build some sense of progress
            # Store that progress in the database under a new System table
            # Save the result in the database
    return
