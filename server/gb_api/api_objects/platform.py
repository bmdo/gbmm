from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class PlatformDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'platform'
        collection_name = 'platforms'
        type_id = 3045
        object_class = Platform
        fields = [
            # Abbreviation of the platform.
            ApiField('abbreviation', str),
            # URL pointing to the platform detail resource.
            ApiField('api_detail_url', str),
            # Company that created the platform.
            ApiField('company', StubObject),
            # Date the platform was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the platform was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the platform.
            ApiField('deck', str),
            # Description of the platform.
            ApiField('description', str),
            # For use in single item api call for platform.
            ApiField('guid', str),
            # Unique ID of the platform.
            ApiField('id', int),
            # Main image of the platform.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Approximate number of sold hardware units.
            ApiField('install_base', int),
            # Name of the platform.
            ApiField('name', str),
            # Flag indicating whether the platform has online capabilities.
            ApiField('online_support', bool),
            # Initial price point of the platform.
            ApiField('original_price', str),
            # Date of the platform.
            ApiField('release_date', str),
            # URL pointing to the platform on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Platform(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = PlatformDefinition()
        super().__init__(self.__definition, result)
