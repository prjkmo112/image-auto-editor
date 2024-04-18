import requests
import numpy as np
import io
from PIL import Image
import cv2

from module.utils import Utils

utils = Utils()


class ProcessImage:
    """
        이미지의 다양한 처리를 위한 클래스
    """
    def __init__(self) -> None:
        pass

    """
        이미지 다운로드
    """
    def getBufferFromImage(self, url:str):
        r = requests.get(url, headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Cookie': '',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })
        imgByte = io.BytesIO(r.content)
        img = Image.open(imgByte)
        return np.array(img)
    
    def resize(self, imgnpData, per):
        return imgnpData[ int(imgnpData.shape[0]*per): , : , : ]
    
    def __makePaddingTuple(self, pad):
        pad_arr = []
        for pad_item in pad:
            if pad_item%2 == 0:
                pad_tupple_item = (int(pad_item/2), int(pad_item/2))
                pad_arr.append(pad_tupple_item)
            else:
                x_pad = int(pad_item/2)
                y_pad = pad_item - x_pad
                pad_tupple_item = (x_pad, y_pad)
                pad_arr.append(pad_tupple_item)

        return tuple(pad_arr)


    def paddingAll(self, img1, img2):
        max_shape = tuple(np.maximum(img1.shape, img2.shape))

        _pad_tupple1 = tuple(np.subtract(max_shape, img1.shape))
        pad_tupple1 = self.__makePaddingTuple(_pad_tupple1)

        _pad_tupple2 = tuple(np.subtract(max_shape, img2.shape))
        pad_tupple2 = self.__makePaddingTuple(_pad_tupple2)

        return (
            np.pad(img1, pad_width=pad_tupple1, mode="constant", constant_values=[255]),
            np.pad(img2, pad_width=pad_tupple2, mode="constant", constant_values=[255])
        )

    def compareArr(self, np1, np2, algorithm=cv2.HISTCMP_BHATTACHARYYA):
        """
        numpy 배열 2개 유사도를 측정함
        """

        cvnpdata1 = cv2.cvtColor(np1, cv2.COLOR_BGR2HSV)
        cvnpdata2 = cv2.cvtColor(np2, cv2.COLOR_BGR2HSV)
        # hsv -> 0~179
        # rgb -> 0~255
        cvnpdata1 = cv2.calcHist([cvnpdata1], [0,1], None, [180,256], [0, 180, 0, 256])
        cvnpdata2 = cv2.calcHist([cvnpdata2], [0,1], None, [180,256], [0, 180, 0, 256])

        cv2.normalize(cvnpdata1, cvnpdata1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(cvnpdata2, cvnpdata2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        res = cv2.compareHist(cvnpdata1, cvnpdata2, algorithm)

        return res

    def sliceImage(self, dest_img, yst, yend):
        return np.append(dest_img[:yst], dest_img[yend:], axis=0)
            
    def getSimilarAxis(self, except_np, dest_img, type="all", sliced_per=0.88, calculateMethod="bhattacharyya", selectBest=True, limit=0.05, batch_size=5):
        """
        `dest_img`에서 `except_np`와 가장 유사한 이미지의 좌표를 가져온다

        ## Parameters
            selectBest (bool):
            'True'인 경우에는 전체 이미지를 모두 검색한 뒤 가장 거리가 짧은(유사도가 높은) 부분을 택하고, 
            'False'인 경우에는 `limit`가 넘어설 경우 중지하고 해당 부분을 가져온다

            calculateMethod ("bhattacharyya"|"correl"|"chisqr"|"all")
        """
        except_np = except_np[:]
        dest_img = dest_img[:]

        ystPos = 0
        yendPos = except_np.shape[0]
        nearestPos = {
            'yst': ystPos,
            'yend': yendPos,
            'distance': 1 if calculateMethod == "bhattacharyya" else 0
        }

        while yendPos < dest_img.shape[0]:
            slicedImgnp = dest_img[ ystPos:yendPos, :, : ]

            if calculateMethod == "all":
                _dist_correl = self.compareArr(slicedImgnp, except_np, cv2.HISTCMP_CORREL) # 1: 완전 일치, -1: 완전 불일치, 0: 무관계
                _dist_chisqr = self.compareArr(slicedImgnp, except_np, cv2.HISTCMP_CHISQR) # 0: 완전 일치, 무한대: 완전 불일치
                _dist_batta = self.compareArr(slicedImgnp, except_np, cv2.HISTCMP_BHATTACHARYYA) # 0: 완전 일치, 1: 완전 불일치

                if _dist_chisqr > 1 or _dist_correl < 0:
                    _distance = 1-_dist_batta
                else:
                    _distance = _dist_correl * 0.1 + (1-_dist_chisqr) * 0.2 + (1-_dist_batta) * 0.7
            elif calculateMethod == "bhattacharyya":
                _distance = self.compareArr(slicedImgnp, except_np, cv2.HISTCMP_BHATTACHARYYA)
            elif calculateMethod == "correl":
                _distance = self.compareArr(slicedImgnp, except_np, cv2.HISTCMP_CORREL)
            elif calculateMethod == "chisqr":
                _distance = self.compareArr(slicedImgnp, except_np, cv2.HISTCMP_CHISQR)

            if not selectBest:
                if ((calculateMethod == "bhattacharyya" or calculateMethod == "chisqr") and _distance < 0.1) or ((calculateMethod == "all" or calculateMethod == "correl") and _distance > 0.95):
                    nearestPos['yst'] = ystPos
                    nearestPos['yend'] = yendPos
                    nearestPos['distance'] = _distance
                    break
            if ((calculateMethod == "bhattacharyya" or calculateMethod == "chisqr") and _distance <= nearestPos['distance']) or ((calculateMethod == "all" or calculateMethod == "correl") and _distance >= nearestPos['distance']):
                nearestPos['yst'] = ystPos
                nearestPos['yend'] = yendPos
                nearestPos['distance'] = _distance

            ystPos += batch_size
            yendPos += batch_size

        return nearestPos