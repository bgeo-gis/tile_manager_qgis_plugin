"""
Copyright © 2024 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version
"""
from qgis.gui import QgisInterface

def classFactory(iface: QgisInterface):
    from .main import MapproxyTileManager
    return MapproxyTileManager(iface)
