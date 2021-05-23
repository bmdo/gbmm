from . import image
from .api_object import ApiObjectDefinition, ApiObject, ApiField, ApiListField
from .stub_api_object import StubObject


class AccessoryDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'accessory'
        collection_name = 'accessories'
        type_id = 3000
        object_class = Accessory
        fields = [
            # URL pointing to the accessory detail resource.
            ApiField('api_detail_url', str),
            # Date the accessory was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the accessory was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the accessory.
            ApiField('deck', str),
            # Description of the accessory.
            ApiField('description', str),
            # For use in single item api call for accessory.
            ApiField('guid', str),
            # Unique ID of the accessory.
            ApiField('id', int),
            # Main image of the accessory.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Name of the accessory.
            ApiField('name', str),
            # URL pointing to the accessory on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Accessory(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = AccessoryDefinition()
        super().__init__(self.__definition, result)
