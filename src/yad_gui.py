#!/usr/bin/env python

# Author: Ankur Shrivastava
# mail : ankur [ at ] ankurs [ dot ] com
# License : GPLv3

from PyQt4 import QtCore, QtGui
from gui import main_gui, about_gui, new_download_gui, settings_gui
import yad
import sys
from hashlib import sha1
from time import time,sleep
from threading import Thread
import pynotify

Downloads = [] # stores all the download objects for reference
gProxy = None # global proxy address
gFolder = "~/" # global save dir
gThreads = 4 # global number of threads
items = [] # holds all items 
pynotify.init("YAD")

class DownloadThread(Thread):
    '''
        handels the actual download
    '''
    def __init__(self,url,folder=None,threads=4):
        Thread.__init__(self) # setup the thread
        id = sha1(str(time())).hexdigest() # generate a hex digest based on current time
        if gProxy:
            self.dl = yad.Download(id,threads,"http://"+gProxy) # if proxy is set we use it
        else:
            self.dl = yad.Download(id,threads) # 
        self.folder = folder
        self.url = url

    def run(self):
        self.dl.download(self.url,folder = self.folder)
        

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


class SettingsDialog(settings_gui.Ui_Dialog):
    '''
        class to handel settings dialog
    '''
    def __init__(self,dialog):
        self.setupUi(dialog) # setup dialogs
        icon = QtGui.QIcon() # create an icon
        icon.addPixmap(QtGui.QPixmap("icons/yad.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off) # get image
        dialog.setWindowIcon(icon) # set as window icon
        self.dialog = dialog # save dialog object
        #dialog.connect(self.proxyBox,QtCore.SIGNAL("stateChanged(int state)"),self.checkProxy)
        #dialog.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.dialog.close) # handel cancel


    def checkProxy(self,state):
        print state

class NewDownload(new_download_gui.Ui_Dialog):
    '''
        class to handel new download
    '''
    def __init__(self,dialog):
        self.setupUi(dialog) # setup the dialogs
        icon = QtGui.QIcon() # create an icon
        icon.addPixmap(QtGui.QPixmap("icons/yad.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off) # set image
        dialog.setWindowIcon(icon) # set as window icon
        self.dialog = dialog # save dialog object
        dialog.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.close) # handel cancel
        dialog.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.doDownload) # handel accept
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
            d = DownloadThread(str(self.url.text()), str(self.folderPath.text()), self.threads.value())
            Downloads.append(d)
            d.start()
            self.close()

class YadInfo(Thread):
    '''
        class to update info of all the DownloadThreads to GUI
    '''
    def __init__(self,UI):
        Thread.__init__(self) # call Threads init
        self.UI = UI # YadUi's reference
        self.running = True # to stop the thread

    def run(self):
        global Downloads
        global items
        while self.running:
            while Downloads: # if new downloads have been added
                d = Downloads.pop() # remove one download
                item = QtGui.QTreeWidgetItem() # create a widget item
                item.setText(0,str(d.url)) # set url
                pynotify.Notification("Yet Another Downloader","Download "+str(d.url)+" added\nsaving in "+str(d.folder)).show() # show notification 
                item.setText(1,str(d.dl.info.progress)) # set progress
                item.setText(2,str(d.dl.info.ET)) # set estimated time
                item.setText(3,str(d.dl.info.cur_speed)) # set current speed
                item.setText(4,str(d.dl.info.avg_speed)) # set average speed
                item.setText(5,str(d.folder)) # set folder where file is being saved
                item.setText(6,str(d.dl.info.length)) # set length
                self.UI.downloadWidget.addTopLevelItem(item) # add item to tree
                items.append([item,d,"running"]) # save for updates
            for i in items: # take a pair of item and download
                item,d,state = i 
                if state == "running":
                    if d.dl.info.finished:
                        pynotify.Notification("Yet Another Downloader","Download "+str(d.url)+" finished\n saved in "+str(d.folder)).show() # show notification
                        i[2] = "done"
                item.setText(1,str(d.dl.info.progress)) # update progress
                item.setText(2,str(d.dl.info.ET)) # update estimated time
                item.setText(3,str(d.dl.info.cur_speed)) # update current time
                item.setText(4,str(d.dl.info.avg_speed)) # update average speed
            sleep(1) # wait for some time

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
        self.aboutDialog = QtGui.QDialog(window) # create a dialog object
        AboutDialog(self.aboutDialog) # set about dialog object
        self.settingsDialog = QtGui.QDialog(window) # create a dialog object
        SettingsDialog(self.settingsDialog)
        self.downloadDialog = NewDownload(QtGui.QDialog(window)) # create a new download dialog object
        # till here
        # connect Signals to slots from here
        window.connect(self.actionExit,QtCore.SIGNAL("triggered()"),self.app_exit) # for app exit
        window.connect(self.actionAbout,QtCore.SIGNAL("triggered()"),self.aboutDialog.show) # for about YAD
        window.connect(self.actionSettings,QtCore.SIGNAL("triggered()"),self.show_settings) # for YAD's settings
        window.connect(self.actionURL,QtCore.SIGNAL("triggered()"),self.downloadDialog.display) # for new download

        self.tray = QtGui.QSystemTrayIcon(icon) # system tray icon
        # setup the contex menu for System Tray Icon
        self.menuMenu = QtGui.QMenu()
        self.menuMenu.setObjectName("menuMenu")
        self.actionHide = QtGui.QAction(self.mainWindow)
        self.actionHide.setObjectName("actionHide")
        self.actionHide.setText(QtGui.QApplication.translate("MainWindowClass", "Hide", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit = QtGui.QAction(self.mainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setText(QtGui.QApplication.translate("MainWindowClass", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings = QtGui.QAction(self.mainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindowClass", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.menuMenu.addAction(self.actionHide)
        self.menuMenu.addAction(self.actionSettings)
        self.menuMenu.addAction(self.actionExit)
        self.tray.setContextMenu(self.menuMenu)
        #setup signal for system tray icon click
        QtCore.QObject.connect(self.actionExit,QtCore.SIGNAL("triggered()"), self.app_exit)
        QtCore.QObject.connect(self.actionHide,QtCore.SIGNAL("triggered()"), self.show_hide)
        QtCore.QObject.connect(self.actionSettings,QtCore.SIGNAL("triggered()"),self.show_settings) # for YAD's settings
        self.tray.setVisible(True) # make syatem tray icon visible
        window.connect(self.tray,QtCore.SIGNAL("activated (QSystemTrayIcon::ActivationReason)"), self.show_hide) # handel click on Status bar icon
        pynotify.Notification("YAD","Yet Another Downloader Started").show()
        self.yadInfo = YadInfo(self) # make info update thread object
        self.yadInfo.start() # start the thread

    def show_hide(self,value=3):
        if value == 3:
            if self.mainWindow.isVisible():
                self.mainWindow.hide() # hide mainWindow
                self.actionHide.setText(QtGui.QApplication.translate("MainWindowClass", "Show", None, QtGui.QApplication.UnicodeUTF8)) # update contex menu
            else:
                self.mainWindow.show() # show mainWindow
                self.actionHide.setText(QtGui.QApplication.translate("MainWindowClass", "Hide", None, QtGui.QApplication.UnicodeUTF8)) # update contex menu
           
    def show_settings(self):
        # open main window and settings
        if not self.mainWindow.isVisible(): # is main window is not visible
            self.show_hide() # we display it and set contex menu accordingly
        self.settingsDialog.show() # show settings dialog

    def app_exit(self):
        '''
            handels application exit
        '''
        self.yadInfo.running = False
        print "bye bye..."
        self.mainWindow.close() # just close the main window


app = QtGui.QApplication(sys.argv)
window = QtGui.QMainWindow()
ui = YadUi(window)
window.show()
sys.exit(app.exec_())
