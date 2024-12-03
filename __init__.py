from qgis.gui import QgisInterface

def classFactory(iface: QgisInterface):
    from .main import MapproxyTileManager
    return MapproxyTileManager(iface)
