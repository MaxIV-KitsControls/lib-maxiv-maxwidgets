from taurus.external.qt import Qt, QtGui
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from taurus.core.taurusoperation import WriteAttrOperation
from taurus.core.taurusbasetypes import TaurusEventType
import numpy as np
import PyTango

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
        self.emptyLabel = QtGui.QLabel("")
        self.layout().addWidget(self.emptyLabel)
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
        return np.array([str(le.text()) for le in self._qlineedits]).astype(astype)

    def setArray(self, arr):
        """
        Set the array to be displayed. If no array display "---"
        """
        if arr is None:
            self.emptyLabel.setText("---")
            return
        if len(arr) > 0:
            self.emptyLabel.setText("")
        else:
            self.emptyLabel.setText("---")
        if not isinstance(arr, np.ndarray):
            return
        while len(self._qlineedits) > len(arr):
            self._removeLineEdit()
        while len(arr) > len(self._qlineedits):
            self._addLineEdit()
        for val, lineedit in zip(arr, self._qlineedits):
            lineedit.setText(str(val))

    def setValidator(self, Qvalidator):
        """
        Set int or double validator to make sure user cannot write other letters
        """
        for le in self._qlineedits:
            le.setValidator(Qvalidator)


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

    def _fixnumberofelements(self):
        """
        When first starting or when the device comes alive, we might need to fix the number of elements displayed.
        If the write value has less elements than the readvalue display the readvalue instead.
        """
        try:
            read_value  = self.getModelObj().getValueObj().value
            write_value = self.getModelObj().getValueObj().w_value
            if len(read_value) != len(write_value):
                self.setArray(read_value)
        except (AttributeError, TypeError):
            return


    def setModel(self,model):
        """
        Set model and fix number of elements displayed.
        """
        TaurusBaseWritableWidget.setModel(self, model)
        self._fixnumberofelements()


    def setValue(self, v):
        """
        Set the value in the widget
        """
        self.setArray(v)

    def getValue(self):
        """
        Get the value from the widget, with the same dtype as the read value
        """
        attr_type = self.getModelObj().getValueObj().value.dtype
        arr = self.array(astype=attr_type)
        return arr


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

    def handleEvent(self, evt_src, evt_type, evt_value):
        """
        Adding the validator from here, also if config event, fix the number of elements displayed
        """
        if evt_type == TaurusEventType.Config:
            self._fixnumberofelements()
            self._updateValidator(evt_value)
        TaurusBaseWritableWidget.handleEvent(self, evt_src, evt_type, evt_value)

    def _updateValidator(self, attrinfo):
        '''This method sets a validator depending on the data type
        attrinfo is an AttributeInfoEx object'''
        if PyTango.is_int_type(attrinfo.data_type):
            validator = Qt.QIntValidator(self) #initial range is -2147483648 to 2147483647 (and cannot be set larger)
            self.setValidator(validator)
        elif PyTango.is_float_type(attrinfo.data_type):
            validator= Qt.QDoubleValidator(self)
            self.setValidator(validator)
        else:
            self.setValidator(None)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        attr_name = sys.argv[1]
    else:
        attr_name = "sys/tg_test/1/float_spectrum"
    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QGridLayout()
    w1 = MAXTaurusArrayLineEdit()
    w1.setModel(attr_name)
    l.addWidget(w1,0,0)
    panel.setLayout(l)
    panel.setVisible(True)
    sys.exit(a.exec_())