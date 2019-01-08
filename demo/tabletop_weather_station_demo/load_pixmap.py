# -*- coding: utf-8 -*-
"""
Tabletop Weather Station
Copyright (C) 2013-2015, 2018 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

load_pixmap.py: Functions to load (frozen) images and optionally convert it to alpha channel pixmap

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

import os
import sys

from PyQt4.QtGui import QPixmap, QColor
from PyQt4.QtCore import Qt, QByteArray

if hasattr(sys, 'frozen'):
    from tabletop_weather_station_demo.frozen_images import image_data
else:
    image_data = None

def get_program_path():
    # from http://www.py2exe.org/index.cgi/WhereAmI
    if hasattr(sys, 'frozen'):
        program_file_raw = sys.executable
    else:
        program_file_raw = __file__

    if sys.hexversion < 0x03000000:
        program_file = unicode(program_file_raw, sys.getfilesystemencoding())
    else:
        program_file = program_file_raw

    return os.path.dirname(os.path.realpath(program_file))

def get_resources_path():
    if sys.platform == "darwin" and hasattr(sys, 'frozen'):
        return os.path.join(os.path.split(get_program_path())[0], 'Resources')
    else:
        return get_program_path()

def load_pixmap(path, apply_mask=False):
    if image_data != None:
        data = QByteArray.fromBase64(image_data[path][1])
        pixmap = QPixmap()
        pixmap.loadFromData(data, image_data[path][0])
    else:
        absolute_path = os.path.join(get_resources_path(), path)
        pixmap = QPixmap(absolute_path)

    return pixmap
