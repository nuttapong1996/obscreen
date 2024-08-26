import json
import mimetypes

from enum import Enum
from typing import Union, List, Optional

from src.util.utils import str_to_enum


class ContentInputType(Enum):

    UPLOAD = 'upload'
    TEXT = 'text'
    STORAGE = 'storage'
    HIDDEN = 'hidden'

    @staticmethod
    def is_editable(value: Enum) -> bool:
        if value == ContentInputType.UPLOAD:
            return False
        elif value == ContentInputType.TEXT:
            return True
        elif value == ContentInputType.STORAGE:
            return True


class ContentType(Enum):

    PICTURE = 'picture'
    URL = 'url'
    YOUTUBE = 'youtube'
    VIDEO = 'video'
    EXTERNAL_STORAGE = 'external_storage'
    COMPOSITION = 'composition'
    TEXT = 'text'

    @staticmethod
    def guess_content_type_file(filename: str):
        mime_type, _ = mimetypes.guess_type(filename)

        if mime_type in [
            'image/gif',
            'image/png',
            'image/jpeg',
            'image/webp',
            'image/jpg'
        ]:
            return ContentType.PICTURE
        elif mime_type in [
            'video/mp4'
        ]:
            return ContentType.VIDEO

        return None

    @staticmethod
    def get_input(value: Enum) -> ContentInputType:
        if value == ContentType.PICTURE:
            return ContentInputType.UPLOAD
        elif value == ContentType.VIDEO:
            return ContentInputType.UPLOAD
        elif value == ContentType.YOUTUBE:
            return ContentInputType.TEXT
        elif value == ContentType.URL:
            return ContentInputType.TEXT
        elif value == ContentType.EXTERNAL_STORAGE:
            return ContentInputType.STORAGE
        elif value == ContentType.COMPOSITION:
            return ContentInputType.HIDDEN
        elif value == ContentType.TEXT:
            return ContentInputType.HIDDEN

    @staticmethod
    def get_fa_icon(value: Union[Enum, str]) -> str:
        if isinstance(value, str):
            value = str_to_enum(value, ContentType)

        if value == ContentType.PICTURE:
            return 'fa-regular fa-image'
        elif value == ContentType.VIDEO:
            return 'fa-video-camera'
        elif value == ContentType.YOUTUBE:
            return 'fa-brands fa-youtube'
        elif value == ContentType.URL:
            return 'fa-link'
        elif value == ContentType.EXTERNAL_STORAGE:
            return 'fa-brands fa-usb'
        elif value == ContentType.COMPOSITION:
            return 'fa-solid fa-clone'
        elif value == ContentType.TEXT:
            return 'fa-solid fa-font'

        return 'fa-file'

    @staticmethod
    def get_color_icon(value: Enum) -> str:
        if isinstance(value, str):
            value = str_to_enum(value, ContentType)

        if value == ContentType.PICTURE:
            return 'info'
        elif value == ContentType.VIDEO:
            return 'success-alt'
        elif value == ContentType.YOUTUBE:
            return 'youtube'
        elif value == ContentType.URL:
            return 'danger'
        elif value == ContentType.EXTERNAL_STORAGE:
            return 'other'
        elif value == ContentType.COMPOSITION:
            return 'purple'
        elif value == ContentType.TEXT:
            return 'gscaleF'

        return 'neutral'

    @staticmethod
    def get_empty_location(value: Enum) -> str:
        if isinstance(value, str):
            value = str_to_enum(value, ContentType)

        if value == ContentType.COMPOSITION:
            return json.dumps({
                "ratio": '16/9',
                "layers": {}
            })
        elif value == ContentType.TEXT:
            return json.dumps({
                "text": 'Hello',
                "fontSize": 12,
                "color": '#FFFFFF',
                "backgroundColor": '#000000',
            })

        return ''
