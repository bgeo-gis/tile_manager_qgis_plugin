## Tile Manager Plugin

Plugin to create a QGIS project with all the layers available from a WMS/WMTS connection. This plugin connects to your current selected WMS/WMTS connection and adds all the available layers inside a group called 'Inventory'.

Use this plugin as a support for [Mapproxy Tiling Service](https://github.com/bgeo-gis/mapproxy-service) in order to create a publishable QGIS Project for QGIS Server.

### Usage

In this example we'll use Mapproxy as the WMS/WMTS Server. First of all, from QGIS, create a new WMS/WMTS connection pointing to the Mapproxy URL.

![image](https://github.com/user-attachments/assets/b2c055bb-99e9-46b6-8646-ee95a91eed03)

In this example the URL is divided in:

1. `https://example.com/` -> Protocol and Hostname
2. `mapproxy/` -> Mapproxy installation
3. `/example` -> Points to a specific Mapproxy configuration, in this case with the name 'example'.
4. `/service?SERVICE=WMTS&REQUEST=GetCapabilities` -> Query parameters


It's important to check the `Ignore GetMap/GetTile/GetLegendGraphic URI reported in capabilities` and `Ignore GetFeatureInfo URI reported in capabilities` checks.

Once the connection is created, click `Connect` and you should see all the layers for the specific Mapproxy configuration. Add a couple of layers to the project and test that you can see them correctly and Mapproxy is working fine.

After testing, you can remove the layers and click on the Tile Manager plugin Icon.

This will connect automatically to the last WMS/WMTS connection (selected) and add all the layers to the project under the group 'Inventory'.

````
NOTE: For a project with a large amount of layers it's possible that the process takes longer than expected or freezes QGIS for a couple of minutes.
````

After all the layers are added, please disable the visibility of all the layers.

### QGIS Server

The last step is to enable service capabilities from `Project` -> `Settings` -> `QGIS Server` -> `Services Capabilities` and also add `Advertised extent` and `CRS restrictions` from the `WMS` tab.
