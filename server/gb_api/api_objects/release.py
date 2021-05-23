from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class ReleaseDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'release'
        collection_name = 'releases'
        type_id = 3050
        object_class = Release
        fields = [
            # URL pointing to the release detail resource.
            ApiField('api_detail_url', str),
            # Date the release was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the release was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the release.
            ApiField('deck', str),
            # Description of the release.
            ApiField('description', str),
            # Companies who developed the release.
            ApiListField('developers', StubObject),
            # Expected day of release. The day is represented numerically. Combine with 'expected_release_month',
            # 'expected_release_year' and 'expected_release_quarter' for Giant Bomb's best guess release date of the
            # release. These fields will be empty if the 'release_date' field is set.
            ApiField('expected_release_day', str),
            # Expected month of release. The month is represented numerically. Combine with 'expected_release_day',
            # expected_release_quarter' and 'expected_release_year' for Giant Bomb's best guess release date of the
            # release. These fields will be empty if the 'release_date' field is set.
            ApiField('expected_release_month', str),
            # Expected quarter of release. The quarter is represented numerically, where 1 = Q1, 2 = Q2, 3 = Q3,
            # and 4 = Q4. Combine with 'expected_release_day', 'expected_release_month' and 'expected_release_year'
            # for Giant Bomb's best guess release date of the release. These fields will be empty if the
            # 'release_date' field is set.
            ApiField('expected_release_quarter', str),
            # Expected year of release. Combine with 'expected_release_day', 'expected_release_month' and
            # 'expected_release_quarter' for Giant Bomb's best guess release date of the game. These fields will be
            # empty if the 'release_date' field is set.
            ApiField('expected_release_year', str),
            # Game the release is for.
            ApiField('game', StubObject),
            # Rating of the release.
            ApiField('game_rating', StubObject),
            # For use in single item api call for release.
            ApiField('guid', str),
            # Unique ID of the release.
            ApiField('id', int),
            # Main image of the release.
            ApiField('image', image.Image),
            # Maximum players
            ApiField('maximum_players', int),
            # Minimum players
            ApiField('minimum_players', int),
            # Multiplayer features
            ApiListField('multiplayer_features', str),
            # Name of the release.
            ApiField('name', str),
            # Platform of the release.
            ApiField('platform', StubObject),
            # The type of product code the release has (ex. UPC/A, ISBN-10, EAN-13).
            ApiField('product_code_type', str),
            # The release's product code.
            ApiField('product_code_value', str),
            # Companies who published the release.
            ApiListField('publishers', StubObject),
            # Region the release is responsible for.
            ApiField('region', StubObject),
            # Date of the release.
            ApiField('release_date', str),
            # Resolutions available
            ApiListField('resolutions', str),
            # Single player features
            ApiListField('singleplayer_features', str),
            # Sound systems
            ApiListField('sound_systems', str),
            # URL pointing to the release on Giant Bomb.
            ApiField('site_detail_url', str),
            # Widescreen support
            ApiField('widescreen_support', bool)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Release(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = ReleaseDefinition()
        super().__init__(self.__definition, result)
