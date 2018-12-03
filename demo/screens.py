# -*- coding: utf-8 -*-

import icons

class Screen:
    WIDTH  = 128
    HEIGHT = 64

    lcd    = None
    text   = "TBD"
    icon   = None
    tws    = None

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
        ret = []
        value_min = min(data)
        value_max = max(data)
        if value_max-value_min == 0:
            return [0]*len(data), 0, 0
        
        for d in data:
            ret.append((d-value_min)*255/(value_max-value_min))
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
        self.lcd.draw_text(78, 16, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'mbar')
        self.lcd.draw_text(78, 46, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, 'IAQ')

        self.lcd.draw_line(0, 26, 127, 26, self.lcd.COLOR_BLACK)
        self.lcd.draw_line(60, 0, 60, 52, self.lcd.COLOR_BLACK)
        self.draw_update()
    
    def draw_update(self):
        if self.tws.air_quality_last_value == None:
            return

        self.iaq_test += 50
        if self.iaq_test > 400:
            self.iaq_test = 0
        
        last_value = self.tws.air_quality_last_value
        iaq_value = self.iaq_test
#        iaq_value = last_value.iaq_index

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
    graphs = ['\xF8C', '%RH', 'mbar', 'IAQ']
    formats = ['{0:.1f}', '{0:.1f}', '{0:.1f}', '{0}']
    divisor = [100, 100, 100, 1]

    def __init__(self):
        self.num = 0

    def draw_init(self):
        self.lcd.set_gui_graph_configuration(0, self.lcd.GRAPH_TYPE_LINE, 40, 0, 87, 52, "h", self.graphs[self.num])

        self.draw_icon(0, 11, icons.IconLeftSwipeUpDown) 
        self.lcd.draw_line(17, 16, 22, 11, self.num != len(self.graphs)-1)
        self.lcd.draw_line(22, 11, 27, 16, self.num != len(self.graphs)-1)
        self.lcd.draw_line(17, 16 + 19, 22, 11 + 19 + 10, self.num != 0)
        self.lcd.draw_line(22, 11 + 19 + 10, 27, 16 + 19, self.num != 0)

        self.draw_update()

    def draw_update(self):
        data = []
        for t, value in self.tws.air_quality_values:
            if self.num == 0:
                data.append(value.temperature)
            elif self.num == 1:
                data.append(value.humidity)
            elif self.num == 2:
                data.append(value.air_pressure)
            elif self.num == 3:
                data.append(value.iaq_index)
            if len(data) >= 118:
                break

        if len(data) < 4:
            return

        scaled_data, value_min, value_max = self.scale_data_for_graph(data)

        temperature_min = self.formats[self.num].format(value_min/self.divisor[self.num])
        temperature_max = self.formats[self.num].format(value_max/self.divisor[self.num])
        temperature_min = ' '*(6 - len(temperature_min)) + temperature_min
        temperature_max = ' '*(6 - len(temperature_max)) + temperature_max
        self.lcd.draw_text(2, 0,  self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, temperature_max)
        self.lcd.draw_text(2, 45, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, temperature_min)
        self.lcd.set_gui_graph_data(0, scaled_data)

    def touch_gesture(self, gesture, duration, pressure_max, x_start, x_end, y_start, y_end, age):
        if gesture == self.lcd.GESTURE_BOTTOM_TO_TOP:
            if self.num < len(self.graphs)-1:
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
            import traceback
            traceback.print_exc()
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
            import traceback
            traceback.print_exc()
            return
        
        last_value = self.tws.outdoor_weather_station_last_value[identifier]

        temperature = '{0:.1f}'.format(last_value.temperature/10.0)
        temperature = ' '*(4 - len(temperature)) + temperature
        humidity    = '{0:.1f}'.format(last_value.humidity)
        humidity    = ' '*(2 - len(humidity)) + humidity
        wind_speed  = '{0:.1f}'.format(last_value.wind_speed/10.0)
        wind_speed  = ' '*(4 - len(wind_speed)) + wind_speed
        rain        = '{0:.1f}'.format(last_value.rain/10.0)
        rain        = ' '*(4 - len(rain)) + rain
        direction   = last_value.wind_direction
        battery_low = last_value.battery_low
        station     = '{0}/{1}'.format(self.num + 1, len(self.keys))

        self.lcd.draw_text(18, 0,  self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, temperature)
        self.lcd.draw_text(18, 30, self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, humidity)
        self.lcd.draw_text(16 + 48, 0,  self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, wind_speed)
        self.lcd.draw_text(16 + 48, 30, self.lcd.FONT_6X16, self.lcd.COLOR_BLACK, rain)
        self.lcd.draw_text(104, 45, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, station)

        self.draw_icon(98, 0, icons.IconCompass)

        try:
            d, xdiff, ydiff = self.directions[direction]
            if len(d) == 1:
                d = ' ' + d + ' '
            elif len(d) == 2:
                d = ' ' + d
#            self.lcd.draw_text(104, 33, self.lcd.FONT_6X8, self.lcd.COLOR_BLACK, d)
            self.lcd.draw_line(113, 15, 113 + xdiff, 15 + ydiff, True)
        except:
            pass

        if direction < 8:
            self.draw_icon(50, 4, icons.IconFlagEast)
        else:
            self.draw_icon(50, 4, icons.IconFlagWest)

        if battery_low:
            self.draw_icon(104, 0, icons.IconBatteryEmpty)
        else:
            self.draw_icon(104, 34, icons.IconBatteryFull)
#            self.draw_icon(118, 0, icons.IconBatteryFullSmall)

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
    settings = ['Display', 'Graph', 'Log']

    def __init__(self):
        self.num = 0

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


    def slider_value(self, index, value):
        if self.num == 0:
            conf = self.lcd.get_display_configuration()
            
            if index == 0:
                self.lcd.set_display_configuration(conf.contrast, value*100/67, conf.invert, conf.automatic_draw)
            elif index == 1:
                self.lcd.set_display_configuration(value, conf.backlight, conf.invert, conf.automatic_draw)

    def draw_update(self):
        pass

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
    print("screen_init {0}".format((initial_init, stations, sensors)))
    if Screen.lcd == None:
        return
   
    if initial_init:
        Screen.lcd.set_gui_tab_configuration(Screen.lcd.CHANGE_TAB_ON_CLICK, False)
        Screen.lcd.remove_all_gui()
        Screen.lcd.clear_display() 

    screens = [IndoorScreen(), GraphScreen()]
    if stations != []:
        screens.append(StationScreen(stations))
    if sensors != []:
        screens.append(SensorScreen(sensors))
    screens.append(SettingsScreen())


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
    
    station_keys = Screen.tws.outdoor_weather_station_last_value.keys()
    sensor_keys  = Screen.tws.outdoor_weather_sensor_last_value.keys()
    if ((len(station_keys) > 0) and (station_screen == None)) or \
       ((len(sensor_keys)  > 0) and (sensor_screen == None)) or \
       (station_keys != station_screen.keys) or \
       (sensor_keys  != sensor_screen.keys):
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