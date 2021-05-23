from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField
from .stub_api_object import StubObject


class GameRatingDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'game_rating'
        collection_name = 'game_ratings'
        type_id = 3065
        object_class = GameRating
        fields = [
            # URL pointing to the game_rating detail resource.
            ApiField('api_detail_url', str),
            # For use in single item api call for game_rating.
            ApiField('guid', str),
            # Unique ID of the game_rating.
            ApiField('id', int),
            # Main image of the game_rating.
            ApiField('image', image.Image),
            # Name of the game_rating.
            ApiField('name', str),
            # Rating board that issues this game_rating.
            ApiField('rating_board', StubObject)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class GameRating(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = GameRatingDefinition()
        super().__init__(self.__definition, result)
