from ..model import ParseFileRequest
from .base_parser import AudioParser

from io import BytesIO
from typing import Union, List, Dict
from _exceptions import BadRequestError

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union, Dict, List


class ParserInterface(ABC):
    @abstractmethod
    def parse(
        self, file_stream: BytesIO, params: ParseFileRequest
    ) -> Union[List[Dict], str]:
        pass


class ParserFactory:
    @staticmethod
    def get_parser(file_ext: str) -> ParserInterface:
        parsers = {
            "mp3": AudioParser(),
            "wav": AudioParser(),
            "aac": AudioParser(),
            "aiff": AudioParser(),
            "flac": AudioParser(),
            "ogg": AudioParser(),
        }
        parser = parsers.get(file_ext.lower())
        if not parser:
            raise BadRequestError(error=f"Unsupported file type: {file_ext.lower()}")
        return parser


class AudioParsingService:
    def __init__(
        self, file_stream: BytesIO, metadata: dict, parser_request: ParseFileRequest
    ):
        self.file_stream = file_stream
        self.file_ext = metadata["label"]
        self.metadata = metadata
        self.parser_request = parser_request

    async def parse(self) -> Union[List[Dict], str]:
        parser = ParserFactory.get_parser(self.file_ext)
        return parser.parse(
            file_stream=self.file_stream,
            params=self.parser_request,
        )
