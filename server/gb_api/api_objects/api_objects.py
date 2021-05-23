from typing import Type, Union
from .api_object import ApiObjectDefinition
from .accessory import Accessory, AccessoryDefinition
from .character import Character, CharacterDefinition
from .chat import Chat, ChatDefinition
from .company import Company, CompanyDefinition
from .concept import Concept, ConceptDefinition
from .dlc import Dlc, DlcDefinition
from .franchise import Franchise, FranchiseDefinition
from .game import Game, GameDefinition
from .game_rating import GameRating, GameRatingDefinition
from .genre import Genre, GenreDefinition
from .image import Image, ImageDefinition
from .location import Location, LocationDefinition
from .object import Object, ObjectDefinition
from .person import Person, PersonDefinition
from .platform import Platform, PlatformDefinition
from .promo import Promo, PromoDefinition
from .rating_board import RatingBoard, RatingBoardDefinition
from .region import Region, RegionDefinition
from .release import Release, ReleaseDefinition
from .review import Review, ReviewDefinition
from .theme import Theme, ThemeDefinition
from .user_review import UserReview, UserReviewDefinition
from .video import Video, VideoDefinition
from .video_category import VideoCategory, VideoCategoryDefinition
from .video_show import VideoShow, VideoShowDefinition


ApiObjectType = Type[Union[
    Accessory,
    Character,
    Chat,
    Company,
    Concept,
    Dlc,
    Franchise,
    Game,
    GameRating,
    Genre,
    Image,
    Location,
    Object,
    Person,
    Platform,
    Promo,
    RatingBoard,
    Region,
    Release,
    Review,
    Theme,
    UserReview,
    Video,
    VideoCategory,
    VideoShow
]]


class ApiObjectDefinitionSet:
    def __init__(self, obj_class: ApiObjectType, definition: ApiObjectDefinition):
        self.obj_class = obj_class
        self.definition = definition


class ApiObjects(list[ApiObjectDefinitionSet]):
    def __init__(self):
        self.accessory = ApiObjectDefinitionSet(Accessory, AccessoryDefinition())
        self.character = ApiObjectDefinitionSet(Character, CharacterDefinition())
        self.chat = ApiObjectDefinitionSet(Chat, ChatDefinition())
        self.company = ApiObjectDefinitionSet(Company, CompanyDefinition())
        self.concept = ApiObjectDefinitionSet(Concept, ConceptDefinition())
        self.dlc = ApiObjectDefinitionSet(Dlc, DlcDefinition())
        self.franchise = ApiObjectDefinitionSet(Franchise, FranchiseDefinition())
        self.game = ApiObjectDefinitionSet(Game, GameDefinition())
        self.game_rating = ApiObjectDefinitionSet(GameRating, GameRatingDefinition())
        self.genre = ApiObjectDefinitionSet(Genre, GenreDefinition())
        self.image = ApiObjectDefinitionSet(Image, ImageDefinition())
        self.location = ApiObjectDefinitionSet(Location, LocationDefinition())
        self.object = ApiObjectDefinitionSet(Object, ObjectDefinition())
        self.person = ApiObjectDefinitionSet(Person, PersonDefinition())
        self.platform = ApiObjectDefinitionSet(Platform, PlatformDefinition())
        self.promo = ApiObjectDefinitionSet(Promo, PromoDefinition())
        self.rating_board = ApiObjectDefinitionSet(RatingBoard, RatingBoardDefinition())
        self.region = ApiObjectDefinitionSet(Region, RegionDefinition())
        self.release = ApiObjectDefinitionSet(Release, ReleaseDefinition())
        self.review = ApiObjectDefinitionSet(Review, ReviewDefinition())
        self.theme = ApiObjectDefinitionSet(Theme, ThemeDefinition())
        self.user_review = ApiObjectDefinitionSet(UserReview, UserReviewDefinition())
        self.video = ApiObjectDefinitionSet(Video, VideoDefinition())
        self.video_category = ApiObjectDefinitionSet(VideoCategory, VideoCategoryDefinition())
        self.video_show = ApiObjectDefinitionSet(VideoShow, VideoShowDefinition())

        super().__init__([
            self.accessory,
            self.character,
            self.chat,
            self.company,
            self.concept,
            self.dlc,
            self.franchise,
            self.game,
            self.game_rating,
            self.genre,
            self.image,
            self.location,
            self.object,
            self.person,
            self.platform,
            self.promo,
            self.rating_board,
            self.region,
            self.release,
            self.review,
            self.theme,
            self.user_review,
            self.video,
            self.video_category,
            self.video_show
        ])


