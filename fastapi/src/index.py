import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from module.utils import Utils

from routers import procimg, chkimg, settings



if os.environ.get('IS_INSIDE_IN_DOCKER_NOT_VALUE_FOR_USER', False):
    load_dotenv( dotenv_path="../../.env", verbose=True, override=True )

utils = Utils()


ALLOWED_IP = [
    # allow only local
    "::1", "localhost", "127.0.0.1", "192.168.0.1", "::ffff:127.0.0.1"
] + list(map(lambda v: v.strip(), (os.environ.get('ALLOWED_IP') or "").split(",")))

description = """
특정 이미지를 제거하고 재생성하는 역할을 함

## Mechanism
1. 제외해야 할 이미지들을 미리 파일로 저장되어있다.
2. 요청이 이미지와 함께 들어온다.
3. 이미지에 제외할 이미지가 있는지 체크한다.
4. 없으면 그냥 되돌린다.
5. 있음 편집하고 편집한 이미지를 되돌려준다.
"""

app = FastAPI(
    title="이미지 Resize API",
    description=description,
    summary="이미지의 특정 이미지를 제외하고 재생성하기 위한 백엔드"
)

# routers
app.include_router(procimg.router)
app.include_router(chkimg.router)
app.include_router(settings.router)


# global middleware
# default middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# user middleware
def ipblock(req:Request, next):
    if req.client.host not in ALLOWED_IP:
        utils.log.warn(f"NOT ALLOW BY ({req.client.host})")
        return JSONResponse(status_code=403, content={ "success": False, "error": True, "errmsg": "Not Allowed" })

def logger(req:Request, next):
    utils.log.info(f'[{req.method} | {req.url}] 요청')

# user middleware
@app.middleware("http")
async def mainMiddleware(req: Request, next):
    ipblock(req, next)
    logger(req, next)

    response = await next(req)
    return response