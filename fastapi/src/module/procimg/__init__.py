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
        cvnpdata1 = cv2.calcHist([cvnpdata1], [0,1], None, [180,256], [0, 180, 0, 256], accumulate=False)
        cvnpdata2 = cv2.calcHist([cvnpdata2], [0,1], None, [180,256], [0, 180, 0, 256], accumulate=False)

        cv2.normalize(cvnpdata1, cvnpdata1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(cvnpdata2, cvnpdata2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        res = cv2.compareHist(cvnpdata1, cvnpdata2, algorithm)

        return res

    def sliceImage(self, dest_img, yst, yend):
        return np.append(dest_img[:int(yst)], dest_img[int(yend):], axis=0)
            
    def getSimilarAxis(
        self, 
        except_np, 
        dest_img, 
        sliced_per=0.88, 
        calculateMethod="bhattacharyya", 
        limit=0.05, 
        batch_size=5,
        batch_size_x=5,
        full_width=False,

        # 해상도가 다른 경우에 기본보다 더 크게 잘리거나 더 작게 잘림을 방지하기 위함.
        # 즉, 제외할 이미지 기준의 px로 box를 만들어 비교했더니 해상도가 맞지 않게 잘림이 문제가 됨.
        # px box 비율을 두어 해당 배열에 있는 대로 모두 비교한다.
        # 다만, full_width 파라미터가 True인 경우 x축의 비율은 고려하지 않도록 한다.
        px_box_ratio=[1]
    ):
        """
        `dest_img`에서 `except_np`와 가장 유사한 이미지의 좌표를 가져온다

        ## Parameters
            limit (float):
            이 파라미터가 전달되면 `limit`가 넘어설 경우 중지하고 해당 부분을 가져온다
            `None`인 경우에는 전체 이미지를 모두 검색한 뒤 가장 거리가 짧은(유사도가 높은) 부분을 택한다.

            calculateMethod ("bhattacharyya"|"correl"|"chisqr"|"all")
        """
        nearestPos = {
            'xst': 0,
            'xend': 0,
            'yst': 0,
            'yend': 0,
            'distance': 1 if calculateMethod == "bhattacharyya" else 0
        }

        for ratio in px_box_ratio:
            ystPos = 0
            yendPos = except_np.shape[0] * ratio
            xstPos = 0
            if full_width:
                xendPos = dest_img.shape[1]
            else:
                xendPos = except_np.shape[1] * ratio

            while yendPos < dest_img.shape[0]:
                while xendPos <= dest_img.shape[1]:
                    slicedImgnp = dest_img[ int(ystPos):int(yendPos), int(xstPos):int(xendPos), : ]

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

                    if ((calculateMethod == "bhattacharyya" or calculateMethod == "chisqr") and _distance <= nearestPos['distance']) or ((calculateMethod == "all" or calculateMethod == "correl") and _distance >= nearestPos['distance']):
                        nearestPos['xst'] = xstPos
                        nearestPos['xend'] = xendPos
                        nearestPos['yst'] = ystPos
                        nearestPos['yend'] = yendPos
                        nearestPos['distance'] = _distance

                        if ((calculateMethod == "bhattacharyya" or calculateMethod == "chisqr") and _distance <= limit) or ((calculateMethod == "all" or calculateMethod == "correl") and _distance >= limit):
                            return nearestPos

                    if full_width:
                        break

                    xstPos += batch_size_x * ratio
                    xendPos += batch_size_x * ratio

                ystPos += batch_size * ratio
                yendPos += batch_size * ratio
                
                xstPos = 0
                if full_width:
                    xendPos = dest_img.shape[1]
                else:
                    xendPos = except_np.shape[1] * ratio

        return nearestPos
    
    def getSimilarAxisFm(
        self,
        except_np, 
        dest_img,
        full_width=False,
        padding=50,
        lowe=0.3 
    ):
        """
        [opencv Example](https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html) 참고
        """
        nearestPos = {}

        # Initiate SIFT detector
        sift = cv2.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1= sift.detectAndCompute(except_np, None)
        kp2, des2 = sift.detectAndCompute(dest_img, None)

        # FLANN parameters
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary
        flann = cv2.FlannBasedMatcher(index_params,search_params)
        matches = flann.knnMatch(des1,des2,k=2)

        pass_lowe = []  # lowe 기준 통과한 비율을 보기 위함
        for i, (m,n) in enumerate(matches):
            # ratio test as per Lowe's paper
            if m.distance < lowe * n.distance:
                point1 = kp2[m.trainIdx]
                point2 = kp2[n.trainIdx]

                if 'xst' not in nearestPos.keys() or point1.pt[0] < nearestPos['xst']:
                    nearestPos['xst'] = point1.pt[0]
                if 'yst' not in nearestPos.keys() or point1.pt[1] < nearestPos['yst']:
                    nearestPos['yst'] = point1.pt[1]
                if 'xend' not in nearestPos.keys() or point1.pt[0] > nearestPos['xend']:
                    nearestPos['xend'] = point1.pt[0]
                if 'yend' not in nearestPos.keys() or point1.pt[1] > nearestPos['yend']:
                    nearestPos['yend'] = point1.pt[1]
                
                nearestPos['distance'] = m.distance
                # m.distance가 너무 상대적인 거리라 비교적 지표가 될 n.distance로 나눠준 값도 추가해줌
                nearestPos['distance_lowe'] = m.distance/n.distance

                pass_lowe.append(matches[i])

        # 10%도 포함안되어 있으면 거리가 낮아도 제외
        if len(pass_lowe)/len(matches) < 0.1:
            return None

        if len(nearestPos.keys()) >= 4:
            # 크기가 자를 대상에 비해 너무 크면 제외
            if nearestPos['yend'] - nearestPos['yst'] > except_np.shape[1] * 3 or nearestPos['xend'] - nearestPos['xst'] > except_np.shape[0] * 2:
                return None

            # padding
            if full_width:
                nearestPos['xst'] = 0
                nearestPos['xend'] = dest_img.shape[1]
            else:
                nearestPos['xst'] -= padding
                nearestPos['xend'] += padding

            nearestPos['yst'] -= padding
            nearestPos['yend'] += padding

            if nearestPos['xst'] < 0:
                nearestPos['xst'] = 0
            if nearestPos['xend'] > dest_img.shape[1]:
                nearestPos['xend'] = dest_img.shape[1]
            if nearestPos['yst'] < 0:
                nearestPos['yst'] = 0
            if nearestPos['yend'] > dest_img.shape[0]:
                nearestPos['yend'] = dest_img.shape[0]

            return nearestPos
        else:
            return None