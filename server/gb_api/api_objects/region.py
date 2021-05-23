from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class RegionDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'region'
        collection_name = 'regions'
        type_id = 3075
        object_class = Region
        fields = [
            # URL pointing to the region detail resource.
            ApiField('api_detail_url', str),
            # Date the region was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the region was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the region.
            ApiField('deck', str),
            # Description of the region.
            ApiField('description', str),
            # For use in single item api call for region.
            ApiField('guid', str),
            # Unique ID of the region.
            ApiField('id', int),
            # Main image of the region.
            ApiField('image', image.Image),
            # Name of the region.
            ApiField('name', str),
            # Rating boards in the region.
            ApiListField('rating_boards', StubObject),
            # URL pointing to the region on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Region(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = RegionDefinition()
        super().__init__(self.__definition, result)
