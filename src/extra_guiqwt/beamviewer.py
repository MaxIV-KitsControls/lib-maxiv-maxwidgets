from guiqwt.plot import ImageWindow
from guiqwt.tools import CommandTool, DefaultToolbarID

import taurus
from taurus.qt import Qt
from taurus.qt.qtgui.resource import getIcon
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.extra_guiqwt.builder import make

from maxwidgets.extra_guiqwt.ui.ui_CameraSettingsDialog import Ui_CameraSettingsDialog

VIDEO_MODES = {'Y8'  : 0,
               'Y16' : 1}

TRIGGER_MODES = {'INTERNAL' : 0,
                 'EXTERNAL' : 2}

class StartTool(CommandTool):
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(StartTool,self).__init__(manager, "Start",
                                       getIcon(":/actions/media_playback_start.svg"),
                                       toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        bv_dev = self.manager.getModelObj()
        try:
            bv_dev.Start()
        except Exception, e:
            self.manager.handleException(e)
                    

class StopTool(CommandTool):
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(StopTool,self).__init__(manager, "Stop",
                                      getIcon(":/actions/media_playback_pause.svg"),
                                      toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        bv_dev = self.manager.getModelObj()
        try:
            bv_dev.Stop()
        except Exception, e:
            self.manager.handleException(e)
        
        
class SettingsTool(CommandTool):
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(SettingsTool,self).__init__(manager, "Camera Settings...",
                                          getIcon(":/designer/toolbutton.png"),
                                          toolbar_id=toolbar_id)
        self.dialog = CameraSettingsDialog(manager)
        
    def activate_command(self, plot, checked):
        self.dialog.setModel(self.manager.getModel())
        self.dialog.show()


class CameraSettingsDialog(Qt.QDialog):
    
    def __init__(self, parent=None):
        Qt.QDialog.__init__(self, parent)

        self.ui = Ui_CameraSettingsDialog()
        self.ui.setupUi(self) 
        
        self.ui.expTimeLineEdit.setUseParentModel(True)
        self.ui.expTimeLineEdit.setAutoApply(True)
        self.ui.expTimeLineEdit.setModel('/Exposure')

        self.ui.gainLineEdit.setUseParentModel(True)
        self.ui.gainLineEdit.setAutoApply(True)
        self.ui.gainLineEdit.setModel('/Gain')

        self.ui.videoModeComboBox.setUseParentModel(True)
        self.ui.videoModeComboBox.setAutoApply(True)
        self.ui.videoModeComboBox.setModel('/VideoMode')

        self.ui.triggerModeComboBox.setUseParentModel(True)
        self.ui.triggerModeComboBox.setAutoApply(True)
        self.ui.triggerModeComboBox.setModel('/TriggerMode')

        self.ui.videoModeComboBox.setValueNames(VIDEO_MODES.items())
        self.ui.triggerModeComboBox.setValueNames(TRIGGER_MODES.items())

    def setModel(self, model):
        self.ui.taurusWidget.setModel(model)


class BeamViewer(ImageWindow, TaurusBaseWidget):
    
    def __init__(self, *args, **kwargs):
        self.call__init__(ImageWindow, *args, **kwargs)
        self.call__init__(TaurusBaseWidget, self.__class__.__name__)
        self.image = None
        
    def register_tools(self):
        self.add_tool(StartTool)
        self.add_tool(StopTool)
        self.add_tool(SettingsTool)
        self.add_separator_tool()
        self.register_standard_tools()
        self.add_separator_tool()
        self.register_image_tools()
        self.add_separator_tool()
        self.register_other_tools()
        self.get_default_tool().activate()
                
    def getModelClass(self):
        return taurus.core.TaurusDevice

    def setModel(self, model):
        TaurusBaseWidget.setModel(self, model)

        plot = self.get_plot()
        if self.image is not None:
            plot.del_item(self.image)
        
        self.image = make.image(taurusmodel='%s/%s' % (model, 'VideoImage'))
        plot.add_item(self.image)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['group'] = 'MAX-lab Taurus Widgets'
        ret['module'] = 'maxwidgets.extra_guiqwt'
        ret['icon'] = ':/designer/qwtplot.png'
        return ret

def main():
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    import sys

    parser = argparse.get_taurus_parser()
    parser.usage = "%prog [options] <BeamViewer device>"

    app = TaurusApplication(sys.argv, cmd_line_parser=parser, 
                            app_name="BeamViewer", app_version="1.0")
        
    args = app.get_command_line_args()

    widget = BeamViewer(toolbar=True)

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
                
    widget.setModel(args[0])
    widget.show()
        
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()