import PyTango
from PyQt4 import QtCore, QtGui, Qt
from taurus.qt.qtgui.panel import TaurusForm
try:
    from taurus.qt.qtgui.panel import TaurusWidget
except ImportError:
    from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.input import TaurusValueComboBox
from taurus.qt.qtgui.display import TaurusLabel

import taurus
try:
    from taurus import tauruscustomsettings  # taurus 3.3
except ImportError:
    from taurus import TaurusCustomSettings  # taurus 3.0


class MotorPresets(TaurusWidget):

    """This is the class for the overall widget of 3 tabs"""

    def __init__(self, parent=None):
        TaurusWidget.__init__(self, parent)
        self._setup_ui()

    def _setup_ui(self):

        hbox = QtGui.QHBoxLayout(self)
        self.setLayout(hbox)
        tabs = QtGui.QTabWidget()
        hbox.addWidget(tabs)

        #main user widget to steer the IOR
        self.ioruser_widget = IORUserPanel()
        self.ioruser_tab = tabs.addTab(self.ioruser_widget, "IOR User")

        #widget to configure the IOR
        self.iorconfig_widget = IORConfigPanel(self.ioruser_widget)
        self.iorconfig_tab = tabs.addTab(self.iorconfig_widget, "IOR Config")

        #widget to configure the motor
        self.motorconfig_widget = MotorConfigPanel()
        self.motorconfig_tab = tabs.addTab(self.motorconfig_widget, "Motor Config")

        tabs.setCurrentIndex(self.ioruser_tab)
        self.resize(800, 400)

    def setModel(self, ior):

        self.iorconfig_widget.setModel(ior)
        #See what motor we are dealing with - check attribute
        motor = (taurus.Attribute(ior+"/TangoAttribute").read().value).rsplit("/",1)[0]
        self.motorconfig_widget.setModel(motor)
        self.ioruser_widget.setModel(ior,motor,firstcall=True,updateIOR=True)


class IORConfigPanel(TaurusWidget):

    """Widget to configure the IOR"""

    config_trigger = QtCore.pyqtSignal()

    def __init__(self, userwidget, parent=None):
        self.userwidget = userwidget
        TaurusWidget.__init__(self, parent)
        self._setup_ui()
        self.oldvalue =  {}

    def updateBoxes(self):
        self.userwidget.updateBoxes(True)

    def _setup_ui(self):
        self.gridLayout = QtGui.QGridLayout(self)
        self.taurusForm = TaurusForm(self)
        self.taurusForm.setWithButtons(False)
        self.gridLayout.addWidget(self.taurusForm, 0, 0, 1, 2)

    def setModel(self, ior):

        attributes = [ior+"/Labels",
                      ior+"/Calibration",
                      ]
        self.taurusForm.setModel(attributes)

        #Need listeners on these attributes to update user widget
        #for a in attributes:
        #    taurus.Attribute(a).addListener(self.configListener)
        #self.config_trigger.connect(self.updateBoxes)

    def configListener(self, src, evt_type, attr_val):

        #is this going to emit every 3 seconds irrespective of whether attribute actually changes?
        if isinstance(src,taurus.core.tango.tangoattribute.TangoAttribute):
            if src not in  self.oldvalue:
                self.oldvalue[src] = attr_val.value
            else:
                if self.oldvalue[src] != attr_val.value:
                    self.oldvalue[src] = attr_val.value
                    self.config_trigger.emit()

class IORUserPanel(TaurusWidget):

    """Widget to use the IOR"""

    def __init__(self, parent=None):
        TaurusWidget.__init__(self, parent)
        self._setup_ui()
        self.ior_model = None
        self.mot_model = None
        self.options = []
        self.dict =  {}

    def updateBoxes(self,arg):
        """ If receive signal to update the options, adjust the model"""
        if self.ior_model is not None and self.mot_model is not None : #only do it once initialised
            self.setModel(self.ior_model, self.mot_model,firstcall=False,updateIOR=True)

    def _setup_ui(self):

        self.gridLayout = QtGui.QGridLayout(self)
        self.taurusForm = TaurusForm(self)


        #form for the standard IOR widget
        self.taurusForm.setWithButtons(False)
        self.gridLayout.addWidget(self.taurusForm, 0, 0, 1, 2)

        #form for the standard motor widget
        self.taurusForm2 = TaurusForm(self)
        self.taurusForm2.setWithButtons(False)
        self.gridLayout.addWidget(self.taurusForm2, 1, 0, 1, 2)

        #form with a custom combo box - can replace the standard IOR widget
        #self.comboBox = TaurusValueComboBox(self)
        #self.comboBox.setAutoApply(True)
        #self.gridLayout.addWidget(self.comboBox, 2, 0, 1, 2)

        #self.label = TaurusLabel(self)
        #self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

    def setModel(self, ior, mot, firstcall=False,updateIOR=False):

        self.ior_model = ior
        self.mot_model = mot
        self.updateIOR = updateIOR
        self.firstcall = firstcall

        #If we triggered a change, have the labels really changed, if so set model
        updated = False
        if self.firstcall or self.updateIOR:

            options = [(option.split(":")[0], option.split(":")[1])
                       for option in (taurus.Attribute(ior+"/Labels").read().value).split()]

            if options != self.options:
                updated = True
                self.options = options
                for opt in self.options:
                    self.dict[opt[0]] = opt[1]
                    #self.comboBox.setValueNames(self.options)

            #set the IOR widget
            try:
                self.taurusForm.setCustomWidgetMap(getattr(tauruscustomsettings,'T_FORM_CUSTOM_WIDGET_MAP',{}))
            except NameError:
                self.taurusForm.setCustomWidgetMap(getattr(TaurusCustomSettings,'T_FORM_CUSTOM_WIDGET_MAP',{}))
            self.taurusForm.setModel([self.ior_model])

            #set the motor widget
            try:
                self.taurusForm2.setCustomWidgetMap(getattr(tauruscustomsettings,'T_FORM_CUSTOM_WIDGET_MAP',{}))
            except NameError:
                self.taurusForm2.setCustomWidgetMap(getattr(TaurusCustomSettings,'T_FORM_CUSTOM_WIDGET_MAP',{}))
            self.taurusForm2.setModel([self.mot_model])

            if self.firstcall:

                #make ior widget auto apply settings
                for widget in self.taurusForm:
                    widget.writeWidget().setAutoApply(True)

                #connect combo box changes to method below
                #self.connect(self.comboBox, QtCore.SIGNAL('currentIndexChanged(const int &)'), self.indexChanged)

                #fill label
                #self.label.setModel(taurus.Attribute(ior+"/Value"))
                #get taurus attribute which is value and also motor pos
                self.position_ior = taurus.Attribute(ior+"/Value")
                #self.position_mot = taurus.Attribute(mot+"/Position")

            #see what index the combo box should have
            #index = self.comboBox.findData(self.position_ior.read().value)
            #self.comboBox.setCurrentIndex(index)


    #def indexChanged(self,index):
        #value = self.dict[str(self.comboBox.currentText())]
        #self.position_ior.write(value)

class MotorConfigPanel(TaurusWidget):

    """Widget for motor"""

    def __init__(self, parent=None):
        TaurusWidget.__init__(self, parent)
        self._setup_ui()

    def _setup_ui(self):

        self.gridLayout = QtGui.QGridLayout(self)
        self.taurusForm = TaurusForm(self)
        self.taurusForm.setWithButtons(False)

        self.gridLayout.addWidget(self.taurusForm, 0, 0, 1, 2)

    def setModel(self, mot):

        attributes = [mot+"/Status",
                      mot+"/State",
                      mot+"/Step_per_unit",
                      mot+"/Offset",
                      mot+"/Sign",
                      mot+"/Position",
                      mot+"/DialPosition",
                      ]

        self.taurusForm.setModel(attributes)


def main():
    from taurus.qt.qtgui.application import TaurusApplication
    import sys

    app = TaurusApplication(sys.argv)
    args = app.get_command_line_args()

    w = MotorPresets()

    if len(args) > 0:

        w.setModel(args[0])
        #app.setCursorFlashTime(0)
        w.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
