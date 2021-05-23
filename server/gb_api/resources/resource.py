from typing import Optional, Type

from config import config
from server.database import GBEntity
from server.requester import requester
from server.gb_api.response_metadata import ResponseMetadata

from .resource_filter import ResourceFilterList


class ResourceException(Exception):
    pass


class InvalidRequestException(ResourceException):
    pass


class InvalidGuidException(ResourceException):
    pass


class EndOfResultsException(ResourceException):
    pass


class Resource:
    api_key_field = config.API_KEY_FIELD

    def __init__(self,
                 path: str,
                 filters: ResourceFilterList,
                 result_entity_type: Type[GBEntity]):
        self.path: str = path
        '''The relative path to this Resource's API endpoint.'''
        self.result_entity_type: Type[GBEntity] = result_entity_type
        '''The class representing the object or objects returned by this Resource.'''
        self.filters: ResourceFilterList = filters
        '''A list of all filter members available to this Resource.'''
        self.base_url = config.API_BASE_URL
        '''The core portion of the API URL. This is the beginning of the URL up until the path.'''
        self.api_key = config.API_KEY
        '''The user's API key.'''
        self.url = ''
        '''The fully-built URL. Built when a request is made.'''
        self.response = None
        '''The response from a request.'''
        self.last_response_metadata: Optional[ResponseMetadata] = None
        '''The metadata of the last response from a request.'''
        self.working_metadata: Optional[ResponseMetadata] = None
        '''The working metadata used to craft new requests.'''
        self.results = None
        '''The results portion of the response from a request.'''
        self.__override_url = None
        '''When set, requests are forced to this URL regardless of this Resource's other state.'''

    def __get_full_path(self) -> str:
        return self.base_url + self.path

    def __build_filter_string(self):
        filter_strings = [
            f.name + '=' + str(f.value)
            for f in self.filters.applied()
        ]
        trail = '&' if len(filter_strings) > 0 else ''
        return '&'.join(filter_strings) + trail

    def __build_api_key_string(self):
        return self.api_key_field + '=' + self.api_key

    def __build_url(self, guid: str = None):
        if guid is None:
            guid = ''
        else:
            guid = f'/{guid}'
        self.url = f'{self.__get_full_path()}{guid}/?{self.__build_filter_string()}{self.__build_api_key_string()}'

    def __build_overridden_url(self):
        self.url = self.__override_url + '/?' + self.__build_api_key_string()

    def _request(self, guid: str = None):
        if self.__override_url is not None:
            self.__build_overridden_url()
        else:
            self.__build_url(guid)
        self.response = requester.request(self.url)
        self.last_response_metadata = ResponseMetadata(self.response)
        self.working_metadata = ResponseMetadata(self.response)
        self.results = self.response.results

    def override_url(self, url: str):
        """
        Overrides the URL for this resource using the supplied ``url``. The ``url`` is assumed to be a valid
        fully-formed URL to a GB API resource. A request to that URL is assumed to return a result that is conveyable as
        an object of the same type as this :class:`SingleResultResource`'s ``result_object_class``.
        :param url: The URL to use to make a request to the GB API.
        :return: An object of the type represented by this SingleResultResource's result_object_class.
        """
        self.__override_url = url


class SingleResultResource(Resource):
    def get(self, *, id: int = None, guid: str = None):
        """
        Gets the result for this resource. Optionally, supply the id or guid to set for this resource before
        sending the request. If an override URL is set for this resource, the id and guid are ignored.
        :param id: The ID of the result to get.
        :param guid: The GUID of the result to get.
        :return:
        """
        if id is not None:
            guid = self.result_entity_type.id_to_guid(id)
        self._request(guid)
        return self.results


class MultipleResultResource(Resource):
    def __init__(self,
                 path: str,
                 filters: ResourceFilterList,
                 result_entity_type: Type[GBEntity],
                 metadata: ResponseMetadata = None):

        super().__init__(path, filters, result_entity_type)
        if metadata is not None:
            self.last_response_metadata = metadata
            self.working_metadata = metadata
            self.__started = True
        else:
            self.__started = False

    @property
    def count_from_beginning(self) -> int:
        """
        Returns the number of items from the beginning of the results to through the last row on the current page.
        :return: The number of items from the beginning of the results to through the last row on the current page.
        """
        if self.working_metadata is None:
            return 0
        return self.working_metadata.offset + self.working_metadata.number_of_page_results

    @property
    def total_results(self) -> int:
        if self.working_metadata is None:
            return 0
        return self.working_metadata.number_of_total_results

    @property
    def page_results(self) -> int:
        if self.working_metadata is None:
            return 0
        return self.working_metadata.number_of_page_results

    @property
    def current_page(self) -> int:
        if self.working_metadata is None:
            return 0
        if self.working_metadata.limit > 0:
            # Get the ceiling
            return -(-self.count_from_beginning // self.working_metadata.limit)
        else:
            return 0

    @property
    def total_pages(self) -> int:
        if self.working_metadata is None:
            return 0
        if self.working_metadata.limit > 0:
            # Get the ceiling
            return -(-self.total_results // self.working_metadata.limit)
        else:
            return 0

    @property
    def is_last_page(self) -> bool:
        if self.working_metadata is None:
            return False
        return self.count_from_beginning >= self.total_results

    def query_metadata(self):
        """
        Retrieves a result containing no fields in order to retrieve initial metadata. Used when a specific page has
        been requested before any query to the API has been performed yet.
        :return:
        """
        saved_value = False
        field_list_value = None
        if self.filters.get('field_list') is not None:
            saved_value = True
            field_list_value = self.filters.get_value('field_list')
            self.filters.set('field_list', 'None')

        self._request()
        self.__started = True

        if saved_value:
            self.filters.set('field_list', field_list_value)

    def page(self, page_num: int):
        """
        Retrieve a single page of results at the page number provided. When a response is received, the
        offset is set to the end of the given page/beginning of the next page.
        :return:
        """
        if not self.__started:
            self.query_metadata()
        if page_num < 1:
            raise ValueError(f'Invalid page number {page_num}. Minimum is 1.')
        elif page_num > self.total_pages:
            raise ValueError(f'Invalid page number {page_num}. Larger than total page number of {self.total_pages}.')

        self.filters.set('offset', (self.working_metadata.limit * page_num) - self.working_metadata.limit)
        # Reset some members of the working metadata, as they no longer apply to our working context
        self.working_metadata.offset = 0
        self.working_metadata.number_of_page_results = 0
        return self.next()

    def next(self):
        """
        Retrieve a single page of results based on the current offset and limit. When a response is received,
        increment the offset by an amount equal to the limit.
        :return:
        """
        if self.is_last_page:
            raise EndOfResultsException()
        self._request()
        self.__started = True

        offset = self.working_metadata.offset
        if offset is not None:
            offset = int(offset)
        else:
            offset = 0

        limit = self.working_metadata.limit
        if limit is not None:
            limit = int(limit)
        else:
            limit = 0
        self.filters.set('offset', offset + limit)
        return [c for c in self.results.iterchildren()]
