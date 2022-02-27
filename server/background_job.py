import logging
import threading

from abc import ABC
from typing import Optional, TypeVar, Type

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from server.database import BackgroundJobStorage, BackgroundJobArchive

BackgroundJobState = BackgroundJobStorage.BackgroundJobState

T = TypeVar('T', bound='BackgroundJob')


class BackgroundJobException(RuntimeError):
    pass


class BackgroundJobData:
    def __init__(self):
        self.__data: dict = {}

    def get(self, key: str):
        try:
            return self.__data[key]
        except KeyError:
            self.__data[key] = None
            return self.__data[key]

    def set(self, key: str, value: any):
        self.__data[key] = value


class BackgroundJob(ABC):
    _pauseable: bool = False
    _recoverable: bool = False
    _logger_suffix: str = 'BackgroundJob'

    def _run(self):
        pass

    def _resume(self):
        pass

    def _recover(self):
        pass

    def __init__(self, session: Session, *, storage: BackgroundJobStorage = None):
        if storage is not None:
            # Retrieving this BackgroundJob from storage
            job_uuid = uuid.UUID(storage.uuid)
        else:
            # Creating a new BackgroundJob
            job_uuid = uuid.uuid1()
            storage = BackgroundJobStorage(
                uuid=str(job_uuid),
                name=self.__class__.__name__,
                pauseable=self._pauseable,
                recoverable=self._recoverable,
                thread=-1,
                state=BackgroundJobState.NotStarted,
                progress_denominator=0,
                progress_current=0
            )
            session.add(storage)

        self.__uuid = job_uuid

        self.__thread: Optional[threading.Thread] = None
        'The thread this background job is running on.'

        self.__thread_lock: threading.RLock = threading.RLock()
        'A lock used to ensure operations on this background job are thread-safe.'

        self.__pause_requested: bool = False
        self.__stop_requested: bool = False

        self.logger: logging.Logger = logging.getLogger('gbmm.BackgroundJob').getChild(self._logger_suffix)
        self.logger.debug(f'Created background job {self.__class__.__name__} with UUID {self.__uuid}.')

        self.data = BackgroundJobData()

    @classmethod
    def get_all(cls: T, session: Session) -> list[T]:
        """
        Get all existing :class:`BackgroundJob`\\s of the same subclass.

        If no criteria are supplied, returns all existing :class:`BackgroundJob`\\s of the same subclass.

        :return: The list of BackgroundJobs of the same subclass matching the given criteria.
        """
        return get_all(session, name=cls.__name__)

    def start(self, session: Session):
        with self.__thread_lock:
            storage = self.__get_storage(session)
            name = storage.name
            uuident = storage.uuid
            if self.running(session):
                self.logger.warning(f'Start attempted for background job {name} with UUID {uuident}, but the '
                                    f'job is already starting or has started.')
                raise BackgroundJobException()

            if self.__pause_requested or self.paused(session):
                self.logger.warning(f'Start attempted for background job {name} with UUID {uuident}, but the '
                                    f'job is pausing or has paused.')
                raise BackgroundJobException()

            if self.__stop_requested or self.stopped(session):
                self.logger.warning(f'Start attempted for background job {name} with UUID {uuident}, but the '
                                    f'job is stopping or has stopped.')
                raise BackgroundJobException()

            storage.state = BackgroundJobState.Running

            self.logger.debug(f'Starting background job {name} with UUID {uuident}.')
            self.__thread = threading.Thread(target=self._run, name=name, daemon=True)
            self.__thread.start()
            self.logger.debug(f'Background job started on thread {self.__thread.ident}.')

    def resume(self, session: Session):
        with self.__thread_lock:
            storage = self.__get_storage(session)
            name = storage.name
            uuident = storage.uuid

            if not storage.pauseable:
                self.logger.warning(f'Resume attempted for background job {name} with UUID {uuident}, but it is of a '
                                    f'job type that cannot be paused.')
                raise BackgroundJobException()

            if self.__pause_requested:
                self.logger.warning(f'Resume attempted for background job {name} with UUID {uuident}, but the '
                                    f'job is in the process of pausing and cannot yet be resumed.')
                raise BackgroundJobException()

            if not self.paused(session):
                self.logger.warning(f'Resume attempted for background job {name} with UUID {uuident}, but the '
                                    f'job is not paused.')
                raise BackgroundJobException()

            storage.state = BackgroundJobState.Running

            self.logger.debug(f'Resuming background job {name} with UUID {uuident}.')
            self.__thread = threading.Thread(target=self._resume, name=name, daemon=True)
            self.__thread.start()
            self.logger.debug(f'Background job started on thread {self.__thread.ident}.')

    def pause(self, session: Session):
        with self.__thread_lock:
            storage = self.__get_storage(session)
            name = storage.name
            uuident = storage.uuid

            if not storage.pauseable:
                self.logger.warning(f'Pause attempted for background job {name} with UUID {uuident}, but it is of a '
                                    f'job type that cannot be paused.')
                raise BackgroundJobException()

            if not self.running(session):
                self.logger.warning(f'Pause requested for background job {name} with UUID {uuident}, but the '
                                    f'job is not running.')
                raise BackgroundJobException()

            if self.__pause_requested or self.__stop_requested:
                self.logger.warning(f'Pause requested for background job {name} with UUID {uuident}, but the '
                                    f'job is already in the process of pausing or stopping.')
                raise BackgroundJobException()

            self.__pause_requested = True

            self.logger.debug(f'Pause requested for background job {name} with UUID {uuident}.')

    def stop(self, session: Session):
        with self.__thread_lock:
            storage = self.__get_storage(session)
            name = storage.name
            uuident = storage.uuid

            # If a pause was already requested, override it
            self.__pause_requested = False

            if self.stopped(session) or self.__stop_requested:
                self.logger.warning(f'Stop requested for background job {name} with UUID {uuident}, but the '
                                    f'job was already stopped.')
                raise BackgroundJobException()

            if not self.running(session) and not self.paused(session):
                self.logger.warning(f'Stop requested for background job {name} with UUID {uuident}, but the '
                                    f'job was never started.')
                raise BackgroundJobException()

            self.__stop_requested = True

            self.logger.debug(f'Stop requested for background job {name} with UUID {uuident} running on thread'
                              f'{self.__thread.ident}.')

    def recover(self, session: Session):
        """
        Recover from system restart.

        :param session: A SQLAlchemy session
        """
        with self.__thread_lock:
            storage = self.__get_storage(session)
            name = storage.name
            uuident = storage.uuid

            if not self._recoverable:
                self.logger.warning(f'Recover requested for background job {name} with UUID {uuident}, but the '
                                    f'job is of a type that is not recoverable.')
                raise BackgroundJobException()

            if self.stopped(session) or self.__stop_requested:
                self.logger.warning(f'Recover requested for background job {name} with UUID {uuident}, but the '
                                    f'job was stopped and cannot be recovered.')
                raise BackgroundJobException()

            if self.running(session) or self.paused(session):
                storage.state = BackgroundJobState.Running
                self.logger.debug(f'Recovering background job {name} with UUID {uuident}.')
                self.__thread = threading.Thread(target=self._recover, name=name, daemon=True)
                self.__thread.start()
                self.logger.debug(f'Background job started on thread {self.__thread.ident}.')

            else:  # Probably never started
                raise BackgroundJobException()

    def archive(self, session: Session):
        with self.__thread_lock:
            storage = self.__get_storage(session)
            archive = BackgroundJobArchive(
                uuid=storage.uuid,
                name=storage.name,
                thread=storage.thread,
                state=storage.state,
                progress_denominator=storage.progress_denominator,
                progress_current=storage.progress_current
            )
            session.add(archive)
            session.query(BackgroundJobStorage).filter_by(uuid=storage.uuid).delete()

    def fail(self, session: Session):
        with self.__thread_lock:
            storage = self.__get_storage(session)
            storage.state = BackgroundJobState.Failed
            self.archive(session)

    def __get_storage(self, session: Session):
        storage = session.query(BackgroundJobStorage).get(str(self.__uuid))
        if storage is None:
            self.logger.error(f'Attempted to retrieve background job with UUID {self.__uuid}, but a job with that'
                              f'UUID does not exist in the database.')
            raise BackgroundJobException()
        return storage

    @property
    def uuid(self):
        return self.__uuid

    @property
    def _should_pause(self):
        return self.__pause_requested

    def _pause_complete(self, session: Session):
        self.__pause_requested = False
        self.__get_storage(session).state = BackgroundJobState.Paused

    @property
    def _should_stop(self):
        return self.__stop_requested

    def _stop_complete(self, session: Session):
        self.__stop_requested = False
        self.__get_storage(session).state = BackgroundJobState.Stopped
        self.archive(session)

    def running(self, session: Session):
        return self.__get_storage(session).state == BackgroundJobState.Running

    def stopped(self, session: Session):
        return self.__get_storage(session).state == BackgroundJobState.Stopped

    def stopping(self):
        return self.__stop_requested

    def paused(self, session: Session):
        return self.__get_storage(session).state == BackgroundJobState.Paused

    def pausing(self):
        return self.__pause_requested

    def _set_progress(self, session: Session, current: int = None, denominator: int = None):
        with self.__thread_lock:
            if current is not None:
                self.__get_storage(session).progress_current = current
            if denominator is not None:
                self.__get_storage(session).progress_denominator = denominator

    def _set_progress_denominator(self, session: Session, denominator: int):
        with self.__thread_lock:
            self._set_progress(session, denominator=denominator)

    def _increment_progress(self, session: Session, increment: int):
        with self.__thread_lock:
            self.__get_storage(session).progress_current += increment

    def progress_denominator(self, session: Session):
        return self.__get_storage(session).progress_denominator

    def progress_current(self, session: Session):
        return self.__get_storage(session).progress_current

    def progress_percent(self, session: Session):
        storage = self.__get_storage(session)
        if storage.progress_denominator == 0:
            return 0
        return storage.progress_current / storage.progress_denominator


class BackgroundJobRegistryEntry:
    def __init__(self, name: str, cls: Type[BackgroundJob]):
        self.name = name
        self.cls = cls


def register(cls: Type[BackgroundJob]):
    """
    Class decorator for defining a background job.

    :param cls: The class representing the background job.
    :return: The decorated background job class.
    """
    __registry.append(cls)
    fn_run = getattr(cls, '_run', None)
    fn_resume = getattr(cls, '_resume', None)
    fn_recover = getattr(cls, '_recover', None)

    assert fn_run is not None and callable(fn_run), 'Background jobs must define a _run function.'

    if fn_resume is not None:
        cls._pauseable = True

    if fn_recover is not None:
        cls._recoverable = True

    cls._logger_suffix = cls.__name__

    return cls


def get(session: Session,
        *,
        job_uuid: uuid.UUID = None,
        name: str = None,
        recoverable: bool = None) -> Optional[BackgroundJob]:
    """
    Get the first existing :class:`BackgroundJob` matching the given criteria.

    If no criteria are supplied, returns the first existing :class:`BackgroundJob`.

    If no :class:`BackgroundJob` matches the given criteria, returns None.

    :return: The first of BackgroundJob matching the given criteria or None.
    """
    jobs = get_all(session, job_uuid=job_uuid, name=name, recoverable=recoverable)
    if len(jobs) > 0:
        return jobs[0]
    else:
        return None


def get_all(session: Session,
            *,
            job_uuid: uuid.UUID = None,
            name: str = None,
            recoverable: bool = None) -> list[BackgroundJob]:
    """
    Get all existing :class:`BackgroundJob`\\s matching the given criteria.

    If no criteria are supplied, returns all existing :class:`BackgroundJob`\\s.

    If no :class:`BackgroundJob`\\s match the given criteria, returns an empty list.

    :return: The list of BackgroundJobs matching the given criteria.
    """

    s = select(BackgroundJobStorage)
    if job_uuid is not None:
        s.filter_by(uuid=job_uuid)
    if name is not None:
        s.filter_by(name=name)
    if recoverable is not None:
        s.filter_by(recoverable=recoverable)
    job_storages = session.execute(s).scalars().all()

    out = []

    for storage in job_storages:
        cls = next((r for r in __registry if r.__name__ == storage.name), None)
        if cls is None:
            raise BackgroundJobException()
        else:
            out.append(cls(session, storage=storage))

    return out


def startup(session: Session):
    not_recoverable = get_all(session, recoverable=False)
    for job_storage in not_recoverable:
        job = get(session, job_uuid=job_storage.uuid)
        job.fail(session)
    for job_storage in session.query(BackgroundJobStorage).scalars().all():  # Everything left is recoverable
        job = get(session, job_uuid=job_storage.uuid)
        job.recover(session)


__registry: list[Type[BackgroundJob]] = []
