import io
import re
import base64
from PIL import Image
import pickle

from .logger import Logger

logger = Logger()


class Utils:
    def __new__(cls):
        if not hasattr(cls, "__instance"):
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        cls = type(self)
        if not hasattr(cls, "__init"):
            self.log = logger.log

            cls.__init = True

    def img_np2byte(self, npimg, format=None):
        img = Image.fromarray(npimg)
        byteimg = io.BytesIO()
        img.save(byteimg, format)

        return byteimg

    def img_byte2base64(self, byteimg):
        base64img = base64.b64encode(byteimg).decode("utf-8")
        return base64img