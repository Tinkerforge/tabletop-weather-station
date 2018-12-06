# -*- coding: utf-8 -*-

"""
Tabletop Weather Station Demo
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

value_db.py: Functions for easy access of sqlite database

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

import sqlite3
import os
import threading
import time

try:
    from Queue import Queue, Empty
except:
    from queue import Queue, Empty

class ValueDB:
    air_quality_first_data = None

    def loop(self):
        self.db = sqlite3.connect('tabletop_weather_station.db')
        self.dbc = self.db.cursor()
        self.create()
        
        self.init_lock.release()

        while self.run:
            try:
                func, data = self.func_queue.get(True, 0.25)
                func(*data)
            except Empty:
                pass
        
    def set_setting(self, key, value):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.set_setting, (key, value)))
            return

        self.dbc.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        self.db.commit()

    def get_setting(self, key):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.get_setting, (key,)))
            return self.func_queue_ret.get()

        try:
            self.dbc.execute('SELECT value FROM settings WHERE key = ?', (key,))
            value = self.dbc.fetchone()[0]
            self.func_queue_ret.put(value)
        except:
            self.func_queue_ret.put(None)

    def get_data(self, num, time_resolution, field, table, identifier = None):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.get_data, (num, time_resolution, field, table, identifier)))
            return self.func_queue_ret.get()

        if identifier == None:
            self.dbc.execute('SELECT time/? AS t, AVG({0}) AS value FROM {1} GROUP BY t ORDER BY t DESC LIMIT ?'.format(field, table), (time_resolution, num))
        else:
            self.dbc.execute('SELECT time/? AS t, AVG({0}) AS value FROM {1} WHERE identifier = ? GROUP BY t ORDER BY t DESC LIMIT ?'.format(field, table), (time_resolution, identifier, num))

        values = self.dbc.fetchall()

        ret = [values[-1][1]]*(num-len(values))
        for value in reversed(values):
            ret.append(value[1])
        
        self.func_queue_ret.put(ret)

    def get_data_air_quality(self, num, time_resolution, field):        
        return self.get_data(num, time_resolution, field, 'air_quality')

    def get_data_station(self, num, time_resolution, field, identifier):
        return self.get_data(num, time_resolution, field, 'station', identifier)

    def get_data_sensor(self, num, time_resolution, field, identifier):
        return self.get_data(num, time_resolution, field, 'sensor', identifier)
    
    def get_data_rain_period_list(self, num, rain_period, identifier):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.get_data_rain_period_list, (num, rain_period, identifier)))
            return self.func_queue_ret.get()

        try:
            # Get rain values in intervals of rain_period
            self.dbc.execute('SELECT time/? AS t, MAX(rain) AS rain FROM station WHERE identifier = ? GROUP BY t ORDER BY t DESC LIMIT ?', (rain_period, identifier, num+1))
            rain_values = self.dbc.fetchall()
            rain_values_fixed = [rain_values[-1][1]]*(num-len(rain_values))

            # Extend data for the case that we don't have enough in the database for one graph yet
            for value in reversed(rain_values):
                rain_values_fixed.append(value[1])

            # Calculate rain values for specific periods (e.g. mm/h)
            rain_period_values = []
            for i in range(1, len(rain_values_fixed)):
                rain_period_values.append(rain_values_fixed[i] - rain_values_fixed[i-1])

            self.func_queue_ret.put(rain_period_values)
        except:
            self.func_queue_ret.put(None)

    def get_data_rain_period(self, identifier, rain_period):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.get_data_rain_period, (identifier, rain_period)))
            return self.func_queue_ret.get()

        try:
            self.dbc.execute('SELECT rain FROM station WHERE identifier = ? ORDER BY time DESC LIMIT 1', (identifier, ))
            period_end_rain = self.dbc.fetchone()[0]

            t = time.time() - rain_period
            self.dbc.execute('SELECT rain, time FROM station WHERE identifier = ? AND time > ? ORDER BY time ASC LIMIT 1', (identifier, t))
            period_start_rain = self.dbc.fetchone()[0]

            period_rain = max(0, period_end_rain - period_start_rain)
            self.func_queue_ret.put(period_rain)
        except:
            self.func_queue_ret.put(None)


    def add_data_air_quality(self, iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.add_data_air_quality, (iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure)))
            return

        self.dbc.execute("""
            INSERT INTO air_quality (iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure) 
            VALUES (?, ?, ?, ?, ?)""",
            (iaq_index, iaq_index_accuracy, temperature, humidity, air_pressure)
        )
        self.db.commit()

    def add_data_station(self, identifier, temperature, humidity, wind_speed, gust_speed, rain, wind_direction, battery_low):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.add_data_station, (identifier, temperature, humidity, wind_speed, gust_speed, rain, wind_direction, battery_low)))
            return

        self.dbc.execute("""
            INSERT INTO station (identifier, temperature, humidity, wind_speed, gust_speed, rain, wind_direction, battery_low) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (identifier, temperature, humidity, wind_speed, gust_speed, rain, wind_direction, battery_low)
        )
        self.db.commit()
    
    def add_data_sensor(self, identifier, temperature, humidity):
        if threading.current_thread() != self.thread:
            self.func_queue.put((self.add_data_sensor, (identifier, temperature, humidity)))
            return
        
        self.dbc.execute("""
            INSERT INTO sensor (identifier, temperature, humidity) 
            VALUES (?, ?, ?)""",
            (identifier, temperature, humidity)
        )
        self.db.commit()

    def create(self):
        self.dbc.execute("""
            CREATE TABLE IF NOT EXISTS air_quality (
                id integer primary key,
                time timestamp default (strftime('%s', 'now')),
                iaq_index integer, 
                iaq_index_accuracy integer, 
                temperature integer, 
                humidity integer, 
                air_pressure integer
            )"""
        )

        self.dbc.execute("""
            CREATE TABLE IF NOT EXISTS station (
                id integer primary key,
                time timestamp default (strftime('%s', 'now')),
                identifier integer,
                temperature integer,
                humidity integer,
                wind_speed integer,
                gust_speed integer,
                rain integer,
                wind_direction integer,
                battery_low integer
            )"""
        )

        self.dbc.execute("""
            CREATE TABLE IF NOT EXISTS sensor (
                id integer primary key,
                time timestamp default (strftime('%s', 'now')),
                identifier integer,
                temperature integer,
                humidity integer
            )"""
        )

        self.dbc.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id integer primary key,
                key text NOT NULL UNIQUE,
                value text
            )"""
        )

        self.db.commit()

    def __init__(self):
        self.run = True
        self.func_queue = Queue()
        self.func_queue_ret = Queue()
        self.init_lock = threading.Lock()
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        self.init_lock.acquire()
        