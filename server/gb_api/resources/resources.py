from typing import Type, Optional, Literal
from .resource_filter import ResourceFilter, ResourceFilterList
from .resource import SingleResultResource, MultipleResultResource, Resource
from server import database
from ..response_metadata import ResponseMetadata

ExtraFilters = list[Literal['platforms', 'games', 'subscriber_only']]


def new_collection_filters(extras: ExtraFilters):
    filter_list = ResourceFilterList([
        ResourceFilter('format', str),
        ResourceFilter('field_list', str),
        ResourceFilter('limit', int),
        ResourceFilter('offset', int),
        ResourceFilter('sort', str),
        ResourceFilter('filter', str)
    ])
    if 'platforms' in extras:
        filter_list.append(
            ResourceFilter('platforms', int)
        )
    if 'game' in extras:
        filter_list.append(
            ResourceFilter('game', int)
        )
    if 'subscriber_only' in extras:
        filter_list.append(
            ResourceFilter('subscriber_only', int)
        )
    return filter_list


def new_item_filters():
    return ResourceFilterList([
        ResourceFilter('format', str),
        ResourceFilter('field_list', str),
    ])


class ResourceFactory:
    def __init__(self, result_entity_type: Type[database.GBEntity]):
        self.result_entity_type = result_entity_type

    def new(self, metadata: ResponseMetadata = None) -> Resource:
        pass


class SingleResultResourceFactory(ResourceFactory):
    def new(self, metadata: ResponseMetadata = None) -> SingleResultResource:
        return SingleResultResource(self.result_entity_type.__item_name__, new_item_filters(), self.result_entity_type)


class MultipleResultResourceFactory(ResourceFactory):
    def __init__(self,
                 result_entity_type: Type[database.GBEntity],
                 extra_filters: ExtraFilters = None):
        super().__init__(result_entity_type)
        if extra_filters is None:
            extra_filters = []
        self.extra_filters = extra_filters

    def new(self, metadata: ResponseMetadata = None) -> MultipleResultResource:
        filters = new_collection_filters(self.extra_filters)
        return MultipleResultResource(
            self.result_entity_type.__collection_name__,
            filters,
            self.result_entity_type, metadata)


class ResourceFactoryCollection(list[ResourceFactory]):
    def __init__(self, resource_factories: list[ResourceFactory]):
        super().__init__(resource_factories)

    @staticmethod
    def __get_type_id_from_guid(guid: str) -> int:
        return int(guid.split('-')[0])

    @staticmethod
    def __get_entity_type_by_guid(guid: str) -> type:
        try:
            stub_type_id = ResourceFactoryCollection.__get_type_id_from_guid(guid)
            return database.get_entity_class_by_type_id(stub_type_id)
        except StopIteration or ValueError:
            raise ValueError(
                'GUID not recognized as belonging to any type of object.')

    def new_resource_by_entity_type(self, entity_type, metadata: ResponseMetadata) -> Optional[Resource]:
        factory = next((r for r in self if r.result_entity_type is entity_type), None)
        if factory is not None:
            return factory.new(metadata)
        else:
            return None

    def new_resource_by_guid(self, guid: str, metadata: ResponseMetadata = None) -> Optional[Resource]:
        entity_type = self.__get_entity_type_by_guid(guid)
        return self.new_resource_by_entity_type(entity_type, metadata)

    def new_resource_for_association(self, association: database.Association, metadata: ResponseMetadata = None) -> Optional[Resource]:
        resource = self.new_resource_by_guid(association.guid, metadata)
        if resource is None:
            return None
        api_detail_url = association.get_field_value('api-detail-url')
        guid = association.get_field_value('guid')
        item_id = association.get_field_value('id')
        if api_detail_url is not None:
            resource.override_url(api_detail_url)
        elif guid is not None:
            resource.guid = guid
        elif item_id is not None:
            resource.id = item_id
        else:
            raise ValueError(
                'Association has no api_detail_url, GUID, or ID.')
        return resource

    def new_resource_by_name(self, item_or_collection_name: str, metadata: ResponseMetadata = None) -> Optional[Resource]:
        """
        :param item_or_collection_name: The name for an individual item or a collection returned by a resource.
        :param metadata: Default metadata for the resource.
        :return: The resource matching the provided name, or None if no resource matches the name.
        """
        factory = next(
            (
                r for r in self
                if r.result_entity_type.__item_name__ == item_or_collection_name
                or r.result_entity_type.__collection_name__ == item_or_collection_name
            ),
            None
        )
        if factory is not None:
            return factory.new(metadata)
        else:
            return None


class ItemResourceFactoryCollection(ResourceFactoryCollection):
    def __init__(self):
        # self.accessory = SingleResultResource(requester, 'accessory', item_filters(), api_objs.accessory) TODO
        # self.character = SingleResultResource(requester, 'character', item_filters(), api_objs.character) TODO
        # self.chat = SingleResultResource(requester, 'chat', item_filters(), api_objs.chat) TODO
        # self.company = SingleResultResource(requester, 'company', item_filters(), api_objs.company) TODO
        # self.concept = SingleResultResource(requester, 'concept', item_filters(), api_objs.concept) TODO
        # self.dlc = SingleResultResource(requester, 'dlc', item_filters(), api_objs.dlc) TODO
        # self.franchise = SingleResultResource(requester, 'franchise', item_filters(), api_objs.franchise) TODO
        # self.game = SingleResultResource(requester, 'game', item_filters(), api_objs.game) TODO
        # self.game_rating = SingleResultResource(requester, 'game_rating', item_filters(), api_objs.game_rating) TODO
        # self.genre = SingleResultResource(requester, 'genre', item_filters(), api_objs.genre) TODO
        # self.location = SingleResultResource(requester, 'location', item_filters(), api_objs.location) TODO
        # self.object = SingleResultResource(requester, 'object', item_filters(), api_objs.object) TODO
        # self.person = SingleResultResource(requester, 'person', item_filters(), api_objs.person) TODO
        # self.platform = SingleResultResource(requester, 'platform', item_filters(), api_objs.platform) TODO
        # self.promo = SingleResultResource(requester, 'promo', item_filters(), api_objs.promo) TODO
        # self.rating_board = SingleResultResource(requester, 'rating_board', item_filters(), api_objs.rating_board) TODO
        # self.region = SingleResultResource(requester, 'region', item_filters(), api_objs.region) TODO
        # self.release = SingleResultResource(requester, 'release', item_filters(), api_objs.release) TODO
        # self.review = SingleResultResource(requester, 'review', item_filters(), api_objs.review) TODO
        # self.theme = SingleResultResource(requester, 'theme', item_filters(), api_objs.theme) TODO
        # self.user_review = SingleResultResource(requester, 'user_review', item_filters(), api_objs.user_review) TODO
        self.video = SingleResultResourceFactory(database.Video)
        self.video_category = SingleResultResourceFactory(database.VideoCategory)
        self.video_show = SingleResultResourceFactory(database.VideoShow)

        super().__init__(
            [
                # self.accessory,
                # self.character,
                # self.chat,
                # self.company,
                # self.concept,
                # self.dlc,
                # self.franchise,
                # self.game,
                # self.game_rating,
                # self.genre,
                # self.location,
                # self.object,
                # self.person,
                # self.platform,
                # self.promo,
                # self.rating_board,
                # self.region,
                # self.release,
                # self.review,
                # self.theme,
                # self.user_review,
                self.video,
                self.video_category,
                self.video_show
            ]
        )


class CollectionResourceFactoryCollection(ResourceFactoryCollection):
    def __init__(self):
        # TODO
        # self.accessories = MultipleResultResource(
        #     requester,
        #     'accessories',
        #     collection_filters(),
        #     api_objs.accessory
        # )
        # self.characters = MultipleResultResource(
        #     requester,
        #     'characters',
        #     collection_filters(),
        #     api_objs.character
        # )
        # self.chats = MultipleResultResource(
        #     requester,
        #     'chats',
        #     item_filters(),
        #     api_objs.chat
        # )
        # self.companies = MultipleResultResource(
        #     requester,
        #     'companies',
        #     collection_filters(),
        #     api_objs.company
        # )
        # self.concepts = MultipleResultResource(
        #     requester,
        #     'concepts',
        #     collection_filters(),
        #     api_objs.concept
        # )
        # self.dlcs = MultipleResultResource(
        #     requester,
        #     'dlcs',
        #     collection_filters(platforms=True),
        #     api_objs.dlc
        # )
        # self.franchises = MultipleResultResource(
        #     requester,
        #     'franchises',
        #     collection_filters(),
        #     api_objs.franchise
        # )
        # self.games = MultipleResultResource(
        #     requester,
        #     'games',
        #     collection_filters(platforms=True),
        #     api_objs.game
        # )
        # self.game_ratings = MultipleResultResource(
        #     requester,
        #     'game_ratings',
        #     collection_filters(),
        #     api_objs.game_rating
        # )
        # self.genres = MultipleResultResource(
        #     requester,
        #     'genres',
        #     collection_filters(),
        #     api_objs.genre
        # )
        # self.images = MultipleResultResource(
        #     requester,
        #     'images',
        #     collection_filters(),
        #     api_objs.image
        # )
        # self.locations = MultipleResultResource(
        #     requester,
        #     'locations',
        #     collection_filters(),
        #     api_objs.location
        # )
        # self.objects = MultipleResultResource(
        #     requester,
        #     'objects',
        #     collection_filters(),
        #     api_objs.object
        # )
        # self.people = MultipleResultResource(
        #     requester,
        #     'people',
        #     collection_filters(),
        #     api_objs.person
        # )
        # self.platforms = MultipleResultResource(
        #     requester,
        #     'platforms',
        #     collection_filters(),
        #     api_objs.platform
        # )
        # self.promos = MultipleResultResource(
        #     requester,
        #     'promos',
        #     collection_filters(),
        #     api_objs.promo
        # )
        # self.rating_boards = MultipleResultResource(
        #     requester,
        #     'rating_boards',
        #     collection_filters(),
        #     api_objs.rating_board
        # )
        # self.regions = MultipleResultResource(
        #     requester,
        #     'regions',
        #     collection_filters(),
        #     api_objs.region
        # )
        # self.releases = MultipleResultResource(
        #     requester,
        #     'releases',
        #     collection_filters(platforms=True),
        #     api_objs.release
        # )
        # self.reviews = MultipleResultResource(
        #     requester,
        #     'reviews',
        #     collection_filters(game=True),
        #     api_objs.review
        # )
        # self.themes = MultipleResultResource(
        #     requester,
        #     'themes',
        #     collection_filters(),
        #     api_objs.theme
        # )
        # self.user_reviews = MultipleResultResource(
        #     requester,
        #     'user_reviews',
        #     collection_filters(game=True),
        #     api_objs.user_review
        # )
        self.videos = MultipleResultResourceFactory(database.Video, extra_filters=['subscriber_only'])
        self.video_categories = MultipleResultResourceFactory(database.VideoCategory)
        self.video_shows = MultipleResultResourceFactory(database.VideoShow)

        super().__init__(
            [
                # self.accessories, TODO
                # self.characters, TODO
                # self.chats, TODO
                # self.companies, TODO
                # self.concepts, TODO
                # self.dlcs, TODO
                # self.franchises, TODO
                # self.games, TODO
                # self.game_ratings, TODO
                # self.genres, TODO
                # self.images, TODO
                # self.locations, TODO
                # self.objects, TODO
                # self.people, TODO
                # self.platforms, TODO
                # self.promos, TODO
                # self.rating_boards, TODO
                # self.regions, TODO
                # self.releases, TODO
                # self.reviews, TODO
                # self.themes, TODO
                # self.user_reviews, TODO
                self.videos,
                self.video_categories,
                self.video_shows
            ]
        )


class ResourceFactories:
    def __init__(self):
        self.item = ItemResourceFactoryCollection()
        self.collection = CollectionResourceFactoryCollection()
