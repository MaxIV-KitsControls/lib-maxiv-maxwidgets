import PyTango
import sys
import taurus
from taurus.qt import Qt, QtGui
from taurus.core import TaurusEventType
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLed
from taurus.qt.qtgui.input import TaurusValueLineEdit
from taurus.qt.qtgui.panel import TaurusDevicePanel
from taurus.qt.qtgui.panel.taurusvalue import \
    TaurusValue, ExpandingLabel, DefaultLabelWidget, DefaultUnitsWidget

from taurus.qt.qtgui.dialog import TaurusMessageBox
from functools import partial


class TaurusAttributeListener(Qt.QObject):
    """
    A class that recieves events on tango attribute changes.
    If that is the case it emits a signal with the event's value.
    """
    def __init__(self):
        Qt.QObject.__init__(self)

    def eventReceived(self, evt_src, evt_type, evt_value):
        if evt_type is TaurusEventType.Error:
            print 'error', evt_src, evt_type, evt_value

        if evt_type not in [TaurusEventType.Change, TaurusEventType.Periodic]:
            return
        value = evt_value.value
        self.emit(Qt.SIGNAL('eventReceived'), value)


class GammaSPCeTVLabelWidget(TaurusWidget):

    def __init__(self, *args):
        TaurusWidget.__init__(self, *args)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)

        self.label = DefaultLabelWidget(self)
        self.label.contextMenuEvent = self.contextMenuEvent
        self.label.getFormatedToolTip = self.getFormatedToolTip

        self.led = TaurusLed(self)
        self.led.setAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
        self.led.contextMenuEvent = self.contextMenuEvent
        self.led.getFormatedToolTip = self.getFormatedToolTip

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.led)

    def setModel(self, model):
        TaurusWidget.setModel(self, model)

        self.label.setModel(model)
        self.label.taurusValueBuddy = self.taurusValueBuddy

        self.led.setModel(model + '/state')

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

    def getFormatedToolTip(self, cache=False):
        tool_tip = [('name', self.getModel())]
        status_info = ''

        obj = self.taurusValueBuddy().getModelObj()
        if obj is not None:
            try:
                state = obj.getAttribute('State').read().value
                status = obj.getAttribute('Status').read().value
            except PyTango.DevFailed:
                return
            tool_tip.append(('state', state))
            status_lines = status.split('\n')
            status_info = '<TABLE width="500" border="0" cellpadding="1" cellspacing="0"><TR><TD WIDTH="80" ALIGN="RIGHT" VALIGN="MIDDLE"><B>Status:</B></TD><TD>' + status_lines[0] + '</TD></TR>'
            for status_line in status_lines[1:]:
                status_info += '<TR><TD></TD><TD>' + status_line + '</TD></TR>'
            status_info += '</TABLE>'

        return self.toolTipObjToStr(tool_tip) + status_info

    def controllerUpdate(self):
        for w in [self.label, self.led]:
            ctrl = w.controller()
            if ctrl is not None:
                ctrl.update()


class GammaSPCeTVReadWidget(ExpandingLabel):

    def setModel(self, model):
        if not model:
            ExpandingLabel.setModel(self, '')
        else:
            display_attr = self.taurusValueBuddy().getDisplayAttr()
            ExpandingLabel.setModel(self, model + '/' + display_attr)


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

        self.device = None
        self.status_listener = None

    def setModel(self, model):
        TaurusValue.setModel(self, model)
        try:
            # disconnect signals
            if self.status_listener is not None:
                self.disconnect(self.status_listener, Qt.SIGNAL('eventReceived'), self.updateStatus)

            # remove listeners
            if self.device is not None:
                self.device.getAttribute('Status').removeListener(self.status_listener)

            if model == '' or model is None:
                self.device = None
                return

            self.device = taurus.Device(model)
            self.status_listener = TaurusAttributeListener()
            self.connect(self.status_listener, Qt.SIGNAL('eventReceived'), self.updateStatus)
            self.device.getAttribute('Status').addListener(self.status_listener)

        except Exception, e:
            self.warning("Exception caught while setting model: %s", repr(e))
            self.device = None
            return

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
        if self.device is None:
            return
        try:
            self.device.Start()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.exec_()

    def stop(self):
        if self.device is None:
            return
        try:
            self.device.Stop()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.exec_()

    def reconnect(self):
        if self.device is None:
            return
        try:
            self.device.Init()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.exec_()

    def updateStatus(self):
        self.labelWidget().controllerUpdate()


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