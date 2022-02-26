import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Optional, cast

from sqlalchemy.exc import SQLAlchemyError

from server.background_job import BackgroundJob
from server.database import Session, Video, from_api_generator
from server.gb_api import GBAPI, SortDirection, ResourceSelect
from server.requester import RequestPriority
from server.system_state import SystemState


class IndexerException(RuntimeError):
    pass


class IndexerBackgroundJob(BackgroundJob, ABC):
    def _run_indexer(self, resource_select: ResourceSelect) -> bool:
        """
        Run the indexer.

        :param resource_select: A ResourceSelect that will be used to query the GBAPI for new items to index.
        :return:
        """
        success = False

        while not resource_select.is_last_page and not self._should_stop and not self._should_pause:
            resource_select.next()
            with Session.begin() as session:
                # Update the state of our progress
                self._set_progress_denominator(session, resource_select.total_results)
                self._increment_progress(session, resource_select.page_results)

                for video in from_api_generator(session, Video, resource_select.results):
                    session.add(video)

                self._logger.debug(f'Indexed {resource_select.page_results} results. '
                                   f'Results indexed so far this run: {self.progress_current(session)}. '
                                   f'Total results to index: {self.progress_denominator(session)}.')

        if self._should_stop:
            self._logger.info('Index refresh stopped.')
        elif self._should_pause:
            self._logger.info('Index refresh paused.')
        else:
            success = True

        return success


class FullIndexerBackgroundJob(IndexerBackgroundJob):
    _name: str = 'full_indexer'

    def __init__(self, session: Session):
        super().__init__(session, FullIndexerBackgroundJob._name)
        self._logger = self._logger.getChild('FullIndexerBackgroundJob')
        self.resource_select: Optional[ResourceSelect] = None

    def _run(self):
        """
        Start an index refresh that indexes all videos.
        """

        self._logger.info(f'Activating a full indexer run.')

        # Loop over all videos available on the Giant Bomb website and add their info to the local database.
        self.resource_select = GBAPI.select('video').sort('id', SortDirection.ASC).limit(100).priority(
            RequestPriority.low)

        success = False

        try:
            success = self._run_indexer(self.resource_select)
        except IndexerException or SQLAlchemyError as err:
            success = False

        if success:
            with Session.begin() as session:
                # Mark now as the last time we ran the quick indexer
                SystemState.get(session).indexer_full__last_update = datetime.now()

            self._logger.info(f'Completed full indexer run.')

    def _resume_run(self):
        """
        Resume an index refresh that indexes all videos.
        """

        self._logger.info(f'Resuming the full indexer run.')

        self._run_indexer(self.resource_select)


class QuickIndexerBackgroundJob(IndexerBackgroundJob):
    _name = 'quick_indexer'

    def __init__(self, session: Session, start_time: datetime):
        super().__init__(session, QuickIndexerBackgroundJob._name)
        self._logger = self._logger.getChild('QuickIndexerBackgroundJob')

        self.__start_time = start_time
        self.resource_select: Optional[ResourceSelect] = None

    def _run(self):
        """
        Start an index refresh that indexes videos published since the completion of the last quick index update. If
        a quick index refresh has never been performed, execute a refresh of all videos published since the
        completion of the last full index refresh.

        The refresh will capture videos published up to 24 hours before the last index refresh time. This extra
        lookback provides a margin of error that handles the case where the indexer is running while a video is
        published and the newly posted video is not captured in the last refresh, even though the publish date may be
        before the recorded time that the last refresh completed.

        :return: The Thread on which the indexer is running.
        """

        self._logger.info(f'Activating a quick indexer run.')

        end_time = datetime.now().replace(microsecond=0).isoformat()
        filter_string = f'{self.__start_time}|{end_time}'
        self.resource_select = GBAPI.select('video') \
            .filter(publish_date=filter_string) \
            .sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)

        success = False

        try:
            success = self._run_indexer(self.resource_select)
        except IndexerException or SQLAlchemyError as err:
            success = False

        if success:
            with Session.begin() as session:
                # Mark now as the last time we ran the quick indexer
                SystemState.get(session).indexer_quick__last_update = datetime.now()

            self._logger.info(f'Completed quick indexer run.')

    def _resume_run(self):
        """
        Resume an index refresh that indexes videos added since the most recent full or quick refresh.
        """

        self._logger.info(f'Resuming the quick indexer run.')

        self._run_indexer(self.resource_select)


class Indexer:
    _logger = logging.getLogger('gbmm.Indexer')

    @staticmethod
    def start_full_indexer(session: Session):

        if Indexer.get_active_job(session) is not None:
            # If an indexer is running, do not start another
            Indexer._logger.warning('Attempted to start a full indexer job, but another indexer job is already '
                                    'active.')
            raise IndexerException()

        FullIndexerBackgroundJob(session).start(session)

    @staticmethod
    def start_quick_indexer(session: Session):
        state = SystemState.get(session)

        if Indexer.get_active_job(session) is not None:
            # If an indexer is running, do not start another
            Indexer._logger.warning('Attempted to start a quick indexer job, but another indexer job is already '
                                    'active.')
            raise IndexerException()

        # If a full index update has never been run, run a full update instead
        if state.indexer_full__last_update is None:
            return Indexer.start_full_indexer(session)

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
        start_time = start_time.replace(microsecond=0).isoformat()

        QuickIndexerBackgroundJob(session, start_time).start(session)

    @staticmethod
    def pause(session: Session):
        """
        If an index refresh is running, pause it, keeping the state. Pausing the refresh occurs asynchronously and this
        method may return before the refresh has paused.

        If no index refresh is running, nothing happens.

        :return:
        """
        active_job = Indexer.get_active_job(session)

        if active_job is None or active_job.stopped(session):
            Indexer._logger.warning('Attempted to pause the running Indexer job, but no job is running.')
            raise IndexerException()

        if active_job.pausing:
            Indexer._logger.warning('Attempted to pause the running Indexer job, but the job is already pausing.')
            raise IndexerException()

        if active_job.stopping:
            Indexer._logger.warning('Attempted to pause the running Indexer job, but the job is already stopping.')
            raise IndexerException()

        active_job.pause(session)

        Indexer._logger.info('Index job pausing...')

    @staticmethod
    def resume(session: Session):
        """
        Resume an in-progress index refresh that was previously paused, possibly due to a system restart.

        :raises IndexerException: Raised if there is no active job or the active job is not paused.
        :param session: A SQLAlchemy Session
        :return:
        """
        active_job = Indexer.get_active_job(session)

        if active_job is None:
            # There is no indexer job to resume
            Indexer._logger.warning('Attempted to resume an indexer job, but no indexer job is active.')
            raise IndexerException()

        if not active_job.paused(session):
            # The currently active job is not paused
            Indexer._logger.warning('Attempted to resume an indexer job, but the active job is not paused.')
            raise IndexerException()

        active_job.resume(session)

    @staticmethod
    def stop(session: Session):
        """
        If an index refresh is running, stop it and reset the state. Stopping the refresh occurs asynchronously and this
        method may return before the refresh has stopped.

        If no index refresh is running, nothing happens.

        :return:
        """
        active_job = Indexer.get_active_job(session)

        if active_job is None or active_job.stopped(session):
            Indexer._logger.warning('Attempted to stop the running Indexer job, but no job is running.')
            raise IndexerException()

        if active_job.stopping:
            Indexer._logger.warning('Attempted to stop the running Indexer job, but the job is already stopping.')
            raise IndexerException()

        active_job.stop(session)

        Indexer._logger.info('Index job stopping...')

    @staticmethod
    def get_active_job(session) -> Optional[IndexerBackgroundJob]:
        bg_jobs = FullIndexerBackgroundJob.get_jobs_of_same_type(session) + \
                  QuickIndexerBackgroundJob.get_jobs_of_same_type(session)

        if len(bg_jobs) < 1:
            return None

        return cast(IndexerBackgroundJob, bg_jobs[0])
