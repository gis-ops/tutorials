### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer Explained](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained/)
- [QGIS 3 Plugins - Plugin Development Part 1](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-1/)
- [QGIS 3 Plugins - Plugin Development Part 2](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-2/)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)

---

# QGIS 3 Plugins - Build your first plugin

This tutorial follows you through the development process of a simple QGIS 3 Python plugin using the amazing [Plugin Builder 3](http://g-sherman.github.io/Qgis-Plugin-Builder/).

The final plugin can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api).

**Goals**:

- get more familiar with `PyQGIS` and `PyQt5` and the respective documentation
- understand how QGIS works with plugins
- build a GUI with QGIS native Qt Designer
- connect GUI elements to Python functions
- deploy the plugin locally and take necessary steps for a successful publication

**Plugin functionality**:

- User copy/pastes X, Y coordinates into a text field and specifies the CRS
- Upon OK button click, the [Nominatim API](https://wiki.openstreetmap.org/wiki/Nominatim) is queried on its Reverse Geocoding endpoint
- A Point layer is generated in-memory, displayed on the map and zoomed to

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **QGIS <= v3.6.3**
> Occassionally, the author might choose to give hints on Windows-specific setups. `Ctrl+F` for WINDOWS flags. Mac OS users should find the instructions reasonably familiar.

## Prerequisites

### Hard prerequisites

- Basic understanding of Python
- QGIS v3.x
- [Plugin Builder](https://plugins.qgis.org/plugins/pluginbuilder3/) QGIS plugin installed
- [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin installed
- Python >= 3.6 (should be your system Python3)

### Recommendations

- Basic Python knowledge
- Familiarity with
	- Qt Designer application, see [our tutorial](https://gis-ops.com/qgis-3-qt-designer-explained/)
	- Python Plugin Basics, see [our tutorial](https://gis-ops.com/qgis-3-plugin-development-reference-guide/)

## First steps

### Run Plugin Builder

If you have successfully installed the Plugin Builder 3 plugin, it is available in the *Plugins* menu in QGIS. Make sure to fill out the details similar to ours:

![Plugin Reloader settings](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/quick_api_img1.png)

Note, there will be a few more dialogs, just use common sense when filling those in. Or accept the defaults.

### Generated files

The Plugin Builder will have generated a lot of (well-intended) files now. Head over to your new plugin project directory and `ls -ll`. Though well-intended, a lot of files are convenience files, which don't really help in the beginning. You can safely delete all files and folders except for these:

```bash
├──quick_api
   ├──icon.png
   ├──__init__.py
   ├──metadata.txt
   ├──quick_api.py
   ├──quick_api_dialog.py
   ├──quick_api_dialog_base.ui
   └──resources.qrc
```

A more thorough explanation of the generated files and methods is available [here](https://gis-ops.com/qgis-3-plugin-development-reference-guide/#detailed-module-and-method-description).

### Compile `resources.qrc`

A more detailed description of the concept of `resources.qrc` can be found [here](https://gis-ops.com/qgis-3-qt-designer-explained/#qt-resourcesqrc).

Plugin Builder 3 will try to compile your resource file, but often enough fails to determine the system path of the `pyrcc5` executable, so you'll have to do it manually:

```bash
pyrcc5 -o resources.py resources.qrc
```

Repeat this step if you make adjustments to `resources.qrc`.

### Test initial plugin

At this point you can already test if QGIS loads your new (very unfunctional) plugin:

#### Deploy plugin to QGIS

First, you should create the directory where your plugin will be picked up on QGIS startup and copy all files there:

```bash
cp -arf ../quick_api $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

Run this command whenever you change something in your development project.

#### Load plugin

Start QGIS and head over to *Plugins* ► *Manage and Install Plugins* et voila:

![Successful installation](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/quick_api_img2.png)

If you activate it, a new icon will be added to the Plugin toolbar. Also, you'll find the plugin in the *Vector* menu in QGIS.

#### Reload plugin

Whenever you replace the plugin code with a newer version, make sure to use the **Plugin Reloader** plugin to reload the plugin, instead of restarting QGIS.

Note, this only works for code alterations outside of the main `__init__.py`.

#### Troubleshooting

- if you can't access `pyrcc5`, it might not be installed on your system for mysterious reasons. In that case, please try `sudo apt-get install pyqt5-dev-tools`, which should contain `pyrcc5`.

- if you don't see the plugin in the manager after a QGIS restart, check you didn't accidentally set the `experimental` flag by allowing experimental plugins in *Plugin Manager* ► *Settings*.

- if you experience a Python error, you likely did something wrong in the previous steps. Best bet: start from scratch before you dump an inconceivable amount of time in finding the bug. Also, check our [QGIS Plugin 101]().

## Qt Designer

First, start Qt Designer. The app is shipped on all OS's with QGIS and should be available as an executable on your computer.

If you haven't worked with Qt Designer before, we recommend our short [Qt Designer](https://gis-ops.com/qgis-3-qt-designer-explained/) tutorial.

### Build GUI

You will build a very simple GUI: only a small box where the user can paste a X, Y coordinate pair and a CRS picker if the coordinate is not in WGS84.

Do the following steps:

1. Select the dialog window and press `Lay Out Vertically` button in the toolbar
2. Drag a `QgsFilterLineEdit` widget to the dialog and insert it above the buttons
3. Alter the following properties of the new widget:
	- `QObject.objectName`: lineedit_xy
	- `QLineEdit.placeholderText`: Y, X (Lat, Lon)
4. Drag a `QgsProjectionSelectionWidget` below the other widget and name it *crs_input*
4. Resize the dialog to fit your needs

Now, your GUI should look similar to this:

![Final GUI](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/quick_api_img4.png)

**Don't forget to save the UI file!** That can be a significant source of frustration.

## Code

**You'll only work in `quick_api.py`.**

In this tutorial we will throw a few fundamental programming principles over board and focus only on the most crucial parts of a QGIS plugin. To this end, we will **not**:

- separate GUI logic from processing logic
- write unit tests

These are really mantras you can't repeat often enough. There will be other tutorials focusing on testing.

Also, if you're not sure about the basics of QGIS Plugins, head over to our [QGIS Plugin 101](https://gis-ops.com/qgis-3-plugin-development-reference-guide/) for reference.

### Logic

In its current state, the plugin will show the correct GUI, but not do anything when OK is pressed. So, to implement our desired functionality, we have to do add a bit of code to `quick_api.py'`'s `run(self)` method.

The logic will be:

1. Read the contents of the GUI field, i.e. the Lat/Long and the CRS
2. Convert the string to Point X & Y and transform to WGS84 decimal coordinate if necessary, as expected by Nominatim
3. Build the request to Nominatim's API and fire it
4. Process the response to add it as a layer to QGIS
5. Add logic to zoom to a bounding box

After each step, pause for a moment, add some `print()` statements to your code to see that everything works as expected (we'll provide some **DEBUG** hints), copy your code to the plugin directory and reload it in QGIS. Open the QGIS Python console and run the plugin logic. If you see unexpected results, revert to the code and investigate.

### Imports

We'll need a few imports from `qgis.core` and `QMessageBox` from `PyQt`, plus `requests` for this to work. Just paste this into your import statements at the top of `quick_api.py`, we'll explain later:

```python
import requests
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsRectangle,
                       QgsPointXY,
                       QgsGeometry,
                       QgsVectorLayer,
                       QgsFeature)
```

Note, in other plugin tutorials people often use star imports, i.e. `from qgis.core import *`. This is bad practice generally. While it makes your import statement a lot more compact, you have no idea where the method comes from, especially when done on multiple modules (and neither does your IDE).

### Set dialog attributes

You included a CRS picker in your plugin. However, there's no option to set a default CRS from Qt Designer. Since you want this to be WGS84 (most coordinates are copied from online map providers such as Google Maps), you have to deal with this in the code. Add the following line to the end in the first `if` statement in `run(self)`:

```python
if self.first_start == True:
		...
    self.dlg.crs_input.setCrs(QgsCoordinateReferenceSystem(4326))
```

`crs_input` is the CRS picker GUI object, an instance of `QgsProjectionSelectionWidget`. In its [documentation](https://qgis.org/api/classQgsProjectionSelectionWidget.html#a2af9a2e3aaf29ddbe9a6a9121d9bf505), you'll find all info on its methods, like `setCrs()`. Which expects a `QgsCoordinateReferenceSystem`, which again can be built from a valid EPSG code as integer.

### Save reference to current project

All throughout the following code we'll need a reference to a `QgisProject` instance, which refers to the QGIS project which is currently active for a user. As that, it deals with all project properties (in `read` and `write` mode), e.g. the file path, the map CRS and also the map layers present in the project. Add the following line above `self.dlg.show()`:

```python
project = QgsProject.instance()
```

### 1. Process user input

Once the GUI is correctly built, it's shown to the user and it'll be open until the user interacts with its buttons. Now, you can add the logic to read the user input once the OK button was clicked. Also, define the output CRS, which will be WGS84:

```python
if result:
    lineedit_text = self.dlg.lineedit_xy.value()
    crs_input = self.dlg.crs_input.crs()
    crs_out = QgsCoordinateReferenceSystem(4326)
```

`lineedit_text` is a string. We need it as coordinate decimal points though:

```python
#if result:
lineedit_yx = [float(coord.strip()) for coord in lineedit_text.split(',')]
```

A lot can go wrong here already: the user doesn't use a comma separator or generally inputs something entirely wrong. To protect against user failure, we add a quick error dialog when there's an error with this function (of course this won't protect against swapping X and Y):

```python
# if result:
try:
    lineedit_yx = [float(coord.strip()) for coord in lineedit_text.split(',')]
except:
    QMessageBox.critical(self.iface.mainWindow(),
                         'QuickAPI error',
                         "Did you really specify a coordinate in comma-separated Lat/Long?\nExiting...")
    return
```

This will just pop up an error message with an OK button and a custom message and then end the plugin logic.

**DEBUG**: add `print(crs_input.authid(), lineedit_yx)` to the end and reload the plugin in QGIS.

### 2. Convert user input to QGIS objects

Next, we need to create an object that QGIS understands to be a Point object. Note, `QgsPointXY` is **not** a geometry yet:

```python
# if result:
point = QgsPointXY(*reversed(lineedit_yx))
```

If the coordinate input was in a CRS differenct from WGS84, we need to transform the point to WGS84:

```python
# if result:
if crs_input.authid() != 'EPSG:4326':
    xform = QgsCoordinateTransform(crs_input,
                                   crs_out,
                                   project)
    point_transform = xform.transform(point)
    point = point_transform
```

`QgsCoordinateReferenceSystem` comes with `authid`, which returns a string in the form `Provider:ID`, e.g. 'EPSG:4326' for WGS84 Lat/Long. `QgsCoordinateTransform` also expects a `QgsProject.instance()` so that custom project-based transformations can be applied (if set).

**DEBUG**: add `print(point)` before and after the transformation.

### 3. Request Nominatim API

Nominatim expects a GET request, which means parameters are encoded in the URL string, e.g. [https://nominatim.openstreetmap.org/reverse?lat=52.098&lon=8.43&format=json](https://nominatim.openstreetmap.org/reverse?lat=52.098&lon=8.43&format=json). It's best practice to pass a base URL and the parameters separately, not in one huge URL string. Additionally, Nominatim's [usage policy](https://operations.osmfoundation.org/policies/nominatim/) dictates to include a descriptive `User-Agent` in the request header to identify applications.

The full parameter list for Nominatim's reverse endpoint can be found [here](https://wiki.openstreetmap.org/wiki/Nominatim#Reverse_Geocoding). We'll just specify coordinate fields and the format.

```python
# if result:
user_agent = 'PyQGIS@GIS-OPS.com'
base_url = 'https://nominatim.openstreetmap.org/reverse'
params = {'lat': point.y(), 'lon': point.x(), 'format': 'json'}

response = requests.get(url=base_url, params=params, headers={'User-Agent': user_agent})
response_json = response.json()
```

Since we requested a JSON format, the response text will be accessible over its `json()` method as a `dict` type.

**DEBUG**: add `print(response.request.full_url)` at the end to see the raw request URL used.

### 4. Process response

First, you need to check whether Nominatim replied with a `200` HTTP status code, which is generally the status code indicating a successful request. Apparently, Nominatim thinks differently and even replies with `200` when there was an error, e.g. sending invalid coordinates. So, additionally you'll have to check for an `error` object in the response JSON, notify the user about it and end the plugin logic:

```python
# if result:
if response.status_code == 200:
    if response_json.get('error'):
        QMessageBox.critical(self.iface.mainWindow(),
			                       "Quick API error",
	                           "The request was not processed succesfully!\n\n"
														 "Message:\n"
														 "{}".format(response.json()))
        return
```

**DEBUG**: add `print(response.text)` to see the raw text of the response.

If everything went well, you can store the most important response fields. All Nominatim response fields seem to be text, i.e. of string type, so you'll have to cast to `float` where necessary:

```python
# if result:
# if response.status_code == 200:
x = float(response_json['lon'])
y = float(response_json['lat'])
address = response_json['display_name']
license = response_json['licence']

```

Next, start to build the output layer. There's more types for [QGIS map layers](https://qgis.org/api/classQgsMapLayer.html#adf3b0b576d7812c4359ece2142170308), you'll use `QgsVectorLayer` here. This class expects a layer **URI, layer name and provider** as a minimum to be constructed.

The **URI** sets the important attributes of the layer and has the general form `<geomType>?crs=<CRS_string>&field=<name>:<type>..`. The CRS string can be any literal `QgsCoordinateReferenceSystem.createFromString()` understands.

The **provider** relates to the layer source, which can be `ogr`, `postgres` or (very useful) `memory`. The `memory` provider creates a layer well.. in memory, i.e. it will not be stored on disk. So, you don't have to mess around with directory paths.

```python
# if result:
# if response.status_code == 200:
layer_out = QgsVectorLayer("Point?crs=EPSG:4326&field=address:string&field=license:string",
                           "Nominatim Reverse Geocoding",
                           "memory")

```

As you can see, you already defined two fields in the URI: `address` and `license` (both `string` type). Now, we just have to create a feature and add it to this layer:

```python
# if result:
# if response.status_code == 200:
point_out = QgsPointXY(x, y)
feature = QgsFeature()
feature.setGeometry(QgsGeometry.fromPointXY(point_out))
feature.setAttributes([address, license])

layer_out.dataProvider().addFeature(feature)
layer_out.updateExtents()
project.addMapLayer(layer_out)
```

First, you build a Point object from the response X & Y. A `QgsFeature` is how QGIS understands a single feature entity. It holds information on geometry and attributes, which you'll have to set. Remember, `QgsPointXY` is not a geometry, only a Point object (confusing, really, since `QgsPoint` **is** a geometry), so we'll have to create a geometry from it first.

The layer's attributes (i.e. the field names) are actually not known to the new feature. But you can still pass an ordered list of attribute values, which will have to be in the same order as the layer initialization in the previous code block, i.e. first `address`, then `license` and of course hold the same data type.

When adding features to map layers, it's important to add them to the `dataProvider()` if you want the features to persist.

Finally, you add the layer to the current project after updating its extents.

### 5. Zoom to bounding box

As a last step, we can instruct QGIS to zoom to the geocoded feature. Nominatim supplies you with a response parameter `boundingbox`, which you'll use here. The coordinates are given as a list of strings in `[<ymin>, <ymax>, <xmin>, <xmax>]` format, which is not ideal, so you have to process them to make them PyQGIS compatible. Also, the CRS of the coordinates is WGS84, while the map canvas likely has a different CRS. So, you'll have to transform them accordingly:

```python
# if result:
# if response.status_code == 200:
bbox = [float(coord) for coord in response_json['boundingbox']]
min_y, max_y, min_x, max_x = bbox
bbox_geom = QgsGeometry.fromPolygonXY([[QgsPointXY(min_x, min_y),
                                        QgsPointXY(min_x, max_y),
                                        QgsPointXY(max_x, max_y),
                                        QgsPointXY(max_x, min_y),
                                       ]])

# Transform bbox if map canvas has a different CRS
if project.crs().authid() != 'EPSG:4326':
    xform = QgsCoordinateTransform(crs_out,
	     		           							 project.crs(),
			           			 						 project)
		bbox_geom.transform(xform)
self.iface.mapCanvas().zoomToFeatureExtent(QgsRectangle.fromWkt(bbox_geom.asWkt()))
```

First, construct `QgsPointXY`s from the extent of `boundingbox` and add those to `QgsGeometry` to build a Polygon geometry. A geometry object can then be transformed in-place. Finally, the `zoomToFeatureExtent()` method of the map canvas expects a `QgsRectangle`, which can be built from the Well-Known-Text (WKT) string of the polygon geometry.

## Final plugin

When you've gone through all the steps above and your plugin works as expected, it's time to prepare for (a hypothetical) upload to the QGIS plugin repository.

The final plugin can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api). Feel free to clone it and compare.

**NOTE: do not upload this plugin to the QGIS repository!!**

### `metadata.txt`

Fill out all details accordingly. Find a suitable icon for your plugin and replace `icon.png` (but keep the name to not break any code). Find a more elaborate explanation [here](https://gis-ops.com/qgis-3-plugin-development-reference-guide/#metadatatxt).

### Zip plugin

For the QGIS plugin repository to accept your plugin, you must zip the whole `quick_api` folder. We recommend to create a `dist` folder top-level:

```bash
mkdir dist/
zip -r dist/quick_api_v0.1.zip quickapi
```

### Upload plugin

The uploading details and more general guidelines can be followed from [the official homepage](https://plugins.qgis.org).
