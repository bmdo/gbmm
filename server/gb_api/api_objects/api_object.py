import copy
from hashlib import md5
from typing import Optional, Union, Callable, Type


# region ApiFields

class ApiField:
    def __init__(self,
                 name: str,
                 value_type: type):
        self.name: str = name
        self.value_type = value_type
        self.is_guid = (name == 'guid')
        self.is_id = (name == 'id')
        self._value: object = None

    @property
    def value(self):
        return self._value

    def set(self, value: any):
        self._value = self.convert(value)

    def convert(self, value):
        if value is None:
            return None
        elif isinstance(value, self.value_type):
            return value
        else:
            return self.value_type(value)

    def shake(self, result):
        """
        'Shakes' the result to find the value for this field and set it. Sets this field's value to None if
        the result does not have a member matching this field's name.
        """
        self.set(getattr(result, self.name, None))


class ApiListField(ApiField):
    def __init__(self,
                 name: str,
                 list_value_type: type):
        super().__init__(name, list_value_type)
        self._value: list[ApiObject] = []

    def set(self, value: object):
        # noinspection SpellCheckingInspection
        if hasattr(value, 'iterchildren'):
            self._value = [self.convert(v) for v in value.iterchildren()]
        elif isinstance(value, list):
            self._value = [self.convert(v) for v in value]
        else:
            raise Exception()

# endregion ApiFields


# region ApiObjects

class FieldObjectDefinition:
    def __init__(self, fields: list[ApiField]):
        self.fields = fields

    def get_field(self, field_name: str):
        return next((f for f in self.fields if f.name == field_name), None)

    def get_field_value(self, field_name: str) -> Optional[Union[int, str, bool, object]]:
        """
        Retrieves the value of the field with the given name from this ApiObject.

        :param field_name: The name of the field.
        :return: The field value. Returns None if the field does not exist or has no value.
        """
        f = self.get_field(field_name)
        return f.value if f is not None else None

    def set_field(self, field_name: str, value: object):
        f = self.get_field(field_name)
        if f is not None:
            f.set(value)


class ApiObjectDefinition(FieldObjectDefinition):
    def __init__(self,
                 item_name: str,
                 collection_name: str,
                 type_id: Optional[int],
                 object_class: Type['ApiObject'],
                 fields: list[ApiField]):
        self.item_name: str = item_name
        self.collection_name: str = collection_name
        self.type_id: int = type_id
        self.object_class = object_class
        super().__init__(fields)


class DownloadableApiObjectDefinition(ApiObjectDefinition):
    def __init__(self,
                 item_name: str,
                 collection_name: str,
                 type_id: Optional[int],
                 object_class: Type['ApiObject'],
                 fields: list[ApiField],
                 default_download_url_field_callback: Callable[['DownloadableApiObject'], Optional[str]]):
        super().__init__(item_name, collection_name, type_id, object_class, fields)
        self.default_download_url_field_callback = default_download_url_field_callback


class GuidlessApiObjectDefinition(ApiObjectDefinition):
    def __init__(self,
                 item_name: str,
                 collection_name: str,
                 type_id: Optional[int],
                 object_class: Type['ApiObject'],
                 fields: list[ApiField]):
        fields = [ApiField('guid', str)] + fields
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class IdentifierlessApiObjectDefinition(GuidlessApiObjectDefinition):
    def __init__(self,
                 item_name: str,
                 collection_name: str,
                 type_id: Optional[int],
                 object_class: Type['ApiObject'],
                 fields: list[ApiField]):
        fields = [ApiField('id', str)] + fields
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class FieldObject(FieldObjectDefinition):
    def __init__(self, definition: FieldObjectDefinition, result: Union[list, object]):
        super().__init__(copy.deepcopy(definition.fields))
        self.definition = definition
        if isinstance(result, list):
            # List object from database
            count = 0
            for f in self.fields:
                self.set_field(f.name, result[count])
                count += 1

        else:
            # Object from lxml/API result
            for f in self.fields:
                f.shake(result)


class ApiObject(FieldObject):
    def __init__(self, definition: ApiObjectDefinition, result: Union[list, object]):
        super().__init__(definition, result)
        self.definition = definition

    def __generate_guid(self):
        return f'{self.definition.type_id}-{self.id}'

    @property
    def guid(self):
        guid_field = next((f for f in self.fields if f.is_guid), None)
        if guid_field is None:
            return None
        elif guid_field.value is None:
            # The guid field exists but was not populated for some reason. This can happen when there is an object
            # nested 2 or more levels down in an API result. We'll instead calculate the guid, which should be
            # reliable.
            return self.__generate_guid()
        else:
            return guid_field.value

    @property
    def id(self):
        id_field = next((f for f in self.fields if f.is_id), None)
        return id_field.value if id_field is not None else None


class DownloadableApiObject(ApiObject):
    def __init__(self, definition: DownloadableApiObjectDefinition, result: Union[list, object]):
        super().__init__(definition, result)
        self.definition = definition

    @property
    def default_download_url_field(self):
        return self.definition.default_download_url_field_callback(self)


class GuidlessApiObject(ApiObject):
    def __init__(self, definition: GuidlessApiObjectDefinition, result: Union[list, object]):
        super().__init__(definition, result)
        self.definition = definition
        self.set_field('guid', self.guid)

    @property
    def guid(self):
        return f'{self.definition.type_id}-{self.id}'


class IdentifierlessApiObject(GuidlessApiObject):
    def __init__(self, definition: IdentifierlessApiObjectDefinition, result: Union[list, object]):
        super().__init__(definition, result)
        self.definition = definition
        self.set_field('id', self.id)

    @property
    def id(self):
        applicable_vals = [
            str.encode(str(self.get_field_value(f.name)), 'utf-8')
            for f in self.fields
            if not f.is_id
            and not f.is_guid
            and not issubclass(f.value_type, ApiObject)
            and self.get_field_value(f.name) is not None
        ]
        return md5(b''.join(applicable_vals)).hexdigest()


# endregion ApiObjects
