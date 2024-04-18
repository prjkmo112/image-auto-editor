import io
import numpy as np
import cv2
from PIL import Image
from fastapi import APIRouter, UploadFile, Form, File
from pydantic import BaseModel

from module.utils import Utils
from module.procimg import ProcessImage

utils = Utils()
procimg = ProcessImage()


router = APIRouter(
    prefix='/chkimg',
    tags=['Check Image']
)


@router.post('/compare')
def compare(
    image1:           bytes=File(),
    image2:           bytes=File(),
    algorithm_method: str="bhattacharyya"
):
    """
    # 이미지 유사도 측정
    """
    npImg1 = np.array(Image.open(io.BytesIO(image1)))
    npImg2 = np.array(Image.open(io.BytesIO(image2)))

    dist = 1
    if algorithm_method == "all":
        correl = procimg.compareArr(npImg1, npImg2, algorithm=cv2.HISTCMP_CORREL)
        chisqr = procimg.compareArr(npImg1, npImg2, algorithm=cv2.HISTCMP_CHISQR)
        bhattacharyya = procimg.compareArr(npImg1, npImg2, algorithm=cv2.HISTCMP_BHATTACHARYYA)

        if chisqr > 0 or correl < 0:
            dist = 1-bhattacharyya
        else:
            dist = correl * 0.1 + (1-chisqr) * 0.2 + (1-bhattacharyya) * 0.7
    elif algorithm_method == "correl":
        dist = procimg.compareArr(npImg1, npImg2, algorithm=cv2.HISTCMP_CORREL)
    elif algorithm_method == "bhattacharyya":
        dist = procimg.compareArr(npImg1, npImg2, algorithm=cv2.HISTCMP_BHATTACHARYYA)

    return { "similarity": dist }
