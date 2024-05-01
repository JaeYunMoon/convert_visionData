import os 
from typing import List, Dict
import numpy as np 
import cv2 

from setting import ConvertType
from general import json_dict


UNREAL_IMAGE_COORDINATE = "./refer/img_coor.json"
class BoundingBox:
    def __init__(self,Bbox:List,FormatType:int) -> None:
        # Sim2real - Bbox [xmin,xmax,ymin,ymax] 
        assert len(Bbox)==4,"Bbox coordinates Error"
        self.xmin,self.xmax,self.ymin,self.ymax = Bbox

        self.width = self.xmax - self.xmin 
        self.height = self.ymax - self.ymin

        self.centor_x = self.width /2 
        self.centor_y = self.height/2 

    def getCOCO(self):
        return [self.xmin,self.ymin,self.width,self.height]
    
    def getYolo(self,imgW,imgH):
        return [self.centor_x/imgW,self.centor_y/imgH,self.width/imgW,self.height/imgH]
    
    def getKitti(self):
        return [self.xmin,self.ymin,self.xmax,self.ymax]
        
class Keypoint2D:
    pass 

class Keypoint3D:
    pass 

class Segmentation:
    def __init__(self,segmentationID:int,segmentationImg:str) -> None:
        self.colorCoordinateJson = json_dict(UNREAL_IMAGE_COORDINATE)
        # sim2real - > int 
        colorcoord = list(self.colorCoordinateJson[str(segmentationID)])
        segImg = cv2.imread(segmentationImg)

        coord = [colorcoord[2],colorcoord[1],colorcoord[0]]
        coord_np = np.array(coord,dtype="int64")
        coord_upper = coord_np + 5
        coord_lower = coord_np - 5 

        img_mask = cv2.inRange(segImg,coord_lower,coord_upper)
        contours,_ = cv2.findContours(img_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_TC89_KCOS)
        
        # if not contours:
        #     continue # 색이 있는데 안나오는 경우 발생 

        for c in contours:
            new_seg = cv2.drawContours()
        
class box3DPX:
    pass 

class RotationBoundingBox:
    # sim2real - rbox2d [degree,x_centor,y_centor,w,h]
    def __init__(self,Rbox:List,FormatType:int)->List:
        self.degree,self.x_centor,self.y_centor,self.x,self.y  = Rbox 

    def getCOCO(self):
        return [self.degree,self.x_centor,self.y_centor,self.x,self.y]



