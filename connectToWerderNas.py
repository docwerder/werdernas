import sys
import os
import signal
from PySide2.QtGui import QPixmap
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget, QPushButton, QLabel, QMessageBox, QFrame, QHBoxLayout

# Important: the next two lines have to be imported after the Pyside2 imports.
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # noqa: F401
import matplotlib.pyplot as plt  # noqa: F401
from qt_material import apply_stylesheet
from multiprocessing import active_children
os.environ['QT_MAC_WANTS_LAYER'] = '1'

def show_dialog_werderNAS(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Connection to WERDERNAS successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

def show_dialog_werderNAS2(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Connection to WERDERNAS2 successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

def show_dialog_werderNASX(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Connection to WERDERNASX successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

def show_dialog_werderNAS2X(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Connection to WERDERNASX successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

def show_window_unmount_werderNAS(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Unmounting to WERDERNAS successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

def show_window_unmount_werderNAS2(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Unmounting to WERDERNAS2 successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

def show_window_unmount_werderNASX(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Unmounting to WERDERNASX successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

def show_window_unmount_werderNAS2X(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Unmounting to WERDERNAS2X successfull!")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

extra = {
    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#17a2b8',
    'mycolor1': '#ffd22b',

    # Font
    # 'font': 'Times',
    'font_size': '12px',
    'line_height': '13px',
    'font_family': 'Roboto',
    # Density scale
    'density_scale': '0',

    # environ:
    'pyside2_dev': True,
    'linux': True,
}


# seaborn has to be imported after the matplotlib modules


# Module import
# Scanning directories
# from emat_mfl_combined.applications.pdw_upload.pdw.pdw_manual_edition \
    # import scan_directories_manually as window_scan_directories

# Feature overview
# from emat_mfl_combined.applications.pdw_upload.pdw.pdw_manual_edition \
    # import feature_overview_manually as window_feature_overview

# Feature upload
# from emat_mfl_combined.applications.pdw_upload.pdw.pdw_manual_edition \
    # import feature_upload_manually as window_feature_upload

# Ongoing code!
# Feature signals
# from emat_mfl_combined.applications.pdw_upload.pdw.pdw_manual_edition \
    # import my_show_feature_signals_manually as window_feature_signals


# import seaborn as sns
# import pandas as pd

sys.path.append(r'/Users/joerg/repos/development')
# from utilities_functions.mnt_functions import mnt_WERDERNAS
from utilities_functions.mountClasses import mountToWerderNas
from utilities_functions.mountClasses import mountToWerderNas2
from utilities_functions.mountClasses import mountToWerderNasx
from utilities_functions.mountClasses import mountToWerderNas2x

from utilities_functions.mountClasses import unMountWerderNas
from utilities_functions.mountClasses import unMountWerderNas2
from utilities_functions.mountClasses import unMountWerderNasx
from utilities_functions.mountClasses import unMountWerderNas2x

# from utilities_functions.mnt_functions import mnt_WERDERNAS2
# from utilities_functions.mnt_functions import mnt_WERDERNASX
# from utilities_functions.mnt_functions import mnt_WERDERNAS2X

from utilities_functions.mnt_functions import CustomDialog

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class Main_WERDERNAS(QMainWindow):
    def __init__(self, x_pos_main_gui, y_pos_main_gui, width_main_gui, height_main_gui, parent=None):
        super(Main_WERDERNAS, self).__init__(parent)

        self.setWindowTitle('WERDERNAS GUI V0.5')
        self.x_pos_main_gui = x_pos_main_gui
        self.y_pos_main_gui = y_pos_main_gui
        self.width_main_gui = width_main_gui
        self.height_main_gui = height_main_gui

        # For control
        # print('x_pos_main_pdw_gui_init: ', self.x_pos_main_pdw_gui)
        # print('y_pos_main_pdw_gui_init: ', self.y_pos_main_pdw_gui)

        self.move(self.x_pos_main_gui, self.y_pos_main_gui)
        # print('width: ', self.width_main_gui)
        # print('height: ', self.height_main_gui)

        # Define the main layout with buttons
        # Define 'headline' consisting of header and logo ...
        lbl_werdernas = QLabel('WERDERNAS GUI 0.6 !')
        #lbl_werdernas.setProperty('class', '#ffd22b')
        lbl_werdernas.setStyleSheet("font-size: 16px;" "color: #ffd22b;")
        self.lbl_werder_logo = QLabel("Werder_logo")
        self.werder_pixmap = QPixmap("werder_logo.png")
        self.scaled_werder_logo = self.werder_pixmap.scaled(self.lbl_werder_logo.size() / 10, QtCore.Qt.KeepAspectRatio)
        self.lbl_werder_logo.setPixmap(self.scaled_werder_logo)
        self.lbl_werder_logo.setScaledContents(False)
        
        # Define Grid of pushbuttons... and their actions...
        self.btn_connect_to_WerderNas = QPushButton('Mount To WERDERNAS')
        # self.btn_connect_to_WerderNas.setProperty('class', '#ffd22b')
        self.btn_connect_to_WerderNas.clicked.connect(mountToWerderNas.execute_applescript_werdernas)
        mytext = "Connected to WERDERNAS successfull"
        print(mytext)
        self.btn_connect_to_WerderNas.clicked.connect(show_dialog_werderNAS)
        
        
        self.btn_unmount_WerderNas = QPushButton('Unmount WERDERNAS')
        self.btn_unmount_WerderNas.clicked.connect(unMountWerderNas.execute_applescript_unmount_werdernas)
        self.btn_unmount_WerderNas.clicked.connect(show_window_unmount_werderNAS)

        # self.btn_connect_to_werdernas.clicked.connect(mountToWerderNas2)
        # self.btn_connect_to_werdernas.clicked.connect(mountToWerderNas2x.execute_applescript_werdernas2x())
        #self.btn_connect_to_werdernas.clicked.connect(self.okButtonClicked)
        self.btn_connect_to_WerderNas2 = QPushButton('Mount To WERDERNAS2')
        self.btn_connect_to_WerderNas2.clicked.connect(mountToWerderNas2.execute_applescript_werdernas2)
        self.btn_connect_to_WerderNas2.clicked.connect(show_dialog_werderNAS2)
        self.btn_unmount_WerderNas2 = QPushButton('Unmount WERDERNAS2')
        self.btn_unmount_WerderNas2.clicked.connect(unMountWerderNas2.execute_applescript_unmount_werdernas2)
        self.btn_unmount_WerderNas2.clicked.connect(show_window_unmount_werderNAS2)

        # self.window_feature_overview = None
        # self.btn_connect_to_werdernas2.clicked.connect(mountToWerderNas2)

        self.btn_connect_to_WerderNasx = QPushButton('Mount To WERDERNASX')
        self.btn_connect_to_WerderNasx.clicked.connect(mountToWerderNasx.
        execute_applescript_werdernasx)
        self.btn_connect_to_WerderNasx.clicked.connect(show_dialog_werderNASX)        
        self.btn_unmount_WerderNasx = QPushButton('Unmount WERDERNASX')
        self.btn_unmount_WerderNasx.clicked.connect(unMountWerderNasx.execute_applescript_unmount_werdernasx)
        self.btn_unmount_WerderNasx.clicked.connect(show_window_unmount_werderNASX)

        # self.window_feature_upload = None
        # self.btn_connect_to_werdernasx.clicked.connect(mountToWerderNasx)
        
        self.btn_connect_to_WerderNas2x = QPushButton('Mount To WERDERNAS2X')       
        self.btn_connect_to_WerderNas2x.clicked.connect(mountToWerderNas2x.execute_applescript_werdernas2x)
        self.btn_connect_to_WerderNas2x.clicked.connect(show_dialog_werderNAS2X)     
        self.btn_unmount_WerderNas2x = QPushButton('Unmount WERDERNAS2X')
        self.btn_unmount_WerderNas2x.clicked.connect(unMountWerderNas2x.execute_applescript_unmount_werdernas2x)
        self.btn_unmount_WerderNas2x.clicked.connect(show_window_unmount_werderNAS2X)

        self.window_show_feature_signals = None
        # Now: Define the Alignment of the buttons and labels via qgridlayout.
        # Define the layout-form, in which the widgets should be aligned...
        # and add the widgets
        # Define layout for horizontal line
        self.hor_line_1_layout = QHBoxLayout()
        # self.hor_line_1_layout.addWidget(QHLine())

        layout = QGridLayout()
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        # self.frame.setFrameShape(QFrame.VLine)
        self.frame.setFrameShadow(QFrame.Sunken)
        layout.addWidget(lbl_werdernas, 0, 0)
        layout.addWidget(self.lbl_werder_logo, 0, 1, alignment=Qt.AlignRight)

        layout.addWidget(self.btn_connect_to_WerderNas, 1, 0)
        layout.addWidget(self.btn_unmount_WerderNas, 2, 0)

        layout.addWidget(self.btn_connect_to_WerderNas2, 1, 1)
        layout.addWidget(self.btn_unmount_WerderNas2, 2, 1)
        
        layout.addWidget(QHLine(), 3, 0, 1, 2)
        
        layout.addWidget(self.btn_connect_to_WerderNasx, 4, 0)
        layout.addWidget(self.btn_unmount_WerderNasx, 5, 0)

        layout.addWidget(self.btn_connect_to_WerderNas2x, 4, 1)
        layout.addWidget(self.btn_unmount_WerderNas2x, 5, 1)
        
        layout.addWidget(QHLine(), 3, 0, 1, 2)
        
        # layout.addWidget(self.btn_unmount_WerderNas2x, 4, 0)
        # layout.setRowStretch(1, 2)
        
        # layout.addWidget(self.frame, 2, 0)

        # Define the scretching of the rows...
        # Dont how exactly how it works...
        # layout.setRowStretch(0, 10)
        # layout.setRowStretch(1, 6)
        # layout.setRowStretch(2, 6)

        # Showing all the widgets via the "logic" of the qwidget
        dummy_widget = QWidget()
        dummy_widget.setLayout(layout)
        self.setCentralWidget(dummy_widget)

        # Dont know, how this value is about 639?
        # width_dw = dummy_widget.frameGeometry().width()
        # print('width_dw ', width_dw)

    # Define the functions, which should be executed, when the buttons are clicked


    # def show_scanning_dirs_window(self):
    #     if self.scanning_dirs_window is None:
    #         self.scanning_dirs_window = window_scan_directories.WindowScanDir(
    #             self.x(), self.y() + self.height() + 30, self.width()
    #         )
    #         self.scanning_dirs_window.show()
    #     else:
    #         self.scanning_dirs_window = None
    #     # self.scanning_window = scanning_window.WindowScanDir()
    #     # self.scanning_window.show()



    # def show_dialog(self):
    #     print("Debug 1")
    #     msgBox = QMessageBox()
    #     print("Debug 2")
    #     msgBox.setIcon(QMessageBox.Information)
    #     print("Debug 3")
    #     # msgBox.setText(str_val)
    #     msgBox.setWindowTitle("Information")
    #     print("Debug 4")
    #     msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    #     print("Debug 5")

    # def show_feature_overview(self):
    #     if self.window_feature_overview is None:
    #         self.window_feature_overview = window_feature_overview.WindowShowFeatureOverview(
    #             self.x(), self.y(), self.width()
    #         )
    #         self.window_feature_overview.show()
    #     else:
    #         self.window_feature_overview = None

    # def show_feature_upload(self):
    #     if self.window_feature_upload is None:
    #         self.window_feature_upload = window_feature_upload.WindowFeatureUpload(
    #             self.x(), self.y(), self.width()
    #         )
    #         self.window_feature_upload.show()
    #     else:
    #         self.window_feature_upload = None

    # def show_feature_signals(self):
    #     if self.window_show_feature_signals is None:
    #         self.window_show_feature_signals = window_feature_signals.WindowShowFeatureSignals(
    #             150, 150, 100
    #         )
    #         self.window_show_feature_signals.show()
    #     else:
    #         self.window_show_feature_signals = None

#/Users/joerg/repos/werdernas/connectToWerderNas_2try.py
#kill $(pgrep -f 'python /Users/joerg/repos/werdernas/connectToWerderNas_2try.py')


# if __name__ == '__main__':
# script_name = '/Users/joerg/repos/werdernas/connectToWerderNas_2try.py'
# try:
        
#     # iterating through each instance of the process
#     for line in os.popen("ps ax | grep " + script_name + " | grep -v grep"):
#         fields = line.split()
            
#         # extracting Process ID from the output
#         pid = fields[0]
            
#         # terminating process
#         # os.kill(int(pid), signal.SIGKILL)
#         print("Process Successfully terminated")
        
# except:
#     print("Error Encountered while running script")
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_amber.xml', extra=extra)
    window = Main_WERDERNAS(200, 150, 250, 150)

    # For example: Get the width of the window, BUT its problematic...
    # width_main_window = window.width()
    # print('width_mw: ', width_main_window)

    window.show()

    sys.exit(app.exec_())
