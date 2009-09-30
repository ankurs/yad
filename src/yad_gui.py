from PyQt4 import QtCore, QtGui
from gui import main_gui, about_gui, new_download_gui
import sys

import time

class AboutDialog(about_gui.Ui_Dialog):
    '''
        class to handel about dialog
    '''
    def __init__(self,dialog):
        self.setupUi(dialog) # setup the dialogs
        dialog.connect(self.closeButton,QtCore.SIGNAL("clicked()"),dialog.close) # close dialog on closeButton press


class YadUi(main_gui.Ui_MainWindow):
    '''
        class to handel all GUI actions
    '''
    def __init__(self,window):
        '''
            constructor take a window as argument, set up all the signals
        '''
        self.setupUi(window) 
        self.mainWindow = window # saving mainwindow object for later reference
        # create dialog objects from here
        self.aboutDialog = QtGui.QDialog() # create a dialog object
        AboutDialog(self.aboutDialog) # set about dialog object
        # till here
        # connect Signals to slots from here
        window.connect(self.actionExit,QtCore.SIGNAL("triggered()"),self.app_exit) # for app exit
        window.connect(self.actionAbout,QtCore.SIGNAL("triggered()"),self.show_about) # for about YAD

    def app_exit(self):
        '''
            handels application exit
        '''
        print "bye bye..."
        self.mainWindow.close() # just close the main window

    def show_about(self):
        '''
            diaplay the about YAD dialog
        '''
        self.aboutDialog.show()

app = QtGui.QApplication(sys.argv)
window = QtGui.QMainWindow()
ui = YadUi(window)
window.show()
sys.exit(app.exec_())
