from taurus.qt.qtgui.input import TaurusValueLineEdit

class MAXLineEdit (TaurusValueLineEdit):

    def _stepBy(self, steps):
        text = str(self.text())
        
        cursor = len(text) - self.cursorPosition()
        
        if not '.' in self.text():
            decimal = 0
        else:
            decimal = len(text) - text.find('.') - 1
 
        if cursor == decimal:
            return
        if cursor == len(text):
            return

        exp = cursor - decimal
        if cursor > decimal:
            exp -= 1
        
        delta = 10**exp

        TaurusValueLineEdit._stepBy(self, steps*delta)
        self.setCursorPosition(len(self.text()) - cursor)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusValueLineEdit.getQtDesignerPluginInfo()
        ret['group']  = 'MAX-lab Taurus Widgets'
        ret['module'] = 'maxwidgets.input'
        return ret

