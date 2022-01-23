from datetime import datetime
from enum import Enum

from sqlalchemy import select
from server.gb_api import GBAPI, SortDirection
from server.requester import RequestPriority
from server.database import Session, SystemState

__defaults = {
    'db__version': '1.0',
    'first_time_setup__initiated': False,
    'first_time_setup__complete': False
}


class IndexUpdateType(Enum):
    quick = 0
    full = 1


def initialize():
    with Session.begin() as session:
        state = session.execute(
            select(SystemState)
        ).scalars().first()

        if state is None:
            state = SystemState(
                db__version=__defaults.get('db__version'),
                first_time_setup__initiated=__defaults.get('first_time_setup__initiated'),
                first_time_setup__complete=__defaults.get('first_time_setup__complete')
            )
            session.add(state)


def update_video_index(t: IndexUpdateType = IndexUpdateType.quick):
    if t == IndexUpdateType.quick:
        return
    else:  # IndexUpdateType.full
        # Loop over all videos available on the Giant Bomb website and add their info to the local database.
        s = GBAPI.select('video').sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)
        while not s.is_last_page:
            s.next()
            with Session.begin() as session:
                state = session.execute(
                    select(SystemState)
                ).scalars().all()
                repr(state)
                #for k, v, t in db_setting_defaults:
                #    setting = Setting.get(session, k)
                #    if setting is None:
                #        setting = Setting(key=k, value=v, type=t)
                #        session.add(setting)

                #session.add()
            #s.total_results
            #s.total_pages
            # TODO
            # Look at the metadata in the result in order to build some sense of progress
            # Store that progress in the database under a new System table
            # Save the result in the database
    return
