import os
import logging
from datetime import datetime



class Logger:
    def __new__(cls):
        if not hasattr(cls, "__instance"):
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        cls = type(self)
        if not hasattr(cls, "__init"):
            if not os.path.exists('/home/logs'):
                os.makedirs('/home/logs')

            logging.basicConfig(
                filename=f'/home/logs/{datetime.now().strftime("%Y-%m-%d.log")}', 
                filemode='a',
                encoding='utf-8', 
                level=logging.NOTSET
            )

            self.log = logging

            cls.__init = True