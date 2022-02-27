import enum
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Type, Callable, Generator

from marshmallow import Schema
from requests.structures import CaseInsensitiveDict
from sqlalchemy import create_engine, Column, Boolean, Integer, String, DateTime, ForeignKey, select, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapper

from config import config
from server.messenger import publish, MessageEventType
from server.serialization import FileSchema, Marshmallowable, DownloadSchema, ImageSchema, VideoSchema,\
    VideoShowSchema, VideoCategorySchema, KeyValueSchema


class DatabaseError(IOError):
    def __init__(self, msg):
        self.msg = msg


class Base:
    def key_value_generator(self):
        """
        Generate attribute name/value pairs, filtering out SQLAlchemy attributes.
        https://stackoverflow.com/a/54034230
        """
        excl = ('_sa_adapter', '_sa_instance_state')
        for k, v in vars(self).items():
            if not k.startswith('_') and not any(hasattr(v, a) for a in excl):
                yield k, v

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in self.key_value_generator())
        return f'{self.__class__.__name__}({params})'


db_path = os.path.join(config.DATABASE_DIR, config.DATABASE_NAME)
# Create the database directory if it does not exist
Path(db_path).parent.absolute().mkdir(parents=True, exist_ok=True)
db_url = f'sqlite+pysqlite:///{db_path}'
engine = create_engine(db_url, future=True)
SessionMaker = sessionmaker(engine)
Base = declarative_base(cls=Base)


class GBBase(Marshmallowable):
    __item_name__: str
    __collection_name__: str
    __type_id__: str
    __marshmallow_schema__: Callable[[], Schema]

    api_detail_url: Column
    '''URL pointing to the detail resource.'''
    id: Column
    '''Unique ID'''
    guid: Column
    '''Cross-entity unique ID'''
    site_detail_url: Column
    '''URL pointing to the item(s) on Giant Bomb.'''
    last_full_refresh: Column
    '''The date of the last full refresh for this API object's information.'''

    @classmethod
    def get_existing(cls, session, obj: 'GBBase'):
        pass

    @classmethod
    def from_api_result(cls, session, result):
        pass


class GBDownloadable:
    file_id: Column
    file: Column


class GBEntity(GBBase):
    @classmethod
    def from_api_result(cls, session, result):
        existing = cls.get_existing(session, api_result=result)
        if existing is not None:
            return existing

        empty = True
        new = cls()
        keys = [attr.key for attr in new._sa_instance_state.attrs]
        for key in keys:
            if hasattr(result, key):
                # Check if this is a mapped entity
                if hasattr(getattr(cls, key).property, 'entity'):
                    # Is a mapped entity
                    target_entity_type = getattr(cls, key).property.entity.entity
                    obj = target_entity_type.from_api_result(session, getattr(result, key))

                    if obj is not None:
                        empty = False
                        setattr(new, key, obj)
                else:
                    # Is not a mapped entity
                    val = getattr(result, key, None).pyval
                    if val is not None:
                        empty = False
                        setattr(new, key, val)

        if empty:
            return None
        else:
            new.last_full_refresh = datetime.now().isoformat()
            return new

    @classmethod
    def get_existing(cls, session, *, obj: 'GBBase' = None, api_result: any = None):
        """
        Checks if the object already exists in the database. If it does, returns the existing object.
        :param session: A database session.
        :param obj: A GBEntity object for which to check for a match.
        :param api_result: An API result object for which to check for a match.
        :return: The existing object, or None if no matching object exists.
        """
        if obj is not None:
            obj_id = obj.id
        elif api_result is not None:
            obj_id = int(getattr(api_result, 'id', -1))
        else:
            return None
        return session.get(cls, obj_id)

    @classmethod
    def id_to_guid(cls, id: int):
        return f'{cls.__type_id__}-{id}'


class Setting(Base, Marshmallowable):
    __tablename__ = 'setting'
    __marshmallow_schema__ = KeyValueSchema
    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    type = Column(String)

    @staticmethod
    def get(session, key: str):
        return session.execute(
            select(Setting)
            .filter_by(key=key)
        ).scalars().first()

    @staticmethod
    def set(session, key: str, value: str):
        setting = session.execute(
            select(Setting)
            .filter_by(key=key)
        ).scalars().first()
        setting.value = value
        session.flush()


class SystemStateStorage(Base):
    __tablename__ = 'system'
    id = Column(String, primary_key=True)
    indexer_full__last_update = Column(DateTime)
    indexer_quick__last_update = Column(DateTime)
    db__version = Column(String)
    first_time_setup__initiated = Column(Boolean)
    first_time_setup__complete = Column(Boolean)


class BackgroundJobStorage(Base):
    class BackgroundJobState:
        NotStarted = 0
        Running = 1
        Paused = 2
        Stopped = 3
        Complete = 4
        Failed = 5

    __tablename__ = 'background_jobs'
    uuid = Column(String, primary_key=True)
    'The unique identifier for this BackgroundJob.'
    name = Column(String)
    'The name of this background job type this BackgroundJob belongs to.'
    pauseable = Column(Boolean)
    'Whether or not this background job can be paused and resumed.'
    recoverable = Column(Boolean)
    'Whether or not this background job can be recovered after a system restart.'
    thread = Column(Integer)
    'The ID of the thread on which this BackgroundJob is running.'
    state = Column(Integer)
    'The state of the background job (E.g., not started, running, paused, stopped, complete).'
    progress_denominator = Column(Integer)
    'The number that represents all of the progress this BackgroundJob will have made when complete.'
    progress_current = Column(Integer)
    'The number that represents the current progress of the BackgroundJob.'


class BackgroundJobArchive(Base):
    __tablename__ = 'background_job_archives'
    uuid = Column(String, primary_key=True)
    'The unique identifier for this BackgroundJob.'
    name = Column(String)
    'The name of this background job type this BackgroundJob belongs to.'
    thread = Column(Integer)
    'The ID of the thread on which this BackgroundJob was running.'
    state = Column(Integer)
    'The final state of the background job (E.g., not started, running, paused, stopped, complete).'
    progress_denominator = Column(Integer)
    'The number that represents all of the progress this BackgroundJob will have made when complete.'
    progress_current = Column(Integer)
    'The number that represents the current progress of the BackgroundJob.'


class File(Base, Marshmallowable):
    __tablename__ = 'file'
    __marshmallow_schema__ = FileSchema
    id = Column(Integer, primary_key=True)
    name = Column(String)
    obj_item_name = Column(String)
    obj_id = Column(Integer)
    obj_url_field = Column(String)
    downloads = relationship('Download', back_populates='file')
    path = Column(String)
    size_bytes = Column(Integer)
    content_type = Column(String)

    @staticmethod
    def __get_url_file_part(url: str):
        if url is None:
            raise ValueError()
        return url.split('/').pop()

    @staticmethod
    def __build_destination_path(d: 'Download'):
        """
        Build and return a string to be used for the file destination.
        """
        dir_id = str(d.obj_id).zfill(5)
        url_file_part = File.__get_url_file_part(d.url)
        filename = f'{dir_id}_{d.obj_url_field}_{url_file_part}'
        directory = os.path.join(config.FILE_ROOT, d.obj_item_name, dir_id[:2], dir_id[:4], dir_id)

        return os.path.join(directory, filename)

    @staticmethod
    def create_from_download(download: 'Download') -> 'File':
        return File(
            name=download.name,
            obj_item_name=download.obj_item_name,
            obj_id=download.obj_id,
            obj_url_field=download.obj_url_field,
            path=File.__build_destination_path(download),
            size_bytes=download.size_bytes,
            content_type=download.content_type
        )


class Download(Base, Marshmallowable):
    __tablename__ = 'download'
    __marshmallow_schema__ = DownloadSchema
    id = Column(Integer, primary_key=True)
    name = Column(String)
    obj_item_name = Column(String)
    obj_id = Column(Integer)
    obj_url_field = Column(String)
    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship('File', back_populates='downloads')
    status = Column(Integer)
    failed_reason = Column(String)
    created_time = Column(DateTime)
    start_time = Column(DateTime)
    finish_time = Column(DateTime)
    url = Column(String)
    _size_bytes = Column('size_bytes', Integer)
    '''Size of the downloadable data in bytes. Set when response_headers is set.'''
    downloaded_bytes = Column(Integer)
    _content_type = Column('content_type', String)
    '''Content MIME type. Set when response_headers is set.'''
    _response_headers = Column('response_headers', String)
    '''Full set of headers returned with the download request as serialized JSON.'''

    class DownloadStatus(enum.IntEnum):
        QUEUED = 10
        IN_PROGRESS = 20
        PAUSED = 30
        COMPLETE = 40
        CANCELLED = 50
        FAILED = 90

    @staticmethod
    def create_from_obj(obj: GBEntity, obj_url_field: str):
        return Download(
            name=getattr(obj, 'name', '(No name)'),
            obj_item_name=obj.__item_name__,
            obj_id=obj.id,
            obj_url_field=obj_url_field,
            url=getattr(obj, obj_url_field),
            created_time=datetime.now(),
            downloaded_bytes=0
        )

    @property
    def size_bytes(self):
        """Size of the downloadable data in bytes. Set when response_headers is set."""
        return self._size_bytes

    @property
    def content_type(self):
        """Content MIME type. Set when response_headers is set."""
        return self._content_type

    @property
    def response_headers(self):
        """Full set of headers returned with the download request as serialized JSON."""
        return self._response_headers

    @response_headers.setter
    def response_headers(self, value: CaseInsensitiveDict):
        """Full set of headers returned with the download request as serialized JSON."""
        self._response_headers = json.dumps(dict(value))
        self._content_type = str(value.get('Content-Type'))
        self._size_bytes = int(value.get('Content-Length', 0))


class Association(Base, GBEntity):
    __tablename__ = 'association'
    __item_name__ = 'association'
    __collection_name__ = 'associations'
    __type_id__ = 910000

    api_detail_url = Column(String)
    '''URL pointing to the detail resource.'''
    id = Column(Integer)
    '''Unique ID within each entity type.'''
    guid = Column(String, primary_key=True, autoincrement=False)
    '''Cross-entity unique ID'''
    site_detail_url = Column(String)
    '''URL pointing to the item(s) on Giant Bomb.'''
    name = Column(String)
    '''Name of the associated item.'''


class Image(Base, GBBase, GBDownloadable):
    __tablename__ = 'image'
    __item_name__ = 'image'
    __collection_name__ = 'images'
    __type_id__ = 920000
    __marshmallow_schema__ = ImageSchema

    # Not from API
    id = Column(Integer, primary_key=True)

    icon_url = Column(String)
    '''URL to the icon version of the image.'''
    medium_url = Column(String)
    '''URL to the medium size of the image.'''
    original_url = Column(String)
    '''URL to the original image.'''
    screen_url = Column(String)
    '''URL to the screenshot version of the image.'''
    screen_large_url = Column(String)
    '''URL to the large screenshot version of the image.'''
    small_url = Column(String)
    '''URL to the small version of the image.'''
    super_url = Column(String)
    '''URL to the super sized version of the image.'''
    thumb_url = Column(String)
    '''URL to the thumb-sized version of the image.'''
    tiny_url = Column(String)
    '''URL to the tiny version of the image.'''
    image_tags = Column(String)
    '''Name of image tag for filtering images.'''

    # Not from API
    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship('File')
    last_full_refresh = Column(String)

    @classmethod
    def from_api_result(cls, session, result):
        existing = cls.get_existing(session, api_result=result)
        if existing is not None:
            return existing

        empty = True
        new = cls()
        keys = [attr.key for attr in new._sa_instance_state.attrs]
        for key in keys:
            if hasattr(result, key):
                val = getattr(result, key, None).pyval
                if val is not None:
                    empty = False
                    setattr(new, key, val)

        if empty:
            return None
        else:
            new.last_full_refresh = datetime.now().isoformat()
            return new

    @classmethod
    def get_existing(cls, session, *, image: 'Image' = None, api_result: any = None):
        """
        Checks if the object already exists in the database. If it does, returns the existing object.
        :param session: A database session.
        :param image: An Image for which to check for a match.
        :param api_result: An API result object for which to check for a match.
        :return: The existing object, or None if no matching object exists.
        """
        if image is not None:
            return session.execute(
                select(cls).filter_by(
                    icon_url=image.icon_url,
                    medium_url=image.medium_url,
                    original_url=image.original_url,
                    screen_url=image.screen_url,
                    screen_large_url=image.screen_large_url,
                    small_url=image.small_url,
                    super_url=image.super_url,
                    thumb_url=image.thumb_url,
                    tiny_url=image.tiny_url
                )
            ).scalars().first()
        elif api_result is not None:
            return session.execute(
                select(cls).filter_by(
                    icon_url=str(getattr(api_result, 'icon_url', None)),
                    medium_url=str(getattr(api_result, 'medium_url', None)),
                    original_url=str(getattr(api_result, 'original_url', None)),
                    screen_url=str(getattr(api_result, 'screen_url', None)),
                    screen_large_url=str(getattr(api_result, 'screen_large_url', None)),
                    small_url=str(getattr(api_result, 'small_url', None)),
                    super_url=str(getattr(api_result, 'super_url', None)),
                    thumb_url=str(getattr(api_result, 'thumb_url', None)),
                    tiny_url=str(getattr(api_result, 'tiny_url', None))
                )
            ).scalars().first()


class Video(Base, GBEntity, GBDownloadable):
    __tablename__ = 'video'
    __item_name__ = 'video'
    __collection_name__ = 'videos'
    __type_id__ = 2300
    __marshmallow_schema__ = VideoSchema

    api_detail_url = Column(String)
    '''URL pointing to the video resource.'''
    # associations = ApiListField('', StubObject), TODO
    '''Related objects to the video.'''
    deck = Column(String)
    '''Brief summary of the video.'''
    guid = Column(String)
    '''Cross-entity unique ID'''
    hd_url = Column(String)
    '''URL to the HD version of the video.'''
    high_url = Column(String)
    '''URL to the High Res version of the video.'''
    low_url = Column(String)
    '''URL to the Low Res version of the video.'''
    embed_player = Column(String)
    '''
    URL for video embed player. To be inserted into an iFrame. You can add ?autoplay=true to auto-play. You
    can add ?time=x where 'x' is an integer between 0 and the length of the video in seconds to start the
    video at that point. You can add ?vol=x where 'x' is a decimal between 0 and 1, .75 for example,
    to set the starting volume. The above three parameters may be used together. Example:
    ?time=45&vol=.5&autoplay=true See https://www.giantbomb.com/api/video-embed-sample/ for more information
    on using the embed player.
    '''
    id = Column(Integer, primary_key=True, autoincrement=False)
    '''Unique ID of the video.'''
    # Not from API
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship('Image')
    '''Main image of the video.'''
    length_seconds = Column(Integer)
    '''Length (in seconds) of the video.'''
    name = Column(String)
    '''Name of the video.'''
    publish_date = Column(String)
    '''Date the video was published on Giant Bomb.'''
    site_detail_url = Column(String)
    '''URL pointing to the video on Giant Bomb.'''
    url = Column(String)
    '''The video's filename.'''
    user = Column(String)
    '''Author of the video.'''
    # Not from API
    video_categories_id = Column(Integer, ForeignKey('video_category.id'))
    video_categories = relationship('VideoCategory')
    '''Video categories'''
    video_show_id = Column(Integer, ForeignKey('video_show.id'))
    video_show = relationship('VideoShow', back_populates='videos')
    '''Video show'''
    youtube_id = Column(String)
    '''Youtube ID for the video.'''
    saved_time = Column(String)
    '''The time where the user left off watching this video'''
    premium = Column(String)
    '''Premium status of video.'''
    hosts = Column(String)
    '''Hosts of the video.'''
    crew = Column(String)
    '''Crew of the video.'''

    # Not from API
    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship('File')
    last_played = Column(String)
    last_full_refresh = Column(String)


class VideoShow(Base, GBEntity):
    __tablename__ = 'video_show'
    __item_name__ = 'video_show'
    __collection_name__ = 'video_shows'
    __type_id__ = 2340
    __marshmallow_schema__ = VideoShowSchema

    api_detail_url = Column(String)
    '''URL pointing to the detail resource.'''
    deck = Column(String)
    '''Brief summary of the video_show.'''
    guid = Column(String)
    '''Cross-entity unique ID'''
    title = Column(String)
    '''Title of the video_show.'''
    position = Column(String)
    '''Editor ordering.'''
    id = Column(Integer, primary_key=True, autoincrement=False)
    '''Unique ID of the show.'''
    # Not from API
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship('Image', foreign_keys=[image_id])
    '''Main image of the video_show.'''
    # Not from API
    logo_id = Column(Integer, ForeignKey('image.id'))
    logo = relationship('Image', foreign_keys=[logo_id])
    '''Show logo.'''
    active = Column(String)
    '''Is this show currently active'''
    display_nav = Column(String)
    '''Should this show be displayed in navigation menus'''
    # latest
    '''The latest episode of a video show. Overrides other sorts when used as a sort field.'''
    premium = Column(String)
    '''Premium status of video_show.'''
    api_videos_url = Column(String)
    '''Endpoint to retrieve the videos attached to this video_show.'''
    site_detail_url = Column(String)
    '''URL pointing to the show on Giant Bomb.'''

    # Not from API
    videos = relationship('Video', back_populates='video_show')
    last_full_refresh = Column(String)


class VideoCategory(Base, GBEntity):
    __tablename__ = 'video_category'
    __item_name__ = 'video_category'
    __collection_name__ = 'video_categories'
    __type_id__ = 2320
    __marshmallow_schema__ = VideoCategorySchema

    api_detail_url = Column(String)
    '''URL pointing to the video_category detail resource.'''
    deck = Column(String)
    '''Brief summary of the video_category.'''
    id = Column(Integer, primary_key=True, autoincrement=False)
    '''Unique ID of the video_category.'''
    name = Column(String)
    '''Name of the video_category.'''
    # Not from API
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship('Image', foreign_keys=[image_id])
    '''Main image of the video_category.'''
    site_detail_url = Column(String)
    '''URL pointing to the video_category on Giant Bomb.'''

    # Not from API
    last_full_refresh = Column(String)


gb_entities = [
    Association,
    Image,
    Video,
    VideoShow,
    VideoCategory
]


def get_entity_class_by_table_name(table_name: str):
    """
    Return the class reference mapped to the table with the given name.
    https://stackoverflow.com/a/23754464

    :param table_name: The name of the table.
    :return: Class reference or None.
    """
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == table_name:
            return c


def get_entity_class_by_type_id(type_id: int) -> type:
    return next(e for e in gb_entities if e.__type_id__ == type_id)


def get_entity_class_by_guid(guid: str) -> type:
    type_id = int(guid.split('-')[0])
    return get_entity_class_by_type_id(type_id)


def get_entity_class_by_item_name(item_name: str) -> Type[GBBase]:
    return next(e for e in gb_entities if e.__item_name__ == item_name)


def from_api(session, entity_type: Type[GBBase], result):
    if isinstance(result, list):
        return [entity_type.from_api_result(session, r) for r in result]
    else:
        return entity_type.from_api_result(session, result)


def from_api_generator(session, entity_type: Type[GBBase], result) -> Generator[GBBase, None, None]:
    # This generator is useful when using this converter to insert lists of entities with nested objects into the
    # database.
    #
    # In a list of entities, multiple of those entities may have related objects. When we process each entity,
    # we will search for its related object in the database, and if it does not exist, we create a new one with the
    # properties received from the API.
    #
    # If the result of from_api is used to add the list of objects from the database, and if an object is related to
    # multiple items in that list but did not already exist in the database, then each time we encounter the related
    # object, we would create a new version of that related object, eventually causing a conflict for any UNIQUE
    # constraints in that related object's schema.
    #
    # By using a generator, we can ensure that even if the result of from_api is used to add objects to the database,
    # we will not create multiple versions of the same related object because it will already have been inserted into
    # the database the next time it is encountered.

    if not isinstance(result, list):
        result = [result]
    for r in result:
        yield entity_type.from_api_result(session, r)


# region Publisher

@event.listens_for(Download, 'after_insert')
def receive_download_after_insert(mapper: Mapper, connection: Connection, target: Download):
    publish(MessageEventType.created, Download, target)


@event.listens_for(Download, 'after_update')
def receive_download_after_update(mapper: Mapper, connection: Connection, target: Download):
    publish(MessageEventType.modified, Download, target)


@event.listens_for(Download, 'after_delete')
def receive_download_after_delete(mapper: Mapper, connection: Connection, target: Download):
    publish(MessageEventType.deleted, Download, target)

# endregion


Base.metadata.create_all(engine)
