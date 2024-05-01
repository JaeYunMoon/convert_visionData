import os 
from typing import List,Dict
import json 

IMAGE_SUFFIX = [".png",".jpg",".jpeg"]
class setDataConvert:
    def __init__(self,gtList:List,refer,formatType,annoDict:Dict,savePath = None) -> None:
        self.gtList = gtList 

    
    def ReadtoJson(self,jsPath):
        with open(jsPath) as f:
            data = json.load(f)
            print(data)
        yield data

    def run(self):
        for i in self.gtList:
            js = self.ReadtoJson(i)
            print(js["img_name"])