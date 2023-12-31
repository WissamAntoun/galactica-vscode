import argparse
import hashlib
import json
import logging
import os
from typing import Any, AsyncGenerator, Callable, Dict, Optional, Tuple

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from starlette.requests import Request
from starlette.responses import Response
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

logger = logging.getLogger(__name__)

TIMEOUT_KEEP_ALIVE = 5  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()
engine = None
do_cache = False

PARAMETERS_MAPPING = {
    "temperature": "temperature",
    "top_p": "top_p",
    "max_new_tokens": "max_tokens",
    "stop": "stop",
}

# EMPTY for now
DEFAULT_PARAMETERS = {
    "temperature": os.getenv("TEMPERATURE", 0.0),
    "top_k": os.getenv("TOP_K", 50),
    "top_p": os.getenv("TOP_P", 0.95),
    "max_tokens": os.getenv("MAX_TOKENS", 64),
}


@app.get("/api/health/")
async def health() -> Response:
    """Health check."""
    return Response(status_code=200)


def generate_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> str:
    cache_key = hashlib.md5(  # noqa: S324
        f"{func.__module__}:{func.__name__}:{args[1:]}:{kwargs}".encode()
    ).hexdigest()
    return f"{namespace}:{cache_key}"


@cache(expire=60 * 60)
async def _generate(request, inputs, sampling_params, stream, cache_key):
    request_id = random_uuid()

    results_generator = engine.generate(inputs, sampling_params, request_id)

    # Streaming case
    async def stream_results() -> AsyncGenerator[bytes, None]:
        async for request_output in results_generator:
            prompt = request_output.prompt
            text_outputs = [prompt + output.text for output in request_output.outputs]
            ret = {
                "generated_text": text_outputs,
            }
            yield (json.dumps(ret) + "\0").encode("utf-8")

    async def abort_request() -> None:
        await engine.abort(request_id)

    if stream:
        background_tasks = BackgroundTasks()
        # Abort the request if the client disconnects.
        background_tasks.add_task(abort_request)
        return StreamingResponse(stream_results(), background=background_tasks)

    # Non-streaming case
    final_output = None
    async for request_output in results_generator:
        if await request.is_disconnected():
            # Abort the request if the client disconnects.
            await engine.abort(request_id)
            return Response(status_code=499)
        final_output = request_output

    assert final_output is not None
    prompt = final_output.prompt
    text_outputs = [prompt + output.text for output in final_output.outputs]
    ret = {
        "generated_text": text_outputs[0],
    }
    return ret


@app.post("/api/generate/")
async def generate(request: Request) -> Response:
    """Generate completion for the request.

    The request should be a JSON object with the following fields:
    - inputs: the inputs to use for the generation.
    - stream: whether to stream the results or not.
    - other fields: the sampling parameters (See `SamplingParams` for details).
    """
    request_dict = await request.json()
    inputs = request_dict.pop("inputs")
    parameters: dict = request_dict.pop("parameters", DEFAULT_PARAMETERS)

    # map parameters to SamplingParams
    new_parameters = {}
    for key, value in parameters.items():
        if key in PARAMETERS_MAPPING:
            new_parameters[PARAMETERS_MAPPING[key]] = value

    # add default parameters
    for key, value in DEFAULT_PARAMETERS.items():
        if key not in new_parameters:
            new_parameters[key] = value

    if new_parameters.get("temperature", 0.0) <= 0.0:
        new_parameters["top_k"] = 1  # greedy sampling
        new_parameters["top_p"] = 1  # greedy sampling

    sampling_params = SamplingParams(**new_parameters)

    # left for the future, but unused in the extension
    stream = request_dict.pop("stream", False)

    if do_cache:
        cache_key = 1
    else:
        cache_key = random_uuid()
    ret = await _generate(request, inputs, sampling_params, stream, cache_key)

    return JSONResponse(content=ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--do_cache", action="store_true")
    parser = AsyncEngineArgs.add_cli_args(parser)
    args = parser.parse_args()

    if args.do_cache:
        do_cache = True

    FastAPICache.init(
        InMemoryBackend(),
        prefix="fastapi-cache",
        key_builder=generate_key_builder,
    )
    engine_args = AsyncEngineArgs.from_cli_args(args)
    engine = AsyncLLMEngine.from_engine_args(engine_args)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="debug",
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
    )
