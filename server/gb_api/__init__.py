import re
from enum import Enum

from marshmallow import Schema, fields, post_load

from .resources import resources, SingleResultResource, MultipleResultResource
from server.database import GBBase
from .response_metadata import ResponseMetadata, ResponseMetadataSchema


class APIError(Exception):
    def __init__(self, msg: str = None):
        self.msg = msg


class AssociationError(APIError):
    pass


class SortDirection(Enum):
    DESCENDING = DESC = 0,
    ASCENDING = ASC = 1


class ResourceSessionData:
    def __init__(self, resource: MultipleResultResource = None):
        super().__init__()
        if resource is not None:
            self.resource_name = resource.result_entity_type.__item_name__
            self.metadata = resource.working_metadata


class ResourceSessionDataSchema(Schema):
    resource_name = fields.Str()
    metadata = fields.Nested(ResponseMetadataSchema)

    @post_load
    def post_load(self, data, **kwargs):
        resource_session_data = ResourceSessionData()
        resource_session_data.resource_name = data.get('resource_name', None)
        resource_session_data.metadata = data.get('metadata', None)
        return resource_session_data


class ResourceSelect:

    def __init__(self, resource: MultipleResultResource):
        self.__resource = resource
        self.__last_results = None

    def to_session_data(self):
        return ResourceSessionDataSchema().dump(ResourceSessionData(self.__resource))

    def filter(self, **kwargs) -> 'ResourceSelect':
        for k, v in kwargs.items():
            self.__resource.filters.set(k, v)
        return self

    def clear_filter(self, name: str) -> 'ResourceSelect':
        self.__resource.filters.clear_filter(name)
        return self

    def field_list(self, *args) -> 'ResourceSelect':
        field_list = []
        for arg in args:
            if isinstance(arg, str):
                field_list.append(arg)
            elif isinstance(arg, list):
                field_list += arg

        self.filter(field_list=','.join(field_list))
        return self

    def sort(self, field: str, direction: SortDirection) -> 'ResourceSelect':
        if direction == SortDirection.DESC:
            dir_str = 'desc'
        elif direction == SortDirection.ASC:
            dir_str = 'asc'
        else:
            raise ValueError(f'Invalid sort direction {direction}')

        self.filter(sort=f'{field}:{dir_str}')
        return self

    def limit(self, limit: int) -> 'ResourceSelect':
        self.filter(limit=limit)
        return self

    def next(self):
        self.__last_results = self.__resource.next()
        return self.__last_results

    def page(self, page_num: int):
        self.__last_results = self.__resource.page(page_num)
        return self.__last_results

    @property
    def results(self):
        return self.__last_results

    @property
    def total_results(self):
        return self.__resource.total_results

    @property
    def page_results(self):
        return self.__resource.page_results

    @property
    def current_page(self):
        return self.__resource.current_page

    @property
    def total_pages(self):
        return self.__resource.total_pages

    @property
    def is_last_page(self):
        return self.__resource.is_last_page


class GBAPI:
    @staticmethod
    def __get_resource(obj_type_or_guid, collection, metadata: ResponseMetadata = None):
        guid = None
        if isinstance(obj_type_or_guid, str):
            # First argument is a string representation of the object type or a GUID
            if GBAPI.is_guid(obj_type_or_guid):
                guid = obj_type_or_guid
                res = collection.new_resource_by_guid(guid, metadata)
            else:
                # Name of the object
                res = collection.new_resource_by_name(obj_type_or_guid, metadata)

        elif issubclass(obj_type_or_guid, GBBase):
            res = collection.new_resource_by_entity_type(obj_type_or_guid, metadata)
        else:
            raise ValueError(
                f'Could not find resource for provided first argument:'
                f'Type: {type(obj_type_or_guid)}, Value: {obj_type_or_guid}'
            )

        return res, guid

    @staticmethod
    def is_guid(string: str):
        return re.fullmatch(r'[0-9]+-[0-9]+', string) is not None

    @staticmethod
    def get_one(obj_type_or_guid, obj_id: int = None):
        """
        Queries the GB API for a single object and returns the result as a GBEntity object.
        :param obj_type_or_guid:
        Any of the following:
          - The name of the object returned by the resource as a string.
          - The python type of the object returned by the resource.
          - The GUID of the object as a string. When a GUID is provided, obj_id is not required.
        :param obj_id: The ID of the object. Not required when a GUID is provided as the first argument.
        :return: The object returned by the GB API.
        """

        res: SingleResultResource
        guid: str
        res, guid = GBAPI.__get_resource(obj_type_or_guid, resources.item)

        if guid is not None:
            return res.get(guid=guid)
        elif obj_id is not None:
            return res.get(id=obj_id)
        else:
            raise ValueError('ID not provided.')

    @staticmethod
    def select(obj_type_or_guid) -> ResourceSelect:
        res: MultipleResultResource
        guid: str
        res, guid = GBAPI.__get_resource(obj_type_or_guid, resources.collection)
        return ResourceSelect(res)

    @staticmethod
    def from_session_data(session_data: list) -> ResourceSelect:
        loaded_data = ResourceSessionDataSchema().load(session_data)
        res, guid = GBAPI.__get_resource(loaded_data.resource_name, resources.collection, loaded_data.metadata)
        return ResourceSelect(res)


is_guid = GBAPI.is_guid
get_one = GBAPI.get_one
select = GBAPI.select
