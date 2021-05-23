from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class ReviewDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'review'
        collection_name = 'reviews'
        type_id = 1900
        object_class = Review
        fields = [
            # URL pointing to the review detail resource.
            ApiField('api_detail_url', str),
            # Brief summary of the review.
            ApiField('deck', str),
            # Description of the review.
            ApiField('description', str),
            # Name of the Downloadable Content package.
            ApiField('dlc_name', str),
            # Game the review is for.
            ApiField('game', StubObject),
            # For use in single item api call for review.
            ApiField('guid', str),
            # Unique ID of the review.
            ApiField('id', int),
            # Platforms the review appeared in.
            ApiListField('platforms', StubObject),
            # Date the review was published on Giant Bomb.
            ApiField('publish_date', str),
            # Release of game for review.
            ApiField('release', StubObject),
            # Name of the review's author.
            ApiField('reviewer', str),
            # The score given to the game on a scale of 1 to 5.
            ApiField('score', int),
            # URL pointing to the review on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Review(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = ReviewDefinition()
        super().__init__(self.__definition, result)
