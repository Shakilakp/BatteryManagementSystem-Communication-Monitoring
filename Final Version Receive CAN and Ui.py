import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QGroupBox, QPushButton, QScrollArea
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
import numpy as np
from collections import deque
import json
import os
import can
import struct
import csv
import time
import sys

# Create a global stop event
stop_event = threading.Event()


class CANMessageReader:
    def __init__(self):
        self.thread = threading.Thread(target=self.receive_can_messages)

    def start(self):
        self.thread.start()

    def receive_can_messages(self):
        cnt = 0
        print('____')
        bus = can.interface.Bus(channel='COM10', interface='seeedstudio', bitrate=125000)
        print("Listening for CAN messages on 'COM10'...")

        try:
            data = []
            while not stop_event.is_set():
                message = bus.recv(1)
                if message:
                    cnt += 1
                    data.extend(str(message).split()[8:])
                if cnt == 15:
                    self.StrToDec(data)
                    data = []
                    cnt = 0

        except KeyboardInterrupt:
            print("\nExiting...")

    def StrToDec(self, hex_strings):
        decoded_numbers = [int(s, 16) for s in hex_strings[:7]]  # Decode uint8_t values
        
        for i in range(7, 53, 2):  # Decode int16_t values
            low_byte = int(hex_strings[i], 16)
            high_byte = int(hex_strings[i + 1], 16)
            combined = (high_byte << 8) | low_byte
            if combined >= 0x8000:  # Convert to signed int16
                combined -= 0x10000
            decoded_numbers.append(combined)
            
        for i in range(53, 71, 2):  # Decode uint16_t values
            low_byte = int(hex_strings[i], 16)
            high_byte = int(hex_strings[i + 1], 16)
            combined = (high_byte << 8) | low_byte
            decoded_numbers.append(combined)
        
        for i in range(71, 77):
            decoded_numbers.append(int(hex_strings[i], 16))

        print(decoded_numbers)
        print(len(decoded_numbers))
        self.CreateJson(decoded_numbers)

    def CreateJson(self, decoded_numbers):
        data_dict = {
            'CellVoltage': decoded_numbers[7:23],
            'Stack_Voltage': decoded_numbers[30],
            'Pack_Voltage': decoded_numbers[31],
            'LD_Voltage': decoded_numbers[32],
            'CC2_current': decoded_numbers[29],
            'Temperature1': decoded_numbers[23],
            'Temperature2': decoded_numbers[24],
            'Temperature3': decoded_numbers[25],
            'Temperature4': decoded_numbers[26],
            'Temperature5': decoded_numbers[27],
            'Temperature6': decoded_numbers[28],
            'soc_char': decoded_numbers[33],
            'value_CB_ACTIVE_CELLS': decoded_numbers[34],
            'value_CBSTATUS1': decoded_numbers[35],
            'value_SafetyAlertA': decoded_numbers[3],
            'value_SafetyStatusA': decoded_numbers[0],
            'value_SafetyAlertB': decoded_numbers[4],
            'value_SafetyStatusB': decoded_numbers[1],
            'value_SafetyAlertC': decoded_numbers[5],
            'value_SafetyStatusC': decoded_numbers[2],
            'value_MANUFACTURINGSTATUS': decoded_numbers[36],
            'value_BatteryStatus': decoded_numbers[37],
            'AlarmBits': decoded_numbers[38],
            'FET_Status': decoded_numbers[6],
            'Date': f"{decoded_numbers[39]}.{decoded_numbers[40]}.{decoded_numbers[41]}",
            'Time': f"{decoded_numbers[42]}.{decoded_numbers[43]}.{decoded_numbers[44]}"
        }
        print(data_dict)

        # Define the directory and filename
        directory = "E:/Documents/University/Dr. Shalchian CAN/Final Documents Project/My test"
        filename = "data.json"
        file_path = os.path.join(directory, filename)

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

        # Write the dictionary to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)

        print(f"Data has been written to {file_path}")

        # Prepare data for CSV
        csv_dict = {f'CellVoltage{i+1}': decoded_numbers[7+i] for i in range(15)}
        csv_dict.update({
            'Stack_Voltage': decoded_numbers[30],
            'Pack_Voltage': decoded_numbers[31],
            'LD_Voltage': decoded_numbers[32],
            'CC2_current': decoded_numbers[29],
            'Temperature1': decoded_numbers[23],
            'Temperature2': decoded_numbers[24],
            'Temperature3': decoded_numbers[25],
            'Temperature4': decoded_numbers[26],
            'Temperature5': decoded_numbers[27],
            'Temperature6': decoded_numbers[28],
            'soc_char': decoded_numbers[33],
            'value_CB_ACTIVE_CELLS': decoded_numbers[34],
            'value_CBSTATUS1': decoded_numbers[35],
            'value_SafetyAlertA': decoded_numbers[3],
            'value_SafetyStatusA': decoded_numbers[0],
            'value_SafetyAlertB': decoded_numbers[4],
            'value_SafetyStatusB': decoded_numbers[1],
            'value_SafetyAlertC': decoded_numbers[5],
            'value_SafetyStatusC': decoded_numbers[2],
            'value_MANUFACTURINGSTATUS': decoded_numbers[36],
            'value_BatteryStatus': decoded_numbers[37],
            'AlarmBits': decoded_numbers[38],
            'FET_Status': decoded_numbers[6],
            'Date': f"{decoded_numbers[39]}.{decoded_numbers[40]}.{decoded_numbers[41]}",
            'Time': f"{decoded_numbers[42]}.{decoded_numbers[43]}.{decoded_numbers[44]}"
        })
        self.CreateCsv(csv_dict)

    def CreateCsv(self, data_dict, csv_file_prefix="C:/Users/Asus/Desktop/Dr. Shalchian CAN/Latest CAN results/My test/CSV Log/output_csv"):
        file_counter = 1
        filename = f"{csv_file_prefix}_{file_counter}.csv"
        os.makedirs(os.path.dirname(csv_file_prefix), exist_ok=True)

        while os.path.exists(filename) and os.path.getsize(filename) >= 10 * 1024 * 1024:  # 10 MB
            file_counter += 1
            filename = f"{csv_file_prefix}_{file_counter}.csv"

        is_new_file = not os.path.exists(filename)

        with open(filename, 'a', newline='') as csvfile:
            fieldnames = data_dict.keys()
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if is_new_file:
                csvwriter.writeheader()
            csvwriter.writerow(data_dict)

    def stop(self):
        stop_event.set()
        self.thread.join()
        



class BMSData:
    def __init__(self):
        self.CellVoltage = [0] * 16
        self.Stack_Voltage = 0
        self.Pack_Voltage = 0
        self.LD_Voltage = 0
        self.CC2_Current = []
        self.Temperature1 = []
        self.Temperature2 = []
        self.Temperature3 = []
        self.Temperature4 = []
        self.value_CB_ACTIVE_CELLS = 0
        self.value_CB_TIME = 0
        self.value_MANUFACTURINGSTATUS = 0
        self.value_SafetyStatusA = 0
        self.value_SafetyStatusB = 0
        self.value_SafetyStatusC = 0
        self.value_SafetyAlertA = 0
        self.value_SafetyAlertB = 0
        self.value_SafetyAlertC = 0
        self.FET_Status = 0
        self.value_BatteryStatus = 0
        self.value_AlarmStatus = 0
        self.value_SOC = 0
        self.Date = ''
        self.Time = ''

class CellVoltagesWindow(QWidget):
    def __init__(self, bms_data):
        super().__init__()
        self.setWindowTitle('Cell Voltages')
        self.setGeometry(200, 200, 700, 500)
        self.bms_data = bms_data

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a plot widget to display cell voltages
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')  # Set background color to white
        layout.addWidget(self.graph_widget)

        self.plot_data()

    def plot_data(self):
        self.graph_widget.clear()
        cell_numbers = list(range(0, 15))
        voltages = []
        for i in range(16):
            if i != 14:
                voltages.append(self.bms_data.CellVoltage[i])

        # Create bar graph item
        bar_graph = pg.BarGraphItem(x=cell_numbers, height=voltages, width=0.8, brush='#3776ab')
        self.graph_widget.addItem(bar_graph)
        self.graph_widget.setYRange(3310, 3330)
        self.graph_widget.setLabel('left', 'Voltage (mV)')
        self.graph_widget.setLabel('bottom', 'Cell Number')
        self.graph_widget.setTitle('Cell Voltages')
        
        # Customize x-axis ticks to show both odd and even cell numbers
        x_axis = self.graph_widget.getAxis('bottom')
        ticks = [(i, str(i+1)) for i in cell_numbers]
        x_axis.setTicks([ticks])
        
        bold_font = QFont()
        bold_font.setBold(True)
        
        # Add text items to show the value of each cell voltage
        for i, voltage in enumerate(voltages):
            text = pg.TextItem(f"{voltage}", anchor=(0.5, -1.5), color='black')
            text.setFont(bold_font)
            self.graph_widget.addItem(text)
            text.setPos(cell_numbers[i], voltage + 3.5)
        
class TemperatureWindow(QWidget):
    def __init__(self, bms_data):
        super().__init__()
        self.setWindowTitle('Temperature Measurements')
        self.setGeometry(100, 200, 1000, 500)  # Increased width for better visibility
        self.bms_data = bms_data

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create plot widgets to display temperatures
        
        self.temperature1_graph_widget = pg.PlotWidget()
        self.temperature2_graph_widget = pg.PlotWidget()
        self.temperature3_graph_widget = pg.PlotWidget()
        self.temperature4_graph_widget = pg.PlotWidget()
        self.temperature1_graph_widget.setBackground('w')
        self.temperature2_graph_widget.setBackground('w')
        self.temperature3_graph_widget.setBackground('w')
        self.temperature4_graph_widget.setBackground('w')

        self.temperature1_graph_widget.setMinimumHeight(150)
        self.temperature2_graph_widget.setMinimumHeight(150)
        self.temperature3_graph_widget.setMinimumHeight(150)
        self.temperature4_graph_widget.setMinimumHeight(150)
        
        layout.addWidget(self.temperature1_graph_widget)
        layout.addWidget(self.temperature2_graph_widget)
        layout.addWidget(self.temperature3_graph_widget)
        layout.addWidget(self.temperature4_graph_widget)
        
        self.plot_data()



    def plot_data(self):
    
        self.temperature1_graph_widget.clear()
        self.temperature2_graph_widget.clear()
        self.temperature3_graph_widget.clear()
        self.temperature4_graph_widget.clear()
        
        
        times = list(range(1, len(self.bms_data.Temperature1) + 1))
        temperature1 = self.bms_data.Temperature1
        temperature2 = self.bms_data.Temperature2
        temperature3 = self.bms_data.Temperature3
        temperature4 = self.bms_data.Temperature4
        
        self.temperature1_graph_widget.plot(times, temperature1, pen=pg.mkPen(color='firebrick', width=2))
        self.temperature2_graph_widget.plot(times, temperature2, pen=pg.mkPen(color='firebrick', width=2))       
        self.temperature3_graph_widget.plot(times, temperature3, pen=pg.mkPen(color='firebrick', width=2))        
        self.temperature4_graph_widget.plot(times, temperature4, pen=pg.mkPen(color='firebrick', width=2))
        
        self.temperature1_graph_widget.setLabel('left', 'Temperature (°C)')
        self.temperature1_graph_widget.setLabel('bottom', 'Time (s)')
        self.temperature1_graph_widget.setTitle('Sensor 1 Temperature')
        
        self.temperature2_graph_widget.setLabel('left', 'Temperature (°C)')
        self.temperature2_graph_widget.setLabel('bottom', 'Time (s)')
        self.temperature2_graph_widget.setTitle('Sensor 2 Temperature')
        
        self.temperature3_graph_widget.setLabel('left', 'Temperature (°C)')
        self.temperature3_graph_widget.setLabel('bottom', 'Time (s)')
        self.temperature3_graph_widget.setTitle('Sensor 3 Temperature')
        
        self.temperature4_graph_widget.setLabel('left', 'Temperature (°C)')
        self.temperature4_graph_widget.setLabel('bottom', 'Time (s)')
        self.temperature4_graph_widget.setTitle('Sensor 4 Temperature')

        
class LogWindow(QWidget):
    def __init__(self, date_time_log):
        super().__init__()
        self.setWindowTitle('Log History')
        self.setGeometry(200, 200, 500, 200)

        self.date_time_log = date_time_log

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QLabel to hold the log text
        self.log_label = QLabel()
        self.log_label.setStyleSheet("font-weight: bold; color: navy; white-space: pre-wrap;")

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.log_label)
        layout.addWidget(self.scroll_area)        
        
    def update_log(self):
        log_text = '\n'.join(self.date_time_log)
        self.log_label.setText(log_text)
        
        # Ensure the scroll bar is adjusted to the bottom
        QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        # Get the vertical scroll bar and set its value to the maximum
        vertical_scroll_bar = self.scroll_area.verticalScrollBar()
        vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())
            
            
class BatteryManagementSystem(QMainWindow):
    def __init__(self, can_reader):
        super().__init__()
        self.setWindowTitle('Battery Management System')
        self.setGeometry(100, 100, 800, 700)  # Adjust the window size as needed

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        self.can_reader = can_reader

        # Initialize BMS data
        self.bms_data = BMSData()

        # Initialize date-time log
        self.date_time_log = []

        # Section titles
        section_titles = [
            'Voltage Measurements', 'Current Measurements', 'Cell and Configuration Data',
            'Temperature Measurements', 'Safety and Protection Status',
            'State and Status Indicators', 'State of Charge (SOC)', 'Time Logs'
        ]

        # Creating the sections with specified titles
        self.sections = []
        for i in range(8):
            section = QGroupBox(section_titles[i])
            section_layout = QVBoxLayout()
            section.setLayout(section_layout)
            section.setStyleSheet("""
                QGroupBox {
                    border: 1px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                }
            """)
            self.sections.append(section)
            self.layout.addWidget(section, i // 4, i % 4)

        # Add items to Voltage Measurements section
        self.add_voltage_measurements()
        
        # Add items to Current Measurements section
        self.add_current_measurements()

        # Add items to Temperature Measurements section        
        self.add_temperature_measurements()
        
        # Add items to Cell & Configuration section
        self.add_conf_data()
        
        # Add items to Safety and Protection Status section
        self.add_safety_status()
        
        # Add items to State and Status Indicators section
        self.add_state_indicators()
        
        # Add items to State of Charge section
        self.add_soc()
        
        # Add items to Timing and Log section
        self.add_log()
        
        # University Logo at the bottom right corner
        self.logo_label = QLabel()
        pixmap = QPixmap('C:/Users/Asus/Desktop/Dr. Shalchian CAN/Latest CAN results/My test/AKUT.svg')  # Replace with your logo path
        pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)  # Resize the logo to width 200
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.layout.addWidget(self.logo_label, 1, 5, 1, 1, Qt.AlignRight | Qt.AlignBottom)
        self.layout.setVerticalSpacing(20)  # Increase vertical spacing between rows
        self.layout.setHorizontalSpacing(20)
        # Timer to update BMS data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second
        

    def add_voltage_measurements(self):
        section = self.sections[0]  # Voltage Measurements section
        
        # 'Show Cell Voltages' button
        show_cell_voltages_btn = QPushButton('Show Cell Voltages')
        show_cell_voltages_btn.clicked.connect(self.show_cell_voltages)
        section.layout().addWidget(show_cell_voltages_btn)
        
        # Create a grid layout for safety status boxes
        grid_layout = QGridLayout()
        section.layout().addLayout(grid_layout)
        
        # Rectangular boxes for voltage values
        voltage_labels = [
            ('Stack Voltage (mV)', 'Stack_Voltage'), 
            ('Pack Voltage (mV)', 'Pack_Voltage'), 
            ('LD Voltage (mV)', 'LD_Voltage')
        ]

        i = 0
        for label, attr_name in voltage_labels:
            box = QGroupBox(label)
            box_layout = QVBoxLayout()
            box.setLayout(box_layout)
            box.setStyleSheet("""
                QGroupBox {
                    border: 1px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex;
                    background-color: #3776ab;
                    color: white;
                }
            """)
            value_label = QLabel('0')
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-weight: bold;")

            box_layout.addWidget(value_label)
            
            # Calculate row and column positions
            row = i // 1
            col = i % 1

            grid_layout.addWidget(box, row, col)
            #section.layout().addWidget(box)  # Add widgets sequentially
            
            # Store the QLabel for updating later
            setattr(self, f'{attr_name}_label', value_label)
            
            i += 1
            

    def show_cell_voltages(self):
        self.cell_voltages_window = CellVoltagesWindow(self.bms_data)
        self.cell_voltages_window.show()
        
    def add_current_measurements(self):
        section = self.sections[1]  # Current Measurements section
        
        # CC2 Current Graph (larger size)
        self.CC2_Current_graph = pg.PlotWidget()
        self.CC2_Current_graph.setBackground('w')
        self.CC2_Current_graph.setMinimumHeight(200)  # Increase height for larger graph
        self.CC2_Current_graph.setMinimumWidth(400)  # Increase height for larger graph
        section.layout().addWidget(self.CC2_Current_graph)

        
    def add_conf_data(self):
        section = self.sections[2] # Cell and Configuration section
        
        # Rectangular boxes for voltage values
        CellConf_labels = [
        ('Manufacturing Status', 'value_MANUFACTURINGSTATUS'),
        ('Cell Being Balanced', 'value_CB_ACTIVE_CELLS'),
        ('Time of Balancing', 'value_CB_TIME')
        ]

        
        for label, attr_name in CellConf_labels:
            box = QGroupBox(label)
            box_layout = QVBoxLayout()
            box.setLayout(box_layout)
            box.setStyleSheet("""
                QGroupBox {
                    border: 1px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex;
                    background-color: olivedrab;
                    color: white;
                }
            """)
            value_label = QLabel('0')
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-weight: bold;")
            
            box_layout.addWidget(value_label)
            section.layout().addWidget(box)
            
            
            # Store the QLabel for updating later
            setattr(self, f'{attr_name}_label', value_label)
        
        
    def add_temperature_measurements(self):
        section = self.sections[3]  # Temperature Measurements section
        
        # 'Show Temperatures' button
        show_temperatures_btn = QPushButton('Show Temperatures')
        show_temperatures_btn.clicked.connect(self.show_temperatures)
        section.layout().addWidget(show_temperatures_btn)

    def show_temperatures(self):
        self.temperature_window = TemperatureWindow(self.bms_data)
        self.temperature_window.show()
        
        
    def add_safety_status(self):
        section = self.sections[4] # Safety and Protection section
        
        # Create a grid layout for safety status boxes
        grid_layout = QGridLayout()
        section.layout().addLayout(grid_layout)
        
        Safety_labels = [
        ('Safety Status A', 'value_SafetyStatusA'),
        ('Safety Status B', 'value_SafetyStatusB'),
        ('Safety Status C', 'value_SafetyStatusC'),
        ('Safety Alert A', 'value_SafetyAlertA'),
        ('Safety Alert B', 'value_SafetyAlertB'),
        ('Safety Alert C', 'value_SafetyAlertC')
        ]
        
        i = 0
        for label, attr_name in Safety_labels:
            box = QGroupBox(label)
            box_layout = QVBoxLayout()
            box.setLayout(box_layout)
            box.setStyleSheet("""
                QGroupBox {
                    border: 1px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex;
                    background-color: rosybrown;
                    color: white;
                }
                QGroupBox::title {
                    subcontrol-position: top center; /* position at the top center */
                }
            """)
            
            value_label = QLabel('0')
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-weight: bold; ")
            
            box_layout.addWidget(value_label)
            
            # Calculate row and column positions
            row = i // 3
            col = i % 3

            grid_layout.addWidget(box, row, col)
            
            # Store the QLabel for updating later
            setattr(self, f'{attr_name}_label', value_label)
            
            i += 1
        
        
    def add_state_indicators(self):
        section = self.sections[5] # State and Status section
        
        # Create a grid layout for safety status boxes
        grid_layout = QGridLayout()
        section.layout().addLayout(grid_layout)
        
        Safety_labels = [
        ('FET Status', 'FET_Status'),
        ('Battery Status', 'value_BatteryStatus'),
        ('Alarm Status', 'value_AlarmStatus')
        ]
        
        i = 0
        for label, attr_name in Safety_labels:
            box = QGroupBox(label)
            box_layout = QVBoxLayout()
            box.setLayout(box_layout)
            box.setStyleSheet("""
                QGroupBox {
                    border: 1px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex;
                    background-color: sienna;
                    color: white;
                }
                QGroupBox::title {
                    subcontrol-position: top center; /* position at the top center */
                }
            """)
            
            value_label = QLabel('0')
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-weight: bold; ")
            
            box_layout.addWidget(value_label)
            
            # Calculate row and column positions
            row = i // 1
            col = i % 1

            grid_layout.addWidget(box, row, col)
            
            # Store the QLabel for updating later
            setattr(self, f'{attr_name}_label', value_label)
            
            i += 1
        
    def add_soc(self):
        section = self.sections[6] # State of Charge section
        
        SOC_labels = [
        ('SOC', 'value_SOC')
        ]
        
        for label, attr_name in SOC_labels:
            box = QGroupBox(label)
            box_layout = QVBoxLayout()
            box.setLayout(box_layout)
            box.setStyleSheet("""
                QGroupBox {
                    border: 1px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex;
                    background-color: goldenrod;
                    color: white;
                }
            """)
            value_label = QLabel('0')
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-weight: bold;")
            
            box_layout.addWidget(value_label)
            section.layout().addWidget(box)
            
            
            # Store the QLabel for updating later
            setattr(self, f'{attr_name}_label', value_label)
            
    def add_log(self):
        section = self.sections[7]  # Time Logs section
        
        log_labels = [
        ('Current Date', 'Date'),
        ('Current Time', 'Time'),
        ]
        
        for label, attr_name in log_labels:
            box = QGroupBox(label)
            box_layout = QVBoxLayout()
            box.setLayout(box_layout)
            box.setStyleSheet("""
                QGroupBox {
                    border: 1px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex;
                    background-color: mediumpurple;
                    color: white;
                }
            """)
            value_label = QLabel('0')
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-weight: bold;")
            
            box_layout.addWidget(value_label)
            section.layout().addWidget(box)
            
            
            # Store the QLabel for updating later
            setattr(self, f'{attr_name}_label', value_label)
        
        # 'Records' button
        show_records_btn = QPushButton('Show Records')
        show_records_btn.clicked.connect(self.show_records)
        section.layout().addWidget(show_records_btn)
        
    def show_records(self):
        self.log_window = LogWindow(self.date_time_log)
        self.log_window.show()
        
           
    def load_data_from_json(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def update_data(self):
        
        data = self.load_data_from_json("E:/Documents/University/Dr. Shalchian CAN/Final Documents Project/My test/data.json")
        
        if data:
            self.bms_data.CellVoltage = data.get("CellVoltage", [0] * 16)
            self.bms_data.Stack_Voltage = data.get("Stack_Voltage", 0)
            self.bms_data.Pack_Voltage = data.get("Pack_Voltage", 0)
            self.bms_data.LD_Voltage = data.get("LD_Voltage", 0)
            self.bms_data.CC2_Current.append(data.get("CC2_current", 0))
            self.bms_data.Temperature1.append(data.get("Temperature1", 0))
            self.bms_data.Temperature2.append(data.get("Temperature2", 0))
            self.bms_data.Temperature3.append(data.get("Temperature3", 0))
            self.bms_data.Temperature4.append(data.get("Temperature5", 0))
            self.bms_data.value_CB_ACTIVE_CELLS = data.get("value_CB_ACTIVE_CELLS", 0)
            self.bms_data.value_CB_ACTIVE_CELLS = data.get("value_CBSTATUS1", 0)
            self.bms_data.value_MANUFACTURINGSTATUS = data.get("value_MANUFACTURINGSTATUS", 0)
            self.bms_data.value_SafetyStatusA = data.get("value_SafetyStatusA", 0)
            self.bms_data.value_SafetyStatusB = data.get("value_SafetyStatusB", 0)
            self.bms_data.value_SafetyStatusC = data.get("value_SafetyStatusC", 0)
            self.bms_data.value_SafetyAlertA = data.get("value_SafetyAlertA", 0)
            self.bms_data.value_SafetyAlertB = data.get("value_SafetyAlertB", 0)
            self.bms_data.value_SafetyAlertC = data.get("value_SafetyAlertC", 0)
            self.bms_data.FET_Status = data.get("FET_Status", 0)
            self.bms_data.value_BatteryStatus = data.get("value_BatteryStatus", 0)
            self.bms_data.value_AlarmStatus = data.get("AlarmBits", 0)
            self.bms_data.value_SOC = data.get("soc_char", 0)
            self.bms_data.Date = data.get("Date", 0)
            self.bms_data.Time = data.get("Time", 0)
            self.date_time_log.append(f"Date: {self.bms_data.Date}    Time: {self.bms_data.Time}")

        # Update GUI labels with new values
        self.update_gui_labels()

    def update_gui_labels(self):
        # Update voltage measurement labels
        self.Stack_Voltage_label.setText(f'{self.bms_data.Stack_Voltage:}')
        self.Pack_Voltage_label.setText(f'{self.bms_data.Pack_Voltage:}')
        self.LD_Voltage_label.setText(f'{self.bms_data.LD_Voltage:}')

        # Update cell voltages labels (if CellVoltagesWindow is open)
        if hasattr(self, 'cell_voltages_window') and self.cell_voltages_window.isVisible():
            self.cell_voltages_window.plot_data()
        

        # Update cc2 current graph with accumulated data
        self.CC2_Current_graph.clear()
        self.CC2_Current_graph.plot(list(range(len(self.bms_data.CC2_Current))), self.bms_data.CC2_Current, pen=pg.mkPen(color='tomato', width=2))
        self.CC2_Current_graph.setLabel('left', 'CC2 Current (A)')
        self.CC2_Current_graph.setLabel('bottom', 'Time (s)')
        self.CC2_Current_graph.setTitle('CC2 Current')
            
        # Update temperature labels (if TemperatureWindow is open)
        if hasattr(self, 'temperature_window') and self.temperature_window.isVisible():
            self.temperature_window.plot_data()
            self.temperature_window.update()
            
        # Update cell configuration labels
        self.value_MANUFACTURINGSTATUS_label.setText(f'{self.bms_data.value_MANUFACTURINGSTATUS:08b}')
        self.value_CB_ACTIVE_CELLS_label.setText(f'{self.bms_data.value_CB_ACTIVE_CELLS:016b}')
        self.value_CB_TIME_label.setText(f'{self.bms_data.value_CB_TIME}')
            
        # Update safety status labels
        self.value_SafetyStatusA_label.setText(f'{self.bms_data.value_SafetyStatusA:08b}')
        self.value_SafetyStatusB_label.setText(f'{self.bms_data.value_SafetyStatusB:08b}')
        self.value_SafetyStatusC_label.setText(f'{self.bms_data.value_SafetyStatusC:08b}')
        self.value_SafetyAlertA_label.setText(f'{self.bms_data.value_SafetyAlertA:08b}')
        self.value_SafetyAlertB_label.setText(f'{self.bms_data.value_SafetyAlertB:08b}')
        self.value_SafetyAlertC_label.setText(f'{self.bms_data.value_SafetyAlertC:08b}')
            
        # Update indicators labels
        self.FET_Status_label.setText(f'{self.bms_data.FET_Status:08b}')
        self.value_BatteryStatus_label.setText(f'{self.bms_data.value_BatteryStatus:016b}')
        self.value_AlarmStatus_label.setText(f'{self.bms_data.value_AlarmStatus:016b}')
            
        # Update SOC labels            
        self.value_SOC_label.setText(f'{self.bms_data.value_SOC/100:.2f}%')
        
        # Update log labels            
        self.Date_label.setText(f'{self.bms_data.Date:}')
        self.Time_label.setText(f'{self.bms_data.Time:}')
        
        # Update the LogWindow if it is visible
        if hasattr(self, 'log_window') and self.log_window.isVisible():
            self.log_window.update_log()
            
    def closeEvent(self, event):
        self.can_reader.stop()
        super().closeEvent(event)
            
    
    
if __name__ == '__main__':
    
    # Start the UI
    app = QApplication(sys.argv)

    # Instantiate the CAN message reader
    can_reader = CANMessageReader()
    can_reader.start()

    window = BatteryManagementSystem(can_reader)
    window.show()
    sys.exit(app.exec_())