"""
TaurusCommandButtonPanel - a panel with TaurusCommandButtons

Copyright (C) 2016  MAX IV Laboratory, Lund Sweden.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import json
from taurus.external.qt import Qt, QtGui
from taurus.qt.qtgui.container import TaurusWidget, TaurusScrollArea
from taurus.qt.qtgui.button import TaurusCommandButton


class TaurusCommandButtonPanel(TaurusWidget):
    """
    A taurus panel containing tauruscommandbuttons.
    Creates a button that can be configured by rightclicking on the panel area.

    One button is stored as a dictionary containing the following keys:
        model: Device to run command on
        command: Command to run
        customtext: Custom text for button
        dangermessage: Danger message that popups before executing the command
        parameters:
        timeout:
    If model is not set the button will use parentmodel i.e.
    If all commands in the panel are connected to the same device one could
    setModel on the panel instead.
    """

    def __init__(self, parent=None, designmode=False):
        TaurusWidget.__init__(self, parent, designmode)
        self._modelcommands = []
        self._buttons = []
        self.setLayout(Qt.QGridLayout())

        self.frame = TaurusWidget(self)
        self.frame.setUseParentModel(True)
        self.frame.setLayout(Qt.QGridLayout())

        self.scrollArea = TaurusScrollArea(self)
        self.scrollArea.setUseParentModel(True)
        self.scrollArea.setWidget(self.frame)
        self.scrollArea.setWidgetResizable(True)
        self.layout().addWidget(self.scrollArea)

        # Adding right click edit action
        self.setContextMenuPolicy(Qt.Qt.ActionsContextMenu)
        self.chooseCommandsAction = Qt.QAction('Modify commands', self)
        self.addAction(self.chooseCommandsAction)
        self.connect(self.chooseCommandsAction,
                     Qt.SIGNAL("triggered()"),
                     self.chooseCommands)

        self.setModifiableByUser(True)

        # Make it saveable
        self.registerConfigProperty(self.commandsToConfig,
                                    self.commandsFromConfig,
                                    'commands')

    def setModelCommands(self, modelcommands):
        """
        Set which commandbutton that show up based on
        dictionary of model and command in a list
        """
        self._modelcommands = modelcommands
        self.clearButtons()
        self.populateButtons()

    def clearButtons(self):
        """
        Remove all the tauruscommandbuttons from gui
        """
        for button in self._buttons:
            self.frame.layout().removeWidget(button)
            button.deleteLater()
        self._buttons = []

    def populateButtons(self):
        """
        Create taurus commandbuttons for everything in modelcommand
        """
        for modelcommand in self._modelcommands:
            button = TaurusCommandButton(self.frame)
            button.setCommand(modelcommand['command'])
            if 'model' in modelcommand:
                button.setModel(modelcommand['model'])
            else:
                button.setUseParentModel(True)
            if 'customtext' in modelcommand:
                button.setCustomText(modelcommand['customtext'])
            if 'dangermessage' in modelcommand:
                button.setDangerMessage(modelcommand['dangermessage'])
            if 'parameters' in modelcommand:
                button.setParameters(modelcommand['parameters'])
            if 'timeout' in modelcommand:
                button.setTimeout(modelcommand['timeout'])
            self.connect(button,
                         Qt.SIGNAL('commandExecuted'),
                         self.onCommandExectued)
            # Make button expand vertically
            button.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                 QtGui.QSizePolicy.Expanding)
            self.frame.layout().addWidget(button)
            self._buttons.append(button)

    def chooseCommands(self):
        """
        Display a dialog that allows user to select which commands to be
        represented in the panel.
        If this panel gets used we could make a nicer dialog
        """
        if len(self._modelcommands) > 0:
            modelcommands = self._modelcommands
        else:
            modelcommands = [{'model': 'sys/tg_test/1', 'command': 'DevVoid'}]

        cmdstr = json.dumps(modelcommands)
        text, ok = QtGui.QInputDialog.getText(None,
                                              'Enter commands json dict',
                                              'Enter dicts in a list: <br>' +
                                              'Dict contents:<br>' +
                                              'model, command <br>' +
                                              'Optional dict keys: ' +
                                              'customtext, dangermessage, ' +
                                              'parameters, timeout',
                                              QtGui.QLineEdit.Normal,
                                              cmdstr)
        if ok:
            newmodelcommands = json.loads(text)
            self.setModelCommands(newmodelcommands)

    def commandsToConfig(self):
        """
        Serialize and the commands dict
        """
        return json.dumps(self._modelcommands)

    def commandsFromConfig(self, config):
        """
        Recreate the commands dictionary
        """
        self.setModelCommands(json.loads(config))

    def onCommandExectued(self, result):
        """
        Slot called when the command is executed
        """
        if result is None:
            print "Command executed and returned None"
            return
        cmdbutton = self.sender()
        output = ('<b>Command:</b> ' + cmdbutton.getCommand() + '<br>' +
                  '<b>Pars:</b> ' + repr(cmdbutton.getParameters()) + '<br>' +
                  '<b>Return Value:</b><br>' + str(result))
        QtGui.QMessageBox.information(None, "Return", output)


if __name__ == "__main__":
    from taurus.qt.qtgui.application import TaurusApplication
    import sys
    app = TaurusApplication()
    dialog = TaurusCommandButtonPanel()
    dialog.show()
    sys.exit(app.exec_())
