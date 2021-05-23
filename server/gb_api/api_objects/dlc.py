from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField
from .stub_api_object import StubObject


class DlcDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'dlc'
        collection_name = 'dlcs'
        type_id = 3020
        object_class = Dlc
        fields = [
            # URL pointing to the dlc detail resource.
            ApiField('api_detail_url', str),
            # Date the dlc was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the dlc was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the dlc.
            ApiField('deck', str),
            # Description of the dlc.
            ApiField('description', str),
            # Game the dlc is for.
            ApiField('game', StubObject),
            # For use in single item api call for dlc.
            ApiField('guid', str),
            # Unique ID of the dlc.
            ApiField('id', int),
            # Main image of the dlc.
            ApiField('image', image.Image),
            # Name of the dlc.
            ApiField('name', str),
            # Platform of the dlc.
            ApiField('platform', StubObject),
            # Date of the dlc.
            ApiField('release_date', str),
            # URL pointing to the dlc on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Dlc(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = DlcDefinition()
        super().__init__(self.__definition, result)
