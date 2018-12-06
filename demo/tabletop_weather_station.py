#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tabletop Weather Station Demo
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

tabletop_weather_station.py: Demo implementation for Tinkerforge
                             Tabletop Weather Station

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

from tinkerforge.ip_connection import IPConnection
from tinkerforge.ip_connection import Error
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_air_quality import BrickletAirQuality, GetAllValues
from tinkerforge.bricklet_outdoor_weather import BrickletOutdoorWeather, GetStationData, GetSensorData

from screens import screen_set_lcd, screen_tab_selected, screen_touch_gesture, screen_update, screen_slider_value, Screen, TIME_SECONDS
from value_db import ValueDB

import logging as log
log.basicConfig(level=log.INFO)

import sys
import time

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
            self.vdb.set_setting('graph_resolution', '0')
        self.graph_resolution_index = int(index)

    def update_logging_period(self):
        index = self.vdb.get_setting('logging_period')
        if index == None:
            index = 0
            self.vdb.set_setting('logging_period', '0')
        self.logging_period_index = int(index)

    def __init__(self, vdb):
        self.vdb = vdb
        self.update_graph_resolution()
        self.update_logging_period()

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
        screen_touch_gesture(gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age)
    
    def cb_gui_tab_selected(self, index):
        screen_tab_selected(index)
    
    def cb_gui_slider_value(self, index, value):
        screen_slider_value(index, value)

    def cb_enumerate(self, uid, connected_uid, position, hardware_version,
                     firmware_version, device_identifier, enumeration_type):
        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            if device_identifier == BrickletLCD128x64.DEVICE_IDENTIFIER:
                try:
                    self.lcd128x64 = BrickletLCD128x64(uid, self.ipcon)
                    
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

    def tick(self):
        return

if __name__ == "__main__":
    log.info('Tabletop Weather Station: Start')

    vdb = ValueDB()
    tws = TabletopWeatherStation(vdb)
    Screen.tws = tws
    Screen.vdb = vdb

    try:
        while True:
            tws.tick()
            screen_update()
            time.sleep(1)
            
    except KeyboardInterrupt:
        if tws.ipcon != None:
            tws.ipcon.disconnect()
        vdb.run = False
        log.info('Tabletop Weather Station: End')