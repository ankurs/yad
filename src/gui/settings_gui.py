# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created: Sun Nov  1 11:18:53 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(335, 316)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.proxyBox = QtGui.QCheckBox(Dialog)
        self.proxyBox.setObjectName("proxyBox")
        self.verticalLayout.addWidget(self.proxyBox)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.url = QtGui.QLineEdit(Dialog)
        self.url.setDragEnabled(True)
        self.url.setObjectName("url")
        self.horizontalLayout_3.addWidget(self.url)
        self.spinBox = QtGui.QSpinBox(Dialog)
        self.spinBox.setMaximum(65565)
        self.spinBox.setProperty("value", QtCore.QVariant(5865))
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_3.addWidget(self.spinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.folderPath = QtGui.QLineEdit(Dialog)
        self.folderPath.setReadOnly(True)
        self.folderPath.setObjectName("folderPath")
        self.horizontalLayout_2.addWidget(self.folderPath)
        self.selectButton = QtGui.QPushButton(Dialog)
        self.selectButton.setObjectName("selectButton")
        self.horizontalLayout_2.addWidget(self.selectButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.threads = QtGui.QSpinBox(Dialog)
        self.threads.setMinimum(1)
        self.threads.setMaximum(200)
        self.threads.setProperty("value", QtCore.QVariant(4))
        self.threads.setObjectName("threads")
        self.horizontalLayout.addWidget(self.threads)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "YAD - Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.proxyBox.setText(QtGui.QApplication.translate("Dialog", "Enable HTTP Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.url.setText(QtGui.QApplication.translate("Dialog", "127.0.0.1", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Save to", None, QtGui.QApplication.UnicodeUTF8))
        self.selectButton.setText(QtGui.QApplication.translate("Dialog", "Select", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Number Of Threads", None, QtGui.QApplication.UnicodeUTF8))

