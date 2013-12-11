from guiqwt.tools import CommandTool, DefaultToolbarID

from taurus.qt import Qt
from taurus.qt.qtgui.resource import getIcon

#from ui.ui_CameraSettingsDialog import Ui_CameraSettingsDialog
from maxwidgets.extra_guiqwt.ui.ui_CameraSettingsDialog import Ui_CameraSettingsDialog

IMAGE_TYPES = {'Bpp8'  : 0,
               'Bpp12' : 4,
               'Bpp16' : 8}

TRIGGER_MODES = {'INTERNAL' : 0,
                 'EXTERNAL' : 2}


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

        self.ui.imageTypeComboBox.setUseParentModel(True)
        self.ui.imageTypeComboBox.setAutoApply(True)
        self.ui.imageTypeComboBox.setModel('/imageType')

        self.ui.triggerModeComboBox.setUseParentModel(True)
        self.ui.triggerModeComboBox.setAutoApply(True)
        self.ui.triggerModeComboBox.setModel('/TriggerMode')

        self.ui.imageTypeComboBox.setValueNames(IMAGE_TYPES.items())
        self.ui.triggerModeComboBox.setValueNames(TRIGGER_MODES.items())

    def setModel(self, model):
        self.ui.taurusWidget.setModel(model)


class StartTool(CommandTool):
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(StartTool, self).__init__(manager, "Start",
                                        getIcon(":/actions/media-playback-start.svg"),
                                        toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        camera = self.manager.getCamera()
        beamviewer = self.manager.getPluginDevice('beamviewer')
        if camera and camera.acq_status != 'Running':
            camera.getAttribute('acq_nb_frames').write(0)
            camera.prepareacq()
            camera.startAcq()
        if beamviewer:
            beamviewer.start()


class StopTool(CommandTool):
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(StopTool,self).__init__(manager, "Stop",
                                      getIcon(":/actions/media-playback-stop.svg"),
                                      toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        camera = self.manager.getCamera()
        beamviewer = self.manager.getPluginDevice('beamviewer')
        if camera and camera.acq_status != 'Ready':
            camera.stopAcq()
        if beamviewer:
            beamviewer.stop()


class SettingsTool(CommandTool):
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(SettingsTool,self).__init__(manager, "Camera Settings...",
                                          getIcon(":/categories/preferences-system.svg"),
                                          toolbar_id=toolbar_id)
        self.settingsDialog = CameraSettingsDialog(manager)
        
    def activate_command(self, plot, checked):
        beamviewer = self.manager.getPluginDevice('beamviewer')
        if not beamviewer:
            return
        self.settingsDialog.setModel(beamviewer.getFullName())
        self.settingsDialog.show()
