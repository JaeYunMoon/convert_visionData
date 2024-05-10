import os 
from typing import List,Dict
class CovertSaveDataset:
    def __init__(self,Dataset,savePath:str,Format,Annotation:Dict) -> None:
        self.savePath = savePath
        self.Dataset = Dataset
        self.Format = Format
        self.anno = Annotation

    def Convert(self):
        savePath = self.getDataSave()


    def getDataSave(self):
        if os.path.exists(self.savePath):
            return os.path.abspath(self.savePath)
        else:
            localAbsPath = os.path.abspath(self.savePath)
            os.makedirs(localAbsPath) # return 없음 
            return localAbsPath
        
