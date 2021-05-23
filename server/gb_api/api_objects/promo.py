from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField


class PromoDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'promo'
        collection_name = 'promos'
        type_id = 1700
        object_class = Promo
        fields = [
            # URL pointing to the promo detail resource.
            ApiField('api_detail_url', str),
            # Date the promo was added to Giant Bomb.
            ApiField('date_added', str),
            # Brief summary of the promo.
            ApiField('deck', str),
            # For use in single item api call for promo.
            ApiField('guid', str),
            # Unique ID of the promo.
            ApiField('id', int),
            # Main image of the promo.
            ApiField('image', image.Image),
            # The link that promo points to.
            ApiField('link', str),
            # Name of the promo.
            ApiField('name', str),
            # The type of resource the promo is pointing towards.
            ApiField('resource_type', str),
            # Author of the promo.
            ApiField('user', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Promo(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = PromoDefinition()
        super().__init__(self.__definition, result)
