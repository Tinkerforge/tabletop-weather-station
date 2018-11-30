#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os
import sys
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
