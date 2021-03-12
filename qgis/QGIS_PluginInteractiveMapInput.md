### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer Explained](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained/)
- [QGIS 3 Plugins - Plugin Development Part 1](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-1/)
- [QGIS 3 Plugins - Plugin Development Part 2](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-2/)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)

---

# QGIS 3 Plugins - Use Interactive Mapping

This tutorial follows up on the [first QGIS plugin development tutorial](https://gis-ops.com/qgis-simple-plugin/), which built a plugin using [Nominatim](https://wiki.openstreetmap.org/wiki/Nominatim)'s reverse geocode endpoint to query user generated coordinates for street addresses. If you have no idea what I'm talking about, go through the [tutorial](https://gis-ops.com/qgis-simple-plugin/) or get the previously prepared plugin from our [repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api).

In this walk-through you'll extend the functionality so that a user doesn't have to manually copy/paste coordinates from a third-party service/document. A user will want to be able to click inside the map and use this point for reverse geocoding. And it's explicitly an extension, a user would still be able to paste coordinates manually.

The final extended plugin can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive).

**Goals**:

- capture interactive map input from users
- create your own Map Tool (like Pan or Zoom Tool in QGIS)
- learn applied examples for signals/slots to create interactivity

**Plugin functionality**:

- User either copies Lat/Long or X/Y to the plugin dialog or uses an interactive Map Tool to capture a coordinate in the map canvas
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
- **[Previous tutorial](https://gis-ops.com/qgis-simple-plugin/)** or alternatively the **[prepared plugin](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api)**
- [Plugin Builder](https://plugins.qgis.org/plugins/pluginbuilder3/) QGIS plugin installed
- [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin installed
- Python >= 3.6 (should be your system Python3)

### Recommendations

- Basic Python knowledge
- Familiarity with
	- Qt Designer application, see [our tutorial](https://gis-ops.com/qgis-3-qt-designer-explained/)
	- Python Plugin Basics, see [our tutorial](https://gis-ops.com/qgis-3-plugin-development-reference-guide/)

## 1 Preparation

First, copy the previous plugin files to a new structure, so you don't mess with a working solution. You can leave all file names the way they are though.

```
mkdir quick_api_interactive
cp -r quick_api/* quick_api_interactive
```

Now all the definitions will be the same for the "new" plugin as it was for the old one, which will conflict with each other in QGIS. So you need to remove the old plugin and add the new one:

```
rm -r ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/quick_api
ln -s ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
```

You can already create the new files and folders which you'll need throughout the tutorial:

```
cd quick_api_interactive
mkdir icons  # We'll provide some icons later on
touch maptool.py  # This will hold our interactive map tool later
```

Now your file structure should look like this:

```
quick_api_interactive
├── icon.png
├── icons
├── __init__.py
├── maptool.py
├── metadata.txt
├── quick_api_dialog_base.ui
├── quick_api_dialog.py
├── quick_api.py
├── resources.py
└── resources.qrc
```

## 2 Qt Designer - Add Map button

If you're not too familiar with Qt Designer, we have a [reference guide](https://gis-ops.com/qgis-3-qt-designer-explained/) for you.

Open the `quick_api_dialog_base.ui` in Qt Designer and perform the following steps in sequence:

1. Change the layout of the main `QDialog` to `Grid` by pressing `Lay Out in a Grid` button in the main toolbar
2. Drag a `QToolButton` to the right side of the `QgsFilterLineEdit` widget and name it *map_button*
3. Resize the rest of the widgets to fill the entire width of the dialog
4. Save the UI file

Now, your UI should look approximately like this:

![new UI](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/quick_api_interactive_ui.png)

## 3 PyQGIS - Add icons

Typically icons are created with Qt's `QIcon` class and there are multiple ways how to create one:

- file-based classic Python approach: simply supply the path of an existing icon file
- access QGIS resources: QGIS has a resource store holding all its file-based resources such as icons. Tapping into that you can simply use what's already in QGIS without having to worry to come up with your own icons.

We'll show you both approaches here.

### File-based

Let's replace the plugin's main icon. Our proposal is the icon of our [Pelias geocoder plugin](https://github.com/pelias/pelias): https://github.com/nilsnolde/pelias-qgis-plugin/raw/master/PeliasGeocoding/gui/img/icon_reverse.png

Add the icon to the `./icons` and adapt the path in `initGui` to reflect the new path:

```python
icon_path = os.path.join(current_dir, 'icons', 'icon.png')
```

Note, whatever you choose the image should be SVG or PNG with background transparency, otherwise it will look awful.

### QGIS resources

Another way is to re-use what QGIS offers out-of-the-box in its own resource store. The real challenge is to find out how to reference the path to the icon/resource to supply it to `QIcon`.

One solution is this [fantastic collection](https://static.geotribu.fr/toc_nav_ignored/qgis_resources_preview_table/#icons) by [Geotribu](https://geotribu.fr/). Finding a suitable icon requires some guesswork w.r.t. its name. For our purposes we choose one icon for both the map tool button and the cursor when the map tool is active:

![test](https://raw.githubusercontent.com/qgis/QGIS/master/images/themes/default/cursors/mCapturePoint.svg): `":images/themes/default/cursors/mCapturePoint.svg"`

To use that icon for the map tool button, you can add the following to the `run()` method:

```python
if self.first_start == True:
    # ...
    self.dlg.map_button.setIcon(QIcon(":images/themes/default/cursors/mCapturePoint.svg"))
```

### Test in QGIS

You already made a lot of changes to the initial plugin, so it's time to make sure everything worked smoothly. Restart QGIS, enable the "new" plugin (called `quick_api_interactive` now) and choose it from the dropdown of _Plugin Reloader_ before reloading it.

## 4 PyQGIS - Set up Map Tool and signal

**Finally** you can do a bit more fun work! You'll start with **`maptool.py`**

This will be the actual tool which will let users choose a point on the map canvas for reverse geocoding. It's surprisingly little code actually.

What you will create is a real Map Tool, like e.g. the Zoom Tool in QGIS or the Pan Tool. Using the new tool will only emit the point clicked in the map canvas to a listening function which will transform the point to WGS84 and subsequently send it to Nominatim. So, let's get started.

First, import the relevant modules:

```python
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QApplication

from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject
                       )
```

Then build a class `PointTool` based on [`QgsMapToolEmitPoint`](https://qgis.org/pyqgis/3.0/gui/Map/QgsMapToolEmitPoint.html) and also create a module-wide CRS based on WGS84:

```python
WGS = QgsCoordinateReferenceSystem("EPSG:4326")


class PointTool(QgsMapToolEmitPoint):
    pass
```

The point tool also needs to know when it needs to capture a click from the user, i.e. it needs to know which `event` is has to listen to. `QgsMapToolEmitPoint` has a few pre-defined event methods available which you can listen to. In this case, you'll use `canvasReleaseEvent`, which is the event triggered when the mouse button was pressed **and released** while hovering over the map canvas. Other events include `canvasMoveEvent` and `canvasPressEvent`. These events are managed by QGIS and need to be implemented before they're doing anything. The `event` it accepts is a [`QgsMapMouseEvent`](https://qgis.org/api/classQgsMapMouseEvent.html), which, among other properties, knows the point coordinates of the click event in the current CRS of the map canvas:

```python
# class PointTool(QgsMapToolEmitPoint):
canvasClicked = pyqtSignal('QgsPointXY')

def canvasReleaseEvent(self, event: QgsMapMouseEvent):
    # Get the click and emit a transformed point

    crs_canvas = self.canvas().mapSettings().destinationCrs()
    xformer = QgsCoordinateTransform(crs_canvas, WGS, QgsProject.instance())

    point_clicked = event.mapPoint()
    point_wgs = xformer.transform(point_clicked)

    self.canvasClicked.emit(point_wgs)
```

This might be the first time you come across `pyqtSignal`, so we recommend to go through our [short primer on PyQt Signal/Slots concept](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained).

Above you define a custom signal `canvasClicked`, which can emit a `QgsPointXY` variable type. It will only emit in the above case when a `canvasReleaseEvent` was triggered and after the point was transformed to WGS84. This emitted `signal` however needs a `slot` to connect to, i.e. a function which does something useful with the emitted point. As you will see shortly, that slot will be the function adding the emitted WGS84 coordinates the user clicked to the `QgsFilterLineEdit` widget in your GUI, which a user had to fill manually before.

## 5 PyQGIS - Implement Map Tool and slot

Now that you set up the signal that will emit the clicked point, you need to tell the plugin what should happen with that `QgsPointXY`.

This is a 2 stage process:
1. connect the `map_button` `QToolButton`'s `clicked` signal to a function initializing your map tool
2. in this initialization function, connect the `canvasClicked` signal of your map tool to the function which will populate the `lineedit_yx` `QgsFilterLineEdit` with the emitted `QgsPointXY`.

First, import the Map Tool to `quick_api.py`:

```python
from .maptool import PointTool
```

### Initialize the Map Tool

you will introduce a new function to `quick_api.py:QuickApi`, which will be called whenever the `map_button` is clicked:

```python
#class QuickApi:
def _on_map_click(self):
    self.dlg.hide()
    self.point_tool = PointTool(self.iface.mapCanvas())
    self.iface.mapCanvas().setMapTool(self.point_tool)
    self.point_tool.canvasClicked.connect(self._write_line_widget)
```

This will:

- hide the plugin's dialog
- set the current Map Tool to your `PointTool`, i.e. now the signal `canvasClicked` will be emitted if the user clicks inside the map canvas
- connect the `canvasClicked` to a new function `self._write_line_widget`, which doesn't exist yet but will come soon

`_on_map_click()` will need to be called when `map_button` is clicked, who doesn't know of its existence yet. So let's change that. Connect the button's signal to the new function in `run()` (note it should be after `self.dlg` is defined obviously):

```python
#class QuickApi:
#def run():
if self.first_start == True:
		...
    self.dlg.map_button.clicked.connect(self._on_map_click)  # added line
```

### Quick re-write of plugin startup

For the plugin to handle this correctly, you need to re-arrange a bit the start-up logic. Without going into too much detail, the [`QDialog.exec_()`](https://doc.qt.io/qt-5/qdialog.html#exec) is not ideal in this case, as that line is blocking, i.e. the code stops there until the user presses the OK or Cancel button. It's usually alright, but it stops working when you introduce new asynchronous functions like event loops, as you did above. The whole logic to show the plugin to the user is a little flawed, so let's rewrite some of it:

In `quick_api.py:QuickApi.run()`, first delete `self.dlg.show()`, which is superfluous anyways. Then replace `self.dlg.exec_()` with `self.dlg.open()`. [`QDialog.open()`](https://doc.qt.io/qt-5/qdialog.html#open) will just open a modal dialog and immediately return control to the code. Its asynchronous nature means you have to know when the user presses OK/Cancel, so you have to listen for the appropriate signal and connect that to a function which does your work in case OK was clicked. The right signal is the dialog's built-in [`finished()`](https://doc.qt.io/qt-5/qdialog.html#finished) signal, which emits the result code (0 for Cancel button, 1 for OK), similar to the return value of the previous `QDialog.exec_()` method.

Now the plugin needs to know what to do when the `finished()` signal is emitted: of course it needs to run your actual code. So, take the whole `if result:` statement and put it into a new method called `result()`, which has to accept the result code the `finished()` signal emits. Your code should finally look approximately like this:

```python
#class QuickApi:
def run(self):
    if self.first_start == True:
        self.first_start = False
        self.dlg = QuickApiDialog()
        self.dlg.map_button.setIcon(QIcon(":images/themes/default/cursors/mCapturePoint.svg"))
        self.dlg.finished.connect(self.result)
        self.dlg.crs_input.setCrs(QgsCoordinateReferenceSystem(4326))
        self.dlg.map_button.clicked.connect(self._on_map_click)

    self.dlg.open()

def result(self, result: int):
    if result:
        project = QgsProject.instance()
				...
```

### Write the clicked coordinates to the GUI

At last you have to set up the `_write_line_widget()` function, which will take the emitted `QgsPointXY` from the `canvasClicked` signal and write it to our `lineedit_xy` `QgsFilterLineEdit` widget:

```python
#class QuickApi:
def _write_line_widget(self, point: QgsPointXY):
    self.dlg.lineedit_xy.setText(f"{point.y():.6f}, {point.x():.6f}")
    self.iface.mapCanvas().unsetMapTool(self.point_tool)
    self.dlg.show()
```

This will:
- set the text to the formatted latitude and longitude of the emitted point
- unset the current map tool, which will take care of some cleaning up (you could also save a reference to the previous map tool in `_on_map_click()` and restore it here)
- finally show the plugin dialog again which will now have the new clicked coordinate in its text field

## 6 Final plugin functionality

Finally the plugin is ready to be fully tested. Reload the plugin in QGIS and see the result. The plugin didn't change much visually, just a tiny new button. But the user experience just went through the roof!

The expected behavior at this point:
- When you click the Map button the plugin window disappears
- When you click the map canvas, the plugin window re-appears and contains the clicked coordinates in WGS84

For all practical purposes you could stop here. However, if you want to learn a few more tricks how to improve this plugin to be more user-friendly, keep on reading.

## 7 Bonus material

### Give the cursor a custom icon

Another neat functionality would be if the cursor of your custom Map Tool would have its own icon, not the default cross-hairs symbol. We opt for the same icon we used for the `QToolButton`.

Open `./maptool.py` and add the following just after declaring `WGS`:

```python
CUSTOM_CURSOR = QCursor(QIcon(':images/themes/default/cursors/mCapturePoint.svg').pixmap(48, 48))
```

We have to do a little bit of a roundabout here: `QCursor` only accepts a `QPixMap`, so our QGIS internal icon will need to be converted first and set to a size of 48 pixels.

Next, you'll have to let QGIS know that it should use that cursor when the `map_button` is clicked. You can also do this in your Map Tool, using its predefined [`activate()`](https://qgis.org/api/classQgsMapTool.html#ae43d0b80202ae4c9706c6154ae04b525) method, which is called when the Map Tool is activated (e.g. from `self.iface.mapCanvas().setMapTool(self.point_tool)`):

```python
#class PointTool(QgsMapToolEmitPoint):
def activate(self):
    QApplication.setOverrideCursor(CUSTOM_CURSOR)
```

Now the icon will change to our image, but it won't change back once the operation is completed. For that, you can hook into the `deactivated` signal which will be emitted when e.g. the map tool in unset. Connect that signal to a function restoring the old cursor:

```python
from PyQt5.QtWidgets import QApplication

def _write_line_widget(self, point):
    ...
    self.point_tool.deactivated.connect(lambda: QApplication.restoreOverrideCursor())
```

And that's it! Best of luck!
