import sys
import time 
import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QBasicTimer, QTimerEvent
from utils.setting import ConvertType
from utils.general import setCheckDataPathDir, setCheckDataReferFile
from pathlib import Path

import logging

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
        self.initUI()
    
    def time_logger(func):
        def wrapper(self):
            start = time.time()
            func(self) 
            end = time.time()
            logging.info(f'Time spent processing : {end - start: .3f} sec')
        return wrapper
    
    def initUI(self):
        """
        UI 설정 
        """
        self.statusBar().showMessage("Setting")# 아래 하단 상태 바 
        self.setWindowIcon(QIcon("./image/Fill_color.png"))
        self.setWindowTitle("Sim2Real")
        widget = QWidget()

        # 기능 별 Group
        format_group = QGroupBox("Data Format")
        anno_group = QGroupBox("Annotation Type")
        opt_group = QGroupBox("Option") # 임시 
        path_group = QGroupBox("Path") # path 관련 
        btn_group = QGroupBox() # 실행 버튼 
        progress_group = QGroupBox()
        log_group = QGroupBox("Log")

        # Format Group UI 내부 설정좌상단 
        format_innerLayout = QVBoxLayout()
        self.format_coco = QRadioButton("COCO")
        self.format_yolo = QRadioButton("YOLO")
        format_innerLayout.addWidget(self.format_coco)
        format_innerLayout.addWidget(self.format_yolo)
        self.format_coco.setChecked(True) # 초기 선택이 되어 있는 CheckBox

        format_group.setLayout(format_innerLayout)
        format_layout = QVBoxLayout()
        format_layout.addWidget(format_group)

        # annotation Type Group UI 내부 설정
        annotation_innerLayout = QVBoxLayout()
        self.Bbox = QCheckBox("Bounding box")
        self.Segmentation = QCheckBox("Segmentation")
        self.Key2d = QCheckBox("Keypoint 2D")
        self.Key3d = QCheckBox("Keypoint 3D")
        self.Rbox = QCheckBox("Roatation Bounding Box")
        self.Box3dpx = QCheckBox("box3DPX")
        annotation_innerLayout.addWidget(self.Bbox)
        annotation_innerLayout.addWidget(self.Segmentation)
        annotation_innerLayout.addWidget(self.Key2d)
        annotation_innerLayout.addWidget(self.Key3d)
        annotation_innerLayout.addWidget(self.Rbox)
        annotation_innerLayout.addWidget(self.Box3dpx)
        
        anno_group.setLayout(annotation_innerLayout)
        anno_layout = QVBoxLayout()
        anno_layout.addWidget(anno_group)
        
        # Option Group UI 내부 설정 
        option_innerLayout = QVBoxLayout()
        self.imageCopy = QCheckBox("Copy Image")


        # 
        datapath_msg = QLabel("Data Path : ")
        self.datapath = QTextEdit("./data/sim2real/",self)
        self.datapath.setFixedHeight(50)  # 높이 조절
        self.datapath.setFixedWidth(250)  # 너비 조절
        label_dict_msg = QLabel("Label Dict(Yaml Path) : ")
        self.lable_dict_path = QTextEdit("./config/sim2real.yaml",self)
        self.lable_dict_path.setFixedHeight(50)  # 높이 조절
        self.lable_dict_path.setFixedWidth(250)  # 너비 조절

        path_innerlayout = QHBoxLayout()
        path_innerlayout.addWidget(datapath_msg)
        path_innerlayout.addWidget(self.datapath)
        path_innerlayout.addWidget(label_dict_msg)
        path_innerlayout.addWidget(self.lable_dict_path)

        path_group.setLayout(path_innerlayout)
        path_layout = QHBoxLayout()
        path_layout.addWidget(path_group)

        #btn 
        ConvertBtn = QPushButton("&Data Format Convert",self)
        dataconfirm_btn = QPushButton("&Data Confirm",self)
        graph_btn = QPushButton("&Graph",self)
        analysis_btn = QPushButton("&Analysis",self)

        btn_innerlayout = QHBoxLayout()
        btn_innerlayout.addWidget(ConvertBtn)
        btn_innerlayout.addWidget(dataconfirm_btn)
        btn_innerlayout.addWidget(graph_btn)
        btn_innerlayout.addWidget(analysis_btn)

        btn_group.setLayout(btn_innerlayout)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_group)


        # progressbar 
        self.pgsbar = QProgressBar(self)
        self.timer = QBasicTimer()
        self.step = 0
        pgs_innerlayout = QHBoxLayout()
        pgs_innerlayout.addWidget(self.pgsbar)
        progress_group.setLayout(pgs_innerlayout)
        pgs_layout = QHBoxLayout()
        pgs_layout.addWidget(progress_group)

        # logger 
        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

        log_innerlayout = QVBoxLayout()
        log_innerlayout.addWidget(logTextBox.widget)
        log_group.setLayout(log_innerlayout)
        log_layout = QHBoxLayout()
        log_layout.addWidget(log_group)

        # Widget Batch 
        TopGroup = QHBoxLayout()
        TopGroup.addLayout(format_layout)
        TopGroup.addLayout(anno_layout)
        TopGroup.addLayout()

        BottomGroup = QVBoxLayout()
        BottomGroup.addLayout(path_layout)
        self.setCentralWidget(widget)

        ConvertBtn.clicked.connect(self.Convert_button)
        #dataconfirm_btn.clicked.connect(self.Confrim_button)
        #graph_btn.clicked.connect(self.graph_function)
        #analysis_btn.clicked.connect(self.analysis_function)

    def Convert_button(self):
        logging.info("Clicked 'Data Format Convert' Button")
        # progress bar setting
        self.pgsbar.setValue(0)
        self.pgsbar.setValue(100)
        # path 값 가져오기 
        dataPath = self.datapath.toPlainText()
        referPath = self.lable_dict_path.toPlainText()

        self.statusBar().showMessage("File Checking..")
        self.format = self.formatRadiobuttonCheck()

        _dataDir = setCheckDataPathDir(dataPath)
        _referinfo = setCheckDataReferFile(referPath)

        print(_dataDir)
    
    def doAction(self,percent):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(percent,self)

    def formatRadiobuttonCheck(self):
        if self.format_coco.isChecked():
            form = ConvertType.COCO
        elif self.format_yolo.isChecked():
            form = ConvertType.YOLO
        # elif self.format_voc.isChecked():
        #     form = ConvertType.VOC
        return form 


if __name__ == "__main__":
    app =QApplication(sys.argv)
    myWindow = MyApp()
    myWindow.show()
    app.exec_()
