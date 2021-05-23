from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField, ApiListField
from .stub_api_object import StubObject


class CompanyDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'company'
        collection_name = 'companies'
        type_id = 3010
        object_class = Company
        fields = [
            # Abbreviation of the company.
            ApiField('abbreviation', str),
            # List of aliases the company is known by. A \n (newline) separates each alias.
            ApiField('aliases', str),
            # URL pointing to the company detail resource.
            ApiField('api_detail_url', str),
            # Characters related to the company.
            ApiListField('characters', StubObject),
            # Concepts related to the company.
            ApiField('concepts', StubObject),
            # Date the company was added to Giant Bomb.
            ApiField('date_added', str),
            # Date the company was founded.
            ApiField('date_founded', str),
            # Date the company was last updated on Giant Bomb.
            ApiField('date_last_updated', str),
            # Brief summary of the company.
            ApiField('deck', str),
            # Description of the company.
            ApiField('description', str),
            # Games the company has developed.
            ApiListField('developed_games', StubObject),
            # Releases the company has developed.
            ApiListField('developer_releases', StubObject),
            # Releases the company has distributed.
            ApiListField('distributor_releases', StubObject),
            # For use in single item api call for company.
            ApiField('guid', str),
            # Unique ID of the company.
            ApiField('id', int),
            # Main image of the company.
            ApiField('image', image.Image),
            # List of image tags to filter the images endpoint.
            ApiListField('image_tags', StubObject),
            # Street address of the company.
            ApiField('location_address', str),
            # City the company resides in.
            ApiField('location_city', str),
            # Country the company resides in.
            ApiField('location_country', str),
            # State the company resides in.
            ApiField('location_state', str),
            # Locations related to the company.
            ApiListField('locations', StubObject),
            # Name of the company.
            ApiField('name', str),
            # Objects related to the company.
            ApiListField('objects', StubObject),
            # People who have worked with the company.
            ApiListField('people', StubObject),
            # Phone number of the company.
            ApiField('phone', str),
            # Games published by the company.
            ApiListField('published_games', StubObject),
            # Releases the company has published.
            ApiListField('publisher_releases', StubObject),
            # URL pointing to the company on Giant Bomb.
            ApiField('site_detail_url', str),
            # URL to the company website.
            ApiField('website', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Company(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = CompanyDefinition()
        super().__init__(self.__definition, result)
