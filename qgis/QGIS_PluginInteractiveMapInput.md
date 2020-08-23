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

```bash
mkdir quick_api_interactive
cp -r quick_api/* quick_api_interactive
```

You can already create the new files and folders which you'll need throughout the tutorial:

```bash
cd quick_api_interactive
mkdir icons  # We'll provide some icons later on
touch maptool.py  # This will hold our interactive map tool later
```

Now your file structure should look like this:

```bash
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

If you want to see it in action in QGIS, be aware that you need to copy these files to the **old plugin directory**, i.e. `$QGIS_PLUGIN_DIR/quick_api/`:

`cp -arf ../quick_api_interactive/* $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/quick_api`

## 2 Qt Designer - Add Map button

If you're not too familiar with Qt Designer, we have a [reference guide](https://gis-ops.com/qgis-3-qt-designer-explained/) for you.

Open the `quick_api_dialog_base.ui` in Qt Designer and perform the following steps in sequence:

1. Change the layout of the main `QDialog` to `Grid` by pressing `Lay Out in a Grid` button in the main toolbar
2. Drag a `QPushButton` to the right side of the `QgsFilterLineEdit` widget and name it *map_button*
3. Resize the rest of the widgets to fill the entire width of the dialog
4. To make it visually more attractive, change it's properties:
	- `QWidget.sizePolicy.Horizontal Policy`: *Fixed*
	- `QWidget.minimumSize.Width` & `QWidget.maximumSize.Width`: *25*
	- Delete the `QAbstractButton.text` value, we'll add an icon here soon
5. Save the UI file

Now, your UI should look approximately like this:

![new UI](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/quick_api_interactive_ui.png)

## 3 Qt Designer - Add file resources

Qt has a very handy in-app resource store, which you can use to store icons for buttons, the plugin etc. See a more in-depth explanation of this concept in our [reference guide](https://gis-ops.com/qgis-3-qt-designer-explained/#qt-resourcesqrc).

### Get images

You will add 3 icons, one for the plugin itself, one for the new Map button and one for the Map cursor which is used when a user clicked the Map button. Choose some free images from the web or our proposals from other plugins:
- plugin icon: https://github.com/nilsnolde/pelias-qgis-plugin/raw/master/PeliasGeocoding/gui/img/icon_reverse.png
- button icon: https://github.com/nilsnolde/orstools-qgis-plugin/raw/master/ORStools/gui/img/icon_isochrones.png
- cursor icon: https://github.com/nilsnolde/pelias-qgis-plugin/raw/master/PeliasGeocoding/gui/img/icon_locate.png

Note, whatever you choose the images should be PNG's with background transparency or it will look awful.

Move your images to the `./img` directory and remove the old icon `./icon.png`.

### Set up the resource store

In Qt Designer in the right panel there is a *Resource Browser* section (if not visible, activate it in *View ► Resource Browser*). Click on the small settings wheel to open the browser. In the browser, click on *Open Resource File*, navigate to your local resource file at `./resources.qrc` and open it.

The `resources.qrc` file has a *prefix path*, which basically acts as a unique identifier for plugins. This is necessary, since the whole QGIS application uses the same resources (your plugin's `resources.qrc` will just be added to QGIS) and if there's no prefixes you might accidentally load unintended images.

You'll notice that it complains that `icon.png` is missing. Doesn't matter, just remove the file from the dialog. Then, add all images to the *prefix path* and hit OK:

![Resource store](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/quick_api_interactive_resources.png)

Now these images are available in Qt Designer and can be accessed in PyQGIS.

### Change the Button icon

In Qt Designer itself you can only make use of the button icon, the others have to be changed in the code.

1. Click on the button in Qt Designer
2. Navigate to the property `QAbstractButton.icon` and from the dropdown choose *Choose Resource*
3. Choose the `icon_isochrones.png`

### Compile resource.qrc

You will have to compile the `resources.qrc` to Python code, so that your plugin understands which files are available from the Qt resource store. This will basically just byte encode the images into the format that QGIS can read:

```bash
pyrcc5 -o resources.py resources.qrc

```

### Compile GUI

Now, that you did changes to the `resources.qrc` store in Qt Designer, you unfortunately have to rebuild your GUI logic a little, otherwise a very annoying bug will be triggered.

First, you need to compile the UI file to a Python file. You haven't seen this command before in this tutorial series, but it's very similar to compiling `resources.qrc`:

```bash
pyuic5 --from-imports --resource-suffix '' quick_api_dialog_base.ui > quick_api_dialog_base.py
```

- `pyuic5` translates the `quick_api_dialog_base.ui` file to the Python representation
- `--from-imports` lets the `resources.py` file be imported from `.` (see last line in the new file `quick_api_dialog_base.py`)
- `--resource-suffix ''` will import `resources.py` (i.e. without a suffix), while the default would try to import `resource_rc.py`

Basically the default behavior is not compatible with Python 3 import system and the Plugin Builder, so you have to jump through these hoops. Also you need to change a few things in the code:

To use the new file, in `./quick_api_dialog.py`, remove these lines:

```python
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'quick_api_dialog_base.ui'))
```

and add an `import` statement for your new `quick_api_dialog_base.py` file:

```python
from .quick_api_dialog_base import Ui_QuickApiDialogBase
```

Also, remove `FORM_CLASS` from the `QuickApiDialog` class constructor and replace it with `Ui_QuickApiDialogBase`.

In the end, `./quick_api_dialog.py` should look like this:

```python
from PyQt5 import QtWidgets

from .quick_api_dialog_base import Ui_QuickApiDialogBase


class QuickApiDialog(QtWidgets.QDialog, Ui_QuickApiDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        super(QuickApiDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
```

Be aware, that every time you **change the GUI, you'll have to run `pyuic5`** to translate the changes to its Python representation.

### Test in QGIS

You already made a lot of changes to the initial plugin, so it's time to make sure everything worked smoothly:

`cp -arf ../quick_api_interactive/* $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/quick_api`

Upon reloading you'll notice that your plugin lost its icon. No worries, that'll be back soon enough:)

### Troubleshooting

- If you get `ModuleNotFoundError: No module named 'resources_rc'` after loading it in QGIS, you didn't delete or comment out the `uic.loadUiType()` lines in `./quick_api_dialog.py`
- If you get `ModuleNotFoundError: No module named 'quick_api_dialog_base'`, you either forgot to import or imported it incorrectly. Remember Python 3 needs a relative import here, i.e. `from quick_api_dialog_base import Ui_QuickApiDialogBase`

## 4 PyQGIS - Set up Map Tool and signal

**Finally** you can do a bit more relevant work! You'll start with **`maptool.py`**

This will be the actual tool which will let users choose a point on the canvas for reverse geocoding. It's surprisingly little code.

What you will need create is a real Map Tool, like e.g. the Zoom Tool in QGIS or the Pan Tool. Using the new tool will only emit the point clicked in the map canvas to a listening function which will transform the point to WGS84 and subsequently send it to Nominatim. So, let's get started.

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

Then build a class `PointTool` based on [`QgsMapToolEmitPoint`](https://qgis.org/pyqgis/3.0/gui/Map/QgsMapToolEmitPoint.html):

```python
class PointTool(QgsMapToolEmitPoint):

    def __init__(self, canvas):

        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
```

This class (and its parent) needs a `QgsMapCanvas` instance in its initialization, to know on which map canvas it should act.

The point tool also needs to know when it needs to capture a click from the user, i.e. it needs to know which `event` is has to listen to. `QgsMapToolEmitPoint` has a few pre-defined event methods available which you can implement. In this case, you'll use `canvasReleaseEvent`, which is the event triggered when the mouse button was pressed **and released** while hovering over the map canvas. Other events include `canvasMoveEvent` and `canvasPressEvent`. These events are managed by QGIS and need to be implemented before they're doing anything. The `event` it accepts is a [`QgsMapMouseEvent`](https://qgis.org/api/classQgsMapMouseEvent.html), which, among other properties, knows the point coordinates of the click event in the current CRS of the map canvas:

```python
# class PointTool(QgsMapToolEmitPoint):
canvasClicked = pyqtSignal('QgsPointXY')
def canvasReleaseEvent(self, event):
    # Get the click and emit a transformed point

    crs_canvas = self.canvas.mapSettings().destinationCrs()

    point_canvas_crs = event.mapPoint()

    wgs = QgsCoordinateReferenceSystem(4326)
    xformer = QgsCoordinateTransform(crs_canvas, wgs, QgsProject.instance())

    point_wgs = xformer.transform(point_canvas_crs)

    self.canvasClicked.emit(point_wgs)
```

This might be the first time you come across `pyqtSignal`, so we recommend to go through our [short primer on PyQt Signal/Slots concept](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained).

Above you define a custom signal `canvasClicked`, which can emit a `QgsPointXY` variable type. It will only emit in the above case when a `canvasReleaseEvent` was triggered and after the point was transformed to WGS84. This emitted `signal` however needs a `slot` to connect to, i.e. a function which does something useful with the emitted point. As you will see shortly, that slot will be the function adding the emitted WGS84 coordinates the user clicked to the `QgsFilterLineEdit` widget in your GUI, which a user had to fill manually before.

## 5 PyQGIS - Implement Map Tool and slot

Now that you set up the signal that will emit the clicked point, you need to tell the plugin what should happen with that `QgsPointXY`.

This is a 2 stage process:
1. connect the `map_button` `QgsPushButton`'s `clicked` signal to a function initializing the Map Tool
2. in this initialization function, connect the `canvasClicked` signal of your Map Tool to the function which will populate the `lineedit_xy` `QgsFilterLineEdit` with the emitted `QgsPointXY`.

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
    self.point_tool.canvasClicked.connect(self._writeLineWidget)
```

This will:

- hide the plugin's dialog
- set the current Map Tool to your `PointTool`, i.e. now the signal `canvasClicked` will be emitted if the canvas is clicked
- connect the `canvasClicked` to a new function `self._writeLineWidget`, which doesn't exist yet but will come soon

This function will need to be called when `map_button` is clicked, who doesn't know of its existence yet. So let's change that. Connect the button's signal to the new function in `run()` (note it should be after `self.dlg` is defined obviously):

```python
#class QuickApi:
#def run():
if self.first_start == True:
		...
    self.dlg.map_button.clicked.connect(self._on_map_click)  # added line
```

### Quick re-write of plugin startup

For the plugin to handle this correctly, you need to re-arrange a bit the start-up logic. Without going into too much detail, the [`QDialog.exec_()`](https://doc.qt.io/qt-5/qdialog.html#exec) is not ideal (ever, but particularly in this case), as that line is blocking, i.e. the code stops there until the user presses the Ok or Cancel button. It's usually alright, but it stops working when you introduce new asynchronous functions like event loops, as you did above. The whole logic to show the plugin to the user is a little flawed, so let's rewrite some of it:

In `quick_api.py:QuickApi.run()`, first delete `self.dlg.show()`, which is superfluous anyways. Then replace `self.dlg.exec_()` with `self.dlg.open()`. [`QDialog.open()`](https://doc.qt.io/qt-5/qdialog.html#open) will just open a modal dialog and immediately return control to the code. Its asynchronous nature means you have to know when the user presses OK/Cancel, so you have to listen for the appropriate signal and connect that to a function which does your work in case OK was clicked. The right signal is the dialog's built-in [`finished()`](https://doc.qt.io/qt-5/qdialog.html#finished) signal, which emits the result code (0 for Cancel button, 1 for OK), similar to the return value of the previous `QDialog.exec_()` method.

Now the plugin needs to know what to do when the `finished()` signal is emitted: of course it needs to run your actual code. So, take the whole `if result:` statement and put it into a new method called `result()`, which has to accept the result code the `finished()` signal emits. Your code should look approximately like this:

```python
#class QuickApi:
def run(self):
    if self.first_start == True:
        self.first_start = False
        self.dlg = QuickApiDialog()
        self.dlg.finished.connect(self.result)
        self.dlg.crs_input.setCrs(QgsCoordinateReferenceSystem(4326))
        self.dlg.map_button.clicked.connect(self._on_map_click)

    self.dlg.open()

def result(self, result):
    if result:
        project = QgsProject.instance()
				...
```

At last, you'll have to connect the new `result()` method to the `finished()` signal in the `run()` method:

```python
#class QuickApi:
#def run(self):
#if self.first_start == True:
#self.first_start = False
#self.dlg = QuickApiDialog()
self.dlg.finished.connect(self.result)
```

### Write the clicked coordinates to the GUI

At last you have to set up the `_writeLineWidget()` function, which will take the emitted `QgsPointXY` from the `canvasClicked` signal and write it to our `lineedit_xy` `QgsFilterLineEdit` widget:

```python
#class QuickApi:
def _writeLineWidget(self, point):

    x, y = point

    self.dlg.lineedit_xy.setText("{0:.6f}, {1:.6f}".format(y, x))
    self.point_tool.canvasClicked.disconnect()
    self.dlg.show()
```

This will:
- set the text to the formatted latitude and longitude of the emitted point
- disconnect the function from its signal
- finally show the plugin dialog again which will now have the new clicked coordinate in its text field

## 6 Final plugin functionality

The last thing to do is to give the plugin an icon. This is really quick, just change the `icon_path` value in `quick_api.py:QuickApi`'s `initGui()` method to `':/plugins/quick_api/img/icon_reverse.png'`.

Finally the plugin is ready to be fully tested. Perform another

```bash
 cp -arf ../quick_api_interactive/* $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/quick_api
```

Reload the plugin in QGIS and see the result. The plugin didn't change much visually, just a tiny new button. But the user experience just went through the roof!

The expected behavior at this point:
- When you click the Map button the plugin window disappears and the cursor changed to cross-hairs
- When you click the map canvas, the plugin window re-appears and contains the clicked coordinates in WGS84
- Upon OK/Cancel the cursor doesn't change, indicating that your map tool is still active

For all practical purposes you could stop here. However, if you want to learn a few more tricks how to improve this plugin to be more user-friendly, keep on reading.

## 7 Bonus material

### Make the plugin window modal

What usually annoys me with a lot of plugins: When the plugin is open and I click inside the QGIS window the plugin disappears, just like any other program window would. In technical terms: the plugin window is modeless. I usually want it to be modal, i.e. it should stay on top of the QGIS main window until I close it myself.

This is by far the easiest modification. When you instantiate the plugin dialog, just give it a parent, the main QGIS window in this case:

```python
#class QuickApi:
#def run(self):
if self.first_start == True:
    #self.first_start = False
    self.dlg = QuickApiDialog(parent=self.iface.mainWindow())
```

### Give the cursor a custom icon

Another neat functionality would be if the cursor of your custom Map Tool would have its own icon, not the default cross-hairs symbol. Not really hard, but a little tricky. Watch..

The icon is already in your resource store, remember? If not, go back to the [resource store section](#3-qt-designer--add-file-resources). So, now you need to access it from the code. You actually already did that for the plugin icon quite recently. To access resource store elements you pass the full resource file path (prefix path + relative path in plugin directory + file name) and prefix it with a colon.

Open `./maptool.py` and add the following to the `PointTool`'s `__init__()`:

```python
self.cursor = QCursor(QPixmap(':/plugins/quick_api/img/icon_locate.png').scaledToWidth(48))
```

This will define the cursor with the `icon_locate.png` as image and a width of 48 pixels.

Next, you'll have to let QGIS know that it should use that cursor when the `map_button` is clicked. You can also do this in your Map Tool, using its predefined [`activate()`](https://qgis.org/api/classQgsMapTool.html#ae43d0b80202ae4c9706c6154ae04b525) method, which is called when the Map Tool is activated:

```python
#class PointTool(QgsMapToolEmitPoint):
def activate(self):
    QApplication.setOverrideCursor(self.cursor)
```

Now the icon will change to our image, but it won't change back once the operation is completed. Also, you still have the problem, that technically your Map Tool is never deactivated and will remain the active Map Tool as long as the user doesn't choose another one in the QGIS GUI. For this, you need to modify `quick_api.py`:

First, let's save a reference to the last map tool the user used before he initiates ours. In the `run()` method add the following:

```python
#class QuickApi:
def run(self):
		...
    self.last_maptool = self.iface.mapCanvas().mapTool()
    #self.dlg.open()
```

To revert to the properties the user had before he executed your tool, you best set the old properties in the last `slot`, i.e. `_writeLineWidget()`:

```python
#class QuickApi:
from PyQt5.QtWidgets import QApplication

def _writeLineWidget(self, point):
    QApplication.restoreOverrideCursor()
    self.iface.mapCanvas().setMapTool(self.last_maptool)
		...
```

And that's it! Best of luck!
