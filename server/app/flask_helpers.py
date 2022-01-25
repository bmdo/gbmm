import logging
import traceback
import types
from functools import wraps
import flask
from flask import Response, request
from sqlalchemy import Column, and_

from config import config
from server.serialization import Marshmallowable


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.API_KEY is None or len(config.API_KEY) == 0:
            return bad_request('API Key required to access API.')
        return f(*args, **kwargs)
    return decorated_function


def json_data(*, required: bool = False):
    if not request.is_json:
        if required:
            raise ValueError('No data provided in POST call.')
        else:
            return None

    if required and request.json is None:
        raise ValueError('No data provided in POST call.')
    else:
        return request.json


# region Responses

def is_ok(r: Response):
    return 0 <= r.status_code - 200 < 100


def ok() -> Response:
    return Response(status=200)


def unavailable() -> Response:
    return Response(status=503)


def not_found(msg: str = 'Page not found') -> Response:
    return Response(
        f'<p>gbmm</p><h1>404</h1><p>{msg}</p>',
        status=404
    )


def bad_request(msg: str = None, exception: Exception = None) -> Response:
    logger = logging.getLogger('gbmm')
    if msg is not None:
        logger.warning(msg)
    if exception is not None:
        if len(exception.args) > 0:
            logger.warning(exception.args[0])
        logger.warning(traceback.format_exc())
        msg = (msg if msg is not None else '') + '\n'.join(exception.args)

    return Response(
        f'<h1>Bad request</h1><p>{msg}</p>',
        status=400
    )

# endregion Responses


class FilterHelper:
    def __init__(self):
        self.filters = []

    def eq_or_in(self, column: Column, value: any):
        if isinstance(value, list):
            self.filters.append(column.in_(value))
        else:
            self.filters.append(column.__eq__(value))

    def to_and(self):
        return and_(*self.filters)


class ListResultMetadata:
    def __init__(self, limit: int, offset: int, current_page: int, total_pages: int, total_results: int):
        self.limit = limit
        self.offset = offset
        self.current_page = current_page
        self.total_pages = total_pages
        self.total_results = total_results

    def dump(self):
        return {
            'offset': self.offset,
            'limit': self.limit,
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'total_results': self.total_results
        }


class ListResult(dict):
    def __init__(self, results, metadata: ListResultMetadata):
        super().__init__()
        self['results'] = results
        self['metadata'] = metadata.dump() if metadata is not None else {}


def dump(content: any, metadata: ListResultMetadata = None):
    result = recursive_dump(content)
    if result is None:
        return dict()
    elif isinstance(result, list):
        return ListResult(result, metadata)
    else:
        return result


def recursive_dump(node: any):
    if isinstance(node, dict):
        data = {}
        for k, v in node.items():
            data[k] = recursive_dump(v)
        return data
    elif isinstance(node, list) or isinstance(node, types.GeneratorType):
        return [recursive_dump(i) for i in node]
    elif isinstance(node, str) or isinstance(node, int) or isinstance(node, bool):
        return node
    elif isinstance(node, Marshmallowable):
        return node.dump()
    else:
        return None
