# import sys, os
# sys.path.insert(
#     0, os.path.abspath("../")
# )  # Adds the parent directory to the system path
from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import uuid
import openai
from openai import AsyncOpenAI
import aiohttp
import litellm
from litellm.router import Router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

litellm_client = AsyncOpenAI(
    base_url="https://exampleopenaiendpoint-production-0ee2.up.railway.app/",
    api_key="sk-1234",
)


http_client: aiohttp.ClientSession = None
# for completion
@app.post("/chat/completions")
@app.post("/v1/chat/completions")
async def proxy_completion(request: Request):
    global http_client
    # Get the raw request body
    body = await request.json()
    
    # Get the authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if http_client is None:
        http_client = aiohttp.ClientSession()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header
    }

    async with http_client.post(
        'https://exampleopenaiendpoint-production-0ee2.up.railway.app/chat/completions',
        headers=headers,
        json=body
    ) as response:
        return await response.json()


router = Router(
    model_list=[
        {
            "model_name": "fake-openai-endpoint",
            "litellm_params": {
                "model": "openai/any",
                "api_key": "my-key",
                "api_base": "https://exampleopenaiendpoint-production-0ee2.up.railway.app/v1/chat/completions",
            },
        }
    ]
)

@app.post("/lite/chat/completions")
@app.post("/lite/v1/chat/completions")
async def lite_completion(request: Request):
    # Get the raw request body
    body = await request.json()
    body.pop("model", None)
    
    # Get the authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    response = await router.acompletion(
        model="fake-openai-endpoint",
        **body,
    )
    return response


@app.post("/lite_sdk/chat/completions")
@app.post("/lite_sdk/v1/chat/completions")
async def lite_sdk_completion(request: Request):
    # Get the raw request body
    body = await request.json()
    body.pop("model", None)
    
    # Get the authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    response = await litellm.acompletion(
        model="openai/fake-openai-endpoint",
        api_base="https://exampleopenaiendpoint-production-0ee2.up.railway.app//v1/chat/completions",
        api_key="my-key",
        **body,
    )
    return response


if __name__ == "__main__":
    import uvicorn

    # run this on 8090, 8091, 8092 and 8093
    uvicorn.run(app, host="0.0.0.0", port=8090)
