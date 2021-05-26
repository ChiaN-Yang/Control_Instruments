from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from connection_interface import Ui_MainWindow
import sys
import pyvisa as visa
import numpy as np
# Instruments
from pymeasure.instruments.srs.sr830 import SR830
from pymeasure.instruments.signalrecovery.dsp7265 import DSP7265
from pymeasure.instruments.keithley import Keithley2400
from labdrivers.oxford import ips120
#from labdrivers.oxford import mercuryips_GPIB

# =============================================================================
# All possible output and input options
# =============================================================================
# SR830
SR830_Method = ['Voltage','Frequency','Current','Phase']

# DSP7265
DSP7265_Method = ['Voltage','Frequency','Current','Phase']

# Keithley2400
Keithely_2400_Method = ['Voltage','Current']

# IPS 120
IPS_120_Method = ['Magnetic field','current']

# Mercury IPS 
Mercury_IPS_Method = ['Magnetic field','current']

# Mercury ITC
Mercury_ITC_Method = ['Temperature','Needle valve']

# Dictionary
Method_dict = {'SR830':SR830_Method,'DSP7265':DSP7265_Method, 'Keithley 2400':Keithely_2400_Method, 'IPS 120':IPS_120_Method, 'mercruy IPS':Mercury_IPS_Method, 'mercruy ITC':Mercury_ITC_Method}
# =============================================================================
# Main class
# =============================================================================
class MainWindow_p1(QtWidgets.QMainWindow):
    """this class is for user to connect instruments"""

    INSTRS = []
    METHOD = []
    FILE_NAME = ''

    def __init__(self):
        super(MainWindow_p1, self).__init__()
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
        self.setWindowIcon(QtGui.QIcon('Qfort.png'))

        # all my instruments
        self.Keithley2400_1 = None
        self.Keithley2400_2 = None
        self.Keithley2400_3 = None
        self.lockin_1 = None
        self.lockin_2 = None
        self.lockin_3 = None

        # is finish
        self.setup_finish = False
    
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
        if self.ui.table_instrList.findItems(self.Ins_VISA_add,QtCore.Qt.MatchExactly) != [] or self.ui.table_instrList.findItems(self.Ins_name,QtCore.Qt.MatchExactly) != []:
            self.p_2_info('This VISA address or name has been used.')
        else:

            if self.Ins_type == 'Lock-in SR830':
                if self.lockin_1 == None:
                    try:
                        self.lockin_1 = SR830(self.Ins_VISA_add)
                        self.INSTRS.append(self.lockin_1)
                        self.add_list()
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.lockin_2 == None:
                    try:
                        self.lockin_2 = SR830(self.Ins_VISA_add)
                        self.INSTRS.append(self.lockin_2)
                        self.add_list()
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.lockin_3 == None:
                    try:
                        self.lockin_3 = SR830(self.Ins_VISA_add)
                        self.INSTRS.append(self.lockin_3)
                        self.add_list()
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
                        self.INSTRS.append(self.Keithley2400_1)
                        self.add_list()
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.Keithley2400_2 == None:
                    try:
                        self.Keithley2400_2 = Keithley2400(self.Ins_VISA_add)
                        self.INSTRS.append(self.Keithley2400_2)
                        self.add_list()
                    except visa.VisaIOError or AttributeError:
                        self.p_2_info("%s connect fail" %self.Ins_type)

                elif self.Keithley2400_3 == None:
                    try:
                        self.Keithley2400_3 = Keithley2400(self.Ins_VISA_add)
                        self.INSTRS.append(self.Keithley2400_3)
                        self.add_list()
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

    def add_list(self):
        self.p_2_info('%s has been connected successfully.' %self.Ins_type)
        # refresh table_instrList
        row_len = self.ui.table_instrList.rowCount() + 1
        self.ui.table_instrList.insertRow(row_len)
        Ins_property = [self.Ins_name, self.Ins_type, self.Ins_VISA_add, self.Ins_usage]
        for i,p in enumerate(Ins_property):
            self.ui.table_instrList.setItem(row_len, i+1, QtWidgets.QTableWidgetItem(p))
        # add METHOD
        if self.Ins_usage == 'output voltage & measure current':
            self.METHOD.append('Keithley2400_oVrI')
        elif self.Ins_usage == 'output current & measure voltage':
            self.METHOD.append('Keithley2400_oIrV')


    def delete_list():
        pass

    def start(self):
        self.FILE_NAME = self.ui.enter_proName.text()
        self.setup_finish = True


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow_p1()
    window.show()
    if window.setup_finish == True:
        pass
    sys.exit(app.exec_())