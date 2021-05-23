from typing import Optional

from .api_object import DownloadableApiObjectDefinition, IdentifierlessApiObjectDefinition, DownloadableApiObject, \
    IdentifierlessApiObject, ApiField


class ImageDefinition(DownloadableApiObjectDefinition, IdentifierlessApiObjectDefinition):
    def __init__(self):
        item_name = 'image'
        collection_name = 'images'
        type_id = 990000
        object_class = Image
        fields = [
            # URL to the icon version of the image.
            ApiField('icon_url', str),
            # URL to the medium size of the image.
            ApiField('medium_url', str),
            # URL to the original image.
            ApiField('original_url', str),
            # URL to the screenshot version of the image.
            ApiField('screen_url', str),
            # URL to the large screenshot version of the image.
            ApiField('screen_large_url', str),
            # URL to the small version of the image.
            ApiField('small_url', str),
            # URL to the super sized version of the image.
            ApiField('super_url', str),
            # URL to the thumb-sized version of the image.
            ApiField('thumb_url', str),
            # URL to the tiny version of the image.
            ApiField('tiny_url', str),
            # Name of image tag for filtering images.
            ApiField('image_tags', str)
        ]

        def default_download_url_field(obj: DownloadableApiObject) -> Optional[str]:
            urls = [
                'original_url',
                'screen_large_url',
                'super_url',
                'screen_url',
                'medium_url',
                'small_url',
                'thumb_url',
                'icon_url',
                'tiny_url'
            ]
            for url in urls:
                if obj.get_field_value(url) is not None:
                    return url
            return None

        super().__init__(item_name, collection_name, type_id, object_class, fields, default_download_url_field)


class Image(DownloadableApiObject, IdentifierlessApiObject):
    __definition = None

    def __init__(self, result):
        if self.__definition is None:
            self.__definition = ImageDefinition()
        super().__init__(self.__definition, result)
