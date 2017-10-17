# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CameraSettingsDialog.ui'
#
# Created: Mon Jun 10 17:03:11 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_CameraSettingsDialog(object):
    def setupUi(self, CameraSettingsDialog):
        CameraSettingsDialog.setObjectName(_fromUtf8("CameraSettingsDialog"))
        CameraSettingsDialog.resize(271, 162)
        self.verticalLayout = QtGui.QVBoxLayout(CameraSettingsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.taurusWidget = TaurusWidget(CameraSettingsDialog)
        self.taurusWidget.setObjectName(_fromUtf8("taurusWidget"))
        self.gridLayout = QtGui.QGridLayout(self.taurusWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(self.taurusWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.imageTypeComboBox = TaurusValueComboBox(self.taurusWidget)
        self.imageTypeComboBox.setObjectName(_fromUtf8("imageTypeComboBox"))
        self.gridLayout.addWidget(self.imageTypeComboBox, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.taurusWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.triggerModeComboBox = TaurusValueComboBox(self.taurusWidget)
        self.triggerModeComboBox.setObjectName(_fromUtf8("triggerModeComboBox"))
        self.gridLayout.addWidget(self.triggerModeComboBox, 1, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.taurusWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.expTimeLineEdit = MAXLineEdit(self.taurusWidget)
        self.expTimeLineEdit.setModel(_fromUtf8(""))
        self.expTimeLineEdit.setUseParentModel(False)
        self.expTimeLineEdit.setObjectName(_fromUtf8("expTimeLineEdit"))
        self.gridLayout.addWidget(self.expTimeLineEdit, 2, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.taurusWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        self.gainLineEdit = MAXLineEdit(self.taurusWidget)
        self.gainLineEdit.setObjectName(_fromUtf8("gainLineEdit"))
        self.gridLayout.addWidget(self.gainLineEdit, 3, 1, 1, 1)
        self.verticalLayout.addWidget(self.taurusWidget)

        self.retranslateUi(CameraSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(CameraSettingsDialog)

    def retranslateUi(self, CameraSettingsDialog):
        CameraSettingsDialog.setWindowTitle(_translate("CameraSettingsDialog", "Camera Settings", None))
        self.label_3.setText(_translate("CameraSettingsDialog", "Image Type", None))
        self.label_4.setText(_translate("CameraSettingsDialog", "Trigger Mode", None))
        self.label_5.setText(_translate("CameraSettingsDialog", "Exposure (ms)", None))
        self.label_6.setText(_translate("CameraSettingsDialog", "Gain (dB)", None))

try:
    from taurus.qt.qtgui.panel import TaurusWidget
except ImportError:
    from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.input import TaurusValueComboBox
from maxwidgets.input import MAXLineEdit
