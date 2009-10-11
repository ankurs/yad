#!/usr/bin/env python

# Author: Ankur Shrivastava
# mail : ankur [ at ] ankurs [ dot ] com
# License : GPLv3

from PyQt4 import QtCore, QtGui
from gui import main_gui, about_gui, new_download_gui
import yad
import sys
from hashlib import sha1
from time import time
from threading import Thread

Downloads = [] # stores all the download objects for reference


class DownloadThread(Thread):
    '''
        handels the actual download
    '''
    def __init__(self,url,folder=None,threads=4):
        Thread.__init__(self) # setup the thread
        id = sha1(str(time())).hexdigest() # generate a hex digest based on current time
        self.d = yad.Download(id,threads)
        self.folder = folder
        self.url = url

    def run(self):
        self.d.download(self.url,folder = self.folder)
        

class AboutDialog(about_gui.Ui_Dialog):
    '''
        class to handel about dialog
    '''
    def __init__(self,dialog):
        self.setupUi(dialog) # setup the dialogs
        dialog.connect(self.closeButton,QtCore.SIGNAL("clicked()"),dialog.close) # close dialog on closeButton press
        icon = QtGui.QIcon() # create an icon
        icon.addPixmap(QtGui.QPixmap("icons/yad.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off) # get image
        dialog.setWindowIcon(icon) # set as window icon


class NewDownload(new_download_gui.Ui_Dialog):
    '''
        class to handel new download
    '''
    def __init__(self,dialog):
        self.setupUi(dialog) # setup the dialogs
        icon = QtGui.QIcon() # create an icon
        icon.addPixmap(QtGui.QPixmap("icons/yad.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off) # get image
        dialog.setWindowIcon(icon) # set as window icon
        self.dialog = dialog # save dialog object
        dialog.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.close) # handel cancel a
        dialog.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.doDownload) # handel cancel a
        dialog.connect(self.selectButton,QtCore.SIGNAL("clicked()"),self.chooseFolder) # handel folder selection
        self.url.selectAll()

    def close(self):
        self.url.setText("http://")
        self.dialog.close()

    def chooseFolder(self):
        fileDialog = QtGui.QFileDialog(self.dialog) # make a folder selection dialog object
        folder = fileDialog.getExistingDirectory() # display the dialog
        self.folderPath.setText(folder+"/") # set folder
        print folder

    def display(self):
        '''
            displays new download dialog to user
        '''
        self.dialog.show() # show the dialog
        self.url.selectAll() # select the url

    def doDownload(self):
        print self.url.text()
        global Downloads
        if self.url.text() and self.folderPath.text():
            d = yad.Download(self.threads.value())
            d = DownloadThread(str(self.url.text()), str(self.folderPath.text()), self.threads.value())
            Downloads.append(d)
            d.start()
            self.close()

class YadUi(main_gui.Ui_MainWindow):
    '''
        class to handel all GUI actions
    '''
    def __init__(self,window):
        '''
            constructor take a window as argument, set up all the signals
        '''
        self.setupUi(window) 
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/yad.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        window.setWindowIcon(icon)
        self.mainWindow = window # saving mainwindow object for later reference
        # create dialog objects from here
        self.aboutDialog = QtGui.QDialog() # create a dialog object
        AboutDialog(self.aboutDialog) # set about dialog object
        self.downloadDialog = NewDownload(QtGui.QDialog()) # create a new download dialog object
        # till here
        # connect Signals to slots from here
        window.connect(self.actionExit,QtCore.SIGNAL("triggered()"),self.app_exit) # for app exit
        window.connect(self.actionAbout,QtCore.SIGNAL("triggered()"),self.aboutDialog.show) # for about YAD
        window.connect(self.actionURL,QtCore.SIGNAL("triggered()"),self.downloadDialog.display) # for new download

        ## remove this CHECK
        item = QtGui.QTreeWidgetItem()
        item.setText(0,"item 1")
        item.setText(1,"skjskld")

        item1 = QtGui.QTreeWidgetItem()
        item1.setText(0,"item 2")
        item1.setText(1,"skjskld")
        self.downloadWidget.addTopLevelItem(item)
        self.downloadWidget.addTopLevelItem(item1)


    def app_exit(self):
        '''
            handels application exit
        '''
        print "bye bye..."
        self.mainWindow.close() # just close the main window


app = QtGui.QApplication(sys.argv)
window = QtGui.QMainWindow()
ui = YadUi(window)
window.show()
sys.exit(app.exec_())
