from marshmallow import Schema, fields, post_load


class ResponseMetadata:
    def __init__(self, response=None):
        if response is not None:
            self.error = str(response.error)
            self.limit = int(response.limit)
            self.offset = int(response.offset)
            self.number_of_page_results = int(response.number_of_page_results)
            self.number_of_total_results = int(response.number_of_total_results)
            self.status_code = int(response.status_code)
            self.version = str(response.version)


class ResponseMetadataSchema(Schema):
    error = fields.Str()
    limit = fields.Int()
    offset = fields.Int()
    number_of_page_results = fields.Int()
    number_of_total_results = fields.Int()
    status_code = fields.Int()
    version = fields.Str()

    @post_load
    def post_load(self, data, **kwargs):
        response_metadata = ResponseMetadata()
        response_metadata.error = data.get('error', None)
        response_metadata.limit = data.get('limit', None)
        response_metadata.offset = data.get('offset', None)
        response_metadata.number_of_page_results = data.get('number_of_page_results', None)
        response_metadata.number_of_total_results = data.get('number_of_total_results', None)
        response_metadata.status_code = data.get('status_code', None)
        response_metadata.version = data.get('version', None)
        return response_metadata
