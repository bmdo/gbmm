import server.indexer as indexer
import server.background_job as background_job

from flask import Blueprint
from server.app import video_shows, video_categories
from server.app.flask_helpers import ok, json_data
from config import config
from server.database import SessionMaker
from server.system_state import SystemState

bp = Blueprint('system', config.SERVER_NAME, url_prefix='/api/system')


def start():
    """
    Run startup tasks.
    """

    with SessionMaker.begin() as session:
        # Clean up and resume background jobs
        background_job.startup(session)


@bp.route('/first-time-setup-state', methods=('GET',))
def get_first_time_setup_state():
    """
    Returns information about the state of first time setup tasks.

    :return: An object representing relevant system state.
    """
    api_key = config.get('api.key')

    with SessionMaker.begin() as session:
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
    with SessionMaker.begin() as session:
        state = SystemState.get(session)
        state.first_time_setup__initiated = True
        # ENHANCE Add shows and categories to indexer
        shows_result = video_shows.refresh_shows(session)
        categories_result = video_categories.refresh_categories(session)
        # Index refresh runs asynchronously
        indexer.start_full_indexer(session)
        state.first_time_setup__complete = True
        return ok()


@bp.route('/get-indexer-state', methods=('GET',))
def get_indexer_state():
    out = {
        'active': False,
        'uuid': None,
        'type': None,
        'state': None,
        'progress_current': None,
        'progress_denominator': None
    }

    with SessionMaker.begin() as session:
        job = indexer.get_active_job(session)
        if job is not None:
            out['active'] = True
            out['uuid'] = str(job.uuid)
            out['state'] = job.state(session)
            out['type'] = 'quick' if job.__class__.__name__ == 'QuickIndexerBackgroundJob' else 'full'
            out['progress_current'] = job.progress_current(session)
            out['progress_denominator'] = job.progress_denominator(session)

    return out


@bp.route('/update-index', methods=('POST',))
def update_index():
    data = json_data()
    t = data.get('updateType', str)
    with SessionMaker.begin() as session:
        if t == 'quick':
            indexer.start_quick_indexer(session)
        else:
            indexer.start_full_indexer(session)
    return ok()


# TODO Provide facility for observing index state on the front end
