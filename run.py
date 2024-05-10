import sys
import time 
import os
import logging

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QBasicTimer, QTimerEvent
from collections import defaultdict
from pathlib import Path

from utils.setting import ConvertType, disable_Button #, Checking_button
from utils.general import setCheckDataPathDir, setCheckDataReferFile
from utils.datasetting import getDatas 
from utils.convert import CovertSaveDataset

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    예외가 발생했을 때 호출되는 콜백 함수.
    """
    error_info = f"에러 발생: {exc_type.__name__}\n\n{exc_value}"
    logging.error("에러 발생!")
    logging.error(error_info)
    # 여기에 예외 처리 코드 추가
    logging.error(exc_type, exc_value)

# 예외 처리를 위한 예외 후크 설정

sys.excepthook = handle_exception

class QTextEditLogger(logging.Handler):
    """
    logging api에서의 정보를 Qt로 가져와서 연결 시키기 위한 클래스 
    """
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class MyApp(QMainWindow,QPlainTextEdit):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.BaseUI()

    def timeLogger(func):
        def wrapper(self):
            start = time.time()
            func(self) 
            end = time.time()
            logging.info(f'Time spent processing : {end - start: .3f} sec')
        return wrapper

    def BaseUI(self):
        self.statusBar().showMessage("Setting")# 아래 하단 상태 바 
        self.setWindowIcon(QIcon("./refer/Fill_color.png"))
        self.setWindowTitle("Sim2Real")
        widget = QWidget()
        
        TopGroup = QHBoxLayout()
        TopGroup.addWidget(self.FormatLayout())
        TopGroup.addWidget(self.AnnotationLayout())
        TopGroup.addWidget(self.OptionLayout())

        BottomGruop = QVBoxLayout()
        BottomGruop.addWidget(self.PathSetting())
        BottomGruop.addWidget(self.ButtonSetting())
        BottomGruop.addWidget(self.ProgressBarSetting())
        BottomGruop.addWidget(self.LoggerSetting())

        
        TotalGroup = QVBoxLayout(widget)
        TotalGroup.addLayout(TopGroup)
        TotalGroup.addLayout(BottomGruop)

        self.setCentralWidget(widget)        
        self.ConvertBtn.clicked.connect(self.Convert_button)
        #dataconfirm_btn.clicked.connect(self.Confrim_button)
        #graph_btn.clicked.connect(self.graph_function)
        #analysis_btn.clicked.connect(self.analysis_function)


    def FormatLayout(self):
        formatGroup = QGroupBox("DataFormat")
                # Format Group UI 내부 설정좌상단 
        format_innerLayout = QVBoxLayout()
        self.format_coco = QRadioButton("COCO")
        self.format_yolo = QRadioButton("YOLO")
        format_innerLayout.addWidget(self.format_coco)
        format_innerLayout.addWidget(self.format_yolo)
        self.format_coco.setChecked(True) # 초기 선택이 되어 있는 CheckBox
        formatGroup.setLayout(format_innerLayout)

        return formatGroup
    
    def AnnotationLayout(self): #Format에 맞춰 활성화 비활성화 시키는 코드 작성 예정 
        annoGroup = QGroupBox("Annotation Type")
        anno_innerLayout = QVBoxLayout()
        self.Bbox = QCheckBox("Bounding Box")
        self.Segmentation = QCheckBox("Segmentation")
        self.Key2d = QCheckBox("Keypoint 2D")
        self.Key3d = QCheckBox("Keypoint 3D")
        self.Rbox = QCheckBox("Roatation Bounding Box")
        self.Box3dpx = QCheckBox("box3DPX")
        anno_innerLayout.addWidget(self.Bbox)
        anno_innerLayout.addWidget(self.Segmentation)
        anno_innerLayout.addWidget(self.Key2d)
        anno_innerLayout.addWidget(self.Key3d)
        anno_innerLayout.addWidget(self.Rbox)
        anno_innerLayout.addWidget(self.Box3dpx)
        annoGroup.setLayout(anno_innerLayout)

        return annoGroup
    
    def OptionLayout(self):
        optionGroup = QGroupBox("Option")
        option_innerLayout= QVBoxLayout()
        self.imageCopy = QCheckBox("Copy Image")
        self.RandomConfirmImage = QCheckBox("Random Images Check Annotation")
        self.DatasaveOption = QCheckBox("Save Path")

        self.RandomImageCount = QSpinBox(self)
        self.RandomImageCount.setMaximum(1000)
        self.RandomImageCount.setMinimum(0)
        self.RandomImageCount.setSingleStep(1)
        self.RandomImageCount.setFixedWidth(250)
        self.RandomImageCount.setFixedHeight(30)
        self.RandomImageCount.setEnabled(False)
        self.RandomConfirmImage.stateChanged.connect(lambda:disable_Button(self.RandomConfirmImage,self.RandomImageCount))

        self.DatasaveOptionPath = QTextEdit("./result",self)
        self.DatasaveOptionPath.setFixedHeight(30)
        self.DatasaveOptionPath.setFixedWidth(250)
        self.DatasaveOptionPath.setEnabled(False)
        self.DatasaveOption.stateChanged.connect(lambda:disable_Button(self.DatasaveOption,self.DatasaveOptionPath))
        
        
        option_innerLayout.addWidget(self.imageCopy)
        option_innerLayout.addWidget(self.RandomConfirmImage)
        option_innerLayout.addWidget(self.RandomImageCount)
        option_innerLayout.addWidget(self.DatasaveOption)
        option_innerLayout.addWidget(self.DatasaveOptionPath)

        optionGroup.setLayout(option_innerLayout)

        return optionGroup

    def PathSetting(self):
        pathGroup = QGroupBox("Path Setting")
        datapath_msg = QLabel("Data Path : ")
        self.datapath = QTextEdit("./data/",self)
        self.datapath.setFixedHeight(30)  # 높이 조절
        self.datapath.setFixedWidth(250)  # 너비 조절
        label_dict_msg = QLabel("Label Dict(Yaml Path) : ")
        self.lable_dict_path = QTextEdit("./data/sim2real.yaml",self)
        self.lable_dict_path.setFixedHeight(30)  # 높이 조절
        self.lable_dict_path.setFixedWidth(250)  # 너비 조절

        path_innerlayout = QHBoxLayout()
        path_innerlayout.addWidget(datapath_msg)
        path_innerlayout.addWidget(self.datapath)
        path_innerlayout.addWidget(label_dict_msg)
        path_innerlayout.addWidget(self.lable_dict_path)

        pathGroup.setLayout(path_innerlayout)
        
        return pathGroup
    
    def ButtonSetting(self):
        btnGroup = QGroupBox("Button")
        self.ConvertBtn = QPushButton("&Data Format Convert",self)
        self.dataconfirm_btn = QPushButton("&Data Confirm",self)
        self.graph_btn = QPushButton("&Graph",self)
        self.analysis_btn = QPushButton("&Analysis",self)

        btn_innerlayout = QHBoxLayout()
        btn_innerlayout.addWidget(self.ConvertBtn)
        btn_innerlayout.addWidget(self.dataconfirm_btn)
        btn_innerlayout.addWidget(self.graph_btn)
        btn_innerlayout.addWidget(self.analysis_btn)

        btnGroup.setLayout(btn_innerlayout)

        return btnGroup
    
    def ProgressBarSetting(self):
        progressGroup = QGroupBox("Progress Bar")
        self.pgsbar = QProgressBar(self)
        self.timer = QBasicTimer()
        self.step = 0
        pgs_innerlayout = QHBoxLayout()
        pgs_innerlayout.addWidget(self.pgsbar)
        progressGroup.setLayout(pgs_innerlayout)

        return progressGroup
    
    def LoggerSetting(self):
        LogGroup = QGroupBox("Log")
        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

        log_innerlayout = QVBoxLayout()
        log_innerlayout.addWidget(logTextBox.widget)
        LogGroup.setLayout(log_innerlayout)

        return LogGroup
    
    def Convert_button(self):
        logging.info("Clicked 'Data Format Convert' Button")
        # progress bar setting
        self.pgsbar.setValue(0)
        self.pgsbar.setValue(100)
        # path 값 가져오기 
        dataPath = self.datapath.toPlainText()
        referPath = self.lable_dict_path.toPlainText()

        self.statusBar().showMessage("File Checking..")
        # self.format = self.formatRadiobuttonCheck()

        _dataDir = setCheckDataPathDir(dataPath)
        _referinfo = setCheckDataReferFile(referPath)
        formatType = self.checkingFormat()
        AnnoDict = self.checkingAnnotation()

        if self.DatasaveOption.isChecked():
            saveRoot = self.DatasaveOptionPath.toPlainText()
        else:
            saveRoot = _dataDir.DataPath

        AllDataset =getDatas(_dataDir.getLabelList(),_referinfo,formatType)
        csd = CovertSaveDataset(AllDataset,
                                saveRoot,
                                AnnoDict,
                                formatType)

        # print(_dataDir.getimgList())
        # print(_dataDir.getLabelList())
        # print(_referinfo.getDataReferInfo())
        # print(formatType)
        # print(AnnoDict)


    def checkingFormat(self):
        if self.format_coco.isChecked():
            return ConvertType.COCO
        elif self.format_yolo.isChecked():
            return ConvertType.YOLO
        
    def checkingAnnotation(self):
        annotationDict = defaultdict(int)
        if self.Bbox.isChecked():
            annotationDict["Bbox"] = 1
        if self.Rbox.isChecked():
            annotationDict["RBox"] = 1 
        if self.Segmentation.isChecked():
            annotationDict["Segmentation"] = 1
        if self.Key2d.isChecked():
            annotationDict["Keypoint2D"] = 1 
        if self.Key3d.isChecked():
            annotationDict["Keypoint3D"] = 1 
        if self.Box3dpx.isChecked():
            annotationDict["box3DPX"] = 1 
    
        return annotationDict
    
if __name__ == "__main__":
    app =QApplication(sys.argv)
    myWindow = MyApp()
    myWindow.show()
    app.exec_()
