import taurus

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
        self.acq_status = ''
        self.acq_status_attr = None
        self.frame_number = -1
        self.frame_number_attr = None
                
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
        
        self.unregisterEvents()

        if model is None:
            return

        beamviewer = self.getPluginDevice('beamviewer')
        if not beamviewer:
            return

        image_attr = beamviewer.getAttribute('VideoImage')

        param = ImageParam()
        param.interpolation = 0 # None (nearest pixel)

        self.image = LimaVideoImageItem(param)
        self.image.setModel(image_attr)
        
        self.connect(self.image.getSignaller(),
                     Qt.SIGNAL("dataChanged"),
                     self.update_cross_sections)

        plot.add_item(self.image)
        self.registerEvents()
    
    def registerEvents(self):
        camera = self.getCamera()
        beamviewer = self.getPluginDevice('beamviewer')
        
        self.acq_status_attr = camera.getAttribute('acq_status')
        self.acq_status_attr.addListener(self)
        
        self.frame_number_attr = beamviewer.getAttribute('FrameNumber')
        self.frame_number_attr.addListener(self)

    def unregisterEvents(self):
        if self.acq_status_attr is not None:
            self.acq_status_attr.removeListener(self)
            self.acq_status_attr = None
            
        if self.frame_number_attr is not None:
            self.frame_number_attr.removeListener(self)
            self.frame_number_attr = None

    def handleEvent(self, src, evt_type, evt_value):
        if not hasattr(evt_value, 'value'):
            return

        if src is self.acq_status_attr:
            self.acq_status = evt_value.value

        if src is self.frame_number_attr:
            self.frame_number = evt_value.value
                
        msg = 'Camera status: %s  Frame number: %d' % (self.acq_status, self.frame_number)
        self.statusBar().showMessage(msg)
    
    def getCamera(self):
        return self.getModelObj()
    
    def getPluginDevice(self, name):
        try:
            dev_name = self.getModelObj().getPluginDeviceNameFromType(name)
        except:
            return None
        return taurus.Device(dev_name) if dev_name else None
               
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

    widget = BeamViewer(toolbar=True, options={'show_contrast' : True})

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
                
    widget.setModel(args[0])
    widget.show()
        
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
