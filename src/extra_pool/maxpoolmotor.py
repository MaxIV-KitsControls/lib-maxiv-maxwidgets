#!/usr/bin/env python

from taurus.qt.qtgui.container import TaurusWidget
from sardana.taurus.qt.qtgui.extra_pool import PoolMotorTV

class MaxPoolMotorTV(PoolMotorTV):
    """MaxIV implementation of PoolMotorTV removing polling."""

    def __init__(self, parent=None, designMode=False):
        PoolMotorTV.__init__(self)

    def showEvent(self, event):
        """Overwrite the showEvent method from PoolMotorSlim."""

        TaurusWidget.showEvent(self, event)
        try:
            self.motor_dev.getAttribute('Position').enablePolling(force=False)
        except AttributeError, e:
            self.debug('Error in showEvent: %s', repr(e))


def main():
    import sys
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

    widgetMap = {'Motor': (MaxPoolMotorTV),
                 'SimuMotor': (MaxPoolMotorTV),
                 'PseudoMotor': (MaxPoolMotorTV)
        }
    form = TaurusForm()
    form.setCustomWidgetMap(widgetMap)
    form.setModel(args)
    form.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

