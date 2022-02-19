import threading
from datetime import datetime
from pathlib import Path
import logging
import requests
from sqlalchemy import select
from tqdm import tqdm
import sys
import traceback

from config import config
import server.gb_api as gb_api
from server import database
from server.database import Session, File, Download, DatabaseError, GBDownloadable


class DownloadFailedError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Downloader:
    headers = config.HEADERS
    chunk_size = 10 * 1024 * 1024  # 10 MB

    def __init__(self):
        self.logger = logging.getLogger('gbmm').getChild('downloader')
        self.__download_pushed_condition = threading.Condition()
        self.logger.debug('Starting downloader daemon')
        self.session = Session()
        self.__daemon = threading.Thread(target=self.__processor, daemon=True).start()

    @staticmethod
    def __api_key_string():
        return f'?{config.API_KEY_FIELD}={config.API_KEY}'

    def __peek_download(self):
        with self.session:
            peeked = self.session.execute(
                select(Download)
                .filter_by(status=Download.DownloadStatus.IN_PROGRESS)
                .order_by(Download.created_time.asc())
            ).scalars().first()

            # If a download is in progress, return that download. We will restart the download.
            # This is most likely to happen if the daemon was stopped in the middle of a download.
            if peeked is not None:
                return peeked

            peeked = self.session.execute(
                select(Download)
                .filter_by(status=Download.DownloadStatus.QUEUED)
                .order_by(Download.created_time.asc())
            ).scalars().first()
        return peeked

    def __processor(self):
        daemon_logger = self.logger.getChild('daemon')
        daemon_logger.debug('Downloader daemon processor thread started')
        while True:
            with self.__download_pushed_condition:
                while self.__peek_download() is None:
                    daemon_logger.debug(f'Downloader daemon awaiting notification.')
                    self.__download_pushed_condition.wait()
                    daemon_logger.debug(f'Downloader daemon received notification.')

            download = self.__peek_download()
            if download is not None:
                daemon_logger.debug(f'Dequeued download: {download}')
                self.__download(download)

    def __download(self, download: Download):
        url = None
        progress_bar = None
        failed = False
        failed_reason = ''
        exc = None

        try:
            self.session.add(download)
            download.status = Download.DownloadStatus.IN_PROGRESS
            url = f'{download.url}{Downloader.__api_key_string()}'
            entity_type = database.get_entity_class_by_item_name(download.obj_item_name)
            if download.obj_id is None:
                raise ValueError('Object ID is None.')
            obj: GBDownloadable = self.session.get(entity_type, download.obj_id)
            self.session.commit()

            if obj is None:
                # The GBEntity data for this download has not been stored to the database yet.
                # Query the API and store it to the database.
                obj_data = gb_api.get_one(entity_type, download.obj_id)
                obj = database.from_api(self.session, entity_type, obj_data)

            if obj is None:
                download.status = Download.DownloadStatus.FAILED
                download.failed_reason = f'Failed to get GBEntity object associated with this download from the GB API.'
                self.session.commit()
                return

            self.session.add(obj)

            name = None
            if hasattr(obj, 'name'):
                name = obj.name
            if name is None:
                name = '(No title)'

            self.logger.info(f'Downloading {obj.__item_name__}: {name} ({obj.id})')
            self.logger.debug(f'Download URL: {url}')

            download.start_time = datetime.now()
            response = requests.get(url, headers=Downloader.headers, stream=True)

            self.logger.debug(f'Response headers:\n{response.headers}')
            download.response_headers = response.headers

            if not response.ok:
                download.status = Download.DownloadStatus.FAILED
                download.failed_reason = f'Bad response from request to download URL: {response.status_code}'
                self.session.commit()
                return

            progress_bar = tqdm(total=download.size_bytes, unit='iB', unit_scale=True)

            self.logger.debug(f'Beginning content stream. Chunk size {Downloader.chunk_size}.')

            self.session.commit()

            # Get or create the file where we will save this download
            file = self.session.execute(
                select(File).filter_by(
                    obj_item_name=download.obj_item_name,
                    obj_id=download.obj_item_name,
                    obj_url_field=download.obj_url_field
                )
            ).scalars().first()

            if file is None:
                file = File.create_from_download(download)
                self.session.add(file)

            # Associate the file with its object and this download
            obj.file = file
            download.file = file

            # Create the destination directory if it does not exist
            Path(file.path).parent.absolute().mkdir(parents=True, exist_ok=True)

            self.session.commit()

            with open(file.path, 'wb') as handle:
                for data in response.iter_content(Downloader.chunk_size):
                    handle.write(data)
                    downloaded_bytes = len(data)
                    self.logger.debug(f'Downloaded {downloaded_bytes}B of data.')
                    progress_bar.update(downloaded_bytes)
                    download.downloaded_bytes += downloaded_bytes
                    self.session.commit()

            download.status = Download.DownloadStatus.COMPLETE
            download.finish_time = datetime.now()
            self.logger.info(f'Download complete.')
            self.logger.debug(
                f'Download time {download.finish_time.timestamp() - download.start_time.timestamp()}s')
            self.session.commit()

        except ValueError as e:
            more_info = ''
            if e.args is not None:
                more_info = ', '.join(e.args)
            failed_reason = f'Unexpected value. {more_info}'
            exc = sys.exc_info()
            failed = True

        except PermissionError or FileNotFoundError or FileExistsError or OSError:
            failed_reason = 'Error saving file.'
            exc = sys.exc_info()
            failed = True

        except requests.ConnectionError:
            failed_reason = 'Connection error.'
            exc = sys.exc_info()
            failed = True

        except requests.HTTPError:
            failed_reason = 'HTTP Error.'
            exc = sys.exc_info()
            failed = True

        except requests.Timeout:
            failed_reason = 'Timeout reached.'
            exc = sys.exc_info()
            failed = True

        except requests.TooManyRedirects:
            failed_reason = 'Too many redirects.'
            exc = sys.exc_info()
            failed = True

        except DatabaseError as e:
            failed_reason = f'Database error: {e.msg}.'
            exc = sys.exc_info()
            failed = True

        except:
            failed_reason = 'Other failure.'
            exc = sys.exc_info()
            failed = True

        finally:
            if progress_bar is not None:
                progress_bar.close()
            if failed:
                failed_message = f'Download failed for {url}: {failed_reason}\n' \
                                 f'{traceback.format_exception(*exc)}'
                self.logger.error(failed_message)
                download.status = Download.DownloadStatus.FAILED
                download.failed_reason = failed_message
                self.session.commit()

    def enqueue(self, session: Session, obj, download_url_field: str):
        download = Download.create_from_obj(obj, download_url_field)
        session.add(obj)
        session.add(download)
        download.status = Download.DownloadStatus.QUEUED
        session.flush()

        self.logger.debug(f"Enqueued download: "
                          f"Object type: {obj.__item_name__}, ID: {obj.id}, url_field: {download_url_field}.")

        with self.__download_pushed_condition:
            self.__download_pushed_condition.notify_all()
            self.logger.debug(f"Download queue condition notified")

        return download


downloader = Downloader()
