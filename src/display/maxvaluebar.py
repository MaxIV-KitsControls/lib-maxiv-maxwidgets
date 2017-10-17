#!/usr/bin/env python

from __future__ import division

from contextlib import contextmanager
from math import log10

import PyQt4.Qt as Qt
from PyQt4 import QtCore, QtGui

import PyTango
from taurus import Configuration
from taurus.core.taurusoperation import WriteAttrOperation
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
try:
    from taurus.qt.qtgui.panel import TaurusWidget
except ImportError:
    from taurus.qt.qtgui.container import TaurusWidget


__all__ = ["MAXValueBar"]

__docformat__ = 'restructuredtext'


class ValueBarWidget(QtGui.QWidget):

    def __init__(self):
        super(ValueBarWidget, self).__init__()

        self.initUI()

    def initUI(self):
        self.setMinimumSize(100, 150)

        self.value = 0
        self.write_value = None

        self.min_value = -100
        self.max_value = 100

        self.warn_high = None
        self.warn_low = None

        self.alarm_low = None
        self.alarm_high = None

        self.pad = 10

    def setValue(self, value):
        if value != self.value:
            self.value = value
            self.repaint()

    def setWriteValue(self, value):
        if value != self.write_value:
            self.write_value = value
            self.repaint()

    def setRange(self, min_value, max_value):
        self.setMinimum(min_value)
        self.setMaximum(max_value)

    def setMinimum(self, value):
        if value is not None:
            self.min_value = value
            self.repaint()

    def setMaximum(self, value):
        if value is not None:
            self.max_value = value
            self.repaint()

    def setWarningLow(self, value):
        self.warn_low = value
        self.repaint()

    def setWarningHigh(self, value):
        self.warn_high = value
        self.repaint()

    def setAlarmLow(self, value):
        self.alarm_low = value
        self.repaint()

    def setAlarmHigh(self, value):
        self.alarm_high = value
        self.repaint()

    def _get_ticks(self):
        if self.min_value < 0 < self.max_value:
            return [self.min_value, 0, self.max_value]
        return [self.min_value, self.max_value]

    def _format_tick(self, tick):
        return "%.1f" % tick

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_widget(qp)
        qp.end()

    def _draw_scale(self, w, h, fh, fw, qp):
        ticks = self._get_ticks()
        n = len(ticks) - 1
        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.drawLine(w, self.pad, w, h+self.pad)
        maxtick = max(ticks)
        mintick = min(ticks)
        height = maxtick - mintick
        scale = h / height
        for i, tick in enumerate(ticks):
            vpos = h - (tick-mintick)*scale
            qp.drawLine(QtCore.QPointF(w, vpos + self.pad),
                        QtCore.QPointF(w+5, vpos + self.pad))
            qp.drawText(w+self.pad, vpos + self.pad + fw/2,
                        self._format_tick(tick))

    @contextmanager
    def _scale(self, qp):
        """A context manager to set up a QPainter with the current scale as
        transform."""
        size = self.size()
        h = size.height() - 2*self.pad

        qp.translate(0, self.pad)
        qp.scale(1, -h/(self.max_value - self.min_value))
        qp.translate(0, -self.max_value)
        yield
        qp.resetTransform()

    def draw_widget(self, qp):

        font = QtGui.QFont('Serif', 7, QtGui.QFont.Light)
        qp.setFont(font)

        metrics = qp.fontMetrics()
        fw = max(metrics.width(self._format_tick(t)) for t in self._get_ticks())
        fh = metrics.height()
        size = self.size()
        w = size.width() - (self.pad + fw)
        h = size.height() - 2*self.pad

        # draw things in the value scale
        with self._scale(qp):

            # frame
            qp.setPen(QtCore.Qt.transparent)
            qp.setBrush(QtGui.QColor(255, 255, 255))
            # need to use e.g. QRectF, or the coordinates get truncated to ints
            qp.drawRect(QtCore.QRectF(0, self.min_value,
                                      w, self.max_value - self.min_value))

            # Warning levels
            if self.warn_high is not None:
                qp.setBrush(QtGui.QColor(255, 200, 150))
                qp.drawRect(QtCore.QRectF(0, self.warn_high,
                                          w, self.max_value - self.warn_high))
            if self.warn_low is not None:
                qp.setBrush(QtGui.QColor(255, 200, 150))
                qp.drawRect(QtCore.QRectF(0, self.min_value,
                                          w, abs(self.min_value - self.warn_low)))

            # Alarm levels
            if self.alarm_high is not None:
                qp.setBrush(QtGui.QColor(255, 170, 170))
                qp.drawRect(QtCore.QRectF(0, self.alarm_high,
                                          w, self.max_value - self.alarm_high))
            if self.alarm_low is not None:
                qp.setBrush(QtGui.QColor(255, 170, 170))
                qp.drawRect(QtCore.QRectF(0, self.min_value,
                                          w, abs(self.min_value - self.alarm_low)))

            # Value bar
            qp.setPen(QtGui.QColor(0, 200, 0))
            qp.setBrush(QtGui.QColor(0, 200, 0))
            qp.drawRect(QtCore.QRectF(10, 0, w-2*self.pad, self.value))

            # Write value line
            qp.setPen(QtGui.QColor(255, 0, 0))
            if self.write_value:
                qp.drawLine(QtCore.QPointF(0, self.write_value),
                            QtCore.QPointF(w, self.write_value))
                # # FIXME: Unfortunately the QPainter transform also transforms the font
                # # size... find some way to write the current value on the axis
                # qp.drawText(w + self.pad, self.write_value,
                #             str(self.write_value))

            # Zero line
            qp.setPen(QtGui.QColor(0, 0, 0))
            if self.min_value < 0 < self.max_value:
                qp.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(w + 5, 0))

        self._draw_scale(w, h, fw, fh, qp)


def float_or_none(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class MAXValueBar(QtGui.QWidget, TaurusBaseWritableWidget):

    value_trigger = QtCore.pyqtSignal(float)
    w_value_trigger = QtCore.pyqtSignal(float)
    conf_trigger = QtCore.pyqtSignal()

    _wheel_delta = 1
    _delta = 1

    def __init__(self, parent=None, designMode=False):
        QtGui.QWidget.__init__(self, parent)
        TaurusBaseWritableWidget.__init__(self, "fisk", taurus_parent=parent, designMode=designMode)
        self._enableWheelEvent = True

        self.w_value = None
        self._setup_ui()

        # self._localModelName = None

        self._throttle_timer = QtCore.QTimer()
        self._throttle_timer.setInterval(200)
        self._throttle_timer.setSingleShot(True)
        self.connect(self._throttle_timer, QtCore.SIGNAL("timeout()"), self._writeValue)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'maxvaluebar'
        ret['group'] = 'MAX-lab Taurus Widgets'
        ret['container'] = ':/designer/frame.png'
        ret['container'] = False
        return ret

    def _setup_ui(self):
        vbox = QtGui.QHBoxLayout(self)
        self.valuebar = ValueBarWidget()
        vbox.addWidget(self.valuebar)
        self.setLayout(vbox)
        self.value_trigger.connect(self.valuebar.setValue)
        self.w_value_trigger.connect(self.valuebar.setWriteValue)
        self.conf_trigger.connect(self.updateConfig)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.conf = None

    def _conf_listener(self, evt_src, evt_type, evt_value):
        self.conf_trigger.emit()

    def _decimalDigits(self, fmt):
        '''returns the number of decimal digits from a format string
        (or None if they are not defined)'''
        # TODO: handle "%e" format too
        try:
            if fmt[-1].lower() in 'fg' and '.' in fmt:
                return int(fmt[:-1].split('.')[-1])
            else:
                return 1
        except:
            return None

    def _make_delta(self, fmt):
        """Return a reasonable step size for the value, taking into
        account the configured format and limits."""
        digits = self._decimalDigits(fmt)
        if digits is not None:
            if fmt.endswith("e"):
                # crude way of getting a scale for a value
                # in scientific notation
                limit = max([abs(float(x))
                             for x in self.conf.getLimits()])
                exponent = int(log10(limit))
            else:
                exponent = 1  # or 0?
            return pow(10, -digits + exponent)

    def updateConfig(self, conf):
        # Note: could be inefficient with lots of redraws?
        self.valuebar.tick_format = conf.format
        self.valuebar.setMaximum(float_or_none(conf.max_value))
        self.valuebar.setMinimum(float_or_none(conf.min_value))
        self.valuebar.setWarningHigh(float_or_none(conf.alarms.max_warning))
        self.valuebar.setWarningLow(float_or_none(conf.alarms.min_warning))
        self.valuebar.setAlarmHigh(float_or_none(conf.alarms.max_alarm))
        self.valuebar.setAlarmLow(float_or_none(conf.alarms.min_alarm))

        # update the wheel delta to correspond to the LSD
        digits = self._decimalDigits(conf.format)
        if digits is not None:
            self._wheel_delta = pow(10, -digits)

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type in (PyTango.EventType.PERIODIC_EVENT,
                        PyTango.EventType.CHANGE_EVENT):
                        # taurus.core.taurusbasetypes.TaurusEventType.Periodic,
                        # taurus.core.taurusbasetypes.TaurusEventType.Change):
            if evt_value.value is not None:
                self.valuebar.setValue(evt_value.value)
            if (evt_value.w_value is not None) and not self._throttle_timer.isActive():
                self.setValue(evt_value.w_value)

        elif evt_type in (PyTango.EventType.ATTR_CONF_EVENT,
                          PyTango.EventType.QUALITY_EVENT):
            self.updateConfig(evt_value)

    def setValue(self, v):
        self.valuebar.setWriteValue(v)

    def getValue(self):
        return self.valuebar.write_value

    @QtCore.pyqtSlot()
    def _writeValue(self, forceApply=True):
        operation = WriteAttrOperation(self.getModelObj(), self.getValue(),
                                       self.getOperationCallbacks())
        operation.setDangerMessage("")
        self._operations = [operation]
        self.writeValue()

    def setEnableWheelEvent(self, b):
        self._enableWheelEvent = b

    def getEnableWheelEvent(self):
        return self._enableWheelEvent

    def resetEnableWheelEvent(self):
        self.setEnableWheelEvent(False)

    def throttledWrite(self, delta):
        """Intead of writing to Tango every time the value changes, we start a
        timer. Writes during the timer will be accumulated and when the timer
        runs out, the last value is written.
        """
        self.setValue(self.getValue() + delta)
        if not self._throttle_timer.isActive():
            self._throttle_timer.start()

    def wheelEvent(self, evt):
        if not self.getEnableWheelEvent():
            return QtGui.QWidget.QWheelEvent(self, evt)
        model = self.getModelObj()
        if model is None or not model.isNumeric():
            return QtGui.QWidget.QWheelEvent(self, evt)

        evt.accept()
        degrees = evt.delta() / 8
        steps = degrees / 15
        modifiers = evt.modifiers()
        if modifiers & Qt.Qt.ControlModifier:
            steps *= 10
        elif (modifiers & Qt.Qt.AltModifier) and model.isFloat():
            steps *= .1

        # change the value by 1 in the least significant digit according
        # to the configured format.
        self.throttledWrite(steps*self._wheel_delta)


def main():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv)
    w = MAXValueBar()
    w.setModel(sys.argv[1])
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
