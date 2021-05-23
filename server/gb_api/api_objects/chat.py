from . import image
from .api_object import ApiObject, ApiObjectDefinition, ApiField


class ChatDefinition(ApiObjectDefinition):
    def __init__(self):
        item_name = 'chat'
        collection_name = 'chats'
        type_id = 2450
        object_class = Chat
        fields = [
            # URL pointing to the chat detail resource.
            ApiField('api_detail_url', str),
            # Name of the video streaming channel associated with the chat.
            ApiField('channel_name', str),
            # Brief summary of the chat.
            ApiField('deck', str),
            # For use in single item api call for chat.
            ApiField('guid', str),
            # Unique ID of the chat.
            ApiField('id', int),
            # Main image of the chat.
            ApiField('image', image.Image),
            # Chat password.
            ApiField('password', str),
            # URL pointing to the chat on Giant Bomb.
            ApiField('site_detail_url', str),
            # Title of the chat.
            ApiField('title', str)
        ]
        super().__init__(item_name, collection_name, type_id, object_class, fields)


class Chat(ApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = ChatDefinition()
        super().__init__(self.__definition, result)
