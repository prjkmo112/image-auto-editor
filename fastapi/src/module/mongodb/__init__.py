import os
import io
import asyncio
from PIL import Image
from pymongo import MongoClient
import numpy as np
import pickle


class DBMongo:
    """
    Mongo DB 클래스
    """
    def __new__(cls):
        if not hasattr(cls, "__instance"):
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def __init__(self) -> None:
        cls = type(self)
        if not hasattr(cls, "__init") or cls.__init is False:
            client = MongoClient(
                f'''mongodb://{os.environ.get("MONGO_USER")}:{os.environ.get("MONGO_PW")}@{os.environ.get("MONGO_HOST")}/?authMechanism={os.environ.get("MONGO_AUTHMECHANISM")}''',
                maxPoolSize=50,
                serverSelectionTimeoutMS=3000
            )

            self.client = client
            self.db = client[os.environ.get('MONGO_COLLECTION')]

            cls.__init = True

    def close(self):
        self.client.close()

    async def __addExceptImg(self, code, imgbyte):
        return self.db['except_images'].insert_one({
            "image": imgbyte,     # np 이미지
            "code": code
        })
    
    async def __addExceptImgRunner(self, code, imgBytes):
        tasks = [self.__addExceptImg(code, byteimg) for byteimg in imgBytes]
        results = await asyncio.gather(*tasks)
        return results
    
    def addExceptImg(self, code, imgBytes):
        _results = asyncio.run(self.__addExceptImgRunner(code, imgBytes))
        
        results = list(map(lambda v: { "success": v is not None and v.inserted_id is not None }, _results))

        return results