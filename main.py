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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

litellm_client = AsyncOpenAI(
    base_url="https://exampleopenaiendpoint-production.up.railway.app/",
    api_key="sk-1234",
)


http_client: aiohttp.ClientSession = aiohttp.ClientSession()


# for completion
@app.post("/chat/completions")
@app.post("/v1/chat/completions")
async def proxy_completion(request: Request):
    # Get the raw request body
    body = {
        "model": "anything",
        "messages": [
            {
                "role": "user",
                "content": "hello who are you",
            }
        ],
    }
    
    # Get the authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header
    }

    async with http_client.post(
        'https://exampleopenaiendpoint-production.up.railway.app/chat/completions',
        headers=headers,
        json=body
    ) as response:
        return await response.json()

if __name__ == "__main__":
    import uvicorn

    # run this on 8090, 8091, 8092 and 8093
    uvicorn.run(app, host="0.0.0.0", port=8090)
