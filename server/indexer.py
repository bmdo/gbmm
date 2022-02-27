import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Optional, cast

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import server.background_job as background_job
from server.database import SessionMaker, Video, from_api_generator
from server.gb_api import GBAPI, SortDirection, ResourceSelect
from server.requester import RequestPriority
from server.system_state import SystemState


class IndexerException(RuntimeError):
    pass


class IndexerBackgroundJob(background_job.BackgroundJob, ABC):
    def __run_inner(self, resource_select: ResourceSelect) -> bool:
        """
        Run the indexer.

        :param resource_select: A ResourceSelect that will be used to query the GBAPI for new items to index.
        :return:
        """

        while not resource_select.is_last_page and not self._should_stop and not self._should_pause:
            resource_select.next()
            with SessionMaker.begin() as session:
                # Update the state of our progress
                self._set_progress_denominator(session, resource_select.total_results)
                self._increment_progress(session, resource_select.page_results)

                for video in from_api_generator(session, Video, resource_select.results):
                    session.add(video)

                self.logger.debug(f'Indexed {resource_select.page_results} results. '
                                  f'Results indexed so far this run: {self.progress_current(session)}. '
                                  f'Total results to index: {self.progress_denominator(session)}.')

        if self._should_stop:
            self.logger.info('Index refresh stopped.')
            return self._stop_complete(session)
        elif self._should_pause:
            self.logger.info('Index refresh paused.')
            return self._pause_complete(session)
        else:
            return self.complete(session)

    def _run_indexer(self, resource_select: ResourceSelect):
        try:
            return self._run_indexer(resource_select)
        except IndexerException:
            self.logger.error('Indexer job failed due to an exception raised by the indexer itself.')
            with SessionMaker.begin() as session:
                return self.fail(session)
        except SQLAlchemyError:
            self.logger.error('Indexer job failed due to an exception raised by the database.')
            with SessionMaker.begin() as session:
                return self.fail(session)
        except AttributeError:
            self.logger.error('Could not run Indexer job because the API resource is not initialized.')
            with SessionMaker.begin() as session:
                return self.fail(session)
        except:
            self.logger.error('Indexer job failed due to an unknown exception.')
            with SessionMaker.begin() as session:
                return self.fail(session)


@background_job.register
class FullIndexerBackgroundJob(IndexerBackgroundJob):
    def _run(self):
        """
        Start an index refresh that indexes all videos.
        """

        self.resource_select = self.data.get('resource_select')
        # Loop over all videos available on the Giant Bomb website and add their info to the local database.
        self.resource_select = GBAPI.select('video').sort('id', SortDirection.ASC).limit(100).priority(
            RequestPriority.low)

        self.__run_2()

    def _resume(self):
        """
        Resume an index refresh that indexes all videos.
        """

        self.logger.info(f'Resuming the full indexer run.')
        self.__run_2()

    def _recover(self):
        self.logger.info(f'Recovering the full indexer run.')
        # ENHANCE Make this smarter instead of starting from the beginning
        self._run()

    def __run_2(self):
        flag = self._run_indexer(self.resource_select)
        if flag.complete:
            with SessionMaker.begin() as session:
                # Mark now as the last time we ran the quick indexer
                SystemState.get(session).indexer_full__last_update = datetime.now()
                self.logger.info(f'Completed full indexer run.')


@background_job.register
class QuickIndexerBackgroundJob(IndexerBackgroundJob):
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

        self.logger.info(f'Activating a quick indexer run.')

        with SessionMaker.begin() as session:
            state = SystemState.get(session)
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

        end_time = datetime.now().replace(microsecond=0).isoformat()
        filter_string = f'publish_date:{start_time}|{end_time}'
        self.resource_select = GBAPI.select('video') \
            .filter(filter=filter_string) \
            .sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)

        flag = self._run_indexer(self.resource_select)

        if flag.complete:
            with SessionMaker.begin() as session:
                # Mark now as the last time we ran the quick indexer
                SystemState.get(session).indexer_quick__last_update = datetime.now()
                self.logger.info(f'Completed quick indexer run.')


def start_full_indexer(session: Session):

    if get_active_job(session) is not None:
        # If an indexer is running, do not start another
        __logger.warning('Attempted to start a full indexer job, but another indexer job is already active.')
        raise IndexerException()

    FullIndexerBackgroundJob(session).start(session)


def start_quick_indexer(session: Session):
    state = SystemState.get(session)

    if get_active_job(session) is not None:
        # If an indexer is running, do not start another
        __logger.warning('Attempted to start a quick indexer job, but another indexer job is already active.')
        raise IndexerException()

    # If a full index update has never been run, run a full update instead
    if state.indexer_full__last_update is None:
        return start_full_indexer(session)

    QuickIndexerBackgroundJob(session).start(session)


def pause(session: Session):
    """
    If an index refresh is running, pause it, keeping the state. Pausing the refresh occurs asynchronously and this
    method may return before the refresh has paused.

    If no index refresh is running, nothing happens.

    :return:
    """
    active_job = get_active_job(session)

    if active_job is None or active_job.stopped(session):
        __logger.warning('Attempted to pause the running Indexer job, but no job is running.')
        raise IndexerException()

    if active_job.pausing:
        __logger.warning('Attempted to pause the running Indexer job, but the job is already pausing.')
        raise IndexerException()

    if active_job.stopping:
        __logger.warning('Attempted to pause the running Indexer job, but the job is already stopping.')
        raise IndexerException()

    active_job.pause(session)

    __logger.info('Index job pausing...')


def resume(session: Session):
    """
    Resume an in-progress index refresh that was previously paused, possibly due to a system restart.

    :raises IndexerException: Raised if there is no active job or the active job is not paused.
    :param session: A SQLAlchemy Session
    :return:
    """
    active_job = get_active_job(session)

    if active_job is None:
        # There is no indexer job to resume
        __logger.warning('Attempted to resume an indexer job, but no indexer job is active.')
        raise IndexerException()

    if not active_job.paused(session):
        # The currently active job is not paused
        __logger.warning('Attempted to resume an indexer job, but the active job is not paused.')
        raise IndexerException()

    active_job.resume(session)


def stop(session: Session):
    """
    If an index refresh is running, stop it and reset the state. Stopping the refresh occurs asynchronously and this
    method may return before the refresh has stopped.

    If no index refresh is running, nothing happens.

    :return:
    """
    active_job = get_active_job(session)

    if active_job is None or active_job.stopped(session):
        __logger.warning('Attempted to stop the running Indexer job, but no job is running.')
        raise IndexerException()

    if active_job.stopping:
        __logger.warning('Attempted to stop the running Indexer job, but the job is already stopping.')
        raise IndexerException()

    active_job.stop(session)

    __logger.info('Index job stopping...')


def get_active_job(session: Session) -> Optional[IndexerBackgroundJob]:
    bg_jobs = [cast(IndexerBackgroundJob, j) for j in FullIndexerBackgroundJob.get_all(session)] + \
              [cast(IndexerBackgroundJob, j) for j in QuickIndexerBackgroundJob.get_all(session)]

    if len(bg_jobs) < 1:
        return None

    return cast(IndexerBackgroundJob, bg_jobs[0])


__logger = logging.getLogger('gbmm.Indexer')
