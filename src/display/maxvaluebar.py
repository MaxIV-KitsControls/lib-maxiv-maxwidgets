#!/usr/bin/env python

from __future__ import division

from contextlib import contextmanager

import PyTango
import PyQt4.Qt as Qt
from PyQt4 import QtGui, QtCore
from taurus.qt.qtgui.panel import TaurusWidget
from taurus import Configuration

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

    def setValue(self, value, write_value=None):
        if value != self.value:
            print "setValue", value
            self.value = value
            if write_value != self.write_value:
                self.write_value = write_value
            self.repaint()

    def setWriteValue(self, value):
        if value != self.write_value:
            print "setWriteValue", value
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
        for i, tick in enumerate(ticks):
            qp.drawLine(QtCore.QPointF(w, h - i*h/n + self.pad),
                        QtCore.QPointF(w+5, h - i*h/n + self.pad))
            qp.drawText(w+self.pad, h - i*h/n + self.pad + fw/2, str(tick))

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
        fw = max(metrics.width(str(s)) for s in self._get_ticks())
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
    except ValueError:
        return None


class MAXValueBar(TaurusWidget):

    value_trigger = QtCore.pyqtSignal(float, float)
    conf_trigger = QtCore.pyqtSignal()

    _delta = 1

    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent, designMode=designMode)
        self._setup_ui()

        self._value = None

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
        self.conf_trigger.connect(self.updateConfig)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def setModel(self, model):
        TaurusWidget.setModel(self, model)
        self.updateConfig()
        conf = Configuration("%s?configuration" % self.model)
        conf.addListener(lambda *args: self.conf_trigger.emit())

    def _decimalDigits(self, fmt):
        '''returns the number of decimal digits from a format string
        (or None if they are not defined)'''
        try:
            if fmt[-1].lower() in ['f', 'g'] and '.' in fmt:
                return int(fmt[:-1].split('.')[-1])
            else:
                return None
        except:
            return None

    def updateConfig(self):
        print self.model
        conf = Configuration("%s?configuration" % self.model)
        # Note: could be inefficient with lots of redraws?
        self.valuebar.setMaximum(float_or_none(conf.max_value))
        self.valuebar.setMinimum(float_or_none(conf.min_value))
        self.valuebar.setWarningHigh(float_or_none(conf.max_warning))
        self.valuebar.setWarningLow(float_or_none(conf.min_warning))
        self.valuebar.setAlarmHigh(float_or_none(conf.max_alarm))
        self.valuebar.setAlarmLow(float_or_none(conf.min_alarm))

        digits = self._decimalDigits(conf.format)
        if digits:
            self._delta = pow(10, -digits)

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type in (PyTango.EventType.PERIODIC_EVENT,
                        PyTango.EventType.CHANGE_EVENT):
            if (evt_value.value is not None and
                    evt_value.w_value is not None):
                self.value_trigger.emit(evt_value.value, evt_value.w_value)

    def wheelEvent(self, evt):
        # if not self.getEnableWheelEvent() or Qt.QLineEdit.isReadOnly(self):
        #     return Qt.QLineEdit.wheelEvent(self, evt)
        model = self.getModelObj()
        if model is None or not model.isNumeric():
            return Qt.QLineEdit.wheelEvent(self, evt)

        evt.accept()
        numDegrees = evt.delta() / 8
        numSteps = numDegrees / 15
        modifiers = evt.modifiers()
        if modifiers & Qt.Qt.ControlModifier:
            numSteps *= 10
        elif (modifiers & Qt.Qt.AltModifier) and model.isFloat():
            numSteps *= .1

        # change the value by 1 in the least significant digit according
        # to the configured format.
        value = max(self.valuebar.min_value,
                    min(self.valuebar.max_value,
                        self.valuebar.write_value + numSteps*self._delta))
        model.write(value)
        self.valuebar.setWriteValue(value)


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
