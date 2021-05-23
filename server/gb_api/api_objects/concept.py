from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class ConceptDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'concept'
        collection_name = 'concepts'
        type_id = 3015
        object_class = Concept
        fields = [
            # List of aliases the concept is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the concept detail resource.
            ApiField('api_detail_url', str),
            # Characters related to the concept.
            ApiListField('characters', StubObject),
            # Concepts related to the concept.
            ApiListField('concepts', StubObject),
            # Date the concept was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the concept was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the concept.
            ApiField('deck', str),
            # Description of the concept.
            ApiField('description', str),
            # Franchise where the concept made its first appearance.
            ApiField('first_appeared_in_franchise', StubObject),
            # Game where the concept made its first appearance.
            ApiField('first_appeared_in_game', StubObject),
            # Franchises related to the concept.
            ApiListField('franchises', StubObject),
            # Games the concept has appeared in.
            ApiListField('games', StubObject),
            # For use in single item api call for concept.
            ApiField('guid', str),
            # Unique ID of the concept.
            ApiField('id', int),
            # Main image of the concept.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Locations related to the concept.
            ApiListField('locations', StubObject),
            # Name of the concept.
            ApiField('name', str),
            # Objects related to the concept.
            ApiListField('objects', StubObject),
            # People who have worked with the concept.
            ApiListField('people', StubObject),
            # Other concepts related to the concept.
            ApiListField('related_concepts', StubObject),
            # URL pointing to the concept on Giant Bomb.
            ApiField('site_detail_url', str),
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Concept(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = ConceptDefinition()
        super().__init__(self.__definition, result)
