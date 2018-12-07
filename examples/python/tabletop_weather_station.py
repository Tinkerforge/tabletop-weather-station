#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import logging as log
log.basicConfig(level=log.INFO)

from tinkerforge.ip_connection import IPConnection
from tinkerforge.ip_connection import Error
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_air_quality import BrickletAirQuality

class WeatherStation:
    HOST = "localhost"
    PORT = 4223

    ipcon = None
    lcd = None
    air_quality = None

    def __init__(self):
        self.ipcon = IPConnection() # Create IP connection

        # Connect to brickd (retry if not possible)
        while True:
            try:
                self.ipcon.connect(WeatherStation.HOST, WeatherStation.PORT)
                break
            except Error as e:
                log.error('Connection Error: ' + str(e.description))
                time.sleep(1)
            except socket.error as e:
                log.error('Socket error: ' + str(e))
                time.sleep(1)

        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE,
                                     self.cb_enumerate)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED,
                                     self.cb_connected)

        # Enumerate Bricks and Bricklets (retry if not possible)
        while True:
            try:
                self.ipcon.enumerate()
                break
            except Error as e:
                log.error('Enumerate Error: ' + str(e.description))
                time.sleep(1)

    def cb_all_values(self, iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure):
        if self.lcd is not None:
            self.lcd.write_line(2, 0, 'IAQ:      {0:6}'.format(iaq_index))
            # 0xF8 == ° on LCD 128x64 charset
            self.lcd.write_line(3, 0, 'Temp:     {0:6.2f} {1}C'.format(temperature/100.0, chr(0xF8)))
            self.lcd.write_line(4, 0, 'Humidity: {0:6.2f} %RH'.format(humidity/100.0))
            self.lcd.write_line(5, 0, 'Air Pres: {0:6.1f} mbar'.format(air_pressure/100.0))

    def cb_enumerate(self, uid, connected_uid, position, hardware_version,
                     firmware_version, device_identifier, enumeration_type):
        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            if device_identifier == BrickletLCD128x64.DEVICE_IDENTIFIER:
                try:
                    # Initialize newly enumerated LCD128x64 Bricklet
                    self.lcd = BrickletLCD128x64(uid, self.ipcon)
                    self.lcd.clear_display()
                    self.lcd.write_line(0, 0, "   Weather Station");
                    log.info('LCD 128x64 initialized')
                except Error as e:
                    log.error('LCD 128x64 init failed: ' + str(e.description))
                    self.lcd = None
            elif device_identifier == BrickletAirQuality.DEVICE_IDENTIFIER:
                try:
                    # Initialize newly enumaratedy Air Quality Bricklet and configure callbacks
                    self.air_quality = BrickletAirQuality(uid, self.ipcon)
                    self.air_quality.set_all_values_callback_configuration(1000, False)
                    self.air_quality.register_callback(self.air_quality.CALLBACK_ALL_VALUES,
                                                       self.cb_all_values)
                    log.info('Air Quality initialized')
                except Error as e:
                    log.error('Air Quality init failed: ' + str(e.description))
                    self.air_quality = None

    def cb_connected(self, connected_reason):
        # Eumerate again after auto-reconnect
        if connected_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
            log.info('Auto Reconnect')

            while True:
                try:
                    self.ipcon.enumerate()
                    break
                except Error as e:
                    log.error('Enumerate Error: ' + str(e.description))
                    time.sleep(1)

if __name__ == "__main__":
    log.info('Weather Station: Start')

    weather_station = WeatherStation()

    if sys.version_info < (3, 0):
        input = raw_input # Compatibility for Python 2.x
    input('Press key to exit\n')

    if weather_station.ipcon != None:
        weather_station.ipcon.disconnect()

    log.info('Weather Station: End')
