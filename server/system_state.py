from sqlalchemy import select
from sqlalchemy.orm import Session
from server.database import SystemStateStorage


class SystemState:
    __defaults = {
        'id': 'SystemState',
        'db__version': '1.0',
        'first_time_setup__initiated': False,
        'first_time_setup__complete': False
    }

    @staticmethod
    def get(session: Session) -> SystemStateStorage:
        """
        Get the system state storage. If the system state storage has not yet been initialized, it will be initialized.

        :param session: A SQLAlchemy session
        :return: The system state storage
        """
        storage = session.execute(
            select(SystemStateStorage)
            .filter_by(id=SystemState.__defaults.get('id'))
        ).scalars().first()

        if storage is None:
            storage = SystemState.__initialize_storage(session)

        return storage

    @staticmethod
    def __initialize_storage(session: Session) -> SystemStateStorage:
        """
        Initialize the system state to default values.

        :param session: A SQLAlchemy session
        :return: The system state storage
        """
        state = SystemStateStorage(
            id=SystemState.__defaults.get('id'),
            db__version=SystemState.__defaults.get('db__version'),
            first_time_setup__initiated=SystemState.__defaults.get('first_time_setup__initiated'),
            first_time_setup__complete=SystemState.__defaults.get('first_time_setup__complete')
        )
        session.add(state)
        return state
