from .api_object import FieldObject, FieldObjectDefinition, ApiField


class InvalidStubException(Exception):
    pass


class StubObjectDefinition(FieldObjectDefinition):
    def __init__(self):
        fields = [
            ApiField('api_detail_url', str),
            ApiField('guid', str),
            ApiField('id', str),
            ApiField('name', str),
            ApiField('site_detail_url', str),
            ApiField('total', int)
        ]
        super().__init__(fields)


class StubObject(FieldObject):
    def __init__(self, result):
        super().__init__(StubObjectDefinition(), result)
        self.target_is_collection: bool = (self.get_field_value('total') is not None)

    @property
    def id(self):
        return self.get_field_value('id')

    @property
    def guid(self):
        return self.get_field_value('guid')
