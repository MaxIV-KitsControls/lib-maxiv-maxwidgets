import PyTango
import sys
try:
    from taurus.qt import Qt, QtGui
except ImportError:
    from taurus.external.qt import Qt, QtGui
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLed
from taurus.qt.qtgui.input import TaurusValueLineEdit
from taurus.qt.qtgui.panel import TaurusDevicePanel
from taurus.qt.qtgui.panel.taurusvalue import \
    TaurusValue, ExpandingLabel, DefaultLabelWidget, DefaultUnitsWidget

from taurus.qt.qtgui.dialog import TaurusMessageBox
from functools import partial


class GammaSPCeTVLabelWidget(DefaultLabelWidget):

    def getFormatedToolTip(self, cache=False):
        return self.taurusValueBuddy().getFormatedToolTip(cache)

    def contextMenuEvent(self, event):
        action_display_current = Qt.QAction(self)
        action_display_current.setText('Display Current')
        action_display_current.setCheckable(True)
        action_display_current.setChecked(self.taurusValueBuddy().getDisplayAttr() == 'current')
        slot = partial(self.taurusValueBuddy().setDisplayAttr, 'current')
        self.connect(action_display_current, Qt.SIGNAL('toggled(bool)'), slot)

        action_display_pressure = Qt.QAction(self)
        action_display_pressure.setText('Display Pressure')
        action_display_pressure.setCheckable(True)
        action_display_pressure.setChecked(self.taurusValueBuddy().getDisplayAttr() == 'pressure')
        slot = partial(self.taurusValueBuddy().setDisplayAttr, 'pressure')
        self.connect(action_display_pressure, Qt.SIGNAL('toggled(bool)'), slot)

        action_display_voltage = Qt.QAction(self)
        action_display_voltage.setText('Display Voltage')
        action_display_voltage.setCheckable(True)
        action_display_voltage.setChecked(self.taurusValueBuddy().getDisplayAttr() == 'voltage')
        slot = partial(self.taurusValueBuddy().setDisplayAttr, 'voltage')
        self.connect(action_display_voltage, Qt.SIGNAL('toggled(bool)'), slot) 

        action_device_panel = Qt.QAction(self)
        action_device_panel.setText('Show Device Panel')
        self.connect(action_device_panel, Qt.SIGNAL('triggered()'), self.taurusValueBuddy().showDevicePanel)

        action_start = Qt.QAction(self)
        action_start.setText('Start')
        self.connect(action_start, Qt.SIGNAL('triggered()'), self.taurusValueBuddy().start)

        action_stop = Qt.QAction(self)
        action_stop.setText('Stop')
        self.connect(action_stop, Qt.SIGNAL('triggered()'), self.taurusValueBuddy().stop)

        action_reconnect = Qt.QAction(self)
        action_reconnect.setText('Reconnect')
        self.connect(action_reconnect, Qt.SIGNAL('triggered()'), self.taurusValueBuddy().reconnect)

        menu = Qt.QMenu(self)
        menu.addAction(action_device_panel)
        menu.addSeparator()
        menu.addAction(action_display_pressure)
        menu.addAction(action_display_current)
        menu.addAction(action_display_voltage)
        menu.addSeparator()
        menu.addAction(action_start)
        menu.addAction(action_stop)
        menu.addSeparator()
        menu.addAction(action_reconnect)
        menu.exec_(event.globalPos())
        event.accept()

    def mouseDoubleClickEvent(self, event):
        self.taurusValueBuddy().showDevicePanel()
        event.accept()


class GammaSPCeTVReadWidget(TaurusWidget):

    def __init__(self, *args):
        TaurusWidget.__init__(self, *args)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)

        self.led = TaurusLed(self)
        self.led.setUseParentModel(True)
        self.led.setModel('/State')
        self.led.getFormatedToolTip = self.getFormatedToolTip
        self.led.setSizePolicy(Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)

        self.label = ExpandingLabel()
        self.label.setUseParentModel(True)

        self.layout().addWidget(self.led)
        self.layout().addWidget(self.label)

    def getFormatedToolTip(self, cache=False):
        return self.taurusValueBuddy().getFormatedToolTip(cache)

    def setModel(self, model):
        TaurusWidget.setModel(self, model)
        display_attr = self.taurusValueBuddy().getDisplayAttr()
        self.label.setModel('/' + display_attr)


class GammaSPCeTVWriteWidget(TaurusValueLineEdit):

    def setModel(self, model):
        if not model:
            TaurusValueLineEdit.setModel(self, '')
        else:
            display_attr = self.taurusValueBuddy().getDisplayAttr()
            TaurusValueLineEdit.setModel(self, model + '/' + display_attr)


class GammaSPCeTVUnitsWidget(DefaultUnitsWidget):

    def setModel(self, model):
        if not model:
            DefaultUnitsWidget.setModel(self, '')
        else:
            display_attr = self.taurusValueBuddy().getDisplayAttr()
            DefaultUnitsWidget.setModel(self, model + '/' + display_attr)


class GammaSPCeTV(TaurusValue):

    display_attr = 'pressure'

    def __init__(self, parent=None):
        TaurusValue.__init__(self, parent)
        self.setLabelWidgetClass(GammaSPCeTVLabelWidget)
        self.setReadWidgetClass(GammaSPCeTVReadWidget)
        self.setUnitsWidgetClass(GammaSPCeTVUnitsWidget)
        self.setLabelConfig('dev_name')

    def getFormatedToolTip(self, cache=False):
        tool_tip = [('name', self.getModel())]
        status_info = ''

        obj = self.getModelObj()
        if obj is not None:
            try:
                state = obj.getAttribute('State').read().value
                status = obj.getAttribute('Status').read().value
            except PyTango.DevFailed:
                return
            tool_tip.append(('state', state))
            # hack for displaying multi-line status messages
            status_lines = status.split('\n')
            status_info = '<TABLE width="500" border="0" cellpadding="1" cellspacing="0"><TR><TD WIDTH="80" ALIGN="RIGHT" VALIGN="MIDDLE"><B>Status:</B></TD><TD>' + status_lines[0] + '</TD></TR>'
            for status_line in status_lines[1:]:
                status_info += '<TR><TD></TD><TD>' + status_line + '</TD></TR>'
            status_info += '</TABLE>'

        return self.toolTipObjToStr(tool_tip) + status_info

    def getDisplayAttr(self):
        return self.display_attr

    def setDisplayAttr(self, display_attr):
        obj = self.getModelObj()
        if not obj:
            return

        attr = obj.getAttribute(display_attr)
        if not attr:
            return

        self.display_attr = display_attr

        if attr.isReadWrite():
            self.setWriteWidgetClass(GammaSPCeTVWriteWidget)
        else:
            self.setWriteWidgetClass(None)

        self.updateReadWidget()
        self.updateUnitsWidget()

    def showDevicePanel(self):
        dialog = TaurusDevicePanel()
        dialog.setModel(self.getModel())
        dialog.show()

    def start(self):
        dev = self.getModelObj()
        if not dev:
            return
        try:
            dev.Start()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.exec_()

    def stop(self):
        dev = self.getModelObj()
        if not dev:
            return
        try:
            dev.Stop()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.exec_()

    def reconnect(self):
        dev = self.getModelObj()
        if not dev:
            return
        try:
            dev.Init()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.exec_()


def main():
    from taurus.core.util import argparse
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.panel import TaurusForm

    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [model1 [model2 ...]]")

    app = TaurusApplication(cmd_line_parser=parser)

    args = app.get_command_line_args()
    if not args:
        parser.print_usage()
        sys.exit(1)

    form = TaurusForm()
    form.setFormWidget(GammaSPCeTV)
    form.setModel(args)
    form.setModifiableByUser(True)
    form.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
