import logging
import threading
from datetime import datetime, timedelta
from typing import Tuple, Optional, Callable, Literal

from server.database import Session, from_api, Video
from server.gb_api import GBAPI, SortDirection, ResourceSelect
from server.requester import RequestPriority
from server.system_state import SystemState


class IndexerAlreadyRunningException(RuntimeError):
    pass


class Indexer:
    _thread_lock = threading.Lock()
    'A lock used to ensure operations are thread-safe when running the indexer, which can be run in a separate thread.'

    _active = False
    '''
    Whether the indexer is processing an index refresh. Used to prevent running multiple instances of the indexer
    simultaneously.
    
    While the indexer may be marked as running in the database, no processing is occurring unless _active is set to
    True. For example, an index refresh may have been started and has been marked as running in the database, but
    the server was restarted before the index operation completed.
    '''

    _active_thread: threading.Thread = None
    'The Thread an index refresh is running on. If no index refresh thread is running, the value is None.'

    _refresh_stop_requested = False
    'Indicates whether the active index refresh thread has been requested to stop.'

    _logger = logging.getLogger('gbmm.Indexer')

    @staticmethod
    def start_full_indexer(session):
        """
        Start an index refresh that indexes all videos.

        :param session: A SQLAlchemy Session
        :return: The Thread on which the indexer is running.
        """
        state = SystemState.get(session)

        # If an indexer is running, raise an exception
        if Indexer.is_running(session):
            raise IndexerAlreadyRunningException(RuntimeError)

        # Set our state to indicate the full indexer is running, and set initial state if it does not exist
        state.indexer_full__in_progress = True
        state.indexer_full__total_results = 0
        state.indexer_full__processed_results = 0
        return Indexer.__run_full_index_wrap(session)

    @staticmethod
    def resume_full_indexer(session: Session):
        """
        Resume an in-progress full index refresh that was previously paused, likely due to a system restart.

        If a full refresh is already in progress, nothing happens.

        :param session: A SQLAlchemy Session
        :return:
        """
        state = SystemState.get(session)
        if state.indexer_full__in_progress and not Indexer._active:
            Indexer.__run_full_index_wrap(session)

    @staticmethod
    def __run_full_index_wrap(session: Session):
        """
        This wrapper helps to run the full index refresh for both starting a new refresh and resuming a paused refresh.

        :param session: A SQLAlchemy Session
        :return: The Thread on which the indexer is running.
        """
        # Loop over all videos available on the Giant Bomb website and add their info to the local database.
        r = GBAPI.select('video').sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)

        def finish_callback(s: Session, error):
            t = SystemState.get(s)
            t.indexer_full__in_progress = False
            if not error:
                t.indexer_full__last_update = datetime.now()

        return Indexer.__run_threaded(r, 'full', finish_callback)

    @staticmethod
    def start_quick_indexer(session: Session):
        """
        Start an index refresh that indexes videos published since the completion of the last quick index update. If
        a quick index refresh has never been performed, execute a refresh of all videos published since the
        completion of the last full index refresh.

        The refresh will capture videos published up to 24 hours before the last index refresh time. This extra
        lookback provides a margin of error that handles the case where the indexer is running while a video is
        published and the newly posted video is not captured in the last refresh, even though the publish date may be
        before the recorded time that the last refresh completed.

        :param session: A SQLAlchemy Session
        :return: The Thread on which the indexer is running.
        """

        state = SystemState.get(session)

        # If an indexer is running, raise an exception
        if Indexer.is_running(session):
            raise IndexerAlreadyRunningException(RuntimeError)

        # If a full index update has never been run, run a full update instead
        if state.indexer_full__last_update is None:
            return Indexer.start_full_indexer(session)

        # Set our state to indicate the quick indexer is running
        state.indexer_quick__in_progress = True
        state.indexer_quick__total_results = 0
        state.indexer_quick__processed_results = 0

        # Use the last time the quick indexer finished as the last update time. If the quick indexer has never been
        # run before, use the last time the full indexer finished.
        if state.indexer_quick__last_update is not None:
            last_update_time = state.indexer_quick__last_update
        elif state.indexer_full__last_update is not None:
            last_update_time = state.indexer_full__last_update
        else:
            # Should never reach this
            last_update_time = datetime.fromtimestamp(0)

        # Add a margin of error to the last update time to prevent race conditions between indexing and
        # new video posting times. An extra day of lookback should not hurt performance much.
        start_time = last_update_time + timedelta(days=-1)
        start_time.replace(microsecond=0).isoformat()
        end_time = datetime.now()
        filter_string = f'{start_time}|{end_time}'
        r = GBAPI.select('video') \
            .filter(publish_date=filter_string) \
            .sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)

        def finish_callback(s: Session, error):
            t = SystemState.get(s)
            t.indexer_quick__in_progress = False
            if not error:
                t.indexer_quick__last_update = datetime.now()

        return Indexer.__run_threaded(r, 'quick', finish_callback)

    @staticmethod
    def stop():
        """
        If an index refresh is running, stop it and reset the state. Stopping the refresh occurs asynchronously and this
        method may return before the refresh has stopped.

        If no index refresh is running, nothing happens.

        :return:
        """
        if Indexer._active_thread is not None:
            Indexer._refresh_stop_requested = True
            Indexer._logger.info('Index refresh stopping...')

    @staticmethod
    def __run_threaded(r: ResourceSelect, t: Literal['quick', 'full'], finish_callback: Callable[[Session, bool], any] = None):
        """
        Start the indexer in a separate thread.

        :param r: A ResourceSelect that will be used to query the GBAPI for new items to index.
        :param t: The type of refresh run, 'quick' or 'full'
        :param finish_callback: A callback run after the index update completes, useful for recording final state.
        :return: The Thread on which the indexer is running.
        """

        # Reset stop flag in case it was previously set
        Indexer._refresh_stop_requested = False

        # Set daemon=True so that the server shuts down even if the indexer is active.
        # Indexer state can be recovered on next startup and the indexer can be resumed.
        Indexer._active_thread = threading.Thread(target=Indexer.__run,
                                                  args=[r, t, finish_callback],
                                                  daemon=True).start()
        return Indexer._active_thread

    @staticmethod
    def __run(r: ResourceSelect, t: Literal['quick', 'full'], finish_callback: Callable[[Session, bool], any] = None):
        """
        Run the indexer.

        :param r: A ResourceSelect that will be used to query the GBAPI for new items to index.
        :param t: The type of refresh run, 'quick' or 'full'
        :param finish_callback: A callback run after the index update completes, useful for recording final state.
        :return:
        """
        error = False

        Indexer._logger.info(f'Activating an indexer run. Type: {t}')

        # Ensure that no other indexer threads are running before starting the indexer.
        # This should never happen because of other higher-level checks.
        with Indexer._thread_lock:
            if Indexer._active is True:
                Indexer._logger.error('An indexer run was activated, but the indexer was already active on a separate '
                                      'thread.')
                return
            else:
                Indexer._active = True

        # Compose SystemStateStorage attribute names
        total_attr = f'indexer_{t}__total_results'
        processed_attr = f'indexer_{t}__processed_results'

        while not r.is_last_page and not Indexer._refresh_stop_requested:
            with Session.begin() as session:
                r.next()

                state = SystemState.get(session)

                # Update the state of our progress
                state.__setattr__(total_attr, r.total_results)
                state.__setattr__(processed_attr, state.__getattribute__(processed_attr) + r.page_results)

                for video in from_api(session, Video, r.results):
                    session.add(video)

                total_results = state.__getattribute__(total_attr)
                processed_results = state.__getattribute__(processed_attr)
                Indexer._logger.debug(f'Indexed {r.page_results} results. '
                                      f'Results indexed so far this run: {processed_results}. '
                                      f'Total results to index: {total_results}.')

        if Indexer._refresh_stop_requested:
            Indexer._logger.info('Index refresh stopped.')
            error = True

        if finish_callback is not None:
            with Session.begin() as session:
                finish_callback(session, error)

        with Indexer._thread_lock:
            Indexer._active = False
            Indexer._active_thread = None

        Indexer._logger.info('Completed indexer run.')

    @staticmethod
    def is_running(session) -> bool:
        """
        Whether an index refresh is in progress.

        :param session: A SQLAlchemy Session
        :return:
        """
        state = SystemState.get(session)
        return state.indexer_full__in_progress or state.indexer_quick__in_progress
