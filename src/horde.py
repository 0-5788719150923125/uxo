import asyncio
import base64
import io
import json
import os
import sys
import traceback
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
from loguru import logger

# logger.remove()
# logger.add(sys.stdout, level="INFO")


async def generate_image(
    simple_client: AIHordeAPIAsyncSimpleClient,
    apikey: str = ANON_API_KEY,
    prompt: str = "(masterpiece, top quality, best quality, official art, beautiful and aesthetic:1.2), (1girl:1.3), (fractal art:1.3),",
    models: list = ["GhostMix"],
    height: int = 256,
    width: int = 256,
    sampler_name: str = "k_lms",
    control_type: str = "canny",
    steps: int = 25,
    denoising_strength: int = 0.65,
    cfg_scale: int = 7.0,
    clip_skip: int = 1,
    source: str = None,
    mask: str = None,
    image_is_control: bool = False,
    hires_fix: bool = True,
    karras: bool = True,
    tis: list = None,
) -> None:
    response: ImageGenerateStatusResponse
    job_id: JobID

    try:
        generations = []
        count = 0

        use_tis = []
        if tis is list:
            for ti in tis:
                use_tis.append(
                    TIPayloadEntry(
                        name=ti["name"],
                        inject_ti="negprompt",
                        strength=ti["strength"],
                    )
                )

        while len(generations) == 0 and count < 3:
            (
                response,
                job_id,
            ) = await simple_client.image_generate_request(
                ImageGenerateAsyncRequest(
                    apikey=apikey,
                    prompt=prompt,
                    source_image=source,
                    source_mask=mask,
                    source_processing="img2img",
                    models=models,
                    # nsfw=True,
                    # censor_nsfw=False,
                    params=ImageGenerationInputPayload(
                        height=height,
                        width=width,
                        steps=steps,
                        sampler_name=sampler_name,
                        control_type=control_type,
                        image_is_control=image_is_control,
                        denoising_strength=denoising_strength,
                        cfg_scale=cfg_scale,
                        hires_fix=hires_fix,
                        karras=karras,
                        clip_skip=clip_skip,
                        # use_nsfw_censor=False,
                        # loras=[
                        #     LorasPayloadEntry(
                        #         name="kl-f8-anime2",
                        #         # model=1,
                        #         # clip=1,
                        #         # inject_trigger="any",  # Get a random color trigger
                        #     ),
                        # ],
                        tis=use_tis,
                        # post_processing=[
                        #     # KNOWN_FACEFIXERS.GFPGAN,
                        #     KNOWN_UPSCALERS.RealESRGAN_x2plus,
                        # ],
                        # post_processing_order=[
                        #     POST_PROCESSOR_ORDER_TYPE.facefixers_first
                        # ]
                    ),
                ),
            )
            generations = response.generations
            count += 1

        if isinstance(response, RequestErrorResponse):
            raise Exception(response.message)
        else:
            single_image, _ = await simple_client.download_image_from_generation(
                generations[0]
            )

            buffer = io.BytesIO()
            single_image.save(buffer, format="WEBP")
            buffer.seek(0)
            image_data = buffer.read()
            data = base64.b64encode(image_data).decode("utf-8")

            return {"data": str(data)}
    except Exception as e:
        return {"err": str(e)}


async def async_generate_image(**kwargs) -> None:
    async with aiohttp.ClientSession() as aiohttp_session:
        simple_client = AIHordeAPIAsyncSimpleClient(aiohttp_session)

        data = await generate_image(simple_client=simple_client, **kwargs)
        return data
