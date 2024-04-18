import io
import base64
import pickle
from PIL import Image, ImageDraw, ImageFont
from typing import Annotated
from fastapi import APIRouter, File, Form
from pydantic import BaseModel, Field

from module.utils import Utils
from module.mongodb import DBMongo


utils = Utils()
mongo = DBMongo()


router = APIRouter(
    prefix="/settings",
    tags=['Setting etc']
)

@router.put('/set_eximg')
def set_except_image(
    images:        Annotated[list[bytes], File()],
    code:          Annotated[str, Form()]
):
    """
    # 제외할 이미지 추가
    """
    result = mongo.addExceptImg(code, images)

    return result

@router.get('/get_ex_img')
def get_except_image(
    code:       str,
    include:    bool=True
):
    """
    # 제외된 이미지를 확인할 수 있음
    """
    except_images = []
    if include:
        cursor = mongo.db['except_images'].find({ "code": { "$regex": "^"+code } })
    else:
        cursor = mongo.db['except_images'].find({ "code": code })

    for doc in cursor:
        base64img = utils.img_byte2base64(doc['image'])
        except_images.append({ "code": doc["code"], "image": base64img })

    return except_images


class Sfilter_get_settedimg(BaseModel):
    fil:    dict=Field(title='{ label: value } 형식으로 이루어진 label,value 쌍의 dict (json)', description="다만 이때 value값에 mongodb의 docs 형태로 넣어도 가능함")

@router.post('/get_settedimg')
def get_settedimg(sfilter: Sfilter_get_settedimg):
    """
    # 잘라내어 저장된 이미지들 확인할 수 있음
    """
    cursor = mongo.db['saved_images'].find({
        "$and": list(map(lambda k: { f'label.{k}': sfilter.fil[k] }, sfilter.fil)) + [ { 'image': { "$exists": True } } ]
    })

    datas = []
    for doc in cursor:
        base64img = utils.img_byte2base64(doc['image'])
        base64originimg = utils.img_byte2base64(doc['origin_image'])

        pil_drawed_orgimg = Image.open(io.BytesIO(doc['origin_image']))
        draw = ImageDraw.Draw(pil_drawed_orgimg)

        for axis in doc['axis']:
            draw.rectangle([(0, axis['yst']), (pil_drawed_orgimg.width, axis['yend'])], outline="red", width=2)

            font = ImageFont.load_default(15)
            draw.text((0, axis['yst']), f'{axis["distance"]}', fill='red', font=font)

        buffered = io.BytesIO()
        pil_drawed_orgimg.save(buffered, format=pil_drawed_orgimg.format)
        base64_drawed_orgimg = base64.b64encode(buffered.getvalue()).decode("utf-8")

        datas.append({
            "label": doc['label'],
            "axis": doc['axis'],
            "image": base64img,
            "origin_image": base64originimg,
            "drawed_orgin_image": base64_drawed_orgimg
        })

    return datas