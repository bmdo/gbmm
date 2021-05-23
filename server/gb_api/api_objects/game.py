from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class GameDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'game'
        collection_name = 'games'
        type_id = 3030
        object_class = Game
        fields = [
            # List of aliases the game is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the game detail resource.
            ApiField('api_detail_url', str),
            # Characters related to the game.
            ApiListField('characters', StubObject),
            # Concepts related to the game.
            ApiListField('concepts', StubObject),
            # Date the game was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the game was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the game.
            ApiField('deck', str),
            # Description of the game.
            ApiField('description', str),
            # Companies who developed the game.
            ApiListField('developers', StubObject),
            # Expected day of release. The month is represented numerically. Combine with 'expected_release_day',
            # 'expected_release_month', 'expected_release_year' and 'expected_release_quarter' for Giant Bomb's best
            # guess release date of the game. These fields will be empty if the 'original_release_date' field is set.
            ApiField('expected_release_day', str),
            # Expected month of release. The month is represented numerically. Combine with 'expected_release_day',
            # 'expected_release_quarter' and 'expected_release_year' for Giant Bomb's best guess release date of the
            # game. These fields will be empty if the 'original_release_date' field is set.
            ApiField('expected_release_month', str),
            # Expected quarter of release. The quarter is represented numerically, where 1 = Q1, 2 = Q2, 3 = Q3, and
            # 4 = Q4. Combine with 'expected_release_day', 'expected_release_month' and 'expected_release_year' for
            # Giant Bomb's best guess release date of the game. These fields will be empty if the
            # 'original_release_date' field is set.
            ApiField('expected_release_quarter', str),
            # Expected year of release. Combine with 'expected_release_day', 'expected_release_month' and
            # 'expected_release_quarter' for Giant Bomb's best guess release date of the game. These fields will be
            # empty if the 'original_release_date' field is set.
            ApiField('expected_release_year', str),
            # Characters that first appeared in the game.
            ApiListField('first_appearance_characters', StubObject),
            # Concepts that first appeared in the game.
            ApiListField('first_appearance_concepts', StubObject),
            # Locations that first appeared in the game.
            ApiListField('first_appearance_locations', StubObject),
            # Objects that first appeared in the game.
            ApiListField('first_appearance_objects', StubObject),
            # People that were first credited in the game.
            ApiListField('first_appearance_people', StubObject),
            # Franchises related to the game.
            ApiListField('franchises', StubObject),
            # Genres that encompass the game.
            ApiListField('genres', StubObject),
            # For use in single item api call for game.
            ApiField('guid', str),
            # Unique ID of the game.
            ApiField('id', int),
            # Main image of the game.
            ApiField('image', image.Image),
            # List of images associated to the game.
            ApiListField('images', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Characters killed in the game.
            ApiListField('killed_characters', StubObject),
            # Locations related to the game.
            ApiListField('locations', StubObject),
            # Name of the game.
            ApiField('name', str),
            # Number of user reviews of the game on Giant Bomb.
            ApiField('number_of_user_reviews', int),
            # Objects related to the game.
            ApiListField('objects', StubObject),
            # Rating of the first release of the game.
            ApiField('original_game_rating', StubObject),
            # Date the game was first released.
            ApiField('original_release_date', str),
            # People who have worked with the game.
            ApiListField('people', StubObject),
            # Platforms the game appeared in.
            ApiListField('platforms', StubObject),
            # Companies who published the game.
            ApiListField('publishers', StubObject),
            # Releases of the game.
            ApiListField('releases', StubObject),
            # Game DLCs
            ApiListField('dlcs', StubObject),
            # Staff reviews of the game.
            ApiListField('reviews', StubObject),
            # Other games similar to the game.
            ApiListField('similar_games', StubObject),
            # URL pointing to the game on Giant Bomb.
            ApiField('site_detail_url', str),
            # Themes that encompass the game.
            ApiListField('themes', StubObject),
            # Videos associated to the game.
            ApiListField('videos', StubObject)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Game(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = GameDefinition()
        super().__init__(self.__definition, result)
