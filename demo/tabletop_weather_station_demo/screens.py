# -*- coding: utf-8 -*-

"""
Tabletop Weather Station
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

screens.py: Weather Station screens (implemented as tabs)

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

from tabletop_weather_station_demo import icons

TIME_SHORTCUTS = ['1s', '2s', '5s', '10s', '30s', '1m', '2m', '5m', '10m', '30m', '1h', '2h', '4h', '8h', '12h', '1d', '10d', '1M']
TIME_STRINGS   = ['1 second', '2 seconds', '5 seconds', '10 seconds', '30 seconds', '1 minute', '2 minutes', '5 minutes', '10 minutes', '30 minutes', '1 hour', '2 hours', '4 hours', '8 hours', '12 hours', '1 day', '10 days', '1 month']
TIME_SECONDS   = [1, 2, 5, 10, 30, 1*60, 2*60, 5*60, 10*60, 30*60, 1*60*60, 2*60*60, 4*60*60, 8*60*60, 12*60*60, 1*60*60*24, 10*60*60*24, 30*60*60*24]

class Screen:
    WIDTH  = 128
    HEIGHT = 64

    lcd    = None
    text   = "TBD"
    icon   = None
    tws    = None
    vdb    = None

    def draw_init(self):
        pass

    def draw_update(self):
        pass

    def touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        pass

    def slider_value(self, index, value):
        pass

    def draw_icon(self, x, y, icon):
        Screen.lcd.write_pixels(x, y, x + icon.WIDTH-1, y + icon.HEIGHT-1, icon.data)

    def scale_data_for_graph(self, data):
        if not data:
            return [0], 0, 0

        ret = []
        value_min = min(data)
        value_max = max(data)
        if value_max-value_min == 0:
            return [127]*len(data), value_min, value_max

        for d in data:
            ret.append(int((d-value_min)*255/(value_max-value_min)))
        return ret, value_min, value_max

class IndoorScreen(Screen):
    text = "Data"
    icon = icons.IconTabData

    def draw_init(self):
        self.iaq_test = 0
        self.draw_icon(6, 4, icons.IconTemperature)
        self.draw_icon(115, 1, icons.IconPressureSmall)
        self.draw_icon(4, 30, icons.IconHumidity)

        self.lcd.draw_text(28, 16, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '\xF8C')
        self.lcd.draw_text(26, 46, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '%RH')
        self.lcd.draw_text(78, 16, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'hPa')
        self.lcd.draw_text(78, 46, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'IAQ')

        self.lcd.draw_line(0, 26, 127, 26, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(60, 0, 60, 52, self.lcd.COLOR_BLACK)
        self.draw_update()

    def draw_update(self):
        if self.tws.air_quality_last_value == None:
            return

        last_value = self.tws.air_quality_last_value
        iaq_value = last_value.iaq_index

        temperature = '{0:.2f}'.format(last_value.temperature/100.0)
        temperature = ' '*(5 - len(temperature)) + temperature
        humidity    = '{0:.2f}'.format(last_value.humidity/100.0)
        humidity    = ' '*(5 - len(humidity)) + humidity
        pressure    = '{0:.2f}'.format(last_value.air_pressure/100.0)
        pressure    = ' '*(5 - len(pressure)) + pressure
        iaq         = '{0}'.format(iaq_value)
        iaq         = ' '*(3 - len(iaq)) + iaq

        self.lcd.draw_text(20, 0,  self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, temperature)
        self.lcd.draw_text(20, 30, self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, humidity)
        self.lcd.draw_text(68, 0,  self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, pressure)
        self.lcd.draw_text(78, 30, self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, iaq)

        if iaq_value < 70:
            self.draw_icon(105, 29, icons.IconThumbsUp)
        elif iaq_value < 140:
            self.draw_icon(105, 29, icons.IconThumbsSide)
        elif iaq_value < 210:
            self.draw_icon(105, 29, icons.IconThumbsDown)
        else:
            self.draw_icon(105, 29, icons.IconHand)

    def touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        pass

class GraphScreen(Screen):
    text = "Graph"
    icon = icons.IconTabGraph

    caption_air_quality  = ['\xF8C', '%RH', 'hPa', 'IAQ']
    formats_air_quality  = ['{0:.1f}', '{0:.1f}', '{0:.1f}', '{0:.0f}']
    divisors_air_quality = [100, 100, 100, 1]
    fields_air_quality   = ['temperature', 'humidity', 'air_pressure', 'iaq_index']

    caption_station      = ['\xF8C', '%RH', 'm/s', 'mm']
    formats_station      = ['{0:.1f}', '{0:.0f}', '{0:.1f}', '{0:.1f}']
    divisors_station     = [10, 1, 10, 10]
    fields_station       = ['temperature', 'humidity', 'wind_speed', 'rain']

    caption_sensor       = ['\xF8C', '%RH']
    formats_sensor       = ['{0:.1f}', '{0:.0f}']
    divisors_sensor      = [10, 1]
    fields_sensor        = ['temperature', 'humidity']

    tables               = ['air_quality', 'station', 'sensor']

    def __init__(self, stations = [], sensors = []):
        self.num      = 0
        self.stations = stations
        self.sensors  = sensors

    def get_value_properties(self):
        num = self.num

        if num < 4:
            return self.caption_air_quality[num], self.formats_air_quality[num], self.divisors_air_quality[num], self.fields_air_quality[num], self.tables[0], None, None
        num -= 4

        for i, station in enumerate(self.stations):
            if num < 4:
                num_icon = (i+1, len(self.stations), icons.rotate_left_90(icons.IconTabStation))
                return self.caption_station[num], self.formats_station[num], self.divisors_station[num], self.fields_station[num], self.tables[1], station, num_icon
            num -= 4

        for i, sensor in enumerate(self.sensors):
            if num < 2:
                num_icon = (i+1, len(self.sensors), icons.rotate_left_90(icons.IconTabSensor))
                return self.caption_sensor[num], self.formats_sensor[num], self.divisors_sensor[num], self.fields_sensor[num], self.tables[2], sensor, num_icon
            num -= 2

        return None # This should never be reachable

    def get_num_graphs(self):
        return len(self.caption_air_quality) + len(self.stations)*len(self.caption_station) + len(self.sensors)*len(self.caption_sensor)

    def draw_init(self):
        def draw_updown(offset):
            self.lcd.draw_line(10+offset, 16, 15+offset, 11, self.num != num_graphs-1)
            self.lcd.draw_line(15+offset, 11, 20+offset, 16, self.num != num_graphs-1)
            self.lcd.draw_line(10+offset, 16 + 19, 15+offset, 11 + 19 + 10, self.num != 0)
            self.lcd.draw_line(15+offset, 11 + 19 + 10, 20+offset, 16 + 19, self.num != 0)

        num_graphs = self.get_num_graphs()
        caption, _, _, _, _, _, num_icon = self.get_value_properties()

        self.lcd.set_gui_graph_configuration(0, self.lcd.GRAPH_TYPE_LINE, 40, 0, 87, 52, TIME_SHORTCUTS[self.tws.graph_resolution_index], caption)

        if num_icon != None:
            # air quality graph
            self.draw_icon(0, 11, icons.IconLeftSwipeUpDownSmall)
            self.lcd.draw_text(32, 18, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, str(num_icon[0]))
            self.lcd.draw_line(32, 26, 37, 28, self.lcd.COLOR_BLACK)
            self.lcd.draw_text(32, 29, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, str(num_icon[1]))
            self.draw_icon(24, 13, num_icon[2])
            draw_updown(0)
        else:
            # station / sensor graph
            self.draw_icon(0, 11, icons.IconLeftSwipeUpDown)
            draw_updown(7)

        self.draw_update()

    def draw_update(self):
        _, fmt, divisor, field, table, identifier, _ = self.get_value_properties()

        # Rain data needs special handling since we need to calculate mm/period while the database has
        # sum of mm over all measurements
        if table == 'station' and field == 'rain':
            data = self.vdb.get_data_rain_period_list(87, TIME_SECONDS[self.tws.graph_resolution_index], identifier)
        else:
            data = self.vdb.get_data(87, TIME_SECONDS[self.tws.graph_resolution_index], field, table, identifier)

        scaled_data, value_min, value_max = self.scale_data_for_graph(data)

        value_min = fmt.format(float(value_min)/divisor)
        value_max = fmt.format(float(value_max)/divisor)
        value_min = ' '*(6 - len(value_min)) + value_min
        value_max = ' '*(6 - len(value_max)) + value_max
        self.lcd.draw_text(2, 0,  self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, value_max)
        self.lcd.draw_text(2, 45, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, value_min)
        self.lcd.set_gui_graph_data(0, scaled_data)

    def touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        num_graphs = self.get_num_graphs()

        if gesture == self.lcd.GESTURE_BOTTOM_TO_TOP:
            if self.num < num_graphs-1:
                self.num += 1
                self.lcd.clear_display()
                self.draw_init()
        elif gesture == self.lcd.GESTURE_TOP_TO_BOTTOM:
            if self.num > 0:
                self.num -= 1
                self.lcd.clear_display()
                self.draw_init()


class SensorScreen(Screen):
    text = 'Senso'
    icon = icons.IconTabSensor

    def __init__(self, keys):
        self.keys = keys
        self.num  = 0

    def draw_init(self):
        self.draw_icon(2, 4, icons.IconTemperature)
        self.draw_icon(50, 4, icons.IconHumidity)
        self.lcd.draw_text(25, 16, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '\xF8C')
        self.lcd.draw_text(70, 16, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '%RH')

        if len(self.keys) >= (self.num + 1)*2:
            self.draw_icon(2, 30, icons.IconTemperature)
            self.draw_icon(50, 30, icons.IconHumidity)
            self.lcd.draw_text(25, 46, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '\xF8C')
            self.lcd.draw_text(70, 46, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '%RH')

        self.lcd.draw_line(0, 26, 127, 26, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(48, 0, 48, 52, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(96, 0, 96, 52, self.lcd.COLOR_BLACK)
        self.draw_update()

    def draw_update(self):
        identifier0 = None
        try:
            identifier0 = self.keys[self.num*2]
            if self.tws.outdoor_weather_sensor_last_value[identifier0] == None:
                return
        except:
            return

        last_value0 = self.tws.outdoor_weather_sensor_last_value[identifier0]

        identifier1 = None
        try:
            identifier1 = self.keys[self.num*2+1]
            last_value1 = self.tws.outdoor_weather_sensor_last_value[identifier1]
        except:
            last_value1 = None

        temperature = '{0:.1f}'.format(last_value0.temperature/10.0)
        temperature = ' '*(4 - len(temperature)) + temperature
        humidity    = '{0:.1f}'.format(last_value0.humidity)
        humidity    = ' '*(2 - len(humidity)) + humidity
        sensor      = '{0}/{1}'.format(self.num*2 + 1, len(self.keys))

        self.lcd.draw_text(18, 0,   self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, temperature)
        self.lcd.draw_text(68, 0,   self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, humidity)
        self.lcd.draw_text(105, 10,  self.lcd.FONT_6X8,  self.lcd.COLOR_BLACK, sensor)

        if last_value1 != None:
            temperature = '{0:.1f}'.format(last_value1.temperature/10.0)
            temperature = ' '*(4 - len(temperature)) + temperature
            humidity    = '{0:.1f}'.format(last_value1.humidity)
            humidity    = ' '*(2 - len(humidity)) + humidity
            sensor      = '{0}/{1}'.format(self.num*2 + 2, len(self.keys))

            self.lcd.draw_text(18, 30,  self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, temperature)
            self.lcd.draw_text(68, 30, self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, humidity)
            self.lcd.draw_text(105, 38,  self.lcd.FONT_6X8,  self.lcd.COLOR_BLACK, sensor)

    def touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        if gesture == self.lcd.GESTURE_BOTTOM_TO_TOP:
            if self.num < ((len(self.keys) + 1)//2) - 1:
                self.num += 1
                self.lcd.clear_display()
                self.draw_init()
        elif gesture == self.lcd.GESTURE_TOP_TO_BOTTOM:
            if self.num > 0:
                self.num -= 1
                self.lcd.clear_display()
                self.draw_init()

class StationScreen(Screen):
    text       = 'Stati'
    icon       = icons.IconTabStation
    directions = [('N', 0, -7), ('NNE', 3, -6), ('NE', 5, -5), ('ENE', 6, -3),
                  ('E', 7, 0), ('ESE', 6, 3), ('SE', 5, 5), ('SSE', 3, 6),
                  ('S', 0, 7), ('SSW', -3, 6), ('SW', -5, 5), ('WSW', -6, 3),
                  ('W', -7, 0), ('WNW', -6, -3), ('NW', -5, -5), ('NNW', -3, -6)]

    def __init__(self, keys):
        self.keys = keys
        self.num  = 0

    def draw_init(self):
        self.draw_icon(2, 4, icons.IconTemperature)
        self.draw_icon(0, 30, icons.IconHumidity)
        self.draw_icon(50, 32, icons.IconRain)

        self.lcd.draw_text(25, 16, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '\xF8C')
        self.lcd.draw_text(23, 46, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '%RH')

        self.lcd.draw_text(70, 16, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'm/s')
        self.lcd.draw_text(68, 46, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'mm/h')

        self.lcd.draw_line(0, 26, 96, 26, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(96, 32, 127, 32, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(96, 42, 127, 42, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(48, 0, 48, 52, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(96, 0, 96, 52, self.lcd.COLOR_BLACK)
        self.draw_update()

    def draw_update(self):
        try:
            identifier = self.keys[self.num]
            if self.tws.outdoor_weather_station_last_value[identifier] == None:
                return
        except:
            return

        last_value  = self.tws.outdoor_weather_station_last_value[identifier]
        # Get rain for period of 60*60 seconds (mm/h)
        period_rain = self.vdb.get_data_rain_period(identifier, 60*60)

        temperature = '{0:.1f}'.format(last_value.temperature/10.0)
        temperature = ' '*(4 - len(temperature)) + temperature
        humidity    = '{0:.1f}'.format(last_value.humidity)
        humidity    = ' '*(2 - len(humidity)) + humidity
        wind_speed  = '{0:.1f}'.format(last_value.wind_speed/10.0)
        wind_speed  = ' '*(4 - len(wind_speed)) + wind_speed

        if period_rain == None:
            period_rain = '  ? '
        else:
            period_rain = '{0:.1f}'.format(period_rain/10.0)
            period_rain = ' '*(4 - len(period_rain)) + period_rain

        direction   = last_value.wind_direction
        battery_low = last_value.battery_low
        station     = '{0}/{1}'.format(self.num + 1, len(self.keys))

        self.lcd.draw_text(18, 0,  self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, temperature)
        self.lcd.draw_text(18, 30, self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, humidity)
        self.lcd.draw_text(16 + 48, 0,  self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, wind_speed)
        self.lcd.draw_text(16 + 48, 30, self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, period_rain)
        self.lcd.draw_text(104, 45, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, station)

        self.draw_icon(98, 0, icons.IconCompass)

        try:
            d, xdiff, ydiff = self.directions[direction]
#            if len(d) == 1:
#                d = ' ' + d + ' '
#            elif len(d) == 2:
#                d = ' ' + d
#            self.lcd.draw_text(104, 33, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, d)
            self.lcd.draw_line(113, 15, 113 + xdiff, 15 + ydiff, True)
        except:
            self.lcd.draw_text(111, 12, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, '?')

        if direction < 8:
            self.draw_icon(50, 4, icons.IconFlagEast)
        else:
            self.draw_icon(50, 4, icons.IconFlagWest)

        if battery_low:
            self.draw_icon(104, 0, icons.IconBatteryEmpty)
        else:
            self.draw_icon(104, 34, icons.IconBatteryFull)

    def touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        if gesture == self.lcd.GESTURE_BOTTOM_TO_TOP:
            if self.num < len(self.keys)-1:
                self.num += 1
                self.lcd.clear_display()
                self.draw_init()
        elif gesture == self.lcd.GESTURE_TOP_TO_BOTTOM:
            if self.num > 0:
                self.num -= 1
                self.lcd.clear_display()
                self.draw_init()

class SettingsScreen(Screen):
    text = "Conf"
    icon = icons.IconTabSettings
    settings = ['Display', 'Graph', 'Logging']

    def __init__(self):
        self.num = 0

    def draw_time_per_pixel(self, index):
        s = '  {0}  '.format(TIME_STRINGS[index])
        self.lcd.draw_text(56 - int(len(s)*6/2), 42, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, s)

    def index_to_slider(self, value):
        return int(round(value*97.0/(len(TIME_STRINGS)-1)))

    def slider_to_index(self, value):
        return int(round(value*(len(TIME_STRINGS)-1)/97.0))

    def draw_init(self):
        self.lcd.draw_text(0, 0, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'Settings: ' + self.settings[self.num])
        self.draw_icon(108, 11, icons.IconRightSwipeUpDown)

        self.lcd.draw_line(108, 16, 113, 11, self.num != len(self.settings)-1)
        self.lcd.draw_line(113, 11, 118, 16, self.num != len(self.settings)-1)
        self.lcd.draw_line(108, 16 + 19, 113, 11 + 19 + 10, self.num != 0)
        self.lcd.draw_line(113, 11 + 19 + 10, 118, 16 + 19, self.num != 0)

        if self.num == 0:
            conf = self.lcd.get_display_configuration()
            brightness = int(conf.backlight*67/100)
            contrast = min(conf.contrast, 67)

            self.lcd.set_gui_slider(0, 30, 10, 75, self.lcd.DIRECTION_HORIZONTAL, brightness)
            self.lcd.draw_text(0, 14, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'Brigh')

            self.lcd.set_gui_slider(1, 30, 32, 75, self.lcd.DIRECTION_HORIZONTAL, contrast)
            self.lcd.draw_text(0, 36, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'Contr')
        elif self.num == 1:
            self.lcd.set_gui_slider(0, 0, 10, 105, self.lcd.DIRECTION_HORIZONTAL, self.index_to_slider(self.tws.graph_resolution_index))
            self.lcd.draw_text(5, 30, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'Graph Resolution')
            self.draw_time_per_pixel(self.tws.graph_resolution_index)
        elif self.num == 2:
            self.lcd.set_gui_slider(0, 0, 10, 105, self.lcd.DIRECTION_HORIZONTAL, self.index_to_slider(self.tws.logging_period_index))
            self.lcd.draw_text(13, 30, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'Logging Period')
            self.draw_time_per_pixel(self.tws.logging_period_index)

    def slider_value(self, index, value):
        if self.num == 0:
            conf = self.lcd.get_display_configuration()

            if index == 0:
                self.lcd.set_display_configuration(conf.contrast, value*100/67, conf.invert, conf.automatic_draw)
            elif index == 1:
                self.lcd.set_display_configuration(value, conf.backlight, conf.invert, conf.automatic_draw)
        elif self.num == 1:
            if index == 0:
                new_res = self.slider_to_index(value)
                if new_res != self.tws.graph_resolution_index:
                    self.tws.graph_resolution_index = new_res
                    self.draw_time_per_pixel(self.tws.graph_resolution_index)
                    self.vdb.set_setting('graph_resolution', str(new_res))
        elif self.num == 2:
            if index == 0:
                new_res = self.slider_to_index(value)
                if new_res != self.tws.logging_period_index:
                    self.tws.logging_period_index = new_res
                    self.draw_time_per_pixel(self.tws.logging_period_index)
                    self.vdb.set_setting('logging_period', str(new_res))

    def touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        if gesture == self.lcd.GESTURE_BOTTOM_TO_TOP:
            if self.num < len(self.settings)-1:
                self.num += 1
                self.lcd.remove_gui_button(255)
                self.lcd.remove_gui_slider(255)
                self.lcd.clear_display()
                self.draw_init()
        elif gesture == self.lcd.GESTURE_TOP_TO_BOTTOM:
            if self.num > 0:
                self.num -= 1
                self.lcd.remove_gui_button(255)
                self.lcd.remove_gui_slider(255)
                self.lcd.clear_display()
                self.draw_init()


screens = []
screen_selected = None

def screen_init(initial_init = True, stations = [], sensors = []):
    global screens, screen_selected
    if Screen.lcd == None:
        return

    if initial_init:
        Screen.lcd.set_gui_tab_configuration(Screen.lcd.CHANGE_TAB_ON_CLICK, False)
        Screen.lcd.remove_all_gui()
        Screen.lcd.clear_display()

    screens = [IndoorScreen(), GraphScreen(stations, sensors)]
    if stations != []:
        screens.append(StationScreen(stations))
    if sensors != []:
        screens.append(SensorScreen(sensors))
    screens.append(SettingsScreen())

    import custom_screens
    custom_pos = custom_screens.CUSTOM_SCREENS_POSITION
    screens[custom_pos:custom_pos] = custom_screens.CUSTOM_SCREENS

    for index, screen in enumerate(screens):
        if screen.icon != None:
            Screen.lcd.set_gui_tab_icon(index, screen.icon.data)
        else:
            Screen.lcd.set_gui_tab_text(index, screen.text)

    if initial_init:
        screen_selected = screens[0]
        Screen.lcd.set_gui_tab_selected(0)
        screen_tab_selected(0)

def screen_update_tabs():
    station_screen = None
    sensor_screen  = None
    for screen in screens:
        if screen.__class__ == StationScreen:
            station_screen = screen
        elif screen.__class__ == SensorScreen:
            sensor_screen = screen

    station_keys = list(Screen.tws.outdoor_weather_station_last_value.keys())
    sensor_keys  = list(Screen.tws.outdoor_weather_sensor_last_value.keys())
    if ((len(station_keys) > 0) and (station_screen == None)) or \
       ((len(sensor_keys)  > 0) and (sensor_screen == None)) or \
       ((station_screen != None) and (station_keys != station_screen.keys)) or \
       ((station_screen != None) and (sensor_keys  != sensor_screen.keys)):
       screen_init(False, station_keys, sensor_keys)

def screen_slider_value(index, value):
    screen_selected.slider_value(index, value)

def screen_touch_gesture(gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
    screen_selected.touch_gesture(gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age)

def screen_tab_selected(index):
    global screen_selected
    Screen.lcd.remove_gui_button(255)
    Screen.lcd.remove_gui_slider(255)
    Screen.lcd.remove_gui_graph(255)
    Screen.lcd.clear_display()
    screen_selected = screens[index]
    screen_selected.draw_init()

def screen_set_lcd(lcd):
    Screen.lcd = lcd
    screen_init()

def screen_update():
    if screen_selected != None:
        screen_update_tabs()
        screen_selected.draw_update()
