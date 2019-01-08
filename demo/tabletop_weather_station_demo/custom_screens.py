# -*- coding: utf-8 -*-

import time
from tabletop_weather_station_demo.screens import Screen

# Simple example for a custom screen.
# In this example we show the time in HH:MM:SS format.
# To try this example out add it to CUSTOM_SCREENS below.
class ClockScreen(Screen):
    # text/icon: Text is taken if no icon is available
    text = "Clock" # Text shown on tab
    icon = None    # Icon shown on tab (see icons.py and data/ sub-directory)

    # Called when tab is selected
    def draw_init(self):
        self.lcd.draw_text(40, 5, self.lcd.FONT_12X16, self.lcd.COLOR_BLACK, 'Time')
        self.draw_update()
    
    # Called when new data is available (usually once per second)
    def draw_update(self):
        # Get current time in HH:MM:SS format
        current_time = time.strftime("%H:%M:%S")
        self.lcd.draw_text(16, 30, self.lcd.FONT_12X16, self.lcd.COLOR_BLACK, current_time)

################################################
# Add your custom screens and tab position here:

CUSTOM_SCREENS          = [] 
CUSTOM_SCREENS_POSITION = 0 

#
# An example for a custom screen can be found above (ClockScreen).
# Comment in below to try it out. It will show a "Clock"-Tab on second
# position that prints the time in HH:MM:SS format.
#
# CUSTOM_SCREENS          = [ClockScreen()] 
# CUSTOM_SCREENS_POSITION = 1  
#
#################################################
