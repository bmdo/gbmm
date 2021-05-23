from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class CharacterDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'character'
        collection_name = 'characters'
        type_id = 3005
        object_class = Character
        fields = [
            # List of aliases the character is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the character detail resource.
            ApiField('api_detail_url', str),
            # Birthday of the character.
            ApiField('birthday', str),
            # Concepts related to the character.
            ApiListField('concepts', StubObject),
            # Date the character was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the character was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the character.
            ApiField('deck', str),
            # Description of the character.
            ApiField('description', str),
            # Enemies of the character.
            ApiListField('enemies', StubObject),
            # Game where the character made its first appearance.
            ApiField('first_appeared_in_game', StubObject),
            # Franchises related to the character.
            ApiListField('franchises', StubObject),
            # Friends of the character.
            ApiListField('friends', StubObject),
            # Games the character has appeared in.
            ApiListField('games', StubObject),
            # Gender of the character. Available options are: Male, Female, Other
            ApiField('gender', int),
            # For use in single item api call for character.
            ApiField('guid', str),
            # Unique ID of the character.
            ApiField('id', int),
            # Main image of the character.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Last name of the character.
            ApiField('last_name', str),
            # Locations related to the character.
            ApiListField('locations', StubObject),
            # Name of the character.
            ApiField('name', str),
            # Objects related to the character.
            ApiListField('objects', StubObject),
            # People who have worked with the character.
            ApiListField('people', StubObject),
            # Real name of the character.
            ApiField('real_name', str),
            # URL pointing to the character on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Character(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = CharacterDefinition()
        super().__init__(self.__definition, result)
