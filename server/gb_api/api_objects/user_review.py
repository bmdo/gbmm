from .api_object import ApiObject, ApiObjectDefinition, ApiField
from .stub_api_object import StubObject


class UserReviewDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'user_review'
        collection_name = 'user_reviews'
        type_id = 2200
        object_class = UserReview
        fields = [
            # URL pointing to the user_review detail resource.
            ApiField('api_detail_url', str),
            # Date the user_review was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the user_review was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the user_review.
            ApiField('deck', str),
            # Description of the user_review.
            ApiField('description', str),
            # Game being reviewed.
            ApiField('game', StubObject),
            # Release being reviewed.
            ApiField('release', StubObject),
            # DLC being reviewed.
            ApiField('dlc', StubObject),
            # For use in single item api call for user_review.
            ApiField('guid', str),
            # Unique ID of the user_review.
            ApiField('id', int),
            # Name of the review's author.'
            ApiField('reviewer', str),
            # The score given to the game on a scale of 1 to 5.
            ApiField('score', int),
            # URL pointing to the user_review on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class UserReview(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = UserReviewDefinition()
        super().__init__(self.__definition, result)
