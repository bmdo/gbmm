from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class LocationDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'location'
        collection_name = 'locations'
        type_id = 3035
        object_class = Location
        fields = [
            # List of aliases the location is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the location detail resource.
            ApiField('api_detail_url', str),
            # Date the location was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the location was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the location.
            ApiField('deck', str),
            # Description of the location.
            ApiField('description', str),
            # Game where the location made its first appearance.
            ApiField('first_appeared_in_game', StubObject),
            # For use in single item api call for location.
            ApiField('guid', str),
            # Unique ID of the location.
            ApiField('id', int),
            # Main image of the location.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Name of the location.
            ApiField('name', str),
            # URL pointing to the location on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Location(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = LocationDefinition()
        super().__init__(self.__definition, result)
