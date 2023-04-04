import sys
import os
import signal
from PySide2.QtGui import QPixmap
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget, QPushButton, QLabel, QMessageBox, QFrame, QHBoxLayout

def showDialog():
   msgBox = QMessageBox()
   msgBox.setIcon(QMessageBox.Information)
   msgBox.setText("Message box pop up window")
   msgBox.setWindowTitle("QMessageBox Example")
   msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#    msgBox.buttonClicked.connect(msgButtonClick)

   returnValue = msgBox.exec()
   if returnValue == QMessageBox.Ok:
      print('OK clicked')


class window():
   app = QApplication(sys.argv)
   win = QWidget()
   button1 = QPushButton(win)
   button1.setText("Show dialog!")
   button1.move(50,50)
   button1.clicked.connect(showDialog)
   win.setWindowTitle("Click button")
   win.show()
   sys.exit(app.exec_())

def msgButtonClick(i):
   print("Button clicked is:",i.text())
	
if __name__ == '__main__': 
   window()