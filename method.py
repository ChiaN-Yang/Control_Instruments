from time import sleep
import numpy as np

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

from pymeasure.experiment import Procedure, IntegerParameter, Parameter, \
    FloatParameter


class Keithley2400_oVrI_Keithley2400_oVrI(Procedure):
    """ instrment type       usage
        Keithley2400         outPut voltage & read current
        Keithley2400         outPut voltage & read current """

    instrs = []
    inputs = ['max_voltage', 'min_voltage', 'voltage_step', 'delay', 'cuurent_range', 'other_voltage']

    max_voltage = FloatParameter('Source.Maximum voltage', units='V', default=10)
    min_voltage = FloatParameter('Source.Minimum voltage', units='V', default=-10)
    voltage_step = FloatParameter('Source.voltage Step', units='A', default=0.1)
    delay = FloatParameter('Source.Delay Time', units='ms', default=20)
    cuurent_range = FloatParameter('Cuurent Range', units='V', default=10)
    other_voltage = FloatParameter('Gate.voltage', units='V', default=10)
    
    DATA_COLUMNS = ['Source.Voltage (V)','Source.Current (A)', 'Gate.Voltage (V)', 'Gate.Current (A)']

    def startup(self):
        log.info("Setting up instruments")
        
        self.source = self.instrs[0]
        self.source.reset() #Resets the instrument and clears the queue
        self.source.use_front_terminals() #Enables the front terminals for measurement, and disables the rear terminals.
        self.source.measure_current() #Configures the measurement of voltage.
        sleep(0.1)
        self.source.apply_voltage() #Configures the instrument to apply a source current
        self.source.voltage_range = self.max_voltage
        self.source.compliance_current = self.cuurent_range
        self.source.enable_source() #Enables the source of voltage depending on the configuration of the instrument.
        sleep(0.1) # wait here to give the instrument time to react
        
        self.meter = self.instrs[1]
        self.meter.reset() #Resets the instrument and clears the queue
        self.meter.use_front_terminals() #Enables the front terminals for measurement, and disables the rear terminals.
        self.meter.measure_current() #Configures the measurement of voltage.
        sleep(0.1)
        self.meter.apply_voltage() #Configures the instrument to apply a source current
        self.meter.voltage_range = self.max_voltage
        self.meter.compliance_current = self.cuurent_range
        self.meter.enable_source() #Enables the source of voltage depending on the configuration of the instrument.
        sleep(0.1) # wait here to give the instrument time to react

    def execute(self):
        voltages_up = np.arange(self.min_voltage, self.max_voltage, self.voltage_step)
        voltages_down = np.arange(self.max_voltage, self.min_voltage, -self.voltage_step)
        voltages = np.concatenate((voltages_up, voltages_down))  # Include the reverse
        steps = len(voltages)
        log.info("Starting to sweep through voltage")
        for i, voltage in enumerate(voltages):
            log.debug("Setting the voltage to %g V" % voltage)
            #output voltage
            self.source.source_voltage = voltage
            self.meter.source_voltage = self.other_voltage
    
            sleep(self.delay*1e-3)
            # Read cuurent value
            souce_current = self.source.current
            meter_current = self.meter.current

            data = {
                self.DATA_COLUMNS[0]: voltage,
                self.DATA_COLUMNS[1]: souce_current,
                self.DATA_COLUMNS[2]: self.other_voltage,
                self.DATA_COLUMNS[3]: meter_current
                }
            self.emit('results', data)
            self.emit('progress', 100.*i/steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.source.shutdown()
        self.meter.shutdown()
        log.info("Finished")



class Keithley2400_oIrV(Procedure):
    """ instrment type       usage
        Keithley2400         outPut current & read voltage """

    instrs = []
    inputs = ['max_current', 'min_current', 'current_step', 'delay', 'voltage_range']
    
    max_current = FloatParameter('Maximum Current', units='mA', default=10)
    min_current = FloatParameter('Minimum Current', units='mA', default=-10)
    current_step = FloatParameter('Current Step', units='mA', default=0.1)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    voltage_range = FloatParameter('Voltage Range', units='V', default=10)

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Resistance (Ohm)']

    def startup(self):
        log.info("Setting up instruments")
        
        self.sourcemeter = self.instrs[0]
        self.sourcemeter.reset() #Resets the instrument and clears the queue
        self.sourcemeter.use_front_terminals() #Enables the front terminals for measurement, and disables the rear terminals.
        self.sourcemeter.measure_voltage() #Configures the measurement of voltage.
        sleep(0.1) # wait here to give the instrument time to react
        self.sourcemeter.apply_current() #Configures the instrument to apply a source current
        self.sourcemeter.source_current_range = self.max_current*1e-3  # A
        self.sourcemeter.compliance_voltage = self.voltage_range
        self.sourcemeter.enable_source() #Enables the source of current depending on the configuration of the instrument.
        sleep(2)

    def execute(self):
        currents_up = np.arange(self.min_current, self.max_current, self.current_step)
        currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        currents = np.concatenate((currents_up, currents_down))  # Include the reverse
        currents *= 1e-3  # to mA from A
        steps = len(currents)
        log.info("Starting to sweep through current")
        for i, current in enumerate(currents):
            log.debug("Setting the current to %g A" % current)

            self.sourcemeter.source_current = current
            #self.sourcemeter.reset_buffer() #Resets the buffer.
            sleep(self.delay*1e-3)
            #self.sourcemeter.start_buffer() #Starts the buffer.
            #log.info("Waiting for the buffer to fill with measurements")
            #self.sourcemeter.wait_for_buffer() #Blocks the program, waiting for a full buffer
            
            voltage = self.sourcemeter.voltage # Read voltage value

            if abs(current) <= 1e-10:
                resistance = np.nan
            else:
                resistance = voltage/current
            data = {
                self.DATA_COLUMNS[0]: current,
                self.DATA_COLUMNS[1]: voltage,
                self.DATA_COLUMNS[2]: resistance
                }
            self.emit('results', data)
            self.emit('progress', 100.*i/steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.sourcemeter.shutdown()
        log.info("Finished")