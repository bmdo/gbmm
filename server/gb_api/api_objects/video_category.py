from . import image
from .api_object import GuidlessApiObject, GuidlessApiObjectDefinition, ApiField


class VideoCategoryDefinition(GuidlessApiObjectDefinition):
    def __init__(self):
        item_name = 'video_category'
        collection_name = 'video_categories'
        type_id = 2320
        object_class = VideoCategory
        fields = [
            # URL pointing to the video_category detail resource.
            ApiField('api_detail_url', str),
            # Brief summary of the video_category.
            ApiField('deck', str),
            # Unique ID of the video_category.
            ApiField('id', int),
            # Name of the video_category.
            ApiField('name', str),
            # Main image of the video_category.
            ApiField('image', image.Image),
            # URL pointing to the video_category on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class VideoCategory(GuidlessApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = VideoCategoryDefinition()
        super().__init__(self.__definition, result)
