import taurus
import PyTango

from guiqwt.plot import ImageWindow
from guiqwt.styles import ImageParam

from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.extra_guiqwt.image import TaurusEncodedImageItem
from taurus.qt.qtgui.dialog import TaurusMessageBox

#from tools import StartTool, StopTool, SettingsTool
from maxwidgets.extra_guiqwt.tools import StartTool, StopTool, SettingsTool

def alert_problems(meth):
    def _alert_problems(self, *args, **kws):
        try:
            return meth(self, *args, **kws)
        except Exception:
            dialog = TaurusMessageBox()
            dialog.setError()
            dialog.show()
    return _alert_problems


class LimaVideoImageItem(TaurusEncodedImageItem):
    dtype = None

    def set_data(self, data, **kwargs):
        TaurusEncodedImageItem.set_data(self, data, **kwargs)
        
        if self.data is None:
            return
        
        if self.data.dtype != self.dtype:
            """ Pixel data type has changed. Update LUT range """
            self.dtype = self.data.dtype
            self.set_lut_range(self.get_lut_range_max())


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
  
    @alert_problems
    def setModel(self, model):
        TaurusBaseWidget.setModel(self, model)
        plot = self.get_plot()

        if self.image is not None:
            self.disconnect(self.image.getSignaller(),
                            Qt.SIGNAL("dataChanged"),
                            self.update_cross_sections)
            plot.del_item(self.image)
            del self.image

        if model is None:
            return

        beamviewer = self.getPluginDevice('beamviewer')
        if beamviewer:
            image_attr = '%s/%s' % (beamviewer.name(), 'VideoImage')
        else:
            image_attr = '%s/%s' % (model, 'video_last_image')

        param = ImageParam()
        param.interpolation = 0 # None (nearest pixel)

        self.image = LimaVideoImageItem(param)
        self.image.setModel(image_attr)
        
        self.connect(self.image.getSignaller(),
                     Qt.SIGNAL("dataChanged"),
                     self.update_cross_sections)
        
        plot.add_item(self.image)


    @alert_problems
    def getCamera(self):
        #return self.getModelObj()
        model = self.getModel()
        return PyTango.DeviceProxy(model) if model else None
    
    @alert_problems
    def getPluginDevice(self, name):
        try:
            dev_name = self.getModelObj().getPluginDeviceNameFromType(name)    
        except:
            return None
        #return taurus.Device(dev_name) if dev_name else None
        return PyTango.DeviceProxy(dev_name) if dev_name else None
               
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
    parser.usage = "%prog [options] <LimaCCDs device>"

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
