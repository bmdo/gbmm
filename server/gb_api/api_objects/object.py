from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class ObjectDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'object'
        collection_name = 'objects'
        type_id = 3055
        object_class = Object
        fields = [
            # List of aliases the object is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the object detail resource.
            ApiField('api_detail_url', str),
            # Characters related to the object.
            ApiListField('characters', StubObject),
            # Companies related to the object.
            ApiListField('companies', StubObject),
            # Concepts related to the object.
            ApiListField('concepts', StubObject),
            # Date the object was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the object was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the object.
            ApiField('deck', str),
            # Description of the object.
            ApiField('description', str),
            # Game where the object made its first appearance.
            ApiField('first_appeared_in_game', StubObject),
            # Franchises related to the object.
            ApiListField('franchises', StubObject),
            # Games the object has appeared in.
            ApiListField('games', StubObject),
            # For use in single item api call for object.
            ApiField('guid', str),
            # Unique ID of the object.
            ApiField('id', int),
            # Main image of the object.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Locations related to the object.
            ApiField('locations', StubObject),
            # Name of the object.
            ApiField('name', str),
            # Objects related to the object.
            ApiListField('objects', StubObject),
            # People who have worked with the object.
            ApiListField('people', StubObject),
            # URL pointing to the object on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Object(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = ObjectDefinition()
        super().__init__(self.__definition, result)
