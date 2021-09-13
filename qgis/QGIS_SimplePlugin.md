### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer Explained](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained/)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 1](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-1/) (First Steps)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 2](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-2/) (Interactivity)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 3](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-3/) (Best Practices)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 4](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-4/) (Tests & CI)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)
- [QGIS 3 Plugins - Background Tasks](https://gis-ops.com/qgis-3-plugin-tutorial-background-tasks-explained/)

---

# QGIS 3 Plugins - Geocoding with Nominatim Part 1

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
   └──quick_api_dialog_base.ui
```

A more thorough explanation of the generated files and methods is available [here](https://gis-ops.com/qgis-3-plugin-development-reference-guide/#detailed-module-and-method-description).

### Link Plugin to QGIS

For maximum convenience, create a symbolic link of your development folder to the QGIS plugin folder. This way code changes are registered by simply clicking the `Plugin Reload` button (s. [below](#reload-plugin)).

```shell
ln -s $PWD $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Test initial plugin

At this point you can already test if QGIS loads your new (very unfunctional) plugin:

#### Load plugin

Start QGIS and head over to *Plugins* ► *Manage and Install Plugins* et voila:

![Successful installation](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/quick_api_img2.png)

If you activate it, a new icon will be added to the Plugin toolbar. Also, you'll find the plugin in the *Vector* menu in QGIS.

#### Reload plugin

Whenever you replace the plugin code with a newer version, make sure to use the **Plugin Reloader** plugin to reload your own plugin, instead of restarting QGIS.

Note, you'll have to restart if you alter the root `__init__.py` and/or functions which are only executed once like `initGui()`.

#### Troubleshooting

- if you don't see the plugin in the manager after a QGIS restart, check you didn't accidentally set the `experimental` flag by allowing experimental plugins in *Plugin Manager* ► *Settings*.

- if you experience a Python error, you likely did something wrong in the previous steps. Best bet: start from scratch before you dump an inconceivable amount of time in finding the bug. Also, check our [QGIS Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/).

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

After each step, pause for a moment, add some `print()` statements to your code to see that everything works as expected (we'll provide some **DEBUG** hints) and reload it in QGIS via `Plugin Reloader`. Open the QGIS Python console and run the plugin logic. If you see unexpected results, go back and investigate.

### Imports and initial cleanup

On top of what's already imported in `quick_api.py`, included these as well, we'll explain later:

```python
import json

from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsRectangle,
                       QgsPointXY,
                       QgsGeometry,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsNetworkAccessManager,
                       QgsNetworkReplyContent)
```

Note, in other plugin tutorials people often use star imports, i.e. `from qgis.core import *`. This is generally bad practice in Python: while it makes your import statement a lot more compact, you have no idea where the method comes from, especially when done on multiple modules (and neither does your IDE unless their symbols are unique in the current environment).

We also need to clean up a little since we don't use the `resources.qrc` approach: remove the line `from .resources import *`, we build this plugin in a future-proof way (`pyrrc` for compiling the `resources.qrc` will be deprecated soon). As a consequence, you also will have to change the way the plugin references the `icon.png` in its `initGui` method: remove `icon_path = ':/plugins/quick_api/icon.png'` in the method and replace with:

```python
current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(current_dir, 'icon.png')
```

### Set dialog attributes

You included a CRS picker in your plugin. However, there's no option to set a default CRS from Qt Designer. Since you want this to be WGS84 (most coordinates are copied from online map providers such as Google Maps), you have to deal with this in the code. Add the following line to the end in the first `if` statement in `run(self)`:

```python
if self.first_start == True:
		...
    self.dlg.crs_input.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
```

`crs_input` is the CRS picker GUI object, an instance of `QgsProjectionSelectionWidget`. In its [documentation](https://qgis.org/api/classQgsProjectionSelectionWidget.html#a2af9a2e3aaf29ddbe9a6a9121d9bf505), you'll find all info on its methods, like `setCrs()`. Which expects a `QgsCoordinateReferenceSystem`, which again can be built from a valid EPSG code (or others, see the documentation for more on the topic.)

### Save reference to current project

All throughout the following code we'll need a reference to the `QgsProject` object, which refers to the currently active QGIS project. As that, it deals with all project properties (in `read` and `write` mode), e.g. the file path, the map CRS and also the map layers present in the project. Add the following line above `self.dlg.show()`:

```python
project = QgsProject.instance()
```

### 1. Process user input

Once the GUI is correctly built, it's shown to the user and it'll be in front until the user interacts with its buttons. Now, you can add the logic to read the user input once the OK button was clicked. Also, define the output CRS, which will be WGS84:

```python
if result:
    lineedit_text = self.dlg.lineedit_xy.value()
    crs_input = self.dlg.crs_input.crs()
    crs_out = QgsCoordinateReferenceSystem('EPSG:4326')
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
                         "Did you really specify a coordinate in comma-separated Lat Long?\nExiting...")
    return
```

This will just pop up an error message with an OK button and a custom message and then end the plugin logic.

**DEBUG**: add `print(crs_input.authid(), lineedit_yx)` to the end and reload the plugin in QGIS with the Python console open.

### 2. Convert user input to QGIS objects

Next, we need to create an object that QGIS understands to be a Point object. Note, `QgsPointXY` is **not** a geometry yet:

```python
# if result:
point = QgsPointXY(*reversed(lineedit_yx))
```

If the coordinate input was in a CRS other than WGS84, we need to transform the point to WGS84:

```python
# if result:
if crs_input.authid() != 'EPSG:4326':
    xform = QgsCoordinateTransform(crs_input,
                                   crs_out,
                                   project)
    point_transform = xform.transform(point)
    point = point_transform
```

`QgsCoordinateReferenceSystem` comes with `authid`, which returns a string in the form `Provider:ID`, e.g. `EPSG:4326` for WGS84 Lat/Long. `QgsCoordinateTransform` also expects a `QgsProject.instance()` so that the correct transformation contect can be applied (if set).

**DEBUG**: add `print(point)` before and after the transformation.

### 3. Request Nominatim API

Nominatim expects a GET request, which means parameters are encoded in the URL string, e.g. [https://nominatim.openstreetmap.org/reverse?lat=52.098&lon=8.43&format=json](https://nominatim.openstreetmap.org/reverse?lat=52.098&lon=8.43&format=json). It's best practice to pass a base URL and the parameters separately, not in one huge URL string. Additionally, Nominatim's [fair usage policy](https://operations.osmfoundation.org/policies/nominatim/) requires you to include a descriptive `User-Agent` in the request header to identify applications.

The full parameter list for Nominatim's reverse geocoding endpoint can be found [here](https://wiki.openstreetmap.org/wiki/Nominatim#Reverse_Geocoding). We'll just specify coordinate fields and the format.

```python
# if result:

# Set up the GET Request to Nominatim
query = QUrlQuery()
query.addQueryItem('lat', str(point.y()))
query.addQueryItem('lon', str(point.x()))
query.addQueryItem('format', 'json')

url = QUrl('https://nominatim.openstreetmap.org/reverse')
url.setQuery(query)

request = QNetworkRequest(url)
request.setHeader(QNetworkRequest.UserAgentHeader, 'PyQGIS@GIS-OPS.com')

nam = QgsNetworkAccessManager()
response: QgsNetworkReplyContent = nam.blockingGet(request)
```

This might seem like a lot of code when comparing it to the compact (and somewhat magical) design of e.g. the `requests` module. However, it's highly recommended to use the built-in Qt & QGIS way of doing requests for several reasons (among others):

- proxies are much easier to deal with: either use QGIS built-in proxy handler or your system's
- you can take advantage of the QGIS authentication manager to handle e.g. Basic Authentication for URLs which require it

The response `QgsNetworkReplyContent` is a QGIS object, which gives the response context, e.g. if an error occurred and of course access to response's `content()`.

### 4. Process response

First, you need to check whether Nominatim replied with a `200` HTTP status code, which is generally the status code indicating a successful request. Apparently, Nominatim thinks differently and even replies with `200` when there was an error, e.g. sending invalid coordinates. So, additionally you'll have to check for an `error` object in the response JSON, notify the user about it and end the plugin logic:

```python
# if result:
status_code = response.attribute(QNetworkRequest.HttpStatusCodeAttribute)
if status_code == 200:
    # Get the content of the response and process it
    response_json = json.loads(bytes(response.content()))
    if response_json.get('error'):
        QMessageBox.critical(self.iface.mainWindow(),
                             "Quick API error",
                             "The request was not processed succesfully!\n\n"
                             "Message:\n"
                             "{}".format(response_json['error']))
        return
```

If everything went well, you can store the most important response fields. All Nominatim response fields seem to be text, i.e. of `str` type, so you'll have to cast to `float` where necessary:

```python
# if result:
# if response.status_code == 200:
x = float(response_json['lon'])
y = float(response_json['lat'])
address = response_json['display_name']
license = response_json['licence']
```

Next, start to build the output layer. There's more types for [QGIS map layers](https://qgis.org/api/classQgsMapLayer.html#adf3b0b576d7812c4359ece2142170308), you'll use `QgsVectorLayer` here. This class expects a layer **URI, layer name and provider** as a minimum to be constructed.

The **URI** sets the important attributes of the layer and has the general form `<geomType>?crs=<CRS_string>&field=<name>:<type>..`. The CRS string can be any literal [`QgsCoordinateReferenceSystem.createFromString()`](https://www.qgis.org/api/classQgsCoordinateReferenceSystem.html#a0b233da61bdfd4f6cdc9e43af21044ed) understands.

The **provider** relates to the layer's source driver, which can be `ogr`, `postgres` or (very useful) `memory`. The `memory` provider creates a layer well.. in memory, i.e. it will not be stored on disk, and the user can decide what to do with the result layer.

```python
# if result:
# if response.status_code == 200:
layer_out = QgsVectorLayer("Point?crs=EPSG:4326&field=address:string&field=license:string",
                           "Nominatim Reverse Geocoding",
                           "memory")
```

As you can see, you already defined two fields in the URI: `address` and `license` (both `string` type). Now, we just have to create a feature and add it to the new layer:

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

As a last step, we can instruct QGIS to zoom to the geocoded feature. Nominatim supplies you with a response parameter `boundingbox`, which you'll use here. The coordinates are given as a list of strings in `[<ymin>, <ymax>, <xmin>, <xmax>]` format, which is really not ideal (awkward coordintate order and of `str` type), so you have to process them to make them PyQGIS compatible. Also, the CRS of the coordinates is WGS84, while the map canvas likely has a different CRS. So, you'll have to transform them accordingly:

```python
# if result:
# if response.status_code == 200:
bbox = [float(coord) for coord in response_json['boundingbox']]
min_y, max_y, min_x, max_x = bbox
bbox_geom = QgsGeometry.fromRect(QgsRectangle(min_x, min_y, max_x, max_y))

# Transform bbox if map canvas has a different CRS
if project.crs().authid() != 'EPSG:4326':
    xform = QgsCoordinateTransform(crs_out,
                                   project.crs(),
                                   project)
    bbox_geom.transform(xform)
self.iface.mapCanvas().zoomToFeatureExtent(QgsRectangle.fromWkt(bbox_geom.asWkt()))
```

First, construct `QgsPointXY`s from the extent of `boundingbox` and add those to `QgsGeometry` to build a Rectangle geometry. A geometry object can then be transformed in-place. Finally, the `zoomToFeatureExtent()` method of the map canvas expects a `QgsRectangle`, which can be built from the geometry's Well-Known-Text (WKT) string.

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

## Next steps

In the next tutorial we'll add some interactivity to the plugin, so the user can click a point on the map to be reverse geocoded rather than copy/pasting the coordinate: https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-2/.
