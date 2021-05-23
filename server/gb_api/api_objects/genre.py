from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField


class GenreDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'genre'
        collection_name = 'genres'
        type_id = 3060
        object_class = Genre
        fields = [
            # URL pointing to the genre detail resource.
            ApiField('api_detail_url', str),
            # Date the genre was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the genre was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the genre.
            ApiField('deck', str),
            # Description of the genre.
            ApiField('description', str),
            # For use in single item api call for genre.
            ApiField('guid', str),
            # Unique ID of the genre.
            ApiField('id', int),
            # Main image of the genre.
            ApiField('image', image.Image),
            # Name of the genre.
            ApiField('name', str),
            # URL pointing to the genre on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Genre(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = GenreDefinition()
        super().__init__(self.__definition, result)
