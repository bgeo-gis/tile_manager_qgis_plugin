"""
Copyright © 2024 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version
"""
from qgis.gui import QgisInterface
from qgis.core import QgsRasterLayer, QgsProject, QgsLayerTreeLayer
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from owslib.wmts import WebMapTileService


class MapproxyTileManager:
    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon("testplug:icon.png"),
            "Mapproxy Tile Manager",
            self.iface.mainWindow()
        )
        self.action.setObjectName("testAction")
        self.action.setWhatsThis("Configuration for test plugin")
        self.action.setStatusTip("This is status tip")
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&MapproxyTileManager", self.action)

    def unload(self):
        self.iface.removePluginMenu("&MapproxyTileManager", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        settings = QSettings()
        # Found int QGIS .ini file
        selected = settings.value("qgis/connections-WMS/selected")
        capabilities_url = settings.value(f"qgis/connections-wms/{selected}/url")
        username = settings.value(f"WMS/{selected}/username")
        password = settings.value(f"WMS/{selected}/password")

        print(f"Selected WMS: {selected}")
        print(f"Capabilities URL: {capabilities_url}")
        print(f"Username: {username}")
        print(f"Password: {password}")

        wmts = WebMapTileService(capabilities_url, username=username, password=password)
        tile_matrix_name = next(iter(wmts.tilematrixsets.keys()))
        tile_matrix = wmts.tilematrixsets[tile_matrix_name]
        crs = tile_matrix.crs

        group_name = "Inventory"

        # Remove layers from the group if it already exists readd them
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(group_name)
        if group is None:
            group = root.addGroup(group_name)

        else:
            for child in group.children():
                group.removeChildNode(child)

        for layer_name in wmts.contents:
            print(f"Layer: {layer_name}")

            # Create layer
            wmts_layer = QgsRasterLayer(
                f"crs={crs}&format=image/png&layers={layer_name}&styles=default&tileMatrixSet={tile_matrix_name}&url={capabilities_url}",
                layer_name,
                "wms"
            )

            # Add qgis server data URL
            wmts_layer.setDataUrl(f"wmts:{capabilities_url}#{layer_name}")

            if not wmts_layer.isValid():
                print(f"Layer {layer_name} is not valid")

            # Add layer to the group
            QgsProject.instance().addMapLayer(wmts_layer, False)
            group.insertChildNode(0, QgsLayerTreeLayer(wmts_layer))
