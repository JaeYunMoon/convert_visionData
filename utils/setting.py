from enum import Enum

class ConvertType(Enum):
    COCO = 1 
    YOLO = 2 
    VOC = 3 

def disable_Button(cbutton,vbutton):
    if not cbutton.isChecked(): # if 문과 elif 문 반대로는 안됨..
        vbutton.setEnabled(False)
    elif cbutton.isChecked():
        vbutton.setEnabled(True)


