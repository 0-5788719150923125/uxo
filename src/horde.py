import argparse
import asyncio
from collections.abc import Coroutine
from pathlib import Path
import base64

import aiohttp
from PIL.Image import Image

from horde_sdk import ANON_API_KEY, RequestErrorResponse
from horde_sdk.ai_horde_api.ai_horde_clients import AIHordeAPIAsyncSimpleClient
from horde_sdk.ai_horde_api.consts import KNOWN_SOURCE_PROCESSING
from horde_sdk.ai_horde_api.apimodels import (
    ImageGenerateAsyncRequest,
    ImageGenerateStatusResponse,
    ImageGenerationInputPayload,
    TIPayloadEntry,
)
from horde_sdk.ai_horde_api.fields import JobID


async def async_one_image_generate_example(
    simple_client: AIHordeAPIAsyncSimpleClient,
    apikey: str = ANON_API_KEY,
) -> None:
    single_generation_response: ImageGenerateStatusResponse
    job_id: JobID

    with open('adam.jpg', 'rb') as image_file:
        source = image_file.read()

    with open('mask.jpg', 'rb') as image_file:
        mask = image_file.read()

    single_generation_response, job_id = await simple_client.image_generate_request(
        ImageGenerateAsyncRequest(
            apikey=apikey,
            prompt="convert human to robot, convert machine pipe to tree branch",
            source_image=base64.b64encode(source),
            source_mask=base64.b64encode(mask),
            source_processing='img2img',
            models=["Deliberate"],
            params=ImageGenerationInputPayload(
                height=512,
                width=512,
                tis=[
                    TIPayloadEntry(
                        name="72437",
                        inject_ti="negprompt",
                        strength=1,
                    ),
                ],
            ),
        ),
    )

    if isinstance(single_generation_response, RequestErrorResponse):
        print(f"Error: {single_generation_response.message}")
    else:
        single_image, _ = await simple_client.download_image_from_generation(single_generation_response.generations[0])

        example_path = Path("/data")
        example_path.mkdir(exist_ok=True, parents=True)

        # single_image.save(example_path / f"{job_id}_simple_async_example.webp")
        single_image.save(example_path / f"eve.webp")


async def async_multi_image_generate_example(
    simple_client: AIHordeAPIAsyncSimpleClient,
    apikey: str = ANON_API_KEY,
) -> None:
    multi_generation_responses: tuple[
        tuple[ImageGenerateStatusResponse, JobID],
        tuple[ImageGenerateStatusResponse, JobID],
    ]
    multi_generation_responses = await asyncio.gather(
        simple_client.image_generate_request(
            ImageGenerateAsyncRequest(
                apikey=apikey,
                prompt="A cat in a blue hat",
                models=["SDXL 1.0"],
                params=ImageGenerationInputPayload(height=1024, width=1024),
            ),
        ),
        simple_client.image_generate_request(
            ImageGenerateAsyncRequest(
                apikey=apikey,
                prompt="A cat in a red hat",
                models=["SDXL 1.0"],
                params=ImageGenerationInputPayload(height=1024, width=1024),
            ),
        ),
    )

    download_image_from_generation_calls: list[Coroutine[None, None, tuple[Image, JobID]]] = []

    for status_response, _ in multi_generation_responses:
        download_image_from_generation_calls.append(
            simple_client.download_image_from_generation(status_response.generations[0]),
        )

    downloaded_images: list[tuple[Image, JobID]] = await asyncio.gather(*download_image_from_generation_calls)

    example_path = Path("/data")
    example_path.mkdir(exist_ok=True, parents=True)

    for image, job_id in downloaded_images:
        image.save(example_path / f"{job_id}_simple_async_example.webp")


async def async_simple_generate_example(apikey: str = ANON_API_KEY) -> None:
    async with aiohttp.ClientSession() as aiohttp_session:
        simple_client = AIHordeAPIAsyncSimpleClient(aiohttp_session)

        await async_one_image_generate_example(simple_client, apikey)
        # await async_multi_image_generate_example(simple_client, apikey)