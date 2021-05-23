from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class PersonDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'person'
        collection_name = 'people'
        type_id = 3040
        object_class = Person
        fields = [
            # List of aliases the person is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the person detail resource.
            ApiField('api_detail_url', str),
            # Date the person was born.
            ApiField('birth_date', str),
            # Characters related to the person.
            ApiListField('characters', StubObject),
            # Concepts related to the person.
            ApiListField('concepts', StubObject),
            # Country the person resides in.
            ApiField('country', str),
            # Date the person was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the person was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Date the person died.
            ApiField('death_date', str),
            # Brief summary of the person.
            ApiField('deck', str),
            # Description of the person.
            ApiField('description', str),
            # Game the person was first credited.
            ApiField('first_credited_game', StubObject),
            # Franchises related to the person.
            ApiListField('franchises', StubObject),
            # Games the person has appeared in.
            ApiListField('games', StubObject),
            # Gender of the person. Available options are: Male, Female, Other
            ApiField('gender', int),
            # For use in single item api call for person.
            ApiField('guid', str),
            # City or town the person resides in.
            ApiField('hometown', str),
            # Unique ID of the person.
            ApiField('id', int),
            # Main image of the person.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Locations related to the person.
            ApiListField('locations', StubObject),
            # Name of the person.
            ApiField('name', str),
            # Objects related to the person.
            ApiListField('objects', StubObject),
            # People who have worked with the person.
            ApiField('people', StubObject),
            # URL pointing to the person on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Person(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = PersonDefinition()
        super().__init__(self.__definition, result)
