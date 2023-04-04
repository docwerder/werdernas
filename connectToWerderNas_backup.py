import numpy as np
import sys
import os
import pandas as pd
from typing import Optional, Dict, List
import pathlib
import time
# import xarray as xr
import json
from tabulate import tabulate


os.environ['QT_MAC_WANTS_LAYER'] = '1'

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
#print(CURR_DIR)
sys.path.append(CURR_DIR)
sys.path.append('/Users/joerg/repos/development/')
for path in sys.path:
    print(path)
from utilities_functions.load_and_normalize_df import load_and_normalize_df

from utilities_functions.path2proj import Path2ProjAnomaliesGeneral


from PySide2.QtCore import QThread
from PySide2.QtCore import Signal as pyqtSignal
# import progressbar_QThread

from PySide2 import QtCore
from PySide2.QtGui import QPixmap

from PySide2.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout,
    QComboBox, QPlainTextEdit, QProgressBar, QPushButton, QCheckBox, QFrame, QScrollArea,
    QWidget, QMainWindow, QLineEdit, QLabel, QFileDialog, QMessageBox
)
from qt_material import apply_stylesheet

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


# class MyThread(QThread):

    # update_process = pyqtSignal(str)
    thread_finished = pyqtSignal(str)
    thread_finished_window = pyqtSignal(str)
    thread_plain_text = pyqtSignal(str)
    thread_change_upload_value = pyqtSignal(int)
    thread_complete_finished = pyqtSignal()

    def __init__(self, pdw, chosen_anom_types, counts_anom_types, path_project_anomalies_dir):

        super().__init__()
        self.pdw = pdw

        self.chosen_anom_types = chosen_anom_types

        self.path_project_anomalies_dir = path_project_anomalies_dir

        self.counts_anom_types = counts_anom_types

        self.ctn_total = sum(self.counts_anom_types[self.chosen_anom_types])

    def run(self) -> None:
        start_time = time.time()
        ctn_all = 0
        self.thread_change_upload_value.emit(ctn_all)
        # print('self.chosen_anom_types -> error!!: ', self.chosen_anom_types)

        for lf in self.chosen_anom_types:
            self.path_to_anomaly_dir = os.path.join(self.path_project_anomalies_dir, lf)

            self.nc_files_in_anomaly_dir = [x for x in os.listdir(self.path_to_anomaly_dir)]
            print('overall_numbers of nc-files in dir...', len(self.nc_files_in_anomaly_dir))
            written_anomalies_text = '== Writing anomaly ' + str(lf)

            self.thread_plain_text.emit(written_anomalies_text)
            # self.output_terminal_text.appendPlainText(written_anomalies_text)

            for nc_files, lf2 in zip(self.nc_files_in_anomaly_dir, range(len(self.nc_files_in_anomaly_dir))):
                self.path_to_nc_file = os.path.join(self.path_to_anomaly_dir, nc_files)

                p = Path2ProjAnomaliesGeneral(self.path_to_nc_file)
                datacube_list_complete = ['angle_pth_offset_corrected', 'rldist_pth_offset_corrected',
                                          'logdistance_pth_offset_corrected', 'logtime', 'logdistance', 'angle_ephh',
                                          'rldist_ephh',
                                          'logdistance_ephh', 'pth_offset_corrected', 'echof', 'echot', 'tranf', 'ephh']
                if p.has_project_info:
                    region_number = p.region_number
                    project_number = p.project_number
                    lineshot_name = p.lineshort_name
                else:
                    region_number = 'proj0'
                    project_number = '12542'
                    lineshot_name = '30305306'

                label_anomaly_dir = 'anomalies'
                print('self.path_to_nc_file: ', self.path_to_nc_file)
                data_single_xarray = xr.open_dataset(self.path_to_nc_file)
                self.single_xarray = self.path_to_nc_file.split("\\")[-1]
                single_feature = self.single_xarray.split('.nc')[0]
                single_anomaly = self.path_to_nc_file.split("\\")[-2]
                self.text_to_emit = single_feature + '  [' + str(lf2 + 1) + ' of ' + \
                    str(len(self.nc_files_in_anomaly_dir)) + ']'
                self.thread_plain_text.emit(self.text_to_emit)
                # self.thread_plain_text.emit(single_feature)

                level_single_feature = '.'.join([pdw_root_level, region_number, project_number,
                                                 lineshot_name, label_anomaly_dir, single_anomaly,
                                                 single_feature])

                level_anomaly_dir = '.'.join([pdw_root_level, region_number, project_number,
                                              lineshot_name, label_anomaly_dir])

                for single_datacube in datacube_list_complete:
                    feature_single_datacube = single_feature + '_' + single_datacube
                    if single_datacube.upper() in data_single_xarray:

                        if not (self.pdw.datacubes.exists(level_single_feature, feature_single_datacube)):

                            real_data_array = data_single_xarray[single_datacube.upper()].data
                            try:
                                self.pdw.datacubes.save(level_single_feature, feature_single_datacube, real_data_array)
                            except self.pdw.errors.DataCubeError:
                                print('DatacubeError....')
                            except ValueError:
                                print('ValueError....')

                # Following data values are INDEPENDENT from the single_feature value and therefore they will be stored
                # at the anomaly-level from the line!
                # Start of writing the data_vars of z-axis and echot-x-axis into pdw!
                # Remember: Storing will be at the anomaly-level of the line, NOT at the single_feature-level!

                for coordinates, coords_data in data_single_xarray.coords.items():
                    if (coordinates.lower() == 'z_axis') | (coordinates.lower() == 'z_axis_echot'):
                        try:
                            self.pdw.datacubes.save(level_anomaly_dir, lineshot_name + '_' + coordinates.lower(),
                                                    coords_data.data)
                        except self.pdw.errors.DataCubeError:
                            print('DatacubeError....')
                        except ValueError:
                            print('ValueError....')

                # writing attributes to pdw
                error_ctn = 0
                for attr_value in data_single_xarray.attrs.keys():
                    level_single_feature = '.'.join([pdw_root_level, region_number, project_number,
                                                     lineshot_name, label_anomaly_dir, single_anomaly, single_feature])
                    single_value = data_single_xarray.attrs[attr_value]
                    if type(single_value) == np.int32 or type(single_value) == np.int64:
                        single_value = int(single_value)

                    if isinstance(single_value, str):
                        try:
                            new_value = json.loads(single_value)
                            if isinstance(new_value, dict) or isinstance(new_value, list):
                                # print(attr_value, new_value, type(new_value))
                                single_value = new_value
                        except ValueError:
                            if len(single_value) > 0 and single_value.startswith("{"):
                                # print('Value error: ', attr_value, single_value, type(single_value))
                                error_ctn += 1
                                # print('ctn: ', error_ctn)

                    try:
                        self.pdw.levels.update_props(level_single_feature, {attr_value: single_value})
                    except DataCubeError:
                        print('DatacubeError....')
                    except ValueError:
                        print('ValueError....')

                ctn_all += 1
                self.thread_change_upload_value.emit(ctn_all * 100 / self.ctn_total)
                print('Transferred value to progressbar: ', ctn_all * 100 / self.ctn_total)

        end_time = round(time.time() - start_time, 2)
        #
        value_ctn_all = ctn_all
        time_per_nc_file = round(end_time / value_ctn_all, 2)
        text_value_summary = 'Total number of nc-files: ' + str(value_ctn_all) + '\n' + \
                             'total time: ' + str(end_time) + ' s.' + '\n' \
                             'Time for upload: ' + str(time_per_nc_file) + ' s per nc_file'

        self.thread_finished.emit(text_value_summary)

        finished_text = "Features have been uploaded \n" + text_value_summary
        self.thread_finished_window.emit(finished_text)

        self.thread_complete_finished.emit()


class WindowFeatureUpload(QMainWindow):
    def __init__(self, x_pos_parent_window, y_pos_parent_window, width_parent_window):
        super().__init__()
        dummy_widget = QWidget()
        self.x_pos_parent_window = x_pos_parent_window
        self.y_pos_parent_window = y_pos_parent_window
        self.width_parent_window = width_parent_window

        print('self.x_pos_parent_window: ', self.x_pos_parent_window)
        print('self.y_pos_parent_window: ', self.y_pos_parent_window)
        print('self.width_parent_window: ', self.width_parent_window)
        self.setFixedSize(1000, 700)
        # made by hand. 27.04.2022
        self.move(self.x_pos_parent_window + self.width_parent_window, self.y_pos_parent_window)
        # self.move(self.x_pos_parent_window + self.width_parent_window, self.y_pos_parent_window)

        # Following the value of feature_over_manually.ps!
        print('width of feature_upload_window: ', self.width())
        self.setWindowTitle("My Layout of feature upload manual edition! - ScrollArea1 inclusive ")

        # Define the necessary variables
        self.upload_step = 0
        self.button_clicked = 0
        self.region_number = None
        self.project_number = None
        self.lineshot_name = None
        self.label_anomaly_dir = None
        self.single_features_list = None
        self.patch_dir = None
        self.exchange_file = None
        self.filtered_exchange_file = None
        self.exchange_file_anom_type = None
        self.counts_anom_types = None
        self.current_nc_index = None
        self.current_filtered_index = None
        self.max_number_of_features = None
        self.exchange_file_anom_types = []
        self.text_string_csv_file = None
        self.path_anomaly_label = None
        self.path_project_anomalies_dir = None
        self.level_anomalies_label = None
        self.path_anomaly_label = None
        self.level_anomalies_label = None
        self.filtered_exchange_file = None
        self.max_number_of_features = None
        self.len_anomalies = None
        self.anomalies = None
        self.max_count_anomalies = None
        self.anomalies_list = None
        self.anomalies_list_immutable = []
        self.path_to_anomaly_dir = None
        self.nc_files_in_anomaly_dir = None
        self.checkbox_handler = None
        self.value_perc_s = None
        self.level_anomalies_label = None
        self.actual_server = None
        self.actual_nc_value = None
        self.anom_type_filter_frame = None
        self.thread = None

        # #############################################
        #  Define the layout
        # #############################################

        # Create the complete layout
        self.complete_layout = QVBoxLayout()

        # Layout for label and Rosen_logo
        self.label_pic_layout = QHBoxLayout()

        # Define label for header and Rosen_logo
        self.lbl_feature_overview = QLabel("Feature upload")
        self.lbl_feature_overview.setStyleSheet("font-size: 18px;" "color: rgb(44, 44, 126);")
        self.lbl_rosen_logo = QLabel("Rosen logo")
        # self.lbl_rosen_logo.setPixmap(QPixmap("rosen_logo.png"))
        self.pixmap = QPixmap("rosen_logo.png")
        scaled = self.pixmap.scaled(self.lbl_rosen_logo.size() / 4, QtCore.Qt.KeepAspectRatio)
        self.lbl_rosen_logo.setPixmap(scaled)
        self.lbl_rosen_logo.setScaledContents(False)

        # Fill the label_pic_layout
        self.label_pic_layout.addWidget(self.lbl_feature_overview)
        self.label_pic_layout.addStretch()
        self.label_pic_layout.addWidget(self.lbl_rosen_logo)

        # Define layout for horizontal line
        self.hor_line_1_layout = QHBoxLayout()
        self.hor_line_1_layout.addWidget(QHLine())

        # Define layout for PDW-server and chosing_box.
        self.pdw_server_layout = QHBoxLayout()
        # self.groups.setAlignment(Qt.AlignTop)
        self.pdw_server_layout.setAlignment(QtCore.Qt.AlignLeft)
        # Define label for pdw_server and drop-down box
        self.lbl_pdw_server = QLabel("PDW-Server: ")
        self.lbl_pdw_server.setStyleSheet("font-size: 14px;" "color: rgb(44, 44, 126);")

        self.chose_pdw_server = QComboBox()
        for cnts in ['http://pdw-lin.roseninspection.net/pdw-emat', 'http://pdw-lin.roseninspection.net/pdw-sandbox']:
            self.chose_pdw_server.addItem(cnts)

        # Fill the layout with the widgets
        # IMPORTANT! With stretch we can controll the ratio between the widgets in one layout!!
        self.pdw_server_layout.addWidget(self.lbl_pdw_server, stretch=1)
        self.pdw_server_layout.addWidget(self.chose_pdw_server, stretch=4)

        # Define layout for horizontal line
        self.hor_line_2_layout = QHBoxLayout()
        self.hor_line_2_layout.addWidget(QHLine())

        # Define layout for load_btn
        self.load_xarray_btn_layout = QHBoxLayout()

        # Define widgets
        self.btn_load_csv_file = QPushButton("Load csv-file...")
        self.lbl_anomalies_dir = QLineEdit("...")

        # Fill the layout with the widgets
        self.load_xarray_btn_layout.addWidget(self.btn_load_csv_file)
        self.load_xarray_btn_layout.addWidget(self.lbl_anomalies_dir)

        # Define layout for horizontal line
        self.hor_line_3_layout = QHBoxLayout()
        self.hor_line_3_layout.addWidget(QHLine())

        # Layout for buttons - now it's a QHbox.
        self.btn_layout = QHBoxLayout()

        # Define buttons..
        self.btn_show_anomalies_frame = QPushButton("Show anomalies of chosen line")
        self.btn_show_frame = QPushButton("Show QFrame")
        self.btn_2_dummy = QPushButton("Dummy button 2")

        # Fill the layout with the buttons...
        self.btn_layout.addWidget(self.btn_show_anomalies_frame)
        self.btn_layout.addWidget(self.btn_show_frame)
        self.btn_layout.addWidget(self.btn_2_dummy)

        # Define layout for horizontal line
        self.hor_line_4_layout = QHBoxLayout()
        self.hor_line_4_layout.addWidget(QHLine())

        # Define the label for chosen anomaly_dir:
        self.lbl_chosen_anomaly_dir_layout = QHBoxLayout()

        # Define the widgets within layout
        # lineshort_name = "30305306"
        self.lbl_chosen_anomaly_dir = QLabel("Available anomalies within the line: ")
        self.lbl_chosen_anomaly_dir.setStyleSheet("font-size: 16px;" "color: rgb(44, 44, 126);")
        # Fill the layout with the widget
        self.lbl_chosen_anomaly_dir_layout.addWidget(self.lbl_chosen_anomaly_dir)

        # Define layout for horizontal line
        self.hor_line_5_layout = QHBoxLayout()
        self.hor_line_5_layout.addWidget(QHLine())

        # NOW. New widget types: QFrame and QPlainTextEdit...
        # Trying to handle wth qsplitter.
        # Link: https://zetcode.com/gui/pysidetutorial/widgets2/
        # First: Define the layout
        # self.frame_splitter_layout = QHBoxLayout()
        #
        # self.frame_frame_output = QFrame()
        # self.frame_frame_output.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        #
        # self.frame_calculation_output = QFrame()
        # self.frame_calculation_output.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        #
        # self.frame_output_terminal = QFrame()
        # self.frame_output_terminal.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        # New version: ScrollArea and button_bar ,,

        self.layout_for_frame = QHBoxLayout()
        self.frame_dummy_left = QFrame()
        self.layout_for_frame.addWidget(self.frame_dummy_left)
        self.frame_dummy_left.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self.calculation_terminal = QPlainTextEdit()
        self.output_terminal = QPlainTextEdit()

        # Define layout and fill this three QPlainTextEdit-Widgets..
        # AND: Define the buttons for the evaluate, write and cancel-functions of the upload
        self.scrollarea_btn_layout = QVBoxLayout()
        self.btn_bar_layout = QHBoxLayout()
        self.evaluate_button = QPushButton("Evaulate...")
        self.write_button = QPushButton("Write...")
        self.cancel_button = QPushButton("Cancel...")

        # Fill the btt_bar_layout
        self.btn_bar_layout.addWidget(self.evaluate_button)
        self.btn_bar_layout.addWidget(self.write_button)
        self.btn_bar_layout.addWidget(self.cancel_button)

        self.frame_for_scrollarea = None
        self.scrolling_area = QScrollArea()
        self.scrolling_area.setWidgetResizable(True)

        self.layout_for_frame.addWidget(self.scrolling_area)

        self.scrollarea_btn_layout.addLayout(self.layout_for_frame)
        self.scrollarea_btn_layout.addLayout(self.btn_bar_layout)

        self.qplainedittext_layout = QHBoxLayout()

        self.qplainedittext_layout.addLayout(self.scrollarea_btn_layout, stretch=10)
        self.qplainedittext_layout.addWidget(self.calculation_terminal, stretch=8)
        self.qplainedittext_layout.addWidget(self.output_terminal, stretch=12)

        # Define layout for horizontal line
        self.hor_line_6_layout = QHBoxLayout()
        self.hor_line_6_layout.addWidget(QHLine())

        # Define the Upload summary labels.

        self.lbl_upload_layout = QHBoxLayout()

        # Define the labels.
        self.lbl_upload_summary = QLabel("Upload summary:")
        self.lbl_upload_summary.setStyleSheet("font-size: 16px;" "color: rgb(44, 44, 126);")
        self.lbl_upload_progress = QLabel("Upload progress:")
        self.lbl_upload_progress.setStyleSheet("font-size: 16px;" "color: rgb(44, 44, 126);")

        # Fill the layout
        self.lbl_upload_layout.addWidget(self.lbl_upload_summary, stretch=1)
        self.lbl_upload_layout.addWidget(self.lbl_upload_progress, stretch=1)

        # Define summary and progress status
        self.summary_and_progress_layout = QHBoxLayout()

        # Define the widgets
        self.upload_summary = QLabel('Detailed information about the upload...')
        self.upload_progress = QProgressBar()
        # self.upload_progress.setGeometry(30, 40, 200, 25)
        self.upload_progress.adjustSize()
        # self.upload_progress.setStyleSheet("QProgressBar::chunk {background-color: #2196F3; height: 30px; width: 20px; margin: 1.5px;}")
        # Fill the layout..
        self.summary_and_progress_layout.addWidget(self.upload_summary, stretch=1)
        self.summary_and_progress_layout.addWidget(self.upload_progress, stretch=1)

        # Fill the complete_layout
        self.complete_layout.addLayout(self.label_pic_layout)
        self.complete_layout.addLayout(self.hor_line_1_layout)
        self.complete_layout.addLayout(self.pdw_server_layout)
        self.complete_layout.addLayout(self.hor_line_2_layout)
        self.complete_layout.addLayout(self.load_xarray_btn_layout)
        self.complete_layout.addLayout(self.hor_line_3_layout)
        self.complete_layout.addLayout(self.btn_layout)
        self.complete_layout.addLayout(self.hor_line_4_layout)
        self.complete_layout.addLayout(self.lbl_chosen_anomaly_dir_layout)
        self.complete_layout.addLayout(self.hor_line_5_layout)
        self.complete_layout.addLayout(self.qplainedittext_layout)
        self.complete_layout.addLayout(self.hor_line_6_layout)
        self.complete_layout.addLayout(self.lbl_upload_layout)
        self.complete_layout.addLayout(self.summary_and_progress_layout)

        # Set the hand-made complete layout in a superordinate QWidget called dummy_widget
        # dummy_widget = QWidget()

        dummy_widget.setLayout(self.complete_layout)
        self.setCentralWidget(dummy_widget)

        # #############################################
        #  End of definition of the layout
        # #############################################

        ###############################################
        # Define the signals
        ###############################################

        self.chose_pdw_server.currentIndexChanged.connect(self.pdw_server_changed)
        self.btn_load_csv_file.clicked.connect(self.load_level_anomaly)
        # self.btn_show_frame.clicked.connect(self.show_frame)
        self.anom_type_filter_frame = None
        # self.btn_show_anomalies_frame.clicked.connect(self.show_anom_type_filter) #TODO: Rename btn_show...
        self.btn_show_anomalies_frame.clicked.connect(self.show_frame)

        ###############################################
        # Define the slots
        ###############################################

    def pdw_server_changed(self):
        self.actual_chosen_pdw_server = self.chose_pdw_server.currentText()
        print('self.actual_chosen_pdw_server: ', self.actual_chosen_pdw_server)

    def load_level_anomaly(self):

        self.patch_dir = QFileDialog.getExistingDirectory(
            parent=None,
            caption="Select single csv-file...",
            directory="",
        )

        if self.patch_dir == "":
            return
        print('patch_dir: ', self.patch_dir)

        self.exchange_file, self.filtered_exchange_file = load_and_normalize_df(self.patch_dir)

        self.exchange_file_anom_types = list(self.exchange_file["type"].unique())
        print('loaded anom_types: ', self.exchange_file_anom_types)
        self.counts_anom_types = self.exchange_file["type"].value_counts()

        self.current_nc_index = 0
        self.current_filtered_index = 0
        self.max_number_of_features = len(self.filtered_exchange_file)
        # self.anom_type_filter_frame.enabling_mapping = None
        print('self.patch_dir: ', self.patch_dir)

        #p = Path2ProjAnomaliesGeneral(self.patch_dir)

        #self.text_string_csv_file = f"" \
        #                            f"exchange_with_anomcenter.csv file for \n " \
        #                            f"{p.lineshort_name} has been loaded  has been loaded!"

        #self.path_anomaly_label = pathlib.Path(self.patch_dir) / "anomalies"
        #self.path_project_anomalies_dir = self.path_anomaly_label
        #self.level_anomalies_label = '.'.join(
        #    ['combeval_dwh', p.region_number, p.project_number, p.lineshort_name, 'anomalies']
        #)

        #self.lbl_anomalies_dir.setText(self.patch_dir)
        #msg = r'anom_types of of line {} have been loaded!'.format(p.lineshort_name)
        #self.print_message(msg)
        self.show_anomalies_within_dir_new()

    def show_frame(self):
        print('show frame function...')

        if self.frame_for_scrollarea is None:

            # self.frame_for_scrollarea = DummyFrame()
            # self.frame_total = self.frame_for_scrollarea.frame_total
            # self.frame_for_scrollarea.setLayout(self.frame_total)
            # self.scrolling_area.setWidget(self.frame_for_scrollarea)

            self.frame_for_scrollarea = AnomTypeFilterFrame_for_scrollarea(parent=self)
            # Define the instance of AnomTypeFilterFrame_for_scrollarea FIRST! Then the
            # connection with the buttons can be coded!
            self.evaluate_button.clicked.connect(self.frame_for_scrollarea.display_chosen_anom_types)
            self.write_button.clicked.connect(self.frame_for_scrollarea.write_to_pdw_function)
            self.cancel_button.clicked.connect(self.frame_for_scrollarea.cancel_to_pdw_function)

            self.frame_for_scrollarea.filter_anom_types_signal.connect(self.set_filtered_exchange_file)
            self.frame_for_scrollarea.filter_anom_types_signal.connect(self.write_nc_files_to_pdw_without_dask_new)
            self.frame_for_scrollarea.show()
            self.frame_for_scrollarea.set_existing_anom_types(self.exchange_file_anom_types)
            self.frame_for_scrollarea.counts_anom_types = self.counts_anom_types
            self.frame_for_scrollarea.path_anomaly_label = self.path_anomaly_label
            self.frame_for_scrollarea.patch_dir = self.patch_dir
            self.frame_for_scrollarea.level_anomalies_label = self.level_anomalies_label
            self.frame_for_scrollarea.chose_pdw_server = self.chose_pdw_server
            self.frame_for_scrollarea.output_terminal = self.output_terminal
            self.frame_for_scrollarea.calculation_terminal = self.calculation_terminal
            self.frame_for_scrollarea.init_ui()
            # self.layout = self.frame_for_scrollarea.layout
            # self.frame_for_scrollarea.setLayout(self.layout)
            self.gorgo = self.frame_for_scrollarea.anom_types_layout
            self.frame_for_scrollarea.setLayout(self.gorgo)

            self.scrolling_area.setWidget(self.frame_for_scrollarea)
        else:
            self.frame_for_scrollarea.hide()
            self.frame_for_scrollarea = None

    def set_filtered_exchange_file(self, chosen_anom_types: List[str]) -> None:

        # self.list_single_features.clear()
        print('Debug...')
        server = "https://pdw-lin.roseninspection.net/pdw-emat"  # the adress of the server
        self.pdw = joerg_pdw_py_wc.connect(server)
        print('chosen_anom_types: ', chosen_anom_types)
        for level_anom_type in chosen_anom_types:
            tmp_level_single_anomaly = ".".join([self.level_anomalies_label, level_anom_type])

            if not self.pdw.levels.exists(tmp_level_single_anomaly):
                continue
            # else:
            #     tmp_chosen_single_feature_list = pdw.get_level_list(tmp_level_single_anomaly)

        """Reduces the loaded exchange file to the current chosen anomaly types"""

        self.filtered_exchange_file = self.exchange_file[self.exchange_file["type"].isin(chosen_anom_types)]
        self.filtered_exchange_file = self.filtered_exchange_file.reset_index()
        self.max_number_of_features = len(self.filtered_exchange_file)

    def print_message(self, str_val):
        QMessageBox.information(self, "Done!", str_val)

    def show_anomalies_within_dir_new(self):

        #self.len_anomalies = [
        #    len(files) for root, dirs, files in os.walk(self.path_project_anomalies_dir, topdown=False)
        #]
        # obiger Code wird per hand ersetzt. Obiger Code scannt durch das Verzeichnis ..anomalies.. und
        # zählt die Gesamtheit der nc-files in jedem Unterverzeichnis ... also mife
        self.len_anomalies = [100, 1481, 2844, 4587, 1240, 1979, 234, 68, 9, 1, 9, 4, 3, 3]

        # Das gleiche für die Einträge der anomalien selber...
        #self.anomalies = [dirs for root, dirs, files in os.walk(self.path_project_anomalies_dir)]
        self.anomalies = ['INST', 'NOTH', 'MELO-CORR', 'MIFE', 'UNKWN', 'LS', 'LS-MIFE', 'LS-MELO', 'OTHER', 'MELO-MIFE', 'LS-IND', 'pLS-IND', 'LIN', 'LIN-GRP']


        self.max_count_anomalies = len(self.len_anomalies) - 1
        self.anomalies_list = [x.lower() for x in self.anomalies[0]]

        self.anomalies_list_immutable = []
        self.anomalies_list_immutable = tuple(self.anomalies_list)

        #p = Path2ProjAnomaliesGeneral(self.patch_dir)
        #self.lbl_chosen_anomaly_dir.setText('Available features within the line:' + p.lineshort_name)

    def write_nc_files_to_pdw_without_dask_new(self, chosen_anom_types: List[str]) -> None:
        print('self.path....: ', self.path_project_anomalies_dir)

        print('self.pdw: ', self.pdw)
        print('self.chosen_anom_types: ', chosen_anom_types)
        print('self.path_project_anomalies_dir: ', self.path_project_anomalies_dir)
        print('self.counts_anom_types: ', self.counts_anom_types)

        self.thread = MyThread(self.pdw, chosen_anom_types, self.counts_anom_types, self.path_project_anomalies_dir)

        self.thread.start()
        self.thread.thread_finished.connect(self.set_upload_finished)
        # self.thread.thread_finished_window.connect(self.show_window_thread_finished)
        self.thread.thread_plain_text.connect(self.paste_text_to_output_terminal_text)
        self.thread.thread_complete_finished.connect(self.thread.quit)
        self.thread.thread_change_upload_value.connect(self.update_the_progressbar)

    def set_upload_finished(self, text_value):
        self.upload_summary.setText(text_value)

    def show_window_thread_finished(self, text):
        show_dialog(text)

    def paste_text_to_output_terminal_text(self, text):
        self.output_terminal.appendPlainText(text)
        self.output_terminal.setStyleSheet("font-size: 12px;" "color: rgb(44, 44, 126);")

    def update_the_progressbar(self, val):

        self.upload_progress.setValue(val)

    def show_anom_type_filter(self) -> None:
        if self.anom_type_filter_frame is None:
            # self.anom_type_filter_frame = AnomTypeFilterFrame(parent=self)
            self.anom_type_filter_frame = AnomTypeFilterFrame_for_scrollarea(parent=self)
            # print('qframe_width: ', self.anom_type_filter_frame.width())
            # self.anom_type_filter_frame.setFixedWidth()
            # self.anom_type_filter_frame.setStyleSheet("background-color: rgb(44, 44, 126);")
            self.anom_type_filter_frame.filter_anom_types_signal.connect(self.set_filtered_exchange_file)
            self.anom_type_filter_frame.filter_anom_types_signal.connect(self.write_nc_files_to_pdw_without_dask_new)
            self.anom_type_filter_frame.show()
            # print('qframe_width: ', self.anom_type_filter_frame.width())
            self.anom_type_filter_frame.set_existing_anom_types(self.exchange_file_anom_types)
            self.anom_type_filter_frame.counts_anom_types = self.counts_anom_types
            self.anom_type_filter_frame.path_anomaly_label = self.path_anomaly_label
            self.anom_type_filter_frame.patch_dir = self.patch_dir
            self.anom_type_filter_frame.level_anomalies_label = self.level_anomalies_label
            self.anom_type_filter_frame.chose_pdw_server = self.chose_pdw_server
            self.anom_type_filter_frame.output_terminal = self.output_terminal
            self.anom_type_filter_frame.calculation_terminal = self.calculation_terminal
            self.anom_type_filter_frame.move(self.frame_dummy_left.x(), self.frame_dummy_left.y())
            self.anom_type_filter_frame.resize(self.frame_dummy_left.width(), self.frame_dummy_left.height())
            self.anom_type_filter_frame.init_ui()
            # self.anom_type_filter_frame.hide()
        else:
            self.anom_type_filter_frame.hide()
            self.anom_type_filter_frame = None

            # print('going in the show_anom_type_filter function ....')
        # """Dynamically creates a new overlay frame that allows to check the current available anomaly types."""

        # print('exchange_file_anom_types_: ', self.exchange_file_anom_types)
        # print('self.counts_anom_types: ', self.counts_anom_types)
        # self.anom_type_filter_frame.move(self.option_nc_file_anom_type_filter_frame_button.pos())

        # self.anom_type_filter_frame.set_existing_anom_types(self.exchange_file_anom_types)

        # Code below is very IMPORTANT!!
        # Normally the class AnomTypeFilterFrame has NO variable or function self.counts_anom_types.
        # This variable is defined within an other class (here: Main-class).
        # For this, the line below is made for the extension of the class AnomTypeFilterFrame with the
        # variable self.counts_anom_types, so that we can use this variable also within the functions
        # of the class AnomTypeFilterFrame !!!

        # self.anom_type_filter_frame.counts_anom_types = self.counts_anom_types
        # self.anom_type_filter_frame.path_anomaly_label = self.path_anomaly_label
        # self.anom_type_filter_frame.patch_dir = self.patch_dir
        # self.anom_type_filter_frame.level_anomalies_label = self.level_anomalies_label
        # self.anom_type_filter_frame.chose_pdw_server = self.chose_pdw_server
        # self.anom_type_filter_frame.output_terminal = self.output_terminal
        # self.anom_type_filter_frame.calculation_terminal = self.calculation_terminal
        # #####

        # self.anom_type_filter_frame.move(self.frame_dummy_left.x(), self.frame_dummy_left.y())
        # self.anom_type_filter_frame.resize(self.frame_dummy_left.width(), self.frame_dummy_left.height())
        # print('self.frame_dummy_left.x(): ', self.frame_dummy_left.x())
        # print('self.frame_dummy_left.y(): ', self.frame_dummy_left.y())
        # print('self.frame_dummy_left.width(): ', self.frame_dummy_left.width())
        # print('self.frame_dummy_left.height(): ', self.frame_dummy_left.height())

        # TODO: Define the correct coodinates

        # self.anom_type_filter_frame.thread = self.thread
        # self.anom_type_filter_frame.init_ui()

    # def get_levels_of_single_anomaly(self):
    #     server = "https://pdw-lin.roseninspection.net/pdw-emat"    # the adress of the server
    #     self.pdw = joerg_pdw_py_wc.connect(server)
    #
    #     self.single_features_list = self.pdw.get_level_list(self.level_single_anomaly)
    #
    #     list_single_features = [x.split(".")[-1] for x in self.single_features_list]
    #     [self.list_single_features.addItem(x) for x in list_single_features]


# class AnomTypeFilterFrame_for_scrollarea(QFrame):
    """Overlay frame to set the current anomaly types to filter the exchange file on.

    Parameters
    ----------
    parent
        Parent widget in which this widget may be embedded into.
    """

    filter_anom_types_signal = pyqtSignal(list)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        style = """AnomTypeFilterFrame_for_scrollarea {
            border: 1px solid;
            background-color: white;
        }
        """
        self.setStyleSheet(style)

        self.existing_anom_types: List[str] = []
        self.chosen_anom_types: List[str] = []
        self.counts_anom_types = None

        self.checkboxes = []
        self.level_anomalies_label = None
        self.df_dcs = None
        # self.apply_button = QtWidgets.QPushButton("Apply/Eval...")
        # self.write_button = QtWidgets.QPushButton("Write...")
        # self.cancel_button = QtWidgets.QPushButton("Cancel ")
        # Optional[List[int]] <=> Union[List[int], None]
        # >> Mapping of my example: Optional[Dict[str, bool]] <=> Union[Dict[str, bool], None]
        # Default value has to be None, than the nomenclature Optional can be used!!

        self.enabling_mapping: Optional[Dict[str, bool]] = None

    def init_ui(self) -> None:
        """Initialize the ui."""
        # Reparent layout to create the new layout without any issues

        if self.layout():
            QWidget().setLayout(self.layout())

        if self.enabling_mapping is None:
            self.enabling_mapping = {}

            for anom_type in ["All"] + self.existing_anom_types:
                self.enabling_mapping[anom_type] = True

            self.enabling_mapping["None"] = False

        self.checkboxes = []

        self.layout = QVBoxLayout()
        self.anom_types_layout = QVBoxLayout()

        # load the corresponding level in the PDW
        # and display the levels (== anomalies) and counts
        # get the anomalies and counts in the dataframe: pdw_all_anom_with_ctns

        #p = Path2ProjAnomaliesGeneral(self.patch_dir)

        #self.level_anomalies_label = '.'.join(
        #    ['combeval_dwh', p.region_number, p.project_number, p.lineshort_name, 'anomalies'])

        #server = "https://pdw-lin.roseninspection.net/pdw-emat"  # the adress of the server

        #self.pdw = joerg_pdw_py_wc.connect(server)

        # no_levels_available = 0

        # if not self.pdw.levels.exists(self.level_anomalies_label):
        #
        #     # pdw_all_anom_with_ctns = pd.DataFrame(
        #     # {'pdw_anom': self.existing_anom_types, 'pdw_ctn': self.counts_anom_types}
        #     # )
        #     pdw_all_anom_with_ctns = pd.DataFrame(
        #         {'pdw_anom': self.existing_anom_types, 'pdw_ctn': 0}
        #     )
        #     print('pdw_all_anom_with_ctn_0: \n', pdw_all_anom_with_ctns)
        #
        # else:
        #
        #     # = counts_in_level(
        #     #    self.pdw.get_level_list(self.level_anomalies_label, recursive=True)
        #     # )
        #
        #     dirname_column_lineshot_tmp = self.pdw.get_pdw_datacubes_catalog(self.pdw, self.level_anomalies_label)
        #     dirname_column_lineshot = sorted(dirname_column_lineshot_tmp['dirname'].unique())
        #     keys_lineshot = set([".".join(v.split(".")[:-1]) for v in dirname_column_lineshot])
        #     dict_lineshot = {k: [] for k in sorted(keys_lineshot)}
        #     for level in dirname_column_lineshot:
        #         parts = level.split(".")
        #         key = ".".join(parts[:-1])
        #         value = parts[-1]
        #         dict_lineshot[key].append(value)
        #
        #     count_lineshot = {k: len(dict_lineshot[k]) for k in dict_lineshot}
        #     count_lineshot.values()
        #
        #     pdw_level_list_with_ctns = [list(count_lineshot.values())[1:], list(count_lineshot.keys())[1:]]
        #
        #     print('pdw_level_list_with_ctns: ', pdw_level_list_with_ctns)
        #     print('type...:', type(pdw_level_list_with_ctns))
        #     pdw_anom_list = [lf.split(".")[-1].upper() for lf in pdw_level_list_with_ctns[1]]
        #     pdw_anom_list = ['pLS-IND' if lf == 'PLS-IND' else lf for lf in pdw_anom_list]
        #     pdw_anom_list = ['LS-pLIN' if lf == 'LS-PLIN' else lf for lf in pdw_anom_list]
        #     pdw_anom_list = ['pLIN' if lf == 'PLIN' else lf for lf in pdw_anom_list]
        #
        #     print('pdw_anom_list: ', pdw_anom_list)
        #
        #     pdw_all_anom_with_ctns = pd.DataFrame({'pdw_anom': pdw_anom_list, 'pdw_ctn': pdw_level_list_with_ctns[0]})


        # level_not_complete_with_datacubes = 0

        ################################################

        # Write the anomalies and counts of the linfile1-anomalies folder in a dataframe

        ctn_all = []

        for anom_type in ["All", "None"] + self.existing_anom_types:

            if anom_type == "All":
                ctn = sum(self.counts_anom_types)
                ctn_all.append(ctn)

            elif anom_type == "None":
                pass
            else:
                ctn = self.counts_anom_types[anom_type]
                ctn_all.append(ctn)

        all_anomalies_with_ctns = pd.DataFrame(
            {'lfile1_anom': ['All'] + self.existing_anom_types, 'lfile1_ctn': ctn_all})
        pdw_all_anom_with_ctns = pd.read_csv('pdw_anom_ctn.csv', index_col=[0])
        print(tabulate(pdw_all_anom_with_ctns, headers='keys', tablefmt='psql'))
        df_merged = all_anomalies_with_ctns.merge(pdw_all_anom_with_ctns, "outer", left_on="lfile1_anom",
                                                  right_on="pdw_anom")
        df_merged['pdw_ctn'] = df_merged['pdw_ctn'].fillna(0).astype(int)
        df_merged['pdw_anom'] = df_merged['pdw_anom'].fillna("")
        del (df_merged['pdw_anom'])
        df_merged.columns = ['anom', 'lfile1_ctn', 'pdw_ctn']
        # print('df_merged: \n ', df_merged)
        df_merged.to_dict("records")
        df_merged['uploaded'] = df_merged['pdw_ctn'].apply(lambda x: x > 0)
        df_uploaded_anom = dict(zip(df_merged['anom'], df_merged['uploaded']))
        #print(tabulate(df_uploaded_anom, headers='keys', tablefmt='psql'))
        print('df_uploaded_anom: \n', df_uploaded_anom)
        #####################################################

        # ctn_all = []

        # self.df_dcs = self.pdw.get_pdw_datacubes_catalog(self.pdw, self.level_anomalies_label)
        # # level_not_complete = []
        level_not_fully_complete = []
        #
        # for my_anom_type in ["All", "None"] + self.existing_anom_types:
        #     if (my_anom_type != "All") & (my_anom_type != "None"):
        #         level_single_anomaly = '.'.join([self.level_anomalies_label, my_anom_type.lower()])
        #
        #         if self.pdw.levels.exists(level_single_anomaly):
        #             level_single_feature = self.pdw.get_level_list(level_single_anomaly)
        #
        #             for single_feature in level_single_feature:
        #                 dcs_in_single_feature = self.df_dcs[self.df_dcs["dirname"] == single_feature]
        #                 ctn_complete = len(dcs_in_single_feature)
        #
        #                 if (ctn_complete != 13) & (ctn_complete != 9):
        #                     level_not_fully_complete.append(single_feature)

        # print('dcs_in_level_db: ', level_not_complete)

        for anom_type in ["All", "None"] + self.existing_anom_types:

            if anom_type == "All":
                ctn = sum(self.counts_anom_types)
                ctn_label = " (CTN = " + str(ctn) + ")"
            elif anom_type == "None":
                ctn_label = ""
            else:
                ctn = self.counts_anom_types[anom_type]
                ctn_label = " (CTN = " + str(ctn) + ")"

            anom_type_checkbox = QCheckBox(anom_type + ctn_label)

            checkbox_content = anom_type_checkbox.text().split(" ")[0]
            print('checkbox_content: ', checkbox_content)

            if (checkbox_content == "None") or (checkbox_content == "All"):
                anom_type_checkbox.setStyleSheet("color: green")

            elif not df_uploaded_anom[checkbox_content]:
                anom_type_checkbox.setStyleSheet("color: red")

            elif df_uploaded_anom[checkbox_content]:
                dcs_not_complete = any(
                    [lf for lf in level_not_fully_complete if f".anomalies.{checkbox_content}.".lower() in lf.lower()]
                )
                print('dcs_not_complete:', dcs_not_complete)

                if dcs_not_complete:
                    anom_type_checkbox.setStyleSheet("color: orange")
                else:
                    anom_type_checkbox.setStyleSheet("color: green")

            anom_type_checkbox.setChecked(self.enabling_mapping[anom_type])
            anom_type_checkbox.clicked.connect(self.toggle_anom_type)
            self.anom_types_layout.addWidget(anom_type_checkbox)
            self.checkboxes.append(anom_type_checkbox)

        self.layout.addLayout(self.anom_types_layout)
        # button_layout = QHBoxLayout()
        # Definition of Buttons will be inside the __init__ function of the class
        # NO!!! Above line leads to an error during the additional call of the frame!!
        # Therefore the definition is here!
        self.evaluate_button = QPushButton("Evaluate...")
        self.write_button = QPushButton("Write...")
        self.cancel_button = QPushButton("Cancel ")
        # self.apply_button.clicked.connect(self.emit_chosen_anom_types)

        self.evaluate_button.clicked.connect(self.display_chosen_anom_types)
        self.write_button.clicked.connect(self.write_to_pdw_function)
        self.cancel_button.clicked.connect(self.cancel_to_pdw_function)
        # button_layout.addWidget(self.evaluate_button)
        # button_layout.addWidget(self.write_button)
        # button_layout.addWidget(self.cancel_button)

        # layout.addLayout(button_layout)
        self.setLayout(self.layout)
        self.setMinimumHeight(25 * (2 + len(self.existing_anom_types)) + 30)
        # print('Debug after self.existing_anom_types')
        mm = []

        for lf in self.existing_anom_types:
            mm.append(len(lf))
        self.setMinimumWidth(25 * (max(mm)) + 10)

        self.show()

    def set_existing_anom_types(self, anom_types: List[str]) -> None:
        """Sets the existing anomaly types for this frame. The input will be sorted.

        Parameters
        ----------
        anom_types
            List of anomaly types, e.g. ["LIN", "MIFE"]
        """
        self.existing_anom_types = sorted(anom_types)
        print('self.existing_anom_types: ', self.existing_anom_types)

    def emit_chosen_anom_types(self) -> None:
        """Emits the chosen anomaly types"""
        self.hide()

        self.chosen_anom_types: List[str] = []

        for anom_type in ["All", "None"] + self.existing_anom_types:
            is_checked = self.enabling_mapping[anom_type]

            if is_checked and anom_type not in {"All", "None"}:
                self.chosen_anom_types.append(anom_type)

        self.filter_anom_types_signal.emit(self.chosen_anom_types)

    def display_chosen_anom_types(self) -> None:
        """Emits the chosen anomaly types"""
        # self.hide()
        print('going into display_chose_anom_types')
        self.chosen_anom_types: List[str] = []

        for anom_type in ["All", "None"] + self.existing_anom_types:
            is_checked = self.enabling_mapping[anom_type]

            if is_checked and anom_type not in {"All", "None"}:
                self.chosen_anom_types.append(anom_type)

        print('chosen_anom_types: \n', self.chosen_anom_types)
        self.ctn_total = sum(self.counts_anom_types[self.chosen_anom_types])
        print('ctn_total = ', str(self.ctn_total))
        upload_time_estimated_min_10s = self.ctn_total * 10 / 60
        upload_time_estimated_hr_10s = self.ctn_total * 10 / 3600

        upload_time_estimated_min_15s = self.ctn_total * 15 / 60
        upload_time_estimated_hr_15s = self.ctn_total * 15 / 3600

        upload_time_estimated_min_20s = self.ctn_total * 20 / 60
        upload_time_estimated_hr_20s = self.ctn_total * 20 / 3600

        self.calculation_terminal.clear()
        self.calculation_terminal.appendPlainText('Estimated upload-time:')
        self.calculation_terminal.appendPlainText(f'ctn_total = {self.ctn_total}')
        self.calculation_terminal.appendPlainText(f'{upload_time_estimated_min_10s:.2f} mins (10s per nc-file)')
        self.calculation_terminal.appendPlainText(f'{upload_time_estimated_hr_10s:.2f} hrs (10s per nc-file)')
        self.calculation_terminal.appendPlainText('======')

        self.calculation_terminal.appendPlainText(f'{upload_time_estimated_min_15s:.2f} mins (15s per nc-file)')
        self.calculation_terminal.appendPlainText(f'{upload_time_estimated_hr_15s:.2f} hrs (15s per nc-file)')
        self.calculation_terminal.appendPlainText('======')

        self.calculation_terminal.appendPlainText(f'{upload_time_estimated_min_20s:.2f} mins (20s per nc-file)')
        self.calculation_terminal.appendPlainText(f'{upload_time_estimated_hr_20s:.2f} hrs (20s per nc-file)')

        # self.filter_anom_types_signal.emit(self.chosen_anom_types)
        print('end apply/eval function...')

    def write_to_pdw_function(self) -> None:
        """Writes the single features of the chosen single anomalies into pdw"""
        self.hide()

        self.chosen_anom_types: List[str] = []

        for anom_type in ["All", "None"] + self.existing_anom_types:
            is_checked = self.enabling_mapping[anom_type]

            if is_checked and anom_type not in {"All", "None"}:
                self.chosen_anom_types.append(anom_type)

        self.filter_anom_types_signal.emit(self.chosen_anom_types)

        print('chosen_anom_types within the write_to_pdw_function: \n', self.chosen_anom_types)

    def cancel_to_pdw_function(self) -> None:
        self.hide()

    def toggle_anom_type(self, state: bool) -> None:
        """Check or uncheck the clicked checkbox and update other checkboxes if needed.

        Since there is an "All" and a "None" checkbox, there is some update logic needed to
        check or uncheck other checkboxes.

        Parameters
        ----------
        state
            True if the checkbox has been checked, False otherwise
        """
        print('before clicked ....')
        clicked_anom_type = self.sender().text().split(" ")[0]
        print('clicked .. ', clicked_anom_type)

        if clicked_anom_type == "All":
            ctn = sum(self.counts_anom_types)
            print('ctn: ', ctn)
        elif clicked_anom_type == "None":
            ctn = 0
            print('ctn: ', str(ctn))

        else:
            print('ctn: ', self.counts_anom_types[clicked_anom_type])

        if state is True:
            if clicked_anom_type == "All":
                for anom_type in ["All"] + self.existing_anom_types:
                    self.enabling_mapping[anom_type] = True

                self.enabling_mapping["None"] = False

            elif clicked_anom_type == "None":
                for anom_type in ["All"] + self.existing_anom_types:
                    self.enabling_mapping[anom_type] = False

                self.enabling_mapping["None"] = True

            else:
                self.enabling_mapping[clicked_anom_type] = True

                all_enabled = True

                for anom_type in self.existing_anom_types:
                    if self.enabling_mapping[anom_type] is False:
                        all_enabled = False
                        break

                self.enabling_mapping["All"] = all_enabled
                self.enabling_mapping["None"] = False

        elif state is False:
            if clicked_anom_type == "All":
                for anom_type in ["All"] + self.existing_anom_types:
                    self.enabling_mapping[anom_type] = False

                self.enabling_mapping["None"] = True
            elif clicked_anom_type == "None":
                for anom_type in ["All"] + self.existing_anom_types:
                    self.enabling_mapping[anom_type] = True

                self.enabling_mapping["None"] = False
            else:
                self.enabling_mapping[clicked_anom_type] = False
                self.enabling_mapping["All"] = False

                none_enabled = True

                for anom_type in self.existing_anom_types:
                    if self.enabling_mapping[anom_type] is True:
                        none_enabled = False
                        break

                self.enabling_mapping["None"] = none_enabled

        else:
            raise ValueError(f"State {state} is not valid.")

        for anom_type, checkbox in zip(["All", "None"] + self.existing_anom_types, self.checkboxes):
            is_checked = self.enabling_mapping[anom_type]
            checkbox.setChecked(is_checked)

        if self.enabling_mapping["None"] is True:
            self.evaluate_button.setEnabled(False)
        else:
            self.evaluate_button.setEnabled(True)


class DummyFrame(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        style = """DummyFrame {
            border: 1px solid;
            background-color: rgba(0, 155, 155, 80);
        }
        """
        self.setStyleSheet(style)

        # Define the layout for adding the buttons to the scrollarea
        self.frame_total = QVBoxLayout()

        for i in range(1, 50):
            object = QCheckBox("CheckBox of dummy Frame!")
            self.frame_total.addWidget(object)

#https://www.pythonguis.com/tutorials/pyside-creating-multiple-windows/
if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(app.instance())
    window = WindowFeatureUpload(200, 200, 100)
    window.show()
    print('active application, or window')
    sys.exit(app.exec_())