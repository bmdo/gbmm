from typing import Optional
from . import image, video_show
from .api_object import DownloadableApiObjectDefinition, DownloadableApiObject, ApiField, ApiListField
from .stub_api_object import StubObject


class VideoDefinition(DownloadableApiObjectDefinition):
    def __init__(self):
        item_name = 'video'
        collection_name = 'videos'
        type_id = 2300
        object_class = Video
        fields = [
            # URL pointing to the video detail resource.
            ApiField('api_detail_url', str),
            # Related objects to the video.
            ApiListField('associations', StubObject),
            # Brief summary of the video.
            ApiField('deck', str),
            # URL to the HD version of the video.
            ApiField('hd_url', str),
            # URL to the High Res version of the video.
            ApiField('high_url', str),
            # URL to the Low Res version of the video.
            ApiField('low_url', str),
            # URL for video embed player. To be inserted into an iFrame. You can add ?autoplay=true to auto-play. You
            # can add ?time=x where 'x' is an integer between 0 and the length of the video in seconds to start the
            # video at that point. You can add ?vol=x where 'x' is a decimal between 0 and 1, .75 for example,
            # to set the starting volume. The above three parameters may be used together. Example:
            # ?time=45&vol=.5&autoplay=true See http://www.giantbomb.com/api/video-embed-sample/ for more information
            # on using the embed player.
            ApiField('embed_player', str),
            # For use in single item api call for video.
            ApiField('guid', str),
            # Unique ID of the video.
            ApiField('id', int),
            # Main image of the video.
            ApiField('image', image.Image),
            # Length (in seconds) of the video.
            ApiField('length_seconds', str),
            # Name of the video.
            ApiField('name', str),
            # Date the video was published on Giant Bomb.
            ApiField('publish_date', str),
            # URL pointing to the video on Giant Bomb.
            ApiField('site_detail_url', str),
            # The video's filename.
            ApiField('url', str),
            # Author of the video.
            ApiField('user', str),
            # Video categories
            ApiField('video_categories', StubObject),
            # Video show
            ApiField('video_show', video_show.VideoShow),
            # Youtube ID for the video.
            ApiField('youtube_id', str),
            # The time where the user left off watching this video
            ApiField('saved_time', str),
            # Premium status of video.
            ApiField('premium', str),
            # Hosts of the video.
            ApiField('hosts', str),
            # Crew of the video.
            ApiField('crew', str)
        ]

        def default_download_url_field(obj: DownloadableApiObject) -> Optional[str]:
            # Get the highest quality URL available
            for url in ['hd_url', 'high_url', 'low_url']:
                field = obj.get_field(url)
                if field is not None and field.value is not None and field.value != '':
                    return field.name
            return None

        super().__init__(item_name, collection_name, type_id, object_class, fields, default_download_url_field)


class Video(DownloadableApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = VideoDefinition()
        super().__init__(self.__definition, result)
