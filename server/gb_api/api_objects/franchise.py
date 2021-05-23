from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class FranchiseDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'franchise'
        collection_name = 'franchises'
        type_id = 3025
        object_class = Franchise
        fields = [
            # List of aliases the franchise is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the franchise detail resource.
            ApiField('api_detail_url', str),
            # Characters related to the franchise.
            ApiListField('characters', StubObject),
            # Concepts related to the franchise.
            ApiListField('concepts', StubObject),
            # Date the franchise was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the franchise was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the franchise.
            ApiField('deck', str),
            # Description of the franchise.
            ApiField('description', str),
            # Games the franchise has appeared in.
            ApiListField('games', StubObject),
            # For use in single item api call for franchise.
            ApiField('guid', str),
            # Unique ID of the franchise.
            ApiField('id', int),
            # Main image of the franchise.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Locations related to the franchise.
            ApiListField('locations', StubObject),
            # Name of the franchise.
            ApiField('name', str),
            # Objects related to the franchise.
            ApiListField('objects', StubObject),
            # People who have worked with the franchise.
            ApiListField('people', StubObject),
            # URL pointing to the franchise on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Franchise(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = FranchiseDefinition()
        super().__init__(self.__definition, result)
