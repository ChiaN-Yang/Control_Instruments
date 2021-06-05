# measurement
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.display.widgets import SequencerWidget
from pymeasure.experiment import Results, unique_filename

# control panel
from PyQt5.QtWidgets import QMessageBox     # TODO: when connect fail, pop up message
from connection_interface import Ui_MainWindow
import pyvisa as visa

# Instruments
from pymeasure.instruments.srs.sr830 import SR830
from pymeasure.instruments.signalrecovery.dsp7265 import DSP7265
from pymeasure.instruments.keithley import Keithley2400
from labdrivers.oxford import ips120
# TODO: from labdrivers.oxford import mercuryips_GPIB
import nidaqmx      # TODO: add NI_cDAQ to interface

# my file
from method import *


class ControlPanel(QtWidgets.QMainWindow):
    """this class is for user to connect instruments"""

    def __init__(self):
        super(ControlPanel, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Pre-run functions
        self.visa_list()
        
        # Buttons
        self.ui.button_refresh.clicked.connect(self.visa_list)
        self.ui.button_add.clicked.connect(self.connection)
        self.ui.button_delete.clicked.connect(self.delete_list)
        self.ui.button_start.clicked.connect(self.start)

        # Table connected instruments
        self.ui.table_instrList.setColumnWidth(0, 100)
        self.ui.table_instrList.setColumnWidth(1, 100)
        self.ui.table_instrList.setColumnWidth(2, 100)
        
        # Menu
        self.ui.retranslateUi(self)
        self.ui.actionQuit.setShortcut('Ctrl+Q')
        self.ui.actionQuit.triggered.connect(app.exit)
        
        # Set Window Icon
        self.setWindowIcon(QtGui.QIcon('Qfort.jpg'))

        # all my instruments
        self.Keithley2400_1 = None
        self.Keithley2400_2 = None
        self.Keithley2400_3 = None
        self.lockin_1 = None
        self.lockin_2 = None
        self.lockin_3 = None
        self.DSP7265_1 = None
        self.DSP7265_2 = None
        self.DSP7265_3 = None

    
    def visa_list(self):
        """detect available address"""
        rm = visa.ResourceManager()
        self.pyvisa_list = rm.list_resources()
        self.ui.list_visa.clear()
        self.ui.list_visa.addItems(self.pyvisa_list)
    

    def p_2_info(self,string):
        """put some word in the information board"""
        self.ui.textBrowser.append(str(string))
        

    def connection(self):
        """add instruments into table_instrList"""
        # Get info from lists
        self.Ins_VISA_add = self.ui.list_visa.currentItem().text()
        self.Ins_type = self.ui.list_type.currentItem().text()
        self.Ins_usage = self.ui.list_usage.currentItem().text()
        self.Ins_name = self.ui.enter_name.text()
    
        # Check existance
        if self.ui.table_instrList.findItems(self.Ins_VISA_add,QtCore.Qt.MatchExactly) != [] or \
        self.ui.table_instrList.findItems(self.Ins_name,QtCore.Qt.MatchExactly) != []:
            self.p_2_info('This VISA address or name has been used.')

        else:
            if self.Ins_type == 'Lock-in SR830':
                if self.lockin_1 == None:
                    try:
                        self.lockin_1 = SR830(self.Ins_VISA_add)
                        self.add_list(self.lockin_1)
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.lockin_2 == None:
                    try:
                        self.lockin_2 = SR830(self.Ins_VISA_add)
                        self.add_list(self.lockin_2)
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.lockin_3 == None:
                    try:
                        self.lockin_3 = SR830(self.Ins_VISA_add)
                        self.add_list(self.lockin_3)
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                else:
                    self.p_2_info('you already have 3 Lock-in SR830. dont be so greedy.')

            if self.Ins_type == 'Lock-in DSP7265 ':
                pass

            if self.Ins_type == 'Keithley 2400':
                if self.Keithley2400_1 == None:
                    try:
                        self.Keithley2400_1 = Keithley2400(self.Ins_VISA_add)
                        self.add_list(self.Keithley2400_1)
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.Keithley2400_2 == None:
                    try:
                        self.Keithley2400_2 = Keithley2400(self.Ins_VISA_add)
                        self.add_list(self.Keithley2400_2)
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.Keithley2400_3 == None:
                    try:
                        self.Keithley2400_3 = Keithley2400(self.Ins_VISA_add)
                        self.add_list(self.Keithley2400_3)
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                else:
                    self.p_2_info('you already have 3 Keithley2400. dont be so greedy.')

            if self.Ins_type == 'Oxford Instrument IPS120':
                pass

            if self.Ins_type == 'Oxford Instrument mercruy IPS':
                pass

            if self.Ins_type == 'Oxford Instrument mercury ITC':
                pass


    def add_list(self, instr):
        """add instrument info to list"""
        self.p_2_info('%s has been connected successfully.' %self.Ins_type)

        # add INSTRNMENT and NAME
        MainWindow.INSTRS.append(instr)
        MainWindow.NAME.append(self.Ins_name)

        # refresh table_instrList
        self.row_len = self.ui.table_instrList.rowCount() -1
        self.ui.table_instrList.insertRow(self.row_len +1)
        Ins_property = [self.Ins_name, self.Ins_type, self.Ins_VISA_add, self.Ins_usage]
        for i,p in enumerate(Ins_property):
            self.ui.table_instrList.setItem(self.row_len, i, QtWidgets.QTableWidgetItem(p))

        # add METHOD
        if self.Ins_usage == 'output voltage & measure current':
            MainWindow.METHOD.append('Keithley2400_oVrI')
        elif self.Ins_usage == 'output current & measure voltage':
            MainWindow.METHOD.append('Keithley2400_oIrV')


    def delete_list(self):
        """delete instrument info from list"""
        if self.row_len >= 0:
            self.ui.table_instrList.removeRow(self.row_len)
            self.row_len -= 1
            MainWindow.METHOD.pop()
            MainWindow.NAME.pop()
            self.p_2_info('Delete successfully.')
        else:
            self.p_2_info('Can not delete empty item.')


    def start(self):
        """start measure"""
        MainWindow.FILE_NAME = self.ui.enter_proName.text()
        self.window = MainWindow()
        self.window.show()



class MainWindow(ManagedWindow):
    """this class use pymeasure to let user control instruments"""
    # variable from ControlPanel
    INSTRS = []
    METHOD = []
    NAME = []
    FILE_NAME = ''

    def __init__(self):

        if self.METHOD == ['Keithley2400_oVrI', 'Keithley2400_oVrI']:
            procedure = Keithley2400_oVrI_Keithley2400_oVrI
            Keithley2400_oVrI_Keithley2400_oVrI.instrs = self.INSTRS
            INPUT = Keithley2400_oVrI_Keithley2400_oVrI.inputs
            COLUMNS = Keithley2400_oVrI_Keithley2400_oVrI.DATA_COLUMNS

        elif self.METHOD == ['Keithley2400_oIrV']:
            procedure = Keithley2400_oIrV
            Keithley2400_oIrV.instrs = self.INSTRS
            INPUT = Keithley2400_oIrV.inputs
            COLUMNS = Keithley2400_oIrV.DATA_COLUMNS
            
        else :
            print("do not have this method")


        super(MainWindow, self).__init__(
            procedure_class=procedure,
            inputs=INPUT,
            displays=INPUT,
            x_axis=COLUMNS[0],
            y_axis=COLUMNS[1],
            sequencer=True,
            sequencer_inputs=INPUT,
            #sequence_file="gui_sequencer_example_sequence.txt",
            inputs_in_scrollarea=True
        )
        self.setWindowTitle('PyMeas')


    def queue(self, *, procedure=None):
        directory = "./"  # Change this to the desired directory
        filename = unique_filename(directory, prefix = self.FILE_NAME)

        if procedure is None:
            procedure = self.make_procedure()

        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtWidgets.QApplication([]) 
    connect_interface = ControlPanel()
    connect_interface.show()
    sys.exit(app.exec_())
