# mongodb 환경 구성
import os
import sys
from pymongo import MongoClient


def proc():
    try:
        client = MongoClient(
            f'''mongodb://{os.environ.get("MONGO_USER")}:{os.environ.get("MONGO_PW")}@{os.environ.get("MONGO_HOST")}/?authMechanism={os.environ.get("MONGO_AUTHMECHANISM")}''',
            serverSelectionTimeoutMS=3000
        )

        db = client[os.environ.get('MONGO_COLLECTION')]

        col_list = db.list_collection_names()

        for colnm in ['except_images', 'saved_images']:
            if colnm in col_list:
                db.create_collection(colnm)

        sys.exit(0)
    except:
        sys.exit(1)