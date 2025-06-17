from dbgpt_client import Client,datasource

from fastapi import APIRouter, Body, Depends, HTTPException
from dbgpt._private.pydantic import BaseModel, Field, model_to_dict
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dbgpt.model.cluster.apiserver.api import APISettings
from dbgpt_serve.flow.api.endpoints import get_service
from typing import AsyncIterator, Optional
from starlette.responses import JSONResponse, StreamingResponse
import json
import asyncio
from dbgpt.component import SystemApp, logger
from sse_starlette import EventSourceResponse

router = APIRouter()
api_settings = APISettings()
get_bearer_token = HTTPBearer(auto_error=False)
client = Client(api_key="dbgpt")

async def check_api_key(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
    service=Depends(get_service),
) -> Optional[str]:
    """Check the api key
    Args:
        auth (Optional[HTTPAuthorizationCredentials]): The bearer token.
        service (Service): The flow service.
    """
    if service.config.api_keys:
        api_keys = [key.strip() for key in service.config.api_keys.split(",")]
        if auth is None or (token := auth.credentials) not in api_keys:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": {
                        "message": "",
                        "type": "invalid_request_error",
                        "param": None,
                        "code": "invalid_api_key",
                    }
                },
            )
        return token
    else:
        return None

class ChatDbQaRequestBody(BaseModel):
    messages: Optional[str] = Field(
        default=None, description="问题"
    )
    DB_NAME: Optional[str] = Field(
        default=None, description="数据源名称"
    )
    conv_uid: Optional[str] = Field(
        default=None, description="会话id"
    )
    model: Optional[str] = Field(
        default=None, description="Qwen-72B"
    )


@router.post("/chat_db_qa", dependencies=[Depends(check_api_key)])
async def chat_db_qa(
        request: ChatDbQaRequestBody = Body(),
        service=Depends(get_service),):
    async def generate_text():
        async for data in client.chat_stream(
                messages=request.messages,
                model="Qwen-72B",
                chat_mode="chat_with_db_qa",
                chat_param=request.DB_NAME,
                conv_uid=request.conv_uid
        ):
            # yield f"data:{data}\n\n"
            yield data.choices[0].delta.content
    logger.info(
        f"chat_completions:{request.DB_NAME},{request.messages},{request.conv_uid}"
    )
    # headers = {
    #     "Content-Type": "text/event-stream",
    #     "Cache-Control": "no-cache",
    #     "Connection": "keep-alive",
    #     "Transfer-Encoding": "chunked",
    # }
    # return StreamingResponse(
    #         generate_text(),
    #         headers=headers,
    #         media_type="text/event-stream",
    #     )
    return EventSourceResponse(generate_text())

@router.post("/craete_db_qa", dependencies=[Depends(check_api_key)])
async def craete_db_qa(
        request: ChatDbQaRequestBody = Body(),
        service=Depends(get_service),):
    response ={"success":False,"err_code":None}
    res = await datasource.get_datasource("/datasources")
    if res.status_code == 200:
        response = res.text
    return response

# async def generate_text():
#     res = await client.get("/datasources")
#     print(res)
#
# asyncio.run(generate_text())