import json 
from utils.dataannotation import BoundingBox,Keypoint2D,Segmentation,Keypoint3D,box3DPX,RotationBoundingBox
from typing import List, Dict
import logging 

IMAGE_SUFFIX = [".png",".jpg",".jpeg"]
def getDatas(gtList:List,
             refer,
             formatType,
             allDatasets = None):
    
    if allDatasets is None:
        allDatasets = AllDatasets()

    for i in gtList:
        segImPath = i.replace("labels","seg").replace(".json",".png")
        js = ReadtoJson(i)
        for j in js:
            imgName = j["img_name"]
            imgWidth,imgHeight = j["width"],j["height"]
            img_anno = j["annotations"]
            for obj in img_anno:
                objName = obj["category_name"]
                objUniq = obj["unique_id"]
                objBbox = BoundingBox(obj["box2d"])
                objRbox = RotationBoundingBox(obj["rbox2d"])
                obj3Dbox = box3DPX(obj["box3DPX"])
                objKpName = obj["keypoint_name"]
                objKp2d = obj["keypoint2d"]
                objKp2dvisible = obj["keypoint2d_visible"]
                objKp3d = obj["keypoint3d"]
                objsegid = obj["segmentation_id"]
                objCustom = obj["custom_info"]

                objKp2dInfo = Keypoint2D(objKp2d,objKp2dvisible,objKpName,imgWidth,imgHeight)
                objKp3dInfo = Keypoint3D(objKp3d)
                objsegInfo = Segmentation(objsegid,segImPath,imgWidth,imgHeight,imgName)
                # print(objBbox.getCOCO())

def ReadtoJson(jsPath):
    with open(jsPath) as f:
        data = json.load(f)
    yield data

class setDatasets:
    def __init__(self,
                 imgName,
                 imgWidth,
                 imgHeight,
                 objName,
                 objUniq,
                 objcustom,
                 Bbox,
                 RBbox,
                 box3dpx,
                 kp2d,
                 kp3d,
                 seg,
                 refer,
                 formatType
                 ) -> None:
        self.Bbox = Bbox
        self.imgName = imgName
        self.objName = objName
        self.w,self.h = imgWidth,imgHeight
        self.objUniq = objUniq
        self.objCustom = objcustom # 추후에 사용 가능 

        self.refer = ReadtoJson(refer) 

        self.seg = seg
        self.key2d = kp2d
        self.key3d = kp3d
        self.Rbox = RBbox
        self.box3dpx = box3dpx
        self.form = formatType

    def getimgName(self):
        return self.imgName
    def getobjNmae(self):
        return self.objName
    def getimSize(self):
        return (self.w,self.h)
    def getBbox(self):
        if self.form == 1:
            return self.Bbox.getCOCO()
        elif self.form == 2:
            return self.Bbox.getYolo()
        elif self.form == 3:
            return self.Bbox.Kitti()
    
    def getSegmentation(self):
        if self.form == 1:
            return self.seg.getCOCO()
        elif self.form == 2:
            return self.seg.getYolo() # 정확하지 않음 

    def getkeypoint2d(self):
        if self.form == 1:
            return self.key2d.getCOCO() 
        elif self.form == 2:
            pass 
    def getkeypoint3d(self):
        if self.form == 1:
            return 

                    
class AllDatasets:
    def __init__(self) -> None:
        self._datasets = [] 
    def addDatasets(self,ds):
        self._datasets.append(ds)

    def getDatasets(self):
        return self._datasets
    