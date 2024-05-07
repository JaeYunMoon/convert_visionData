import os 
from typing import List, Dict
import numpy as np 
import cv2 
import logging 
from utils.general import json_dict


UNREAL_IMAGE_COORDINATE = "./refer/img_coor.json"
class BoundingBox:
    def __init__(self,Bbox:List) -> None:
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
    def __init__(self,keypoint2d,keypoint_visible,keypoint_name,width,height) -> None:
        self.keypoint2d = keypoint2d
        self.keypoint_visible = keypoint_visible
        self.w = width
        self.h = height
        self.keypointName = keypoint_name

    def getCOCO(self):
        # shape [17,3]
        self.kp = [] 
        self.count = 0
        for i in range(len(self.keypoint_visible)):
            x,y = self.keypoint2d[i]
            vk = self.keypoint_visible[i]
            if x < 0 or y<0 or x>self.w or y > self.h:
                z = 0  # 이미지를 넣어선 것 
            elif vk == 1:
                z = 1 # 가려진 것 
            elif vk == 0 :
                z = 2 
                self.count +=1 

            self.kp.append(x)
            self.kp.append(y)
            self.kp.append(z)

        return self.kp, self.count
    def getNameCOCO(self):
        # len 9개임 -> point 는 17개임 
        return self.keypointName

class Segmentation:
    def __init__(self,segmentationID:int,segmentationImg:str,imgWidth,imgHeight,imgName) -> None:
        self.colorCoordinateJson = json_dict(UNREAL_IMAGE_COORDINATE)
        self.w,self.h = imgWidth,imgHeight
        self.imgName = imgName
        # sim2real - > int 
        colorcoord = list(self.colorCoordinateJson[str(segmentationID)])
        segImg = cv2.imread(segmentationImg)

        coord = [colorcoord[2],colorcoord[1],colorcoord[0]]
        coord_np = np.array(coord,dtype="int64")
        coord_upper = coord_np + 5
        coord_lower = coord_np - 5 

        img_mask = cv2.inRange(segImg,coord_lower,coord_upper)
        contours,_ = cv2.findContours(img_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_TC89_KCOS)

        if not contours:
            self.contours = []  
        else:
            self.contours = contours
    def segFlatten(poly):
        seg = [] 
        for i in poly:
            a = i.flatten()
            for j in a:
                seg.append(j)
        return list(map(int,seg))
    
    def getCOCO(self):
        total = []
        for i in self.contours:
            z = self.segFlatten(i)
            total.append(z)
        return total 
    
    def getYolo(self):
        total = self.getCOCO() # 끊긴 obj에 대해 이중리스트 
        if len(total) > 1:
            if len(total) > 2:
                logging.info(f"Occurrence of 3 equal parts of objects {self.imgName}")
            s1 = self.mergeMultiSeg(total)
            s1 = (np.concatenate(s1,axis=0)/np.array([self.w,self.h])).reshape(-1).tolist()
            return s1
        else:
            return (np.array(total).reshape(-1,2)/np.array([self.w,self.h])).reshape(-1).tolist()
        
    def min_index(self,arr1, arr2):
        dis = ((arr1[:, None, :] - arr2[None, :, :]) ** 2).sum(-1)
        #print(dis)
        return np.unravel_index(np.argmin(dis, axis=None), dis.shape)
    
    def mergeMultiSeg(self,segments):
        s = []
        segments = [np.array(i).reshape(-1, 2) for i in segments]
        idx_list = [[] for _ in range(len(segments))]

        # record the indexes with min distance between each segment
        for i in range(1, len(segments)):
            idx1, idx2 = self.min_index(segments[i - 1], segments[i])
            idx_list[i - 1].append(idx1)
            idx_list[i].append(idx2)

        # use two round to connect all the segments
        for k in range(2):
            # forward connection
            if k == 0:
                for i, idx in enumerate(idx_list):
                    # middle segments have two indexes
                    # reverse the index of middle segments
                    if len(idx) == 2 and idx[0] > idx[1]:
                        idx = idx[::-1]
                        segments[i] = segments[i][::-1, :]

                    segments[i] = np.roll(segments[i], -idx[0], axis=0)
                    segments[i] = np.concatenate([segments[i], segments[i][:1]])
                    # deal with the first segment and the last one
                    if i in [0, len(idx_list) - 1]:
                        s.append(segments[i])
                    else:
                        idx = [0, idx[1] - idx[0]]
                        s.append(segments[i][idx[0] : idx[1] + 1])

            else:
                for i in range(len(idx_list) - 1, -1, -1):
                    if i not in [0, len(idx_list) - 1]:
                        idx = idx_list[i]
                        nidx = abs(idx[1] - idx[0])
                        s.append(segments[i][nidx:])
        return s

class Keypoint3D:
    def __init__(self,kp3d) -> None:
        self.kp3d = kp3d

    def getCOCO(self):
        return self.kp3d

class box3DPX:
    def __init__(self,box3DPX) -> None:
        self.box3DPX = box3DPX
    
    def getCOCO(self):
        return self.box3DPX

class RotationBoundingBox:
    # sim2real - rbox2d [degree,x_centor,y_centor,w,h]
    def __init__(self,Rbox:List)->List:
        self.degree,self.x_centor,self.y_centor,self.x,self.y  = Rbox 

    def getCOCO(self):
        return [self.degree,self.x_centor,self.y_centor,self.x,self.y]



