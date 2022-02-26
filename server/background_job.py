import logging
import threading

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import uuid

from sqlalchemy import select

from server.database import Session, BackgroundJobStorage


class BackgroundJobException(RuntimeError):
    pass


class BackgroundJobState(Enum):
    NotStarted = 0
    Running = 1
    Paused = 2
    Stopped = 3
    Complete = 4


class BackgroundJob(ABC):
    _name: str = 'unknown_background_job'

    def __init__(self, session: Session, name: str):
        uuident = uuid.uuid1()

        with session:
            self.__storage: BackgroundJobStorage = BackgroundJobStorage(
                uuid=uuident,
                name=name,
                thread=-1,
                state=BackgroundJobState.NotStarted,
                progress_denominator=0,
                progress_current=0
            )
            session.add(self.__storage)

        self.__thread: Optional[threading.Thread] = None
        'The thread this background job is running on.'

        self.__thread_lock: threading.RLock = threading.RLock()
        'A lock used to ensure operations on this background job are thread-safe.'

        self.__pause_requested: bool = False
        self.__stop_requested: bool = False

        self._logger: logging.Logger = logging.getLogger('gbmm.BackgroundJob')
        self._logger.debug(f'Created background job {name} with UUID {uuident}.')

    @classmethod
    def get(cls, session: Session, *, job_uuid: uuid.UUID = None, name: str = None) -> list['BackgroundJob']:
        """
        Get existing :class:`BackgroundJob`\\s matching the given criteria.

        If no criteria are supplied, returns all existing :class:`BackgroundJob`\\s.

        :return: The list of BackgroundJobs matching the given criteria.
        """

        s = select(BackgroundJobStorage)
        if job_uuid is not None:
            s.filter_by(uuid=job_uuid)
        if name is not None:
            s.filter_by(name=name)
        return session.execute(s).scalars().all()

    @classmethod
    def get_jobs_of_same_type(cls, session: Session) -> list['BackgroundJob']:
        """
        Get existing :class:`FullIndexerBackgroundJob`\\s matching the given criteria.

        If no criteria are supplied, returns all existing :class:`FullIndexerBackgroundJob`\\s.

        :return: The list of FullIndexerBackgroundJob matching the given criteria.
        """
        return cls.get(session, name=cls._name)

    def start(self, session: Session):
        with self.__thread_lock:
            with session:
                name = self.__storage.name
                uuident = self.__storage.uuid
                if self.running(session):
                    self._logger.warning(f'Start attempted for background job {name} with UUID {uuident}, but the '
                                         f'job is already starting or has started.')
                    raise BackgroundJobException()

                if self.__pause_requested or self.paused(session):
                    self._logger.warning(f'Start attempted for background job {name} with UUID {uuident}, but the '
                                         f'job is pausing or has paused.')
                    raise BackgroundJobException()

                if self.__stop_requested or self.stopped(session):
                    self._logger.warning(f'Start attempted for background job {name} with UUID {uuident}, but the '
                                         f'job is stopping or has stopped.')
                    raise BackgroundJobException()

                self.__storage.state = BackgroundJobState.Running

                self._logger.debug(f'Starting background job {name} with UUID {uuident}.')
                self.__thread = threading.Thread(target=self._run, name=name, daemon=True)
                self.__thread.start()
                self._logger.debug(f'Background job started on thread {self.__thread.ident}.')

    def resume(self, session: Session):
        with self.__thread_lock:
            with session:
                name = self.__storage.name
                uuident = self.__storage.uuid
                if self.__pause_requested:
                    self._logger.warning(f'Resume attempted for background job {name} with UUID {uuident}, but the '
                                         f'job is in the process of pausing and cannot yet be resumed.')
                    raise BackgroundJobException()

                if not self.paused(session):
                    self._logger.warning(f'Resume attempted for background job {name} with UUID {uuident}, but the '
                                         f'job is not paused.')
                    raise BackgroundJobException()

                self.__storage.state = BackgroundJobState.Running

                self._logger.debug(f'Resuming background job {name} with UUID {uuident}.')
                self.__thread = threading.Thread(target=self._resume_run, name=name, daemon=True)
                self.__thread.start()
                self._logger.debug(f'Background job started on thread {self.__thread.ident}.')

    def pause(self, session: Session):
        with self.__thread_lock:
            with session:
                name = self.__storage.name
                uuident = self.__storage.uuid
                if not self.running(session):
                    self._logger.warning(f'Pause requested for background job {name} with UUID {uuident}, but the '
                                         f'job is not running.')
                    return

                if self.__pause_requested or self.__stop_requested:
                    self._logger.warning(f'Pause requested for background job {name} with UUID {uuident}, but the '
                                         f'job is already in the process of pausing or stopping.')
                    return

                self.__pause_requested = True

                self._logger.debug(f'Pause requested for background job {name} with UUID {uuident}.')

    def stop(self, session: Session):
        with self.__thread_lock:
            with session:
                name = self.__storage.name
                uuident = self.__storage.uuid

                # If a pause was already requested, override it
                self.__pause_requested = False

                if self.stopped(session) or self.__stop_requested:
                    self._logger.warning(f'Stop requested for background job {name} with UUID {uuident}, but the '
                                         f'job was already stopped.')
                    return

                if not self.running(session) and not self.paused(session):
                    self._logger.warning(f'Stop requested for background job {name} with UUID {uuident}, but the '
                                         f'job was never started.')
                    return

                self.__stop_requested = True

                self._logger.debug(f'Stop requested for background job {name} with UUID {uuident} running on thread'
                                   f'{self.__thread.ident}.')

    @property
    def _should_pause(self):
        return self.__pause_requested

    def _pause_complete(self, session: Session):
        with session:
            self.__pause_requested = False
            self.__storage.state = BackgroundJobState.Paused

    @property
    def _should_stop(self):
        return self.__stop_requested

    def _stop_complete(self, session: Session):
        with session:
            self.__stop_requested = False
            self.__storage.state = BackgroundJobState.Stopped

    def running(self, session: Session):
        with session:
            return self.__storage.state == BackgroundJobState.Running

    def stopped(self, session: Session):
        with session:
            return self.__storage.state == BackgroundJobState.Stopped

    def stopping(self):
        return self.__stop_requested

    def paused(self, session: Session):
        with session:
            return self.__storage.state == BackgroundJobState.Paused

    def pausing(self):
        return self.__pause_requested

    def _set_progress(self, session: Session, current: int = None, denominator: int = None):
        with self.__thread_lock:
            with session:
                if current is not None:
                    self.__storage.progress_current = current
                if denominator is not None:
                    self.__storage.progress_denominator = denominator

    def _set_progress_denominator(self, session: Session, denominator: int):
        with self.__thread_lock:
            self._set_progress(session, denominator=denominator)

    def _increment_progress(self, session: Session, increment: int):
        with self.__thread_lock:
            with session:
                self.__storage.progress_current += increment

    def progress_denominator(self, session: Session):
        with session:
            return self.__storage.progress_denominator

    def progress_current(self, session: Session):
        with session:
            return self.__storage.progress_current

    def progress_percent(self, session: Session):
        with session:
            if self.__storage.progress_denominator == 0:
                return 0
            return self.__storage.progress_current / self.__storage.progress_denominator

    @abstractmethod
    def _run(self):
        pass

    @abstractmethod
    def _resume_run(self):
        pass


