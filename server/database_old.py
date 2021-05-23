import logging
import sqlite3
import threading
import os
from collections import namedtuple
from pathlib import Path
from typing import Type, Optional, Union, TypeVar, Callable
from config import config
from server.gb_api.api_objects import ApiField
from server.gb_api.api_objects import ApiListField
from server.gb_api.api_objects import ApiObject
from server.gb_api.api_objects import Image
from server.gb_api.api_objects import ApiObjects, ApiObjectDefinitionSet, ApiObjectType
from server.gb_api.api_objects import StubObject

_DATABASE_SCHEMA_VERSION = '1'
_DATABASE_CONNECTION_PATH = os.path.join(config.DATABASE_DIR, config.DATABASE_NAME)

T = TypeVar('T', bound=ApiObjectType)


def _translate_type(t: type):
    if issubclass(t, str):
        return 'TEXT'
    elif issubclass(t, int):
        return 'INTEGER'
    elif issubclass(t, bool):
        return 'INTEGER'
    elif hasattr(t, '__origin__') and issubclass(t.__origin__, list):
        # For ApiListField
        return 'INTEGER'
    elif issubclass(t, ApiObject):
        return 'INTEGER'
    elif issubclass(t, StubObject):
        return 'INTEGER'
    else:
        raise TypeError('Invalid Python type for translation to SQL column type.')


class ApiObjectException(RuntimeError):
    pass


class ReferencedObjectNotFoundException(ApiObjectException):
    pass


class InvalidApiObjectClassException(ApiObjectException):
    pass


class NotChildApiObjectException(ApiObjectException):
    pass


class QueryException(RuntimeError):
    pass


class QueryColumnsValuesLengthMismatchException(QueryException):
    pass


class DatabaseError(RuntimeError):
    pass


class TableException(DatabaseError):
    pass


class TableStructureException(TableException):
    pass


class ColumnDefinition:
    def __init__(self, name: str, py_type: type, primary_key: bool = False, obj_field: bool = False):
        self.name: str = name
        self.py_type = py_type
        self.sql_type = _translate_type(py_type)
        self.primary_key = primary_key
        self.obj_field = obj_field

    @staticmethod
    def from_field(field: ApiField):
        primary_key = False
        if field.is_id:
            primary_key = True
        return ColumnDefinition(field.name, field.value_type, primary_key, True)


class StubMapping:
    def __init__(self,
                 stub_map_id: int = -1,
                 parent_guid: str = '',
                 parent_id: str = '',
                 field_name: str = '',
                 is_collection: bool = False,
                 stub_guid: str = '',
                 stub_id: str = '',
                 api_detail_url: str = '',
                 name: str = '',
                 site_detail_url: str = '',
                 total: int = 0):
        self.stub_map_id = stub_map_id
        self.parent_guid = parent_guid
        self.parent_id = parent_id
        self.field_name = field_name
        self.is_collection = is_collection
        self.stub_guid = stub_guid
        self.stub_id = stub_id
        self.api_detail_url = api_detail_url
        self.name = name
        self.site_detail_url = site_detail_url
        self.total = total


class ObjectMapping:
    def __init__(self,
                 object_map_id: int = -1,
                 parent_guid: str = '',
                 parent_id: str = '',
                 field_name: str = '',
                 child_guid: str = '',
                 child_id: str = ''):
        self.object_map_id = object_map_id
        self.parent_guid = parent_guid
        self.parent_id = parent_id
        self.field_name = field_name
        self.child_guid = child_guid
        self.child_id = child_id


# region Tables

class Table:
    def __init__(self,
                 database: 'Database',
                 name: str,
                 columns: list[ColumnDefinition]):
        self.logger = logging.getLogger('gbdl.database').getChild('table')
        self.name: str = name
        self.columns: list[ColumnDefinition] = columns
        self.database: 'Database' = database
        self.__queries = CommonQueries(self)

    def exists_in_database(self) -> bool:
        return self.__queries.get_table_definition() is not None

    def create_in_database(self):
        self.__queries.create_table()

    def get_column(self, name: str) -> ColumnDefinition:
        return next((c for c in self.columns if c.name == name), None)

    @property
    def primary_key_column(self):
        return next(c for c in self.columns if c.primary_key)

    def initialize(self):
        if not self.exists_in_database():
            self.create_in_database()


class TableController:
    def __init__(self, table: Table):
        self.name = table.name
        self.table = table
        self.db = table.database
        self.logger = table.logger


class DatabaseMetadataTable(Table):
    def __init__(self, database: 'Database'):
        name = '_meta'
        columns = [
            ColumnDefinition('key', str, primary_key=True),
            ColumnDefinition('value', str)
        ]
        super().__init__(database, name, columns)
        self.__queries = DatabaseMetadataQueries(self)

    def __initialize_metadata(self, metadata: dict):
        for k, v in metadata.items():
            row = self.__queries.get_row_by_primary_key(k)
            if row is None:
                self.__queries.insert_row_with_columns(['key', 'value'], [k, v])

    def initialize(self):
        super().initialize()
        self.__initialize_metadata(self.database.metadata)

    def get_metadata(self) -> dict:
        rows = self.__queries.get_all_rows()
        return dict(rows)


class StubMappingTable(Table):
    def __init__(self, database: 'Database'):
        name = '_stub_mappings'
        columns = [
            ColumnDefinition('stub_map_id', int, primary_key=True),
            ColumnDefinition('parent_guid', str),
            ColumnDefinition('parent_id', str),
            ColumnDefinition('field_name', str),
            ColumnDefinition('is_collection', bool),
            ColumnDefinition('stub_guid', str),
            ColumnDefinition('stub_id', str),
            ColumnDefinition('api_detail_url', str),
            ColumnDefinition('name', str),
            ColumnDefinition('site_detail_url', str),
            ColumnDefinition('total', str)
        ]
        super().__init__(database, name, columns)
        self.__queries = StubMappingQueries(self)

    def add_stub_mapping(self, parent_obj: ApiObject, field_name: str, stub: StubObject) -> StubMapping:
        """
        Adds the mapping to the table. Does nothing if a mapping for the same objects already exists.
        Returns the map_id of the added mapping or the existing mapping found.
        """
        match = self.get_stub_mapping_match(parent_obj, field_name, stub)
        if match is None:
            # Did not find existing mapping. Insert the new mapping.
            return self.__insert_stub_mapping(parent_obj, field_name, stub)
        else:
            # Found existing mapping. Return the ID of the existing mapping.
            return match

    def get_stub_mappings_for_field(self, obj_guid: str, field_name: str) -> list[StubMapping]:
        rows = self.__queries.get_all_stub_mappings_for_field(obj_guid, field_name)
        return [StubMapping(*r) for r in rows]

    def get_stub_mapping_match(self,
                               parent_obj: ApiObject,
                               field_name: str,
                               stub: StubObject
                               ) -> Optional[StubMapping]:
        row = self.__queries.get_matching_stub_mapping(parent_obj.guid, field_name, stub.guid)
        if row is not None:
            return StubMapping(*row)
        else:
            return None

    def __insert_stub_mapping(self, parent_obj: ApiObject, field_name: str, stub: StubObject) -> Optional[StubMapping]:
        columns = [
            'parent_guid',
            'parent_id',
            'field_name',
            'is_collection',
            'stub_guid',
            'stub_id',
            'api_detail_url',
            'name',
            'site_detail_url',
            'total'
        ]
        values = [
            parent_obj.guid,
            parent_obj.id,
            field_name,
            stub.target_is_collection,
            stub.guid,
            stub.id,
            stub.get_field_value('api_detail_url'),
            stub.get_field_value('name'),
            stub.get_field_value('site_detail_url'),
            stub.get_field_value('total')
        ]
        self.__queries.insert_row_with_columns(columns, values)
        stub_map_id = self.__queries.get_last_rowid()
        row = self.__queries.get_stub_mapping_by_id(stub_map_id)
        if row is not None:
            return StubMapping(*row)
        else:
            return None


class ObjectMappingTable(Table):
    def __init__(self, database: 'Database'):
        name = '_object_mappings'
        columns = [
            ColumnDefinition('object_map_id', int, primary_key=True),
            ColumnDefinition('parent_guid', str),
            ColumnDefinition('parent_id', str),
            ColumnDefinition('field_name', str),
            ColumnDefinition('child_guid', str),
            ColumnDefinition('child_id', str)
        ]
        super().__init__(database, name, columns)
        self.__queries = ObjectMappingQueries(self)

    def add_object_mapping(self, parent_obj: ApiObject, field_name: str, child_obj: ApiObject) -> ObjectMapping:
        """
        Adds an ObjectMapping to the table for the given ApiObjects. Does nothing if a mapping for the same ApiObjects
        already exists.
        Returns the added ObjectMapping or the existing mapping found.
        """
        match = self.get_object_mapping_match(parent_obj, field_name, child_obj)
        if match is None:
            # Did not find existing mapping. Insert the new mapping.
            return self.__insert_object_mapping(parent_obj, field_name, child_obj)
        else:
            # Found existing mapping. Return the ID of the existing mapping.
            return match

    def get_object_mappings_for_field(self, obj_guid: str, field_name: str) -> list[ObjectMapping]:
        rows = self.__queries.get_all_object_mappings_for_field(obj_guid, field_name)
        return [ObjectMapping(*r) for r in rows]

    def get_object_mapping_match(self,
                                 parent_obj: ApiObject,
                                 field_name: str,
                                 child_obj: ApiObject
                                 ) -> Optional[ObjectMapping]:
        row = self.__queries.get_matching_object_mapping(parent_obj.guid, field_name, child_obj.guid)
        if row is not None:
            return ObjectMapping(*row)
        else:
            return None

    def __insert_object_mapping(self,
                                parent_obj: ApiObject,
                                field_name: str,
                                child_obj: ApiObject
                                ) -> Optional[ObjectMapping]:
        columns = [
            'parent_guid',
            'parent_id',
            'field_name',
            'child_guid',
            'child_id'
        ]
        values = [
            parent_obj.guid,
            parent_obj.id,
            field_name,
            child_obj.guid,
            child_obj.id
        ]
        self.__queries.insert_row_with_columns(columns, values)
        object_map_id = self.__queries.get_last_rowid()
        row = self.__queries.get_object_mapping_by_id(object_map_id)
        if row is not None:
            return ObjectMapping(*row)
        else:
            return None


class ObjectTable(Table):
    def __init__(self, database: 'Database', obj_definition_set: ApiObjectDefinitionSet):
        self.obj_definition = obj_definition_set.definition
        self.obj_class = obj_definition_set.obj_class
        obj_columns = [ColumnDefinition.from_field(c) for c in self.obj_definition.fields]

        super().__init__(database, self.obj_definition.collection_name, obj_columns)

        self.id_column = self.get_column('id')
        self.guid_column = self.get_column('guid')


class ObjectTableController(TableController):
    def __init__(self, object_table: ObjectTable):
        self.obj_definition = object_table.obj_definition
        self.obj_class = object_table.obj_class

        super().__init__(object_table)
        self.table = object_table

        self.__queries = ObjectQueries(object_table)

    def __create_object_list_from_rows(self, rows: list[tuple]) -> list[Optional[any]]:
        return [self.__create_object_from_row(r) for r in rows]

    def __create_object_from_row(self, row_tuple: tuple):
        if row_tuple is None:
            return None
        source_list: list = list(row_tuple)
        obj_id = None
        obj_guid = None

        count = 0
        for f in self.obj_definition.fields:
            if count >= len(source_list):
                break
            if f.is_id:
                obj_id = source_list[count]
            if f.is_guid:
                obj_guid = source_list[count]
            count += 1

        if obj_id is None or obj_guid is None:
            raise TableStructureException()

        count = 0
        # Create sub-objects from linked object references
        for f in self.obj_definition.fields:
            if count >= len(source_list):
                break

            value = source_list[count]

            if value is not None:
                if issubclass(f.value_type, StubObject):
                    # Need to grab the StubObject(s) this field references from the database
                    stub_mappings = self.db.get_stub_mappings_for_field(obj_guid, f.name)

                    if len(stub_mappings) != value:
                        self.logger.warning(f'When retrieving field {f.name} for object with guid {obj_guid}, expected '
                                            f'{value} stub mappings but found {len(stub_mappings)}.')

                    stubs = []
                    for m in stub_mappings:
                        Result = namedtuple('Result',
                                            [
                                                'api_detail_url',
                                                'guid',
                                                'id',
                                                'name',
                                                'site_detail_url',
                                                'total'
                                            ]
                                            )
                        result = Result(
                            api_detail_url=m.api_detail_url,
                            guid=m.stub_guid,
                            id=m.stub_id,
                            name=m.name,
                            site_detail_url=m.site_detail_url,
                            total=m.total
                        )
                        stubs.append(StubObject(result))

                    if isinstance(f, ApiListField):
                        # Insert this as a list
                        source_list[count] = stubs
                    else:
                        # Insert this as an individual object
                        if len(stubs) > 0:
                            source_list[count] = stubs[0]
                        else:
                            source_list[count] = None

                elif issubclass(f.value_type, ApiObject):
                    # Need to grab the ApiObject(s) this field references from the database
                    obj_mappings = self.db.get_object_mappings_for_field(obj_guid, f.name)

                    if len(obj_mappings) != value:
                        self.logger.warning(f'When retrieving field {f.name} for object with guid {obj_guid}, expected '
                                            f'{value} object mappings but found {len(obj_mappings)}.')

                    api_objects = []
                    for m in obj_mappings:
                        obj = self.db.objects.get_one(obj_guid=m.child_guid)
                        if obj is None:
                            self.logger.warning(f'When retrieving field {f.name} for object with guid {obj_guid}, '
                                                f'could not retrieve mapped object with guid {m.child_guid}.')
                        api_objects.append(obj)

                    if isinstance(f, ApiListField):
                        # Insert this as a list
                        source_list[count] = api_objects
                    else:
                        # Insert this as an individual object
                        source_list[count] = api_objects[0]

            count += 1

        return self.obj_class(source_list)

    def insert_object(self, obj: T) -> T:
        def insert_stub_mapping(field_name: str, stub: StubObject) -> bool:
            """Returns True if a stub mapping was actually inserted, false otherwise"""
            # Add the stub object mapping if it does not already exist
            has_value = False
            for f in stub.fields:
                has_value = f.value is not None
                if has_value:
                    break

            if not has_value:
                return False

            stub_mapping = self.db.get_matching_stub_mapping(obj, field_name, stub)
            if stub_mapping is None:
                self.db.add_stub_mapping(obj, field_name, stub)

            return True

        def insert_mapped_object(field_name: str, mapped_obj: ApiObject):
            # Add the object mapping if it does not already exist
            match = self.db.get_matching_object_mapping(obj, field_name, mapped_obj)
            if match is None:
                # Did not find existing object, so we need to insert it into the database
                self.db.add_object_mapping(obj, field_name, mapped_obj)

            # Insert the object if it does not already exist
            match = self.db.objects.get_one(obj_guid=mapped_obj.guid)
            if match is None:
                # Did not find existing object, so we need to insert it into the database
                self.db.objects.add(field.value)

        # Get the names of all columns for this object
        valid_columns = [f.name for f in obj.fields]
        values = []

        # For any columns that are objects, find or insert those objects and track the reference.
        # Otherwise, get the actual value.
        for c in valid_columns:
            field = obj.get_field(c)
            # Does this field contain a list of objects?
            if field.value is None:
                # This object was not populated. Set the reference to NULL.
                values.append(None)

            elif issubclass(field.value_type, StubObject):
                # This field contains a StubObject
                if isinstance(field, ApiListField):
                    # This is a list of StubObjects
                    # Append the count of StubObjects in this list as the value for the column
                    count = 0
                    for v in field.value:
                        count += insert_stub_mapping(field.name, v)
                    values.append(count)
                else:
                    # This is a single StubObject
                    # Append 1 (the count of StubObjects) as the value
                    count = 0
                    count += insert_stub_mapping(field.name, field.value)
                    values.append(count)

            elif issubclass(field.value_type, ApiObject):
                # Restrict inserting objects to images. Some results have nested objects that cause circular
                # references and have incomplete info, so inserting them is harmful. video_shows, for example,
                # returns an entire video object for its 'latest' field. This video object contains its own
                # video_show member, which is the same as the original video show we were trying to insert. This
                # causes us to insert the video show we were attempting to originally insert before we can actually
                # finish inserting it in the first place, which is difficult to detect and leads us to try to insert
                # two conflicting rows in the database.
                # ENHANCE We can probably allow other nested objects someday if it becomes useful.
                if issubclass(field.value_type, Image):
                    # This field contains an ApiObject
                    if isinstance(field, ApiListField):
                        # This is a list of objects
                        # Append the count of objects in this list as the value for the column
                        values.append(len(field.value))
                        for v in field.value:
                            insert_mapped_object(field.name, v)
                    else:
                        # This is a single object
                        # Append 1 (the count of objects) as the value
                        values.append(1)
                        insert_mapped_object(field.name, field.value)
                else:
                    values.append(None)

            else:
                # This is a scalar value, so just insert it
                values.append(field.value)

        # We have calculated all of the values to insert. Insert a new row with these values.
        self.__queries.insert_row_with_columns(valid_columns, values)
        # Return the object we just inserted
        return obj

    def __get_by_id(self, obj_id: Union[int, str]) -> Optional[ApiObjectType]:
        row = self.__queries.get_row_by_primary_key(obj_id)
        if row is not None:
            return self.__create_object_from_row(row)
        else:
            return None

    def __get_by_guid(self, api_guid: str) -> Optional[ApiObjectType]:
        if self.table.guid_column is not None:
            row = self.__queries.get_row_by_guid(api_guid)
            if row is not None:
                return self.__create_object_from_row(row)
        return None

    def add(self, obj: T) -> T:
        """
        Adds the object to the table. Does nothing if an object with the same GUID, ID, or hash already exists.
        Returns the id of the added object or the existing object found.
        """
        found_obj = self.__get_by_id(obj.id)
        if found_obj is not None:
            return found_obj

        # We did not find the object in the database. Insert a new entry.
        inserted_obj = self.insert_object(obj)
        return inserted_obj

    # TODO provide a generic method for specifying filters rather than specific controller methods for guid and id
    def get(self, *, obj_guid: str = None, obj_id: Union[int, str] = None) -> Optional[T]:
        obj = None
        if obj_guid is not None:
            return self.__get_by_guid(obj_guid)
        elif obj_id is not None:
            return self.__get_by_id(obj_id)
        return obj


class ObjectTableControllerCollection:
    def __init__(self, object_tables: list[ObjectTable]):
        self.__tables = object_tables
        self.controllers = [ObjectTableController(t) for t in object_tables]
        if len(self.__tables) > 0:
            self.db = self.__tables[0].database

    def __get_controller_by_class(self, obj_class: Type[ApiObject]) -> Optional[ObjectTableController]:
        try:
            return next(t for t in self.controllers if t.obj_class is obj_class)
        except StopIteration:
            raise InvalidApiObjectClassException()

    def add(self, obj: T) -> T:
        """
        Adds the object to the database. Does nothing if an object with the same GUID or hash already exists.
        Returns the added object or the existing object found.
        """
        return self.__get_controller_by_class(obj.__class__).add(obj)

    # TODO make get_one generic so it can apply to any table
    # TODO make different generic gets, including for multiple

    def get_one(self,
                *,
                obj_class: T = None,
                obj_item_name: str = None,
                obj_guid: str = None,
                obj_id: Union[int, str] = None
                ) -> Optional[T]:
        """
        Retrieves the first object matching the provided filters from the database.

        Do not pass multiple class filters. In the case multiple class filters are provided,
        the filters take precedence with the priorities below (in descending order).

        Class filters:
         * obj_class
         * obj_item_name
         * obj_guid

        :param obj_class:
        :param obj_id:
        :param obj_guid:
        :param obj_item_name:
        """
        if obj_class is None:
            if obj_item_name is not None:
                obj_class = self.db.api_objects.get_type_by_item_name(obj_item_name)
            elif obj_guid is not None:
                obj_class = self.db.api_objects.get_type_by_guid(obj_guid)

        if obj_class is None:
            raise ValueError()

        controller = self.__get_controller_by_class(obj_class)

        obj = None
        if obj_guid is not None:
            obj = controller.get(obj_guid=obj_guid)
        elif obj_id is not None:
            obj = controller.get(obj_id=obj_id)

        return obj


# endregion Tables
# region Queries

class CommonQueries:
    def __init__(self, table: Table):
        self.table = table
        self.database = table.database

    def get_table_definition(self):
        sql = f'''
            SELECT *
            FROM sqlite_master
            WHERE type='table'
            AND name='{self.table.name}'
            '''
        return self.database.query_manager.execute_fetch_one(sql)

    def create_table(self):
        cols = ','.join([
            c.name + ' ' + c.sql_type + (' NOT NULL PRIMARY KEY' if c.primary_key else '')
            for c in self.table.columns
        ])
        sql = f'''
            CREATE TABLE {self.table.name} ({cols})
            '''
        return self.database.query_manager.execute(sql)

    def insert_row_with_columns(self, cols: [str], values: list):
        if len(cols) != len(values):
            raise QueryColumnsValuesLengthMismatchException()
        question_marks = ['?'] * len(cols)
        cols = ','.join(cols)
        values_placeholder = ','.join(question_marks)
        sql = f'''
            INSERT INTO {self.table.name}
            ({cols})
            VALUES ({values_placeholder})
            '''
        return self.database.query_manager.execute(sql, tuple(values))

    def insert_row(self, values: []):
        question_marks = ['?'] * len(values)
        values_placeholder = ','.join(question_marks)
        sql = f'''
            INSERT INTO {self.table.name}
            VALUES ({values_placeholder})
            '''
        return self.database.query_manager.execute(sql, values)

    def get_last_rowid(self):
        sql = f'''
            SELECT last_insert_rowid()
            FROM {self.table.name}
            '''
        return self.database.query_manager.execute_fetch_scalar(sql)

    def get_row_by_primary_key(self, primary_key: Union[int, str]):
        sql = f'''
            SELECT *
            FROM {self.table.name}
            WHERE {self.table.primary_key_column.name} = ?
            '''
        return self.database.query_manager.execute_fetch_one(sql, (primary_key,))

    def get_multiple(self, filters: tuple[str, str] = None):
        where_str = ''
        values = None
        if filters is not None and len(filters) > 0:
            filter_str = ' AND '.join([f'{f[0]}=?' for f in filters])
            values = tuple(f[1] for f in filters)
            where_str = f'WHERE {filter_str}'
        sql = f'''
            SELECT *
            FROM {self.table.name}
            {where_str}
            '''
        return self.database.query_manager.execute_fetch_all(sql, values)


class DatabaseMetadataQueries(CommonQueries):
    def get_all_rows(self):
        sql = f'''
            SELECT *
            FROM {self.table.name}
            '''
        return self.database.query_manager.execute_fetch_all(sql)


class StubMappingQueries(CommonQueries):
    def get_all_stub_mappings_for_field(self,
                                        parent_guid: str,
                                        field_name: str
                                        ) -> list[tuple]:
        sql = f'''
            SELECT *
            FROM {self.table.name}
            WHERE
                parent_guid = ? AND field_name = ?
            '''
        values = tuple([parent_guid, field_name])
        return self.database.query_manager.execute_fetch_all(sql, values)

    def get_matching_stub_mapping(self,
                                  parent_guid: str,
                                  field_name: str,
                                  stub_guid: str
                                  ) -> tuple[int]:
        sql = f'''
            SELECT *
            FROM {self.table.name}
            WHERE
                parent_guid = ? AND field_name = ? AND stub_guid = ?
            '''
        values = tuple([parent_guid, field_name, stub_guid])
        return self.database.query_manager.execute_fetch_one(sql, values)

    def get_stub_mapping_by_id(self, stub_map_id: int) -> tuple[int]:
        sql = f'''
            SELECT *
            FROM {self.table.name}
            WHERE
                stub_map_id = ?
            '''
        values = (stub_map_id,)
        return self.database.query_manager.execute_fetch_one(sql, values)


class ObjectMappingQueries(CommonQueries):
    def get_all_object_mappings_for_field(self,
                                          parent_guid: str,
                                          field_name: str
                                          ) -> list[tuple]:
        sql = f'''
            SELECT *
            FROM {self.table.name}
            WHERE
                parent_guid = ? AND field_name = ?
            '''
        values = tuple([parent_guid, field_name])
        return self.database.query_manager.execute_fetch_all(sql, values)

    def get_matching_object_mapping(self,
                                    parent_guid: str,
                                    field_name: str,
                                    child_guid: str
                                    ) -> tuple[int]:
        sql = f'''
            SELECT *
            FROM {self.table.name}
            WHERE
                parent_guid = ? AND field_name = ? AND child_guid = ?
            '''
        values = tuple([parent_guid, field_name, child_guid])
        return self.database.query_manager.execute_fetch_one(sql, values)

    def get_object_mapping_by_id(self, object_map_id: int) -> tuple[int]:
        sql = f'''
            SELECT *
            FROM {self.table.name}
            WHERE
                object_map_id = ?
            '''
        values = (object_map_id,)
        return self.database.query_manager.execute_fetch_one(sql, values)


class ObjectQueries(CommonQueries):
    def __init__(self, table: ObjectTable):
        super().__init__(table)
        self.table = table

    def get_row_by_guid(self, api_guid: str):
        sql = f'''
            SELECT * FROM {self.table.name}
            WHERE {self.table.guid_column.name} = ?
            '''
        return self.database.query_manager.execute_fetch_one(sql, (api_guid,))


# endregion Queries


class Query:
    def __init__(self, execute_callback: Callable[['Query'], any], sql: str, values: tuple = None):
        self.execute_callback = execute_callback
        self.sql = sql
        self.values = values
        self.result: any = None
        self.condition = threading.Condition()

    def execute(self):
        return self.execute_callback(self)


class QueryManager:
    def __init__(self):
        self.logger = logging.getLogger('gbdl.database').getChild('querymanager')

        self.__connection = None
        self.__cursor = None
        self.__queue: list[Query] = []
        self.__queue_lock = threading.Lock()
        self.__queue_pushed_condition = threading.Condition(self.__queue_lock)
        self.logger.debug('Starting querymanager daemon')
        self.__daemon = threading.Thread(target=self.__processor, daemon=True).start()

    def __processor(self):
        daemon_logger = self.logger.getChild('daemon')
        daemon_logger.debug('QueryManager daemon processor thread started')
        daemon_logger.debug(f'Opening connection to database using path {_DATABASE_CONNECTION_PATH}')
        self.__connection = sqlite3.connect(_DATABASE_CONNECTION_PATH)
        self.__cursor = self.__connection.cursor()
        while True:
            self.__queue_lock.acquire()
            if len(self.__queue):
                query = self.__queue.pop()
                self.__queue_lock.release()
                daemon_logger.debug(f"Dequeued query: "
                                    f"SQL: {query.sql}, Values: {query.values}")
                query.execute()
                with query.condition:
                    query.condition.notify_all()
            else:
                self.__queue_lock.release()

            with self.__queue_pushed_condition:
                while len(self.__queue) == 0:
                    daemon_logger.debug(f"QueryManager daemon awaiting notification.")
                    self.__queue_pushed_condition.wait()
                    daemon_logger.debug(f"QueryManager daemon received notification.")

    def __execute(self, query: Query):
        if query.values is None:
            self.__cursor.execute(query.sql)
        else:
            self.__cursor.execute(query.sql, query.values)
        if self.__connection.in_transaction:
            self.__connection.commit()
        query.result = None

    def __execute_fetch_all(self, query: Query):
        self.__execute(query)
        query.result = self.__cursor.fetchall()

    def __execute_fetch_one(self, query: Query):
        self.__execute(query)
        query.result = self.__cursor.fetchone()

    def __execute_fetch_scalar(self, query: Query):
        self.__execute_fetch_one(query)
        if query.result is not None and len(query.result) > 0:
            query.result = query.result[0]
        else:
            query.result = None

    def __enqueue_and_wait(self, query: Query):
        with self.__queue_lock:
            self.__queue.append(query)
        with self.__queue_pushed_condition:
            self.__queue_pushed_condition.notify_all()
        with query.condition:
            query.condition.wait()
        self.logger.debug(f'Query result:\n{query.result}')
        return query.result

    def execute(self, sql: str, values: tuple = None):
        query = Query(self.__execute, sql, values)
        return self.__enqueue_and_wait(query)

    def execute_fetch_all(self, sql: str, values: tuple = None) -> [tuple]:
        query = Query(self.__execute_fetch_all, sql, values)
        return self.__enqueue_and_wait(query)

    def execute_fetch_one(self, sql: str, values: tuple = None) -> Optional[tuple]:
        query = Query(self.__execute_fetch_one, sql, values)
        return self.__enqueue_and_wait(query)

    def execute_fetch_scalar(self, sql: str, values: tuple = None) -> Union[int, str, float, bytes, None]:
        query = Query(self.__execute_fetch_scalar, sql, values)
        return self.__enqueue_and_wait(query)


# region Database

class Database:
    def __init__(self, api_objects: ApiObjects):
        self.logger = logging.getLogger('gbdl').getChild('database')

        self.api_objects = api_objects
        self.query_manager = QueryManager()

        self.__object_tables = [ObjectTable(self, t) for t in self.api_objects]
        self.objects = ObjectTableControllerCollection(self.__object_tables)
        self.stub_mapping_table = StubMappingTable(self)
        self.object_mapping_table = ObjectMappingTable(self)
        self.metadata_table = DatabaseMetadataTable(self)
        self.metadata = {
            'schema_version': _DATABASE_SCHEMA_VERSION
        }
        self.__initialize()
        self.__conversions()

    def __initialize(self):
        Path(config.DATABASE_DIR).mkdir(parents=True, exist_ok=True)
        for t in self.__object_tables:
            t.initialize()
        self.stub_mapping_table.initialize()
        self.object_mapping_table.initialize()
        self.metadata_table.initialize()

    def __conversions(self):
        self.logger.debug('Checking database schema version.')
        target_schema_version = self.metadata.get("schema_version")
        self.logger.debug(f'Program schema version is {target_schema_version}.')

        schema_valid = False

        for k, v in self.metadata_table.get_metadata().items():
            if k == 'schema_version':
                self.logger.debug(f'Database schema version is {v}.')
                if v != target_schema_version:
                    raise DatabaseError(f'Existing database schema version is {v}. '
                                        f'Target database schema version is {target_schema_version}. '
                                        f'No conversion exists to convert to version {target_schema_version} '
                                        f'from version {v}.')
                else:
                    self.logger.debug(f'Database schema version is current.')
                    schema_valid = True

        if not schema_valid:
            raise DatabaseError('Could not validate database schema version.')

    # Public methods
    def add_stub_mapping(self, parent_obj: ApiObject, field_name: str, stub: StubObject) -> StubMapping:
        """
        Adds the stub mapping to the table. Does nothing if a mapping for the same objects already exists.
        Returns the added StubMapping or the existing Mapping found in the database.
        """
        return self.stub_mapping_table.add_stub_mapping(parent_obj, field_name, stub)

    def get_stub_mappings_for_field(self, obj_guid: str, field_name: str) -> list[StubMapping]:
        return self.stub_mapping_table.get_stub_mappings_for_field(obj_guid, field_name)

    def get_matching_stub_mapping(self,
                                  parent_obj: ApiObject,
                                  field_name: str,
                                  stub: StubObject
                                  ) -> Optional[StubMapping]:
        return self.stub_mapping_table.get_stub_mapping_match(parent_obj, field_name, stub)

    def add_object_mapping(self, parent_obj: ApiObject, field_name: str, child_obj: ApiObject) -> ObjectMapping:
        """
        Adds the object mapping to the table. Does nothing if a mapping for the same objects already exists.
        Returns the added Mapping or the existing Mapping found in the database.
        """
        return self.object_mapping_table.add_object_mapping(parent_obj, field_name, child_obj)

    def get_object_mappings_for_field(self, obj_guid: str, field_name: str) -> list[ObjectMapping]:
        return self.object_mapping_table.get_object_mappings_for_field(obj_guid, field_name)

    def get_matching_object_mapping(self,
                                    parent_obj: ApiObject,
                                    field_name: str,
                                    child_obj: ApiObject
                                    ) -> Optional[ObjectMapping]:
        return self.object_mapping_table.get_object_mapping_match(parent_obj, field_name, child_obj)

# endregion Database
