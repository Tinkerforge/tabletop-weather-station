#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tabletop Weather Station Demo
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

icon_from_image.py: Generates Weather Station icons for image files

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
if (sys.hexversion & 0xFF000000) != 0x03000000:
    print('Python 3.x required')
    sys.exit(1)

import os
from PIL import Image, ImageFont, ImageDraw

def bool_list_from_pil_image(image, width=128, height=64):
    # Convert image to black/white pixels
    image_data = image.load()
    pixels = []

    for row in range(height):
        for column in range(width):
            if column < image.size[0] and row < image.size[1]:
                pixel_data = image_data[column, row]
                if type(pixel_data) == int:
                    pixel = pixel_data > 0
                else:
                    pixel = (image_data[column, row][0] < 255) or (image_data[column, row][1] < 255) or (image_data[column, row][2] < 255)
            else:
                pixel = False

            pixels.append(pixel)
    
    return pixels   

def load_image(path):
    image = Image.open(path)
    width, height = image.size
    return bool_list_from_pil_image(image, width, height), width, height

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Give image file as parameter')
        sys.exit()

    data, width, height = load_image(sys.argv[1])
    print('class IconName(Icon):')
    print('    WIDTH  = {0}'.format(width))
    print('    HEIGHT = {0}'.format(height))
    print('    data   = {0}'.format(data))
