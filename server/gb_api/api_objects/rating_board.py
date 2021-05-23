from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField
from .stub_api_object import StubObject


class RatingBoardDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'rating_board'
        collection_name = 'rating_boards'
        type_id = 3070
        object_class = RatingBoard
        fields = [
            # URL pointing to the rating_board detail resource.
            ApiField('api_detail_url', str),
            # Date the rating_board was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the rating_board was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the rating_board.
            ApiField('deck', str),
            # Description of the rating_board.
            ApiField('description', str),
            # For use in single item api call for rating_board.
            ApiField('guid', str),
            # Unique ID of the rating_board.
            ApiField('id', int),
            # Main image of the rating_board.
            ApiField('image', image.Image),
            # Name of the rating_board.
            ApiField('name', str),
            # Region the rating_board is responsible for.
            ApiField('region', StubObject),
            # URL pointing to the rating_board on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class RatingBoard(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = RatingBoardDefinition()
        super().__init__(self.__definition, result)
