from taurus.qt.qtgui.input import TaurusValueSpinBox
from maxwidgets.input import MAXLineEdit

class MAXSpinBox(TaurusValueSpinBox):
    
    def __init__(self, parent = None, designMode = False):
        TaurusValueSpinBox.__init__(self, parent)
        self.setLineEdit(MAXLineEdit(designMode=designMode))

    def stepBy(self, steps):
        self.lineEdit()._stepBy(steps)
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusValueSpinBox.getQtDesignerPluginInfo()
        ret['group']  = 'MAX-lab Taurus Widgets'
        ret['module'] = 'maxwidgets.input'
        return ret

