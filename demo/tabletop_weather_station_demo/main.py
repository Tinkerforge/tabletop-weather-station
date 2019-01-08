#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tabletop Weather Station
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

main.py: Main implementation for Tinkerforge Tabletop Weather Station

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import sys

if hasattr(sys, 'frozen'):
    gui = True
else:
    gui = '--gui' in sys.argv[1:]

if gui:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

    from PyQt4 import QtCore, QtGui

import os
import signal

import logging as log
log.basicConfig(format='%(asctime)s <%(levelname)s> %(message)s', level=log.INFO)

import time
import threading

try:
    import Queue as queue
except:
    import queue

def prepare_package(package_name):
    # from http://www.py2exe.org/index.cgi/WhereAmI
    if hasattr(sys, 'frozen'):
        program_file_raw = sys.executable
    else:
        program_file_raw = __file__

    if sys.hexversion < 0x03000000:
        program_file = unicode(program_file_raw, sys.getfilesystemencoding())
    else:
        program_file = program_file_raw

    program_path = os.path.dirname(os.path.realpath(program_file))

    # add program_path so OpenGL is properly imported
    sys.path.insert(0, program_path)

    # allow the program to be directly started by calling 'main.py'
    # without '<package_name>' being in the path already
    if not package_name in sys.modules:
        head, tail = os.path.split(program_path)

        if not head in sys.path:
            sys.path.insert(0, head)

        if not hasattr(sys, 'frozen'):
            # load and inject in modules list, this allows to have the source in a
            # directory named differently than '<package_name>'
            sys.modules[package_name] = __import__(tail, globals(), locals(), [], -1)

prepare_package('tabletop_weather_station_demo')

from tinkerforge.ip_connection import IPConnection
from tinkerforge.ip_connection import Error
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_air_quality import BrickletAirQuality, GetAllValues
from tinkerforge.bricklet_outdoor_weather import BrickletOutdoorWeather, GetStationData, GetSensorData

from tabletop_weather_station_demo.screens import screen_set_lcd, screen_tab_selected, screen_touch_gesture, screen_update, screen_slider_value, Screen, TIME_SECONDS
from tabletop_weather_station_demo.value_db import ValueDB
from tabletop_weather_station_demo.config import DEMO_VERSION

if gui:
    class GUIHandler(QtCore.QObject, log.Handler):
        qtcb_add = QtCore.pyqtSignal(str)

        def __init__(self, log_edit):
            QtCore.QObject.__init__(self, log_edit)
            log.Handler.__init__(self)

            self.log_edit = log_edit

            self.qtcb_add.connect(self.cb_add)

        def emit(self, record):
            entry = self.format(record)

            self.qtcb_add.emit(entry)

        def cb_add(self, entry):
            self.log_edit.appendPlainText(entry)
            self.log_edit.centerCursor()

class TabletopWeatherStation:
    HOST = "localhost"
    PORT = 4223

    vdb = None
    ipcon = None
    lcd128x64 = None
    air_quality = None
    outdoor_weather = None

    outdoor_weather_station_last_value = {}
    outdoor_weather_sensor_last_value = {}
    air_quality_last_value = None

    graph_resolution_index = None
    logging_period_index = None

    def update_graph_resolution(self):
        index = self.vdb.get_setting('graph_resolution')
        if index == None:
            index = 0
            self.vdb.set_setting('graph_resolution', '1')
        self.graph_resolution_index = int(index)

    def update_logging_period(self):
        index = self.vdb.get_setting('logging_period')
        if index == None:
            index = 0
            self.vdb.set_setting('logging_period', '1')
        self.logging_period_index = int(index)

    def __init__(self, vdb):
        self.vdb = vdb
        self.update_graph_resolution()
        self.update_logging_period()

        # We use this lock to make sure that there is never an update at the
        # same time as a gesture or GUI callback. Otherwise we might draw two
        # different GUI elements at the same time.
        self.update_lock = threading.Lock()

        self.last_air_quality_time = 0
        self.last_station_time = 0
        self.last_sensor_time = 0

        self.ipcon = IPConnection()
        while True:
            try:
                self.ipcon.connect(TabletopWeatherStation.HOST, TabletopWeatherStation.PORT)
                break
            except Error as e:
                log.error('Connection Error: ' + str(e.description))
                time.sleep(1)
            except socket.error as e:
                log.error('Socket error: ' + str(e))
                time.sleep(1)

        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, self.cb_enumerate)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, self.cb_connected)

        while True:
            try:
                self.ipcon.enumerate()
                break
            except Error as e:
                log.error('Enumerate Error: ' + str(e.description))
                time.sleep(1)

    def update(self):
        if self.lcd128x64 == None:
            return

    def cb_touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        self.update_lock.acquire()
        screen_touch_gesture(gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age)
        self.update_lock.release()

    def cb_gui_tab_selected(self, index):
        self.update_lock.acquire()
        screen_tab_selected(index)
        self.update_lock.release()

    def cb_gui_slider_value(self, index, value):
        self.update_lock.acquire()
        screen_slider_value(index, value)
        self.update_lock.release()

    def cb_enumerate(self, uid, connected_uid, position, hardware_version,
                     firmware_version, device_identifier, enumeration_type):
        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            if device_identifier == BrickletLCD128x64.DEVICE_IDENTIFIER:
                try:
                    self.lcd128x64 = BrickletLCD128x64(uid, self.ipcon)
                    self.lcd128x64.set_response_expected_all(True)

                    # Register touch gesture callback to function cb_touch_gesture
                    self.lcd128x64.register_callback(self.lcd128x64.CALLBACK_TOUCH_GESTURE, self.cb_touch_gesture)
                    self.lcd128x64.register_callback(self.lcd128x64.CALLBACK_GUI_TAB_SELECTED, self.cb_gui_tab_selected)
                    self.lcd128x64.register_callback(self.lcd128x64.CALLBACK_GUI_SLIDER_VALUE, self.cb_gui_slider_value)
                    self.lcd128x64.set_touch_gesture_callback_configuration(10, True)
                    self.lcd128x64.set_gui_tab_selected_callback_configuration(100, True)
                    self.lcd128x64.set_gui_slider_value_callback_configuration(100, True)

                    screen_set_lcd(self.lcd128x64)
                    log.info('LCD 128x64 Bricklet initialized')
                except Error as e:
                    log.error('LCD 128x64 Bricklet init failed: ' + str(e.description))
                    self.lcd128x64 = None
                    screen_set_lcd(None)
            elif device_identifier == BrickletAirQuality.DEVICE_IDENTIFIER:
                try:
                    self.air_quality = BrickletAirQuality(uid, self.ipcon)

                    # Update data once directly on initial enumerate
                    self.cb_air_quality_all_values(*self.air_quality.get_all_values())

                    self.air_quality.register_callback(self.air_quality.CALLBACK_ALL_VALUES, self.cb_air_quality_all_values)
                    self.air_quality.set_all_values_callback_configuration(1000, False)

                    log.info('Air Quality Bricklet initialized')
                except Error as e:
                    log.error('Air Quality Bricklet init failed: ' + str(e.description))
                    self.air_quality = None
            elif device_identifier == BrickletOutdoorWeather.DEVICE_IDENTIFIER:
                try:
                    self.outdoor_weather = BrickletOutdoorWeather(uid, self.ipcon)

                    # Update data once directly on initial enumerate
                    for i in self.outdoor_weather.get_station_identifiers():
                        self.cb_outdoor_weather_station_data(i, *self.outdoor_weather.get_station_data(i))

                    for i in self.outdoor_weather.get_sensor_identifiers():
                        self.cb_outdoor_weather_sensor_data(i, *self.outdoor_weather.get_sensor_data(i))

                    self.outdoor_weather.register_callback(self.outdoor_weather.CALLBACK_STATION_DATA, self.cb_outdoor_weather_station_data)
                    self.outdoor_weather.set_station_callback_configuration(True)

                    self.outdoor_weather.register_callback(self.outdoor_weather.CALLBACK_SENSOR_DATA, self.cb_outdoor_weather_sensor_data)
                    self.outdoor_weather.set_sensor_callback_configuration(True)

                    log.info('Outdoor Weather Bricklet initialized')
                except Error as e:
                    log.error('Outdoor Weather Bricklet init failed: ' + str(e.description))
                    self.outdoor_weather = None

    def cb_connected(self, connected_reason):
        if connected_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
            log.info('Auto Reconnect')

            while True:
                try:
                    self.ipcon.enumerate()
                    break
                except Error as e:
                    log.error('Enumerate Error: ' + str(e.description))
                    time.sleep(1)

    def cb_outdoor_weather_station_data(self, identifier, temperature, humidity, wind_speed, gust_speed, rain, wind_direction, battery_low, last_change = 0):
        self.outdoor_weather_station_last_value[identifier] = GetStationData(temperature, humidity, wind_speed, gust_speed, rain, wind_direction, battery_low, last_change)

        now = time.time()
        if now - self.last_station_time >= TIME_SECONDS[self.logging_period_index]:
            self.vdb.add_data_station(identifier, temperature, humidity, wind_speed, gust_speed, rain, wind_direction, battery_low)
            self.last_station_time = now

    def cb_outdoor_weather_sensor_data(self, identifier, temperature, humidity, last_change = 0):
        self.outdoor_weather_sensor_last_value[identifier] = GetSensorData(temperature, humidity, 0)

        now = time.time()
        if now - self.last_sensor_time >= TIME_SECONDS[self.logging_period_index]:
            self.vdb.add_data_sensor(identifier, temperature, humidity)
            self.last_sensor_time = now

    def cb_air_quality_all_values(self, iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure):
        self.air_quality_last_value = GetAllValues(iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure)

        now = time.time()
        if now - self.last_air_quality_time >= TIME_SECONDS[self.logging_period_index]:
            self.vdb.add_data_air_quality(iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure)
            self.last_air_quality_time = now

def loop(tws, run_ref, stop_queue):
    while run_ref[0]:
        tws.update_lock.acquire()

        try:
            screen_update()
        except:
            log.exception('Error during screen update')

        tws.update_lock.release()

        try:
            stop_queue.get(timeout=1.0)
            break
        except queue.Empty:
            pass

def main():
    if gui:
        from tabletop_weather_station_demo.load_pixmap import load_pixmap

        app = QtGui.QApplication(sys.argv)

        main_widget = QtGui.QWidget()
        main_widget.setWindowIcon(QtGui.QIcon(load_pixmap('tabletop_weather_station_demo-icon.png')))
        main_widget.setWindowTitle('Tabletop Weather Station Demo ' + DEMO_VERSION)
        main_widget.setMinimumSize(800, 450)

        button_layout = QtGui.QHBoxLayout()

        main_layout = QtGui.QVBoxLayout()

        log_edit = QtGui.QPlainTextEdit(main_widget)
        log_edit.setReadOnly(True)
        log_edit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        log_edit.setMaximumBlockCount(3000)

        log_handler = GUIHandler(log_edit)
        log_handler.setFormatter(log.Formatter('%(asctime)s <%(levelname)s> %(message)s'))

        log.getLogger().addHandler(log_handler)

        for other in log.getLogger().handlers:
            if other != log_handler:
                log.getLogger().removeHandler(other)

        hide_button = QtGui.QPushButton('Hide', main_widget)
        hide_button.setVisible(QtGui.QSystemTrayIcon.isSystemTrayAvailable())
        hide_button.clicked.connect(main_widget.hide)

        exit_button = QtGui.QPushButton('Exit', main_widget)
        exit_button.clicked.connect(app.quit)

        button_layout.addWidget(hide_button)
        button_layout.addWidget(exit_button)

        main_layout.addWidget(log_edit)
        main_layout.addLayout(button_layout)

        main_widget.setLayout(main_layout)
        main_widget.show()

        def tray_icon_activated(reason):
            if reason != QtGui.QSystemTrayIcon.Context:
                main_widget.show()
                tray_icon.hide()

        tray_icon = QtGui.QSystemTrayIcon(QtGui.QIcon(load_pixmap('tabletop_weather_station_demo-icon.png')), None)
        tray_icon.activated.connect(tray_icon_activated)
        tray_icon.setToolTip('Tabletop Weather Station Demo')

        tray_menu = QtGui.QMenu(None)

        tray_show_action = tray_menu.addAction('Show')
        tray_show_action.triggered.connect(main_widget.show)
        tray_show_action.triggered.connect(tray_icon.hide)

        tray_exit_action = tray_menu.addAction('Exit')
        tray_exit_action.triggered.connect(app.quit)

        tray_icon.setContextMenu(tray_menu)

        hide_button.clicked.connect(tray_icon.show)

    log.info('Tabletop Weather Station: Start')

    vdb = ValueDB()
    tws = TabletopWeatherStation(vdb)
    Screen.tws = tws
    Screen.vdb = vdb
    run_ref = [True]
    stop_queue = queue.Queue()

    if gui:
        thread = threading.Thread(target=loop, args=(tws, run_ref, stop_queue))
        thread.daemon = True
        thread.start()

        def quit_(*args):
            log.info('Exiting')
            app.quit()

        signal.signal(signal.SIGINT, quit_)
        signal.signal(signal.SIGTERM, quit_)
        signal.signal(signal.SIGQUIT, quit_)

        ec = app.exec_()

        run_ref[0] = False
        stop_queue.put(None)
        thread.join(2)
    else:
        def quit_(*args):
            log.info('Exiting')
            run_ref[0] = False
            stop_queue.put(None)

        signal.signal(signal.SIGINT, quit_)
        signal.signal(signal.SIGTERM, quit_)
        signal.signal(signal.SIGQUIT, quit_)

        loop(tws, run_ref, stop_queue)

        ec = 0

    vdb.stop()

    if tws.ipcon != None:
        tws.ipcon.disconnect()

    log.info('Tabletop Weather Station: End')

    sys.exit(ec)

if __name__ == '__main__':
    main()
