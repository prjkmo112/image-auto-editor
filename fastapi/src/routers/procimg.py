import os
import io
import re
import numpy as np
from PIL import Image
from enum import Enum
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from concurrent.futures import ProcessPoolExecutor

from module.utils import Utils
from module.mongodb import DBMongo
from module.procimg import ProcessImage


utils = Utils()
mongo = DBMongo()
procimg = ProcessImage()


router = APIRouter(
    prefix="/procimg",
    tags=['Process Image']
)

def cleanWorker(delimg, destImg, body):
    axis = procimg.getSimilarAxis(
        except_np=delimg,
        dest_img=destImg,
        calculateMethod=body.algorithm_method,
        batch_size=body.batch_size,
        batch_size_x=body.batch_size_x,
        full_width=body.full_width,
        px_box_ratio=body.px_box_ratio
    )

    return axis

def cleanWorkerLambda(v):
    return cleanWorker(*v)


def cleanWorkerFm(delimg, destimg, body):
    axis = procimg.getSimilarAxisFm(
        except_np=delimg,
        dest_img=destimg,
        full_width=body.full_width,
        lowe=body.lowe,
        limit_custom=body.limit_custom
        use_kmeans_custom_result=body.use_kmeans_custom_result
    )

    return axis

def cleanWorkerFmLambda(v):
    return cleanWorkerFm(*v)


class Item_clean_type(str, Enum):
    hist = 'hist'
    fm = 'fm'

class Item_clean_set_del_code(str, Enum):
    common = 'common'

class Item_clean_algorithmMethod(str, Enum):
    bhattacharyya = 'bhattacharyya'
    correl = 'correl'
    chisqr = 'chisqr'
    all = 'all'

class Item_clean(BaseModel):
    type:              Item_clean_type = Item_clean_type.hist
    image:             str = Field(title='처리할 이미지 url', description="처리할 이미지 url을 str형으로 보냅니다.", examples=['https://....~~...jpg'])
    set_del_code:      str
    set_except_images: list[str] = []
    algorithm_method:  Item_clean_algorithmMethod = Item_clean_algorithmMethod.bhattacharyya
    limit_value:       float=0.13
    save_db:           bool=True
    use_db:            bool=True
    db_label:          dict = Field(title='db의 구분하기 위한 label', examples=[{"key": "value", "key2": "value2"}], default={})
    db_filter:         dict = Field(title='db에서 찾기 위한 label 구분자', description="mongodb docs `label`컬럼에 대한 filter 형식", examples=[{ "(`db_label`에서 정한 key)": "(`db_label`에서 정한 value)" }], default={})
    full_width:        bool=True
    batch_size:        int=5
    batch_size_x:      int=5
    px_box_ratio:      list[float] = [1]

    lowe:              float=0.3
    limit_custom:      list[str] = Field(default=['passlowe_over_10'])
    use_kmeans_custom_result: bool=False
    

@router.post('/clean')
async def clean(item:Item_clean):
    """
    # 이미지 정리

    > 이미지로부터 정해진 제외할 이미지를 잘라냄  

    ## Params
    `type`  
    *hist* 히스토그램 분포를 비교하여 유사하면 잘라냄.  
    *fm* 기존의 히스토그램 분포로 작동하는 "*hist*"에는 동일한 색분포의 다른 그림을 유사하다고 판단하는 문제라던지 동일한 그림이지만 그림자체의 크기나 해상도가 달라져버리면 유사도가 낮아지는 문제가 컸음. 따라서 opencv를 사용해 특징점을 추출한 뒤 매칭을 하여 KNN을 통한 가장 가까운 것만 추려내 좌표를 구해 잘라내도록 한다.  
    
    `image`  
    처리할 이미지 url을 str형으로 보냄.

    `set_del_code`
    처리할 이미지들의 구분 기준을 정함.

    `set_except_images`  
    __(미완)__ 제외할 이미지들을 정함. 이 값이 None이 아닐 경우 기존의 [default 처리할 이미지](except_images/)들은 무시됨.
    
    `use_gpu`
    __(미완)__ GPU 를 사용

    `save_db`
    db에 저장 여부

    `db_label`
    db의 구분하기 위한 label 지정 {key: value, key2: value2,...} 형식

    `db_filter`
    db에서 찾기 위한 구분자 mongodb docs filter 형식
    이 파라미터를 넘기는 순간 db의 값을 사용하는 것에 동의하는 것임. 만약 db의 값을 사용하기 싫다면 이 파라미터를 주지 않으면 된다.
    
    list 요소인 dict 간에 상관관계는 `and`임.

    `full_width`
    잘라낼 때 x축을 고려하지 않고 잘라낸다. 즉, 오직 y축만을 잘라낸다.

    <br><hr>
    
    ### type이 *hist* 일 경우
    `algorithm_method`
    적용할 알고리즘을 선택함. 공통적으로 RGV -> HSV 변환하여 히스토그램으로 인식을 한 다음 분포등 특정 기준으로 유사도를 측정한다
    각 공식은 [CV2 공식 사이트](https://docs.opencv.org/3.4/d8/dc8/tutorial_histogram_comparison.html) 참고  
    *bhattacharyya* 바타차랴 거리법을 적용.   
    *correl* 상관관계 정도를 측정. (두 편차의 곱에 합을 두 표준편차의 곱으로 나눈 값)  
    *chisqr* 카이제곱  
    *all* 3개의 알고리즘을 정해진 공식으로 조합하여 사용   
        ```_dist_correl * 0.1 + (1-_dist_chisqr) * 0.2 + (1-_dist_batta) * 0.7```  
    <span style="font-size:12px; color: #979797">*all* 일 경우 속도가 저하될 수 있음</span>

    `limit_value`
    지우는 기준에 대한 max(min)의 범위를 정한다.
    다만, algoritm_method가 'all'인 경우에는 값이 클수록, 'battacharya'인 경우에는 작을수록 유사도가 높다는 걸 주의해야 함.

    `batch_size`
    비교할 때 y축의 batch 크기를 정한다. 이때 단위는 pixel임.

    `batch_size_x`
    비교할 때 x축의 batch 크기를 정한다. 이때 단위는 pixel임
    full_width 파라미터가 False인 경우에만 의미가 있는 값임

    `px_box_ratio`
    해상도가 다른 경우에 기본보다 더 크게 잘리거나 더 작게 잘림을 방지하기 위함.
    즉, 제외할 이미지 기준의 px로 box를 만들어 비교했더니 해상도가 맞지 않게 잘림이 문제가 됨.
    px box 비율을 두어 해당 배열에 있는 대로 모두 비교함. 다만, `full_width` 파라미터가 True인 경우 x축의 비율은 고려하지 않도록 함.

    <br><hr>
    
    ### type이 *fm* 일 경우
    `lowe`  
    ratio test as per Lowe's paper

    `limit_custom`
    특징점 과매칭으로 인한 오류나 그외 여러가지 오류를 방지하기 위한 limit
        `passlowe_over_10`  : lowe test를 통과한 매칭이 10%도 안된다면 아무리 유사도가 높아도 제외시킴
        `size_over_twice`   : 자른 결과가 비교한 대상에 비해 2배를 넘는 사이즈라면 제외시킴 (이때 비율 고려 없음, 무조건 사이즈 유사해야 함)
        `ratio_over_twice`  : `size_over_twice`와 비슷하지만 비율을 고려함

    `use_kmeans_custom_result`
    같은 특징점이 다른 위치에 있을 경우 그 곳에도 매칭되어버려 문제점이 생김  
    K-means 군집분류를 통해 군집을 2개로 나뉘어 나뉜 keypoint가 많이 벗어나있다면 제외하고 다시 계산하도록 수정  

    > 대부분의 경우에서는 사용하는 것이 더 정확도가 높게 나올 것임.
    > 하지만, 데이터의 사이즈에 따른 속도 감소는 감수해야할 사항임.
    """
    USE_DB = False
    RESULT_AXIS = []
    returnByteImage = None
    mediatype = "image/jpeg"

    # 이미지 포맷 확인
    if not re.search(r'(?:jpe?g|png|gif)$', item.image, flags=re.I):
        raise HTTPException(status_code=415, detail=f"지원하지 않는 이미지 포맷입니다 ({item.image})")

    # mongodb에 저장된 이미지 있는지 확인
    db_img = []
    if item.use_db and len(item.db_filter.keys()) > 0:
        db_img = list(
            map(
                lambda doc: dict({ "createdAt": doc['_id'].generation_time }, **doc),
                mongo.db['saved_images']
                    .find({ 
                        "$and": list(map(lambda v: { f'label.{v}': item.db_filter[v] }, item.db_filter)) + [ { 'image': { "$exists": True } } ]
                    })
                    .sort({ "_id": -1 })
                    .limit(1)
            )
        )
    
    if len(db_img) == 1:
        # 저장된 이미지를 return
        returnByteImage = db_img[0]['image']
        format = Image.open(io.BytesIO(returnByteImage))
        if format == "JPEG":
            mediatype = 'image/jpeg'
        elif format == "PNG":
            mediatype = 'image/png'
        USE_DB = True
    else:
        # db에 저장된게 없는 경우 직접 유사도 측정 후 정제 작업
        if len(item.set_except_images) == 0:
            del_images = []
            cursor = mongo.db['except_images'].find({ "code": item.set_del_code })
            for doc in cursor:
                del_images.append(np.array(Image.open(io.BytesIO(doc['image']))))

            origin_destImg = procimg.getBufferFromImage(item.image)
            destImg = origin_destImg.copy()

            if item.type == "hist":
                workerFn = cleanWorker
                workerLambdaFn = cleanWorkerLambda
            elif item.type == "fm":
                workerFn = cleanWorkerFm
                workerLambdaFn = cleanWorkerFmLambda

            if os.environ['PARALLEL_PROC'] == 'none':
                results = []
                for delimg in del_images:
                    results.append(workerFn(delimg, destImg, item))
            elif os.environ['PARALLEL_PROC'] == 'proc':
                # cpu bound -> multi-processing
                params = list(map(lambda v: (v, destImg, item), del_images))
                max_multi_proc = os.environ['MAX_MULTI_PROCESS']
                max_workers = None if max_multi_proc == "cpu_core" else int(max_multi_proc)
                with ProcessPoolExecutor(max_workers=max_workers) as executor:
                    results = list(executor.map(workerLambdaFn, params))

            results = list(filter(lambda v: v is not None, results))

            if len(results) > 0:
                # image slice
                results.sort(key=lambda v: v['yst'])

                # 범위 내에 겹치는 부분 제외, 이때 정확도가 낮은 것 우선으로 제외하기
                for idx1,axis1 in enumerate(results):
                    for idx2,axis2 in enumerate(results):
                        if idx2 <= idx1:
                            continue

                        if not (
                            (axis1['xend'] < axis2['xst'] or axis1['xst'] > axis2['xend']) or
                            (axis1['yend'] < axis2['yst'] or axis1['yst'] > axis2['yend'])
                        ):
                            # 겹침
                            # 정확도 비교
                            if (item.algorithm_method == "all" and axis1['distance'] > axis2['distance']) or (axis1['distance'] < axis2['distance']):
                                # 더 정확한걸 남긴다(axis1)
                                axis2['dup'] = True
                            else:
                                axis1['dup'] = True

                results = list(filter(lambda v: 'dup' not in v.keys() or not v['dup'], results))

                totalSlicedLen = 0
                for axis in results:
                    if (
                        (item.type == "fm" and axis['distance'] < 0.3) or
                        (item.type == "hist" and (item.algorithm_method == "all" and axis['distance'] > 0.8) or (item.algorithm_method == "bhattacharyya" and axis['distance'] < 0.2))
                    ):
                        RESULT_AXIS.append(axis)
                        destImg = procimg.sliceImage(destImg, axis['yst'] - totalSlicedLen, axis['yend'] - totalSlicedLen)
                        totalSlicedLen += axis['yend'] - axis['yst']
        else:
            # 미완
            pass

        byteimg = utils.img_np2byte(destImg, "JPEG")
        mediatype = "image/jpeg"
        returnByteImage = byteimg.getvalue()

        if not USE_DB and item.save_db:
            # 추가 : 기존 이미지
            origin_img = Image.fromarray(origin_destImg)
            origin_byteimg = io.BytesIO()
            if re.search(r'\.jpe?g$', item.image):
                mediatype = "image/jpeg"
                origin_img.save(origin_byteimg, format='JPEG')
            else:
                mediatype = 'image/png'
                origin_img.save(origin_byteimg, format='PNG')
            originByteImage = origin_byteimg.getvalue()

            doc = { "$set": { "origin_image": originByteImage, "image": returnByteImage, "axis": RESULT_AXIS } }
            mongo.db['saved_images'].update_one({ "label": item.db_label }, doc, upsert=True)

    if returnByteImage is not None:
        return Response(content=returnByteImage, media_type=mediatype)
    else:
        raise HTTPException(status_code=500, detail="UNKNOWN ERROR")