from .api_object import ApiObject, ApiObjectDefinition, ApiField


class ThemeDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'theme'
        collection_name = 'themes'
        type_id = 3032
        object_class = Theme
        fields = [
            # URL pointing to the theme detail resource.
            ApiField('api_detail_url', str),
            # For use in single item api call for theme.
            ApiField('guid', str),
            # Unique ID of the theme.
            ApiField('id', int),
            # Name of the theme.
            ApiField('name', str),
            # URL pointing to the theme on Giant Bomb.
            ApiField('site_detail_url', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Theme(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = ThemeDefinition()
        super().__init__(self.__definition, result)
