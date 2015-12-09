from taurus.external.qt import Qt, QtGui
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from taurus.core.taurusoperation import WriteAttrOperation
import numpy as np

class MAXQArrayLineEdit(QtGui.QWidget):
    """
    Creates a QLineedit for every element in an array, send the pyqtsignals together the same
    way as they would have if they where alone
    """
    textChanged     = Qt.pyqtSignal(object)
    returnPressed   = Qt.pyqtSignal()
    editingFinished = Qt.pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self._qlineedits = []

    def _addLineEdit(self):
        """
        Add one qlineedit to the widget, connect it to the coupled signals
        """
        le = QtGui.QLineEdit()
        self.connect(le, Qt.SIGNAL('textChanged(const QString &)'), self.onTextChanged)
        self.connect(le, Qt.SIGNAL('returnPressed()'), self.onReturnPresesd)
        self.connect(le, Qt.SIGNAL('editingFinished()'), self.onEditingFinsihed)
        self._qlineedits.append(le)
        self.layout().addWidget(le)

    def _removeLineEdit(self):
        """
        Remove one qlineedit from the widget
        """
        le = self._qlineedits.pop()
        self.disconnect(le, Qt.SIGNAL('textChanged(const QString &)'), self.onTextChanged)
        self.disconnect(le, Qt.SIGNAL('returnPressed()'), self.onReturnPresesd)
        self.disconnect(le, Qt.SIGNAL('editingFinished()'), self.onEditingFinsihed)
        le.deleteLater()

    def onTextChanged(self, arg):
        """
        Couple the signals together
        """
        self.textChanged.emit(arg)

    def onReturnPresesd(self):
        """
        Couple the signals together
        """
        self.returnPressed.emit()

    def onEditingFinsihed(self):
        """
        Couple the signals together
        """
        self.editingFinished.emit()

    def array(self, astype=None):
        """
        Returns the edited array
        """
        if astype is None:
            astype = float
        return np.array([le.text() for le in self._qlineedits]).astype(astype)

    def setArray(self, arr):
        """
        Set the array displayed to be
        """
        while len(self._qlineedits) > len(arr):
            self._removeLineEdit()
        while len(arr) > len(self._qlineedits):
            self._addLineEdit()
        for val, lineedit in zip(arr, self._qlineedits):
            lineedit.setText(str(val))

class MAXTaurusArrayLineEdit(MAXQArrayLineEdit, TaurusBaseWritableWidget):
    """Similar to TaurusValueLineEdit but displays one lineedit for each
    item in a 1D array. Suitable for editing e.g. an array of three values x,y,t
    """
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        MAXQArrayLineEdit.__init__(self, parent)
        TaurusBaseWritableWidget.__init__(self, name, designMode=designMode)
        self.textChanged.connect(self.valueChanged)
        self.returnPressed.connect(self.writeValue)
        self.editingFinished.connect(self._onEditingFinished)
        self.connect(self, Qt.SIGNAL('valueChanged'), self.updatePendingOperations)

    def setModel(self,model):
        """
        If the read value has more elements than the write value, we suspect that this is due
         to the device being started with wrong length on the write value. So at start we populate
         with the read value.
        """
        # TODO I'm not happy with this solution and would love another!
        TaurusBaseWritableWidget.setModel(self, model)
        read_value  = self.getModelObj().getValueObj().value
        write_value = self.getModelObj().getValueObj().w_value
        if len(read_value) != len(write_value):
            self.setArray(read_value)

    def setValue(self, v):
        """
        Set the value in the widget
        """
        self.setArray(v)

    def getValue(self):
        """
        Get the value from the widget
        """
        arr = self.array()
        try:
            return arr
        except:
            return None

    def updatePendingOperations(self):
        """
        Copied from taurusvaluelineedit and added np.all to be able to handle numpy arrays
        """
        model = self.getModelObj()
        try:
            model_value = model.getValueObj().w_value
            wigdet_value = self.getValue()
            if np.all(model.areStrValuesEqual(model_value, wigdet_value)) and len(model_value) == len(wigdet_value):
                self._operations = []
            else:
                operation = WriteAttrOperation(model, wigdet_value,
                                               self.getOperationCallbacks())
                operation.setDangerMessage(self.getDangerMessage())
                self._operations = [operation]
        except:
            self._operations = []
        self.updateStyle()

    def updateStyle(self):
        """
        Removed validators that only work for scalar numerics
        """
        TaurusBaseWritableWidget.updateStyle(self)
        color, weight = 'black', 'normal' #default case: the value is in normal range with no pending changes
        if self.hasPendingOperations(): #the value is in valid range with pending changes
            color, weight= 'blue','bold'
        self.setStyleSheet('QLineEdit {color: %s; font-weight: %s}'%(color,weight))

    def _onEditingFinished(self):
        '''slot for performing autoapply only when edition is finished'''
        if self._autoApply:
            self.writeValue()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        attr_name = sys.argv[1]
    else:
        attr_name = "sys/tg_test/1/double_spectrum"
    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QGridLayout()
    w1 = MAXTaurusArrayLineEdit()
    w1.setModel(attr_name)
    l.addWidget(w1,0,0)
    panel.setLayout(l)
    panel.setVisible(True)
    sys.exit(a.exec_())