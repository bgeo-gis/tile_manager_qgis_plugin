"""
Copyright © 2025 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version
"""
from qgis.gui import QgisInterface
from qgis.core import QgsRasterLayer, QgsProject, QgsLayerTreeLayer, QgsMessageLog, Qgis
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from owslib.wmts import WebMapTileService
import urllib
import os


class MapproxyTileManager:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):

        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons/tile-manager.png')),
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

        # Check if the selected WMS connection is set
        selected = settings.value("connections/ows/items/wms/connections/selected")
        if not selected:
            # If not set, set it to a default value ('mapproxy_server')
            selected = 'mapproxy_server'
            settings.setValue("ows/items/wms/connections/selected", selected)
            QgsMessageLog.logMessage(f"Selected WMS connection was not set. Defaulting to: {selected}", level=Qgis.Critical)

        QgsMessageLog.logMessage(f"Using selected WMS connection: {selected}", level=Qgis.Info)

        # Get connection details
        capabilities_url_key = f"connections/ows/items/wms/connections/items/{selected}/url"
        username_key = f"connections/ows/items/wms/connections/items/{selected}/username"
        password_key = f"connections/ows/items/wms/connections/items/{selected}/password"
        headers_key = f"connections/ows/items/wms/connections/items/{selected}/http-header"

        capabilities_url = settings.value(capabilities_url_key)
        username = settings.value(username_key)
        password = settings.value(password_key)
        headers = settings.value(headers_key)

        # Ensure all values are strings
        capabilities_url = str(capabilities_url) if capabilities_url else None
        username = str(username) if username else ""
        password = str(password) if password else ""

        if not capabilities_url:
            QgsMessageLog.logMessage("Error: Capabilities URL is not set.", level=Qgis.Critical)
            return

        QgsMessageLog.logMessage(f"Selected WMS: {selected}", level=Qgis.Info)
        QgsMessageLog.logMessage(f"Capabilities URL: {capabilities_url}", level=Qgis.Info)

        wmts = WebMapTileService(capabilities_url, username=username, password=password, headers=headers)
        group_name = "Inventory"
        QgsMessageLog.logMessage(wmts.serviceMetadataURL)

        # Remove layers from the group if it already exists readd them
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(group_name)
        if group is None:
            group = root.addGroup(group_name)
        else:
            for child in group.children():
                group.removeChildNode(child)

        layers_to_add = []

        for layer_name in wmts.contents:
            QgsMessageLog.logMessage(f"Layer: {layer_name}", level=Qgis.Info)

            layer_info = wmts.contents[layer_name]

            tile_matrix_name = layer_info.tilematrixsets[0]
            tile_matrix = wmts.tilematrixsets[tile_matrix_name]
            crs = tile_matrix.crs

            # Create layer with additional parameters
            layer_source = f"crs={crs}&format=image/png&layers={layer_name}&styles=default&tileMatrixSet={tile_matrix_name}&url={capabilities_url}"

            wmts_layer = QgsRasterLayer(
                layer_source,
                layer_name,
                "wms"
            )

            # Add qgis server data URL
            wmts_layer.setDataUrl(f"wmts:{capabilities_url}#{layer_name}")

            if not wmts_layer.isValid():
                QgsMessageLog.logMessage(f"Layer {layer_name} is not valid", level=Qgis.Warning)
                break;
            # Append layer
            layers_to_add.append(wmts_layer)

        # Add layers to the project
        QgsProject.instance().addMapLayers(layers_to_add, False)

        # Insert layers into the group
        group.insertChildNodes(0,[QgsLayerTreeLayer(layer) for layer in layers_to_add])

        # TODO: Uncheck visibility of the layers
        # for layer in layers_to_add:
        #     root.setItemVisibilityChecked(root.findLayer(layer.id()), False)
