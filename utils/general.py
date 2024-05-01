import os 
from typing import List,Dict
from pathlib import Path 
import yaml
import json

from easydict import EasyDict as edict

IMAGE_SUFFIX = ["png","jpg","jpeg"]
GT_SUFFIX = ["txt","json"]

class setCheckDataPathDir():
    def __init__(self,DataPath:str)->List:
        self.DataPath = chnageAbsPath(DataPath,"Data Path")
        self.imPath,self.gtPath,self.segPath,self.depthPath= self.innerDirectoyCheck(self.DataPath)
        
    def getFileList(self,directorys,nameArg,suf = "txt"):
        """
        Input:
            directorys : Path (str)
            nameArg : parse_option name (str) 
        Fuction:
            directorys 경로 받아서 경로가 잘못되어 있는지 확인 후
            directorys 안에 txt파일이 있는지 확인 
            nameArg은 로그를 위한 값 잘못 되었을 때 parse_opt중에 어떤게 잘 못 되어 있는지 확인하는 용도 
        
        output:
            File list(list) : Directorys 안에 있는 파일  
            
        """
        dirs = directorys.replace("\\",os.sep)
        assert os.path.isdir(dirs),f"argument {nameArg} : Directory does not exist {directorys}"
        files_list = os.listdir(dirs)
        f = [os.path.join(directorys,file) for file in files_list if file.endswith(f".{suf}")]
        
        return f

    def innerDirectoyCheck(self,dataPath:str)->List:
        """
        DataPath 안에 들어가 있는 폴더가 추가 될 때 여기서 추가 해야한다. 

        상위 클래스에서 함수를 추가 하는 것도 있지 말아야 한다. 
        """
        assert os.path.exists(dataPath), f"Invalid data path {dataPath}"
        # imgdir,labeldir,segdir,depth

        for file in os.listdir(dataPath):
            if file in ("img","images","image"):
                imageDir = os.path.join(dataPath,file)
            elif file in ("labels","label","s2rJson","json"):
                labelDir = os.path.join(dataPath,file)
            elif file in ("seg","segmentation"):
                segDir = os.path.join(dataPath,file)
            elif file in ("depth","depthImage"):
                depthDir = os.path.join(dataPath,file)
        
        return imageDir,labelDir,segDir,depthDir

    def getLabelList(self):
        nameArg = "Labels Path"
        for suf in GT_SUFFIX:
            fileList = self.getFileList(self.gtPath,nameArg,suf)
            if len(fileList) > 0:
                return self.getFileList(self.gtPath,"Labels Path","json")
            
        raise Exception(f"argument {nameArg} : {GT_SUFFIX} files does not exist in Directory {self.gtPath}")
        
    
    def getimgList(self):
        nameArg = "Images Path"
        for suf in IMAGE_SUFFIX:
            fileList = self.getFileList(self.imPath,nameArg,suf)
            if len(fileList) > 0:
                return self.getFileList(self.imPath,nameArg,suf)
        raise Exception(f"argument {nameArg} : {IMAGE_SUFFIX} files done not exist in Directory {self.imPath}")
    
    
    def getsegList(self):
        nameArg = "Segmentaion Images Path"
        for suf in IMAGE_SUFFIX:
            fileList = self.getFileList(self.segPath,nameArg,suf)
            if len(fileList) > 0:
                return self.getFileList(self.segPath,nameArg,suf)
        raise Exception(f"argument {nameArg} : {IMAGE_SUFFIX} files done not exist in Directory {self.segPath}")
    
    def getdepthPaht(self):
        nameArg = "Depth Images Path"
        for suf in IMAGE_SUFFIX:
            fileList = self.getFileList(self.depthPath,nameArg,suf)
            if len(fileList) > 0:
                return self.getFileList(self.depthPath,nameArg,suf)
        raise Exception(f"argument {nameArg} : {IMAGE_SUFFIX} files done not exist in Directory {self.depthPath}")
    
class setCheckDataReferFile:
    def __init__(self,DataRefer:str) -> Dict:
        self.DataRefer = chnageAbsPath(DataRefer,"Data Referanse Information File")
    
    def getDataReferInfo(self):
        suf = Path(self.DataRefer).suffix
        if suf == ".yaml":
            with open(self.DataRefer) as f:
                data = yaml.load(f,Loader=yaml.FullLoader)

        elif suf == ".json":
            with open(self.DataRefer) as f:
                data = json.load(f)
        return data 
        
    
def chnageAbsPath(path,name):
    if os.path.exists(path):
        return os.path.abspath(path)
    else:
        raise FileExistsError(f"{name} Error,Please Check {name}")
    
def json_dict(jpth):
    with open(jpth,"r",encoding="cp949") as f:
        js_file = edict(json.load(f))
    return js_file

def yaml_dict(ypth):
    with open(ypth) as f:
        data = yaml.load(f,Loader=yaml.FullLoader)
    return data 