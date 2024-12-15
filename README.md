# Battery Management System UI with CAN Integration

This repository contains a Python-based project for managing and visualizing data from a Battery Management System (BMS). The application integrates CAN communication to receive and process real-time data and provides an intuitive PyQt5 user interface for monitoring key parameters like voltages, currents, temperatures, and safety alerts.

## Features

- **CAN Communication**: Implements CAN communication using the `python-can` library to receive data in real-time.
- **Data Decoding**: Converts raw CAN messages into meaningful battery system metrics such as cell voltages, temperatures, and safety statuses.
- **Data Visualization**: Displays processed data through dynamic graphs and tables using PyQt5 and PyQtGraph.
- **Data Logging**: Saves received data into JSON and CSV formats for further analysis.
- **User Interface**: A clean UI to monitor:
  - Cell voltages
  - Temperature readings
  - Safety and protection statuses
  - Current and SOC (State of Charge) levels
  - Log history
- **Customizable Alerts**: Includes sections for safety alerts and configuration statuses.
- **Scalable Design**: Supports future expansions for additional data metrics.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/repository-name.git
2. Install required dependencies
3. Ensure your CAN interface (e.g., Seedstudio CAN module) is set up and connected.

## Usage
1. Run the application:
   ```bash
   python main.py
2. The application initializes the CAN interface and starts reading incoming data from a specified channel (COM10).
3. Navigate through the user interface to explore different data visualizations:
   - **Voltage Measurements**: Click "Show Cell Voltages" to view cell-specific voltage levels.
   - **Temperature Measurements**: Click "Show Temperatures" to monitor thermal data.
   - **Log History**: Access time-stamped logs of received data.

## Dependencies
- Python 3.8 or later
- PyQt5
- PyQtGraph
- python-can
- numpy

## Project Structure
- main.py: Entry point for the application.
- CANMessageReader: Handles CAN communication and data decoding.
- BatteryManagementSystem: Main UI class for displaying BMS metrics.
- CellVoltagesWindow and TemperatureWindow: Sub-windows for visualizing specific parameters.
- Data saving and logging handled via JSON and CSV files.

## Screenshots
![blur](https://github.com/user-attachments/assets/501dd38e-566d-41c5-821c-5bb6d1da06c7)
