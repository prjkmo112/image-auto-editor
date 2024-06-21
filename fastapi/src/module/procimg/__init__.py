import requests
import numpy as np
import re
import io
from PIL import Image
import cv2
from sklearn.cluster import KMeans

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
        img = img.convert("RGB")
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
        lowe=0.3,
        set_padding=5,
        limit_custom=[],
        custom_functions=[]
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

        def calcAxis(_matches):
            _axis = {}
            _pass_lowe = []

            for i, (m,n) in enumerate(_matches):
                if m.distance < lowe * n.distance:
                    point1 = kp2[m.trainIdx]
                    point2 = kp2[n.trainIdx]

                    if 'xst' not in _axis.keys() or point1.pt[0] < _axis['xst']:
                        _axis['xst'] = point1.pt[0]
                    if 'yst' not in _axis.keys() or point1.pt[1] < _axis['yst']:
                        _axis['yst'] = point1.pt[1]
                    if 'xend' not in _axis.keys() or point1.pt[0] > _axis['xend']:
                        _axis['xend'] = point1.pt[0]
                    if 'yend' not in _axis.keys() or point1.pt[1] > _axis['yend']:
                        _axis['yend'] = point1.pt[1]
                    
                    _axis['distance'] = m.distance
                    _axis['distance_lowe'] = m.distance/n.distance

                    _pass_lowe.append(_matches[i])
            
            return _pass_lowe, _axis

        pass_lowe, nearestPos = calcAxis(matches)

        # 10%도 포함안되어 있으면 거리가 낮아도 제외
        if 'passlowe_over_10' in limit_custom and len(pass_lowe)/len(matches) < 0.1:
            return None

        if len(nearestPos.keys()) >= 4:
            # 크기가 자를 대상에 비해 너무 크면 제외
            if (
                'size_over_twice' in limit_custom and 
                (
                    nearestPos['yend'] - nearestPos['yst'] > except_np.shape[1] * 2 or 
                    (not full_width and nearestPos['xend'] - nearestPos['xst'] > except_np.shape[0] * 2)
                )
            ):
                return None
            
            # x,y 비율이 자를 대상과 너무 다르면 제외
            nearestPosRatio = (nearestPos['xend'] - nearestPos['xst'])/(nearestPos['yend'] - nearestPos['yst'])
            ratio = except_np.shape[1]/except_np.shape[0]
            if 'ratio_over_twice' in limit_custom and (nearestPosRatio-ratio > 0.5 or ratio-nearestPosRatio > 0.5):
                return None

            if 'use_kmeans' in custom_functions:
                # 같은 특징점이 다른 위치에 있을 경우 그곳에도 매칭되어버려 문제점이 생김
                # kmeans 군집분류를 통해 군집을 2개로 나뉘어 나뉜 keypoint가 많이 벗어나있다면 제외하고 다시 계산하도록 수정
                n_cluster = 2
                kmeans = KMeans(n_clusters=n_cluster, init="k-means++", max_iter=100, random_state=0)
                kmeans.fit(list(map(lambda v: [ kp2[v[0].trainIdx].pt[0], kp2[v[0].trainIdx].pt[1] ], pass_lowe)))

                main_label = 0
                sub_label = 1
                main_indexes = np.where(kmeans.labels_ == 0)[0]
                sub_indexes = np.where(kmeans.labels_ == 1)[0]
                if len(sub_indexes) > len(main_indexes):
                    main_label = 1
                    sub_label = 0
                    _ = main_indexes
                    main_indexes = sub_indexes
                    sub_indexes = _

                # all_indexes = []
                # for i in range(0, n_cluster):
                #     all_indexes.append({ "kmeans": np.where(kmeans.labels_ == i)[0], "label": i })

                # main_indexes = all_indexes[0]['kmeans']
                # main_label = all_indexes[0]['label']
                # sub_indexes = all_indexes[1]['kmeans']
                # sub_label = all_indexes[1]['label']

                # sub index 길이가 50% 이상이면 삭제 포기
                if 'kmeans_sub_limit' in limit_custom and len(sub_indexes) > 1 and len(sub_indexes) / len(kmeans.labels_) > 0.5:
                    return None

                # sub index 빼고 다시 axis 계산
                sub_trainIdxes = list(map(lambda v: pass_lowe[v][0].trainIdx, sub_indexes))
                pass_lowe_kmeans, axis_kmeans = calcAxis([ v for v in matches if v[0].trainIdx not in sub_trainIdxes ])

                # sub_index 와 main_index 간에 중심점 거리 확인
                # 중심점 사이간에 거리가 해당 점 제외하고 계산하여 나온 axis 범위와 차이가 너무 (크다면 kmeans 적용한 axis를), (작다면 기존 axis를 사용)
                x_cluster = kmeans.cluster_centers_[main_label][0] - kmeans.cluster_centers_[sub_label][0]
                y_cluster = kmeans.cluster_centers_[main_label][1] - kmeans.cluster_centers_[sub_label][1]

                axis_x = axis_kmeans['xend'] - axis_kmeans['xst']
                axis_y = axis_kmeans['yend'] - axis_kmeans['yst']

                use_kmeans = False
                if y_cluster/axis_y > 2 or axis_y/y_cluster > 2:
                    use_kmeans = True
                if not full_width and (x_cluster/axis_x > 2 or axis_x/x_cluster > 2):
                    use_kmeans = True

                if use_kmeans:
                    nearestPos = axis_kmeans
                    pass_lowe = pass_lowe_kmeans
                    # __dest_img = self.sliceImage()
                    # keypoint 다시 설정..
                    # kp2, des2 = sift.detectAndCompute(dest_img, None)
            

            # padding
            if full_width:
                nearestPos['xst'] = 0
                nearestPos['xend'] = dest_img.shape[1]
            else:
                if re.search(r'^[0-9]+%$', set_padding):
                    padding = (nearestPos['xend'] - nearestPos['xst']) * int(set_padding[:-1]) / 100
                else:
                    padding = int(set_padding)

                nearestPos['xst'] -= padding
                nearestPos['xend'] += padding

            if re.search(r'^[0-9]+%$', set_padding):
                padding = (nearestPos['yend'] - nearestPos['yst']) * int(set_padding[:-1]) / 100
            else:
                padding = int(set_padding)

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