from . import image, video
from .api_object import ApiObject, ApiObjectDefinition, ApiField


class VideoShowDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'video_show'
        collection_name = 'video_shows'
        type_id = 2340
        object_class = VideoShow
        fields = [
            # URL pointing to the video_show detail resource.
            ApiField('api_detail_url', str),
            # Brief summary of the video_show.
            ApiField('deck', str),
            # For use in single item api call for video_show.
            ApiField('guid', str),
            # Unique ID of the video_show.
            ApiField('id', int),
            # Title of the video_show.
            ApiField('title', str),
            # Editor ordering.
            ApiField('position', str),
            # Main image of the video_show.
            ApiField('image', image.Image),
            # Show logo.
            ApiField('logo', image.Image),
            # URL pointing to the video_show on Giant Bomb.
            ApiField('site_detail_url', str),
            # Is this show currently active
            ApiField('active', str),
            # Should this show be displayed in navigation menus
            ApiField('display_nav', str),
            # The latest episode of a video show. Overrides other sorts when used as a sort field.
            ApiField('latest', video.Video),
            # Premium status of video_show.
            ApiField('premium', str),
            # Endpoint to retrieve the videos attached to this video_show.
            ApiField('api_videos_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class VideoShow(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = VideoShowDefinition()
        super().__init__(self.__definition, result)
