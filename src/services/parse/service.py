import httpx
from io import BytesIO
from magika import Magika

from .utils import (
    generate_filename_from_url,
    get_filename_from_cd,
    TextProcessingPipeline,
)

from .text.service import TextParsingService
from .audio.service import AudioParsingService
from .image.service import ImageParsingService
from .video.service import VideoParsingService


from .model import ParseFileRequest

from _exceptions import BadRequestError
from _utils import create_success_response


class ParseHandler:
    def __init__(self, file_url, contents):
        self.file_url = file_url
        self.contents = contents

    async def download_file_to_memory(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.file_url)
                if response.status_code == 200:
                    filename = get_filename_from_cd(
                        response.headers.get("content-disposition")
                    )
                    if not filename:
                        filename = generate_filename_from_url(self.file_url)

                    return response.content, filename
                else:
                    raise BadRequestError(error={"message": "Error downloading file"})

        except Exception as e:
            raise BadRequestError(error={"message": "Error downloading file"})

    def download_text_to_memory(self):
        return self.contents.encode("utf-8"), "file.txt"

    def detect_filetype(self, contents):
        try:
            m = Magika()
            res = m.identify_bytes(contents)
            data = {
                "label": res.output.ct_label,
                "mime_type": res.output.mime_type,
                "group": res.output.group,
            }
            return data
        except Exception as e:
            raise BadRequestError(
                error={"message": "Error occurred while detecting filetype"}
            )

    async def parse(self, modality: str, parser_request: ParseFileRequest):
        if parser_request.contents:
            contents, filename = self.download_text_to_memory()
        else:
            contents, filename = await self.download_file_to_memory()

        stream = BytesIO(contents)
        metadata = self.detect_filetype(stream.getvalue())
        metadata.update({"filename": filename})

        if modality == "text":
            text_service = TextParsingService(
                file_stream=stream,
                metadata=metadata,
                parser_request=parser_request,
            )
            output = await text_service.parse()

        elif modality == "audio":
            audio_service = AudioParsingService(
                file_stream=stream,
                metadata=metadata,
                parser_request=parser_request,
            )
            output = await audio_service.parse()

        elif modality == "image":
            image_service = ImageParsingService(
                file_stream=stream,
                metadata=metadata,
                parser_request=parser_request,
            )
            output = await image_service.parse()

        elif modality == "video":
            video_service = VideoParsingService(
                file_stream=stream,
                metadata=metadata,
                parser_request=parser_request,
            )
            output = await video_service.parse()

        else:
            raise BadRequestError(error="Modality not supported")

        pipeline = TextProcessingPipeline()

        # additional params to process
        if parser_request.extract_tags:
            tags = await pipeline.extract_tags(output, "text")
            metadata.update({"tags": tags})

        # if parser_request.summarize:
        #     summary = await pipeline.summarize(output, "text")
        #     metadata.update({"summary": summary})

        return create_success_response({"output": output, "metadata": metadata})
