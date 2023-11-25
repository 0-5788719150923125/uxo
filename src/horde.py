import argparse
import asyncio
import base64
import logging
from collections.abc import Coroutine
from pathlib import Path

import aiohttp
from horde_sdk import ANON_API_KEY, RequestErrorResponse
from horde_sdk.ai_horde_api.ai_horde_clients import AIHordeAPIAsyncSimpleClient
from horde_sdk.ai_horde_api.apimodels import (
    ImageGenerateAsyncRequest,
    ImageGenerateStatusResponse,
    ImageGenerationInputPayload,
    LorasPayloadEntry,
    TIPayloadEntry,
)
from horde_sdk.ai_horde_api.consts import (
    KNOWN_FACEFIXERS,
    KNOWN_MISC_POST_PROCESSORS,
    KNOWN_SOURCE_PROCESSING,
    KNOWN_UPSCALERS,
    POST_PROCESSOR_ORDER_TYPE,
)
from horde_sdk.ai_horde_api.fields import JobID
from PIL.Image import Image

# logging.getLogger("horde_sdk").setLevel(logging.WARNING)


async def async_one_image_generate_example(
    simple_client: AIHordeAPIAsyncSimpleClient,
    apikey: str = ANON_API_KEY,
) -> None:
    single_generation_response: ImageGenerateStatusResponse
    job_id: JobID

    with open("adam.jpg", "rb") as image_file:
        source = image_file.read()

    with open("mask.jpg", "rb") as image_file:
        mask = image_file.read()

    prompt = "(masterpiece, top quality, best quality, official art, beautiful and aesthetic:1.2), (1girl:1.3), (fractal art:1.3),"

    single_generation_response, job_id = await simple_client.image_generate_request(
        ImageGenerateAsyncRequest(
            apikey=apikey,
            prompt=prompt,
            # prompt="(masterpiece, top quality, best quality, official art, colorful, beautiful and aesthetic:1.2), anime robot (head:1.3) and (face:1.2) connected to a large metallic pipe",
            # prompt="artwork by yang xueguo, cgsociety, an ancient robot face connected to a large metallic pipe, stoic, lovecraftian, photorealistic, leviathan, monolithic, surreal, ethereal, coherent, believable, uncanny",
            # source_image=base64.b64encode(source),
            # source_mask=base64.b64encode(mask),
            # source_processing="img2img",
            models=[
                "GhostMix",
                # "Deliberate 3.0",
                # "Dreamshaper"
            ],
            # nsfw=True,
            # censor_nsfw=False,
            params=ImageGenerationInputPayload(
                height=512,
                width=512,
                steps=50,
                sampler_name="k_dpm_adaptive",
                # control_type="canny",
                # image_is_control=True,
                denoising_strength=0.65,
                cfg_scale=7.0,
                hires_fix=True,
                # karras=True,
                clip_skip=2,
                # use_nsfw_censor=False,
                loras=[
                    LorasPayloadEntry(
                        name="kl-f8-anime2",
                        # model=1,
                        # clip=1,
                        # inject_trigger="any",  # Get a random color trigger
                    ),
                ],
                tis=[
                    TIPayloadEntry(
                        name="ng_deepnegative_v1_75t",
                        inject_ti="negprompt",
                        strength=1,
                    ),
                    TIPayloadEntry(
                        name="easynegative",
                        inject_ti="negprompt",
                        strength=1,
                    ),
                ],
                # post_processing=[
                #     KNOWN_FACEFIXERS.GFPGAN,
                #     KNOWN_UPSCALERS.RealESRGAN_x2plus,
                # ],
                # post_processing_order=[
                #     POST_PROCESSOR_ORDER_TYPE.facefixers_first
                # ]
            ),
        ),
    )

    if isinstance(single_generation_response, RequestErrorResponse):
        print(f"Error: {single_generation_response.message}")
    else:
        single_image, _ = await simple_client.download_image_from_generation(
            single_generation_response.generations[0]
        )

        example_path = Path("/data")
        example_path.mkdir(exist_ok=True, parents=True)

        # single_image.save(example_path / f"{job_id}_simple_async_example.webp")
        single_image.save(example_path / f"eve.webp")


# async def async_multi_image_generate_example(
#     simple_client: AIHordeAPIAsyncSimpleClient,
#     apikey: str = ANON_API_KEY,
# ) -> None:
#     multi_generation_responses: tuple[
#         tuple[ImageGenerateStatusResponse, JobID],
#         tuple[ImageGenerateStatusResponse, JobID],
#     ]
#     multi_generation_responses = await asyncio.gather(
#         simple_client.image_generate_request(
#             ImageGenerateAsyncRequest(
#                 apikey=apikey,
#                 prompt="A cat in a blue hat",
#                 models=["SDXL 1.0"],
#                 params=ImageGenerationInputPayload(height=1024, width=1024),
#             ),
#         ),
#         simple_client.image_generate_request(
#             ImageGenerateAsyncRequest(
#                 apikey=apikey,
#                 prompt="A cat in a red hat",
#                 models=["SDXL 1.0"],
#                 params=ImageGenerationInputPayload(height=1024, width=1024),
#             ),
#         ),
#     )

#     download_image_from_generation_calls: list[
#         Coroutine[None, None, tuple[Image, JobID]]
#     ] = []

#     for status_response, _ in multi_generation_responses:
#         download_image_from_generation_calls.append(
#             simple_client.download_image_from_generation(
#                 status_response.generations[0]
#             ),
#         )

#     downloaded_images: list[tuple[Image, JobID]] = await asyncio.gather(
#         *download_image_from_generation_calls
#     )

#     example_path = Path("/data")
#     example_path.mkdir(exist_ok=True, parents=True)

#     for image, job_id in downloaded_images:
#         image.save(example_path / f"{job_id}_simple_async_example.webp")


async def async_simple_generate_example(apikey: str = ANON_API_KEY) -> None:
    async with aiohttp.ClientSession() as aiohttp_session:
        simple_client = AIHordeAPIAsyncSimpleClient(aiohttp_session)

        await async_one_image_generate_example(simple_client, apikey)
        # await async_multi_image_generate_example(simple_client, apikey)
