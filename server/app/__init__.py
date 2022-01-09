from pathlib import Path
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os

from config import config


def create_app():
    # region helpers
    def __set_up_logging():
        logging.basicConfig(level=logging.DEBUG)
        Path(config.LOG_DIR).mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)-8.8s %(name)s: %(message)s')
        log_path = os.path.join(config.LOG_DIR, config.LOG_FILE)
        log_max_size = config.LOG_MAX_SIZE * 1000  # Kilobytes
        file_handler = RotatingFileHandler(log_path, maxBytes=log_max_size, backupCount=config.LOG_BACKUP_COUNT)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(config.LOG_LEVEL)
        file_handler.name = 'file'
        server.logger.handlers.clear()
        server.logger.addHandler(file_handler)
        server.logger.propagate = False

    # endregion helpers
    server = Flask(
        'server.app',
        instance_path=config.SERVER_ROOT,
        instance_relative_config=True,
        template_folder='areas'
    )
    server.name = config.SERVER_NAME
    server.secret_key = config.SECRET_KEY
    __set_up_logging()
    Path(config.SERVER_ROOT).mkdir(parents=True, exist_ok=True)

    server.logger.info(f'Starting {config.SERVER_NAME} version {config.SERVER_VERSION}.')

    # Blueprints
    from . import index
    server.register_blueprint(index.bp)
    from . import definitions
    server.register_blueprint(definitions.bp)
    from . import downloads
    server.register_blueprint(downloads.bp)
    from . import videos
    server.register_blueprint(videos.bp)
    from . import video_categories
    server.register_blueprint(video_categories.bp)
    from . import video_shows
    server.register_blueprint(video_shows.bp)
    from . import settings
    server.register_blueprint(settings.bp)
    from . import startup
    server.register_blueprint(startup.bp)
    from . import system
    server.register_blueprint(system.bp)
    from . import media
    server.register_blueprint(media.bp)

    settings.initialize()

    return server



