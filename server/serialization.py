from typing import Type

from marshmallow import Schema, fields


class Marshmallowable:
    __marshmallow_schema__: Type[Schema]

    def dump(self):
        return self.__marshmallow_schema__().dump(self)


class KeyValueSchema(Schema):
    id = fields.Int()
    key = fields.Str()
    value = fields.Str()


class DownloadSchema(Schema):
    __tablename__ = 'download'
    id = fields.Int()
    name = fields.Str()
    obj_item_name = fields.Str()
    obj_id = fields.Int()
    obj_url_field = fields.Str()
    file_id = fields.Int()
    file = fields.Nested('FileSchema', exclude=('downloads',))
    status = fields.Int()
    failed_reason = fields.Str()
    created_time = fields.DateTime()
    start_time = fields.DateTime()
    finish_time = fields.DateTime()
    url = fields.Str()
    size_bytes = fields.Int(attribute='_size_bytes')
    '''Size of the downloadable data in bytes. Set when response_headers is set.'''
    downloaded_bytes = fields.Int()
    content_type = fields.Str(attribute='_content_type')
    '''Content MIME type. Set when response_headers is set.'''
    response_headers = fields.Str(attribute='_response_headers')
    '''Full set of headers returned with the download request as serialized JSON.'''


class FileSchema(Schema):
    __tablename__ = 'file'
    id = fields.Int()
    obj_item_name = fields.Str()
    obj_id = fields.Int()
    obj_url_field = fields.Str()
    downloads = fields.List(fields.Nested(DownloadSchema, exclude=('file',)))
    path = fields.Str()
    size_bytes = fields.Int()
    content_type = fields.Str()


class ImageSchema(Schema):
    __tablename__ = 'image'
    __item_name__ = 'image'
    __collection_name__ = 'images'
    __type_id__ = 920000

    # Not from API
    id = fields.Int()

    icon_url = fields.Str()
    '''URL to the icon version of the image.'''
    medium_url = fields.Str()
    '''URL to the medium size of the image.'''
    original_url = fields.Str()
    '''URL to the original image.'''
    screen_url = fields.Str()
    '''URL to the screenshot version of the image.'''
    screen_large_url = fields.Str()
    '''URL to the large screenshot version of the image.'''
    small_url = fields.Str()
    '''URL to the small version of the image.'''
    super_url = fields.Str()
    '''URL to the super sized version of the image.'''
    thumb_url = fields.Str()
    '''URL to the thumb-sized version of the image.'''
    tiny_url = fields.Str()
    '''URL to the tiny version of the image.'''
    image_tags = fields.Str()
    '''Name of image tag for filtering images.'''


class VideoSchema(Schema):
    __tablename__ = 'video'
    __item_name__ = 'video'
    __collection_name__ = 'videos'
    __type_id__ = 2300

    api_detail_url = fields.Str()
    '''URL pointing to the video resource.'''
    # associations = ApiListField('', StubObject), TODO
    '''Related objects to the video.'''
    deck = fields.Str()
    '''Brief summary of the video.'''
    guid = fields.Str()
    '''Cross-entity unique ID'''
    hd_url = fields.Str()
    '''URL to the HD version of the video.'''
    high_url = fields.Str()
    '''URL to the High Res version of the video.'''
    low_url = fields.Str()
    '''URL to the Low Res version of the video.'''
    embed_player = fields.Str()
    '''
    URL for video embed player. To be inserted into an iFrame. You can add ?autoplay=true to auto-play. You
    can add ?time=x where 'x' is an integer between 0 and the length of the video in seconds to start the
    video at that point. You can add ?vol=x where 'x' is a decimal between 0 and 1, .75 for example,
    to set the starting volume. The above three parameters may be used together. Example:
    ?time=45&vol=.5&autoplay=true See https://www.giantbomb.com/api/video-embed-sample/ for more information
    on using the embed player.
    '''
    id = fields.Int()
    '''Unique ID of the video.'''
    # Not from API
    image_id = fields.Int()
    image = fields.Nested(ImageSchema)
    '''Main image of the video.'''
    length_seconds = fields.Str()
    '''Length (in seconds) of the video.'''
    name = fields.Str()
    '''Name of the video.'''
    publish_date = fields.Str()
    '''Date the video was published on Giant Bomb.'''
    site_detail_url = fields.Str()
    '''URL pointing to the video on Giant Bomb.'''
    url = fields.Str()
    '''The video's filename.'''
    user = fields.Str()
    '''Author of the video.'''
    # video_categories = ApiField('', StubObject), TODO
    '''Video categories'''
    video_show_id = fields.Int()
    video_show = fields.Nested('VideoShowSchema', exclude=('videos',))
    '''Video show'''
    youtube_id = fields.Str()
    '''Youtube ID for the video.'''
    saved_time = fields.Str()
    '''The time where the user left off watching this video'''
    premium = fields.Str()
    '''Premium status of video.'''
    hosts = fields.Str()
    '''Hosts of the video.'''
    crew = fields.Str()
    '''Crew of the video.'''


class VideoShowSchema(Schema):
    __tablename__ = 'video_show'
    __item_name__ = 'video_show'
    __collection_name__ = 'video_shows'
    __type_id__ = 2340

    api_detail_url = fields.Str()
    '''URL pointing to the detail resource.'''
    deck = fields.Str()
    '''Brief summary of the video_show.'''
    guid = fields.Str()
    '''Cross-entity unique ID'''
    title = fields.Str()
    '''Title of the video_show.'''
    position = fields.Str()
    '''Editor ordering.'''
    id = fields.Int()
    '''Unique ID of the show.'''
    # Not from API
    image_id = fields.Int()
    image = fields.Nested(ImageSchema)
    '''Main image of the video_show.'''
    # Not from API
    logo_id = fields.Int()
    logo = fields.Nested(ImageSchema)
    '''Show logo.'''
    active = fields.Str()
    '''Is this show currently active'''
    display_nav = fields.Str()
    '''Should this show be displayed in navigation menus'''
    # latest
    '''The latest episode of a video show. Overrides other sorts when used as a sort field.'''
    premium = fields.Str()
    '''Premium status of video_show.'''
    api_videos_url = fields.Str()
    '''Endpoint to retrieve the videos attached to this video_show.'''
    site_detail_url = fields.Str()
    '''URL pointing to the show on Giant Bomb.'''
    # Not from API
    videos = fields.List(fields.Nested(VideoSchema, exclude=('video_show',)))


class VideoCategorySchema(Schema):
    __tablename__ = 'video_category'
    __item_name__ = 'video_category'
    __collection_name__ = 'video_categories'
    __type_id__ = 2320

    api_detail_url = fields.Str()
    '''URL pointing to the video_category detail resource.'''
    deck = fields.Str()
    '''Brief summary of the video_category.'''
    id = fields.Int()
    '''Unique ID of the video_category.'''
    name = fields.Str()
    '''Name of the video_category.'''
    # Not from API
    image_id = fields.Int()
    image = fields.Nested(ImageSchema)
    '''Main image of the video_category.'''
    site_detail_url = fields.Str()
    '''URL pointing to the video_category on Giant Bomb.'''


class MessageSchema(Schema):
    event_type = fields.Int(attribute='event_type_id')
    subject_type = fields.Str()
    subject_id = fields.Int()
    data = fields.Raw()
