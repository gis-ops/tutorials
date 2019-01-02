# Create a quick QGIS 3 Plugin

This tutorial is not intended to be a deep dive into QGIS plugin development, but rather a guideline for creating a plugin from available boiler plate code based on the very useful [Plugin Builder](http://g-sherman.github.io/Qgis-Plugin-Builder/). It focuses a lot on the conceptual how's and why's of Python plugins. The actual development part is fairly quick.

**Goals**:

- get more familiar with `PyQGIS` and `PyQt5` and the respective documentation
- build a GUI with QGIS native Qt Designer
- understand QGIS interaction with plugins
- connect GUI elements to Python functions
- deploy the plugin locally and upload to QGIS official plugin repository

**Plugin functionality**:

- User copy/pastes X, Y coordinates into a text field
- Upon OK button click, the [Nominatim API](https://wiki.openstreetmap.org/wiki/Nominatim) is queried
- A Point layer is generated in-memory, displayed on the map and zoomed to

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **QGIS v3.4**
> Occassionally, the author might choose to give hints on Windows-specific setups. `Ctrl+F` for WINDOWS flags. Mac OS users should find the instructions reasonably familiar.

## Prerequisites

### Hard prerequisites

- Basic understanding of Python
- QGIS v3.x
- [Plugin Builder](https://plugins.qgis.org/plugins/pluginbuilder3/) QGIS plugin installed
- Python >= 3.6 (should be your system Python3)

### Recommendations

- Use an IDE, such as [Sypder](https://www.spyder-ide.org) or [PyCharm](https://www.jetbrains.com/pycharm/)
- Even though we're developing **on** Ubuntu, we should make sure Windows users can use the plugin as well. Unfortunately there's no list of Python modules which are available via Win installers.  [This page](https://trac.osgeo.org/osgeo4w/wiki/PackageListing#Languages) is fairly outdated. The base Python distribution is [Python's own](https://www.python.org/downloads/release/python-360/). Additionally, the following Python packages are definitely shipped: matploblib, SciPy, NumPy, requests, shapely. In worst case, find a Windows machine and do `pip list` in a OSGeo4W terminal.
- Use the system's Python3 as interpreter for your IDE: `/usr/bin/python3`
- **WINDOWS**: you're locked in with OSGeo4W for QGIS, but you can have a look [here](https://trac.osgeo.org/osgeo4w/wiki/ExternalPythonPackages#UsestandardWindowsinstallers) on how to change your default Python interpreter to the one shipped with OSGeo4W, for a better developing experience

If you follow above recommendations, you should now be able to run the following in your IDE's Python console:

```bash
import qgis
import PyQt5
```

If that was successful, you're all set to start the development!

### Troubleshooting

- if you can't import qgis and/or PyQt5, you likely are not working with the correct Python executable, i.e. the system's Python3. Typing `import sys; print(sys.executable)` should print `/usr/bin/python3.6`

- if that's the case, your QGIS installation is probably broken. A re-installation will help.

## First steps

### Plugin Builder

#### About Plugin Builder

The Plugin Builder arguably takes a lot of work off your shoulders, as it creates all necessary boiler plate code you need to immediately start development. However, we found the amount of (well-intended) overhead it imposes on developers a little overwhelming in the beginning. Consequently, we'll focus for the rest of the tutorial on the most crucial parts of your new plugin and ignore the rest.

#### Run Plugin Builder

If you have successfully installed the Plugin Builder 3 plugin, it is available in the 'Plugins' menu in QGIS. Make sure to fill out the details similar to ours:

![Plugin Reloader settings](static/img/quick_api_img1.png)

Note, there will be a few more dialogs, just use common sense when filling those in. Or accept the defaults.

After confirming where to store your new plugin, you'll presented with a dialog detailing what to find where and which steps to take from this point on. For the sake of this tutorial (and maybe your sanity), ignore its contents for now. If anything goes wrong with the short descriptions it provides you'll be left with more questions than answers. By the end of this tutorial, you'll have a lot more knowledge on the topics it suggests and you can more comfortably use its recommendations.

#### Generated files

The Plugin Builder will have generated a lot of files now. Head over to your new plugin project directory and `ll .`. To avoid confusion and make it as simple as possible, you can safely delete all files and folders except for these:

```bash
├──quickapi
   ├──icon.png
   ├──__init__.py 									# mandatory for minimal plugin
   ├──metadata.txt
   ├──quick_api.py									# mandatory for minimal plugin
   ├──quick_api_dialog.py							 # mandatory for minimal plugin
   ├──quick_api_dialog_base.ui						# mandatory for minimal plugin
   └──resources.qrc								   # mandatory for minimal plugin
```

This is still a lot to take in. So let's look at them in little more detail:

- `icon.png`: the default icon for the plugin. You will change this to reflect your own icon.

- `__init__.py`: contains the function which will initialize the plugin on QGIS startup and register it with QGIS, so it knows about this plugin.

- `metadata.txt`: contains information about the plugin, which will be used by the official QGIS plugin repository and the QGIS Plugin Manager to display information about your plugin, e.g. description, version, author, URL etc.

- `quick_api.py`: contains the heart of the plugin: all custom functionality will go into this file.

- `quick_api_dialog.py`: loads the plugin User Interface (UI), when QGIS starts up. You won't alter this file in this tutorial.

- `quick_api_dialog_base.ui`: this is the Qt Designer file to style and build the UI, i.e. plugin window.

- `resource.qrc`: contains the resources for Qt. You will only edit this file when you rename the plugin icon or you want to add additional icons. **Needs to be compiled to resources.py**.

### Test initial plugin

At this point you can already test if QGIS loads your new (very unfunctional) plugin.

#### Compile `resources.qrc`

First you need to compile the `resources.qrc` file to `resources.py`, so that QGIS can pick up the plugin icon:

```bash
pyrcc5 -o resources.py resources.qrc
```

More on `resources.qrc` [here](#resources-qrc).

#### Copy code to plugin directory

Next, you should create the directory where your plugin will be picked up by QGIS on startup and copy all files there:

```bash
cp -arf ../quickapi $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

Run this command whenever you change something in your development project.

#### Load plugin

Start QGIS and head over to `Plugins > Manage and Install Plugins` et voila:

![Successful installation](static/img/quick_api_img2.png)

If you activate it, a new icon will be added to the Plugin toolbar. Also, you'll find the plugin in the 'Vector' menu in QGIS.

#### Troubleshooting

- if you don't see the plugin in the manager after a QGIS restart, check you didn't accidentally set the `experimental` flag by allowing experimental plugins in `Plugin Manager > Settings`.

- if you experience a Python error, you likely did something wrong in the previous steps. Best bet: start from scratch before you dump an inconceivable amount of time in finding the bug.

## Qt Designer

First, start Qt Designer. The app is shipped on all OS's with QGIS and should be available as an executable on your computer.

### Short roundup of Qt Designer

In the startup dialog, open `quickapi/quick_api_dialog_base.ui` and you'll see your bare-bone plugin UI. For easier navigation, here's a quick breakdown of the Qt Designer interface:

![Qt Designer Interface](static/img/quick_api_img3.png)

#### 1 Available widgets

In Qt lingo all GUI elements are classified as `Widgets`, which can have all kinds of actual UI functionality like buttons, containers or user input elements. Drag a few widgets into your dialog and experiment a bit. There's also several custom QGIS widgets at the very bottom, which extend functionality of Qt widgets (like CRS picker). We'll use one of the QGIS ones in this tutorial.

#### 2 Object inspector

You can click on widgets in your dialog to select them. But sometimes it's good to see the hierarchy of widgets or select it from a list, e.g. when they're overlapping each other in the dialog.

#### 3 Property Editor

Each widget exposes a list of properties, like geometry or font, which you will find in this panel. You didn't see any actual code yet, but these properties are accessible methods through the Python class of your GUI. So it's also a good reference to available widget properties to be modified. It gives you a whole lot more information though:
- the name you give the widget
- the PyQt5 class name, e.g. `QDialogButtonBox` for the OK/Cancel button group
- you can immediately see the sub-classing for each widget by examining the tabs of the Property dialog. E.g. the `QDialogButtonBox` is sub-classed from (in descending order):
	- `QObject`, which only exposes the `objectName` property and will be widget identifier in your code
	- `QWidget`, which exposes multiple properties, mostly layout related
	- and finally `QDialogButtonBox`, which has mostly functional properties, e.g. which buttons are displayed

#### 4 Layout toolbar

Quick access to different layouts for container widgets. Explanation follows in [a following section](#important-qt-designer-concepts).

### Build GUI

You will build a very simple GUI: only a small box where the user can paste a X, Y coordinate pair and a CRS picker if the coordinate is not in WGS84.

Do the following steps:

1. Select the dialog window and press `Lay Out Vertically` button in the [toolbar](#4-layout-toolbar)
2. Drag a `QgsFilterLineEdit` widget to the dialog and insert it above the buttons
3. Alter the following properties of the new widget:
	- `QObject.objectName`: lineedit_xy
	- `QLineEdit.placeholderText`: Lat, Long
4. Drag a `QgsProjectionSelectionWidget` below the other widget and name it 'crs_input'
4. Resize the dialog to fit your needs

Now, your GUI should look similar to this:

![Final GUI](static/img/quick_api_img4.png)

### Important Qt Designer concepts

- **Every container widget needs a layout!** In your case that's only the `QDialog` dialog window containing both the line edit widget and `QDialogButtonBox`. Layouts help you in... well, layouting (to keep consistent element spacing when resizing etc.). Try other layout types and add a few more widgets to see the differences.

- **Every widget needs a unique name property defined in `QObject.objectName`!** It'll auto-name your widgets and while it's not required it's highly recommended to use structured naming for your widgets. It'll help you a lot when you access them in your code later on, which becomes a lot more important with a multitude of widgets.

- **Size policies are important!** When building bigger GUIs it will be increasingly important to define how widgets behave visually within their layout. When the user changes the window size, it can be disorienting if a button scales with the resizing. Size policies define the widget's size behaviour within the layout.

## Code Preparations

In this tutorial we will throw a few fundamental programming principles over board and focus only on the most crucial parts of a QGIS plugin. To this end, we will **not**:

- separate GUI logic from processing logic
- write unit tests

These are really mantras you can't repeat often enough. There will be other tutorials focusing on testing.

You will work exclusively with `quick_api.py`. But we'll give a short explanation of `quick_api_dialog.py` as well, for reference.

### Library documentation: Help yourself!

Before we start to get into the fun part, just a quick reminder on how to best help yourself once you're stuck. If you're an experienced developer, you can probably skip this section. Still helpful to have the links below though.

#### PyQt5

PyQt5 (and its C++ parent Qt) is the GUI framework QGIS relies on. Most UI related objects, methods and properties can be found in this library. Mostly, you'll deal with `PyQt5.QWidgets` and `PyQt5.QtGui`.

Unfortunately, the direct code documentation of PyQt5 provided by Riverside is non-existing. However, there are a few ways to help yourself here:

- you're using an IDE? Great! If you're lucky `Ctrl+Q` in PyCharm (`Ctrl+I` in Spyder) will show input and output parameters of the selected function.

- the main documentation is [here](http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets). However, it usually only refers you to the C++ documentation of the Qt library, which PyQt5 wraps for Python. That documentation can be slightly overwhelming. You'll get through it though, just consider these few guidelines (taking `QLineEdit` as reference):
	- in [Functions](https://doc.qt.io/qt-5/qlineedit.html#public-functions) description, the first column tells you which object type is returned. `void` does not return anything. `QString` is implemented as a simple Python `str`. The first few rows let you know how to construct an instance of the widget.
	- the Properties are implemented as methods, not attributes, i.e. in [`QLineEdit`](https://doc.qt.io/qt-5/qlineedit.html#properties), `text` is implemented in `PyQt5` as `<some QLineEdit widget>.text()`, which will give you the current text of the widget
	- obviously every widget inherits a plethora of functions, methods and signals of its parent widgets, which is why using the C++ documentation is only good for specific lookups
	- Signal and Slots we'll deal with later

- to lookup properties of a specific widget, use Qt Creator's [Properties](#3-property-editor) panel

#### PyQGIS

PyQGIS is the standard synonym for the `qgis` Python library (which will help you a lot when googling solutions). For Linux users (with IDE's), documentation is fairly straight forward, as they benefit from auto-completion and inline documentation. **WINDOWS** users who did not manually change their Python executable to QGIS' one (or include the appropriate directories in their PYTHONPATH), won't be as lucky.

- main documentation is here: https://www.qgis.org/pyqgis/master/. From QGIS v3.x on, the documentation improved A LOT! If you ever wonder how to access certain QGIS related properties or methods, either use the search box. Or drill down manually. Basically, the (commonly) 2 most important modules in PyQGIS are `gui` and `core`. The classes are ordered by broader GIS topics (Attributes, Fields and so on) and class names are very descriptive, so you should find your way easily. **Note**, that some class names are prefixed by `Qgs`, some are prefixed by `Qgis` (no, that's not confusing at all...). Occassionally, you'll find that the [C++ documentation](https://qgis.org/api/) is more descriptive than the Python one.

- the main online platform is [Stack Exchange](https://gis.stackexchange.com). All the great QGIS goddesses and gods frequently visit and can help you out of your misery. Apply common sense before asking questions though, i.e. research for at least 20 mins. It really boosts your understanding if you solve problems on your own.

- For more general questions which could be interesting for the whole community, subscribe to the QGIS developer [mailing list](https://lists.osgeo.org/mailman/listinfo/qgis-developer)

PyQGIS, despite its ingenuity, can be an awkward beast. Almost the whole API is made up of classes and there are virtually no class attributes (at least not where you'd expect them); all is accessed through methods. If you ever really feel like jumping out the window, don't worry, we've all been there and it says nothing about your capabilities as a developer.

### Explanation of files, methods and constants

#### `resources.qrc`

That's a Qt resource file. Basically, it contains instructions for the Qt framework where to find which resources, e.g. plugin icons. Find a more detailed discussion [here](#resources-qrc). It needs to be compiled to `resources.py` and imported in `quick_api.py`.

#### `__init__.py`

Apart from initializing the entire `quickapi` package, it's also responsible to make QGIS aware of its existence. Which is what the `classFactory()` class does by instantiating your plugin's main class from `quick_api.py`. More on that further down.

**Don't alter the classFactory() class!** It's implicitly expected by QGIS. Which you'll find is a common thing in QGIS' Python API.

#### `quick_api_dialog.py`

This file only contains a single class: `QuickApiDialog`, which sub-classes `QDialog` and `FORM_CLASS`, hence inherits all methods of both classes.

- `QDialog`: a `QWidget` which will represent your plugin window (**not** the UI elements themselves). You can see its properties in [Qt Creator](#3-property-editor). You won't interact much with it.

- `FORM_CLASS`: loads your UI file into a class.

The `QuickApiDialog` class will be instantiated in the main `quick_api.py` module, which you will see later. The main line to note here is:

```python
		self.setupUi(self)
```

`setupUi()` is a method of `FORM_CLASS`, which will set up your UI elements in your `QDialog` plugin window. What is highly confusing here: the caller's `self` refers to `FORM_CLASS`, the argument `self` refers to `QDialog` (as `setupUi()` takes a `QWidget` as argument). That's entirely valid, since `QuickApiDialg` sub-classes both classes, but it sure is confusing to any newcomers.

#### `quick_api.py`

This is a bigger beast and you'll spend most time here. It looks scary at first, but trust us, there's a lot of unnecessary boiler plate code here (at least for your current purposes). Instead of stripping it down to the most essential parts, we'll explain all methods. But you will only work with the most important ones. [**required**] methods are implicitly expected and called by the main QGIS application, so don't alter their name or input parameters!

It only contains a single class `QuickApi`. This class will be instantiated by the plugin's `__init__.py`'s `classFactory` class, which in turn is called by QGIS on startup to make your plugin known to QGIS. So, really, this is the heart of the plugin.

##### `def __init__(self, iface)` [**required**]

The `QuickApi` class is passed the `iface` parameter, which is a `QgisInterface` and lets you interact with the QGIS GUI.

We'll go through the lines in order:

- `self.iface`: arguably the most important instance. It saves a reference to the QGIS GUI interface (`qgis.gui.QgisInterface`)

- `locale`: all code lines concerning locales, you can (more or less) safely ignore for now. They mostly deal with translations.

- `self.actions`: a container for `QAction`s, which we'll explain a little later.

- `self.menu`: the name which will appear in the menu bar for this plugin.

##### `def tr(self, message)`

If translation would be set up, this method would handle that. You can read a little more about it [here](https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/plugins.html#translation). You won't deal with translations. But you can't delete this method either without modifying quite a bit of code. So, leave it where it is, it doesn't hurt, really.

##### `def add_action(self, ...)`

It's creating a `QAction` object, which can be used to instruct QGIS to add icons to a menu, toolbar etc. What it really only does, is:

- add icon to Plugin Toolbar
- add entry to QGIS 'Vector' menu list
- set help texts if specified (`setStatusTip`, `setWhatsThis`)
- add a callback to the action, which is executed when either the icon or the menu item are clicked (`action.triggered.connect(callback)`)

##### `def initGui(self)` [**required**]

This method is called by QGIS when the main GUI starts up or when the plugin is enabled in the Plugin Manager.

It only calls the `add_action()` method above, which initiates the plugin menu entry and toolbar icon. You can add additional parameters to the call like `whats_this` or `status_tip`, which give some help to the plugin user.

**Note the `callback` paramter** is set to `self.run`. Meaning, the `self.run()` will be executed once the user clicks on the plugin menu item or on the toolbar icon. So, you can already guess, that that's the most important function in this class.

Also note the icon path: `':/plugins/quick_api/icon.png'`. The colon instructs QGIS to use the compiled `resources.py` file to locate the icon. Open the original `resources.qrc` file and you'll see the connection. A more detailed discussion of the resource file is given [here]().

Also, we state here that the plugin is started for the first time during the lifetime of a running QGIS session.

##### `def unload(self)` [**required**]

Will be executed when the plugin is disabled. Either in the Plugin Manager or when QGIS shuts down.

It only removes the previously defined `QAction` object from the menu and remove the plugin icon from the toolbar.

##### `def run(self)`

So, finally we arrived at the main code block, which executes the custom plugin functionality. This method is called by the previously defined `QAction` object, which went into the toolbar icon and the menu entry.

Really, this function could be called anything you'd like. There's no hidden meaning to it, as there is for `unload(self)` or `initGui(self)`. You could even have multiple callbacks like `run(self)` connected to a `QAction`.

First thing it does here: check if this is the first time the plugin is called. Remember, this function is called every time the user clicks on the plugin toolbar button/menu entry. Only if it's the first start, it'll build the GUI by instantiating the `QuickApiDialog` class (which calls its `setupUi()` in its `__init__()`) and assigning it to `dlg`. If the GUI would be freshly built every time the user calls the plugin, all previous GUI settings would be lost. `dlg` now holds all plugin GUI objects, which can be accessed by the names you gave them in Qt Designer.

`dlg.show()` shows the GUI modeless (i.e. the user can interact with QGIS while the GUI is open) .

`dlg.exec_()` is a shortcut method to show the GUI (yes, this is actually duplicate functionality) and returns the option the user chose (0 for pressing Cancel button, 1 for pressing OK button). The internals are little elaborate and you can read more about it [here](http://doc.qt.io/qt-5/qdialog.html#modal-dialogs). I think the reason why `show()` is implemented on top of `exec_()` is that `exec_()` will return a modal dialog (i.e. user can't interact with parent window), while `show()` makes sure it's modeless. Nevertheless, a little dirty.

*Fun fact*: `exec_()` is equivalent to `exec()` and was introduced by `PyQt`, since `exec` was a reserved keyword until Python 3. `exec_()` is still best practice.

So, if `result` is `True` (or 1, which is equivalent in Python), meaning the user clicked OK, we want the plugin to execute its costum code. This is finally where the boiler plate ends and the action starts.

## Custom plugin code

In its current state, the plugin will show the correct GUI, but not do anything when OK is pressed. So, to implement our desired functionality, we have to do add a bit of code to the `run(self)` method.

The logic will be:

1. Read the contents of the GUI field, i.e. the Lat/Long and the CRS
2. Convert the string to Point X & Y and transform to WGS84 decimal coordinate if necessary, as expected by Nominatim
3. Build the request to Nominatim's API and fire it
4. Process the response to add it as a layer to QGIS
5. Add logic to zoom to a bounding box

After each step, pause for a moment, add some `print()` statements to your code to see that everything goes as expected, copy your code to the plugin directory and reload it in QGIS. Open a Python console and run the plugin logic. If you see unexpected results, revert to the code and investigate.

### Imports

We'll need a few import from `qgis.core` and `QMessageBox`, plus `requests` for this to work. Just paste this into your import statements at the top of the file, we'll explain later:

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

Note, in other tutorials people often use star imports, i.e. `from qgis.core import *`. This is bad practice generally. While it makes your import statement a lot more compact, you have no idea where the method comes from when this is done to multiple modules (and neither does your IDE).

### Set dialog attributes

We included a CRS picker in our plugin. However, there's no option to set a default CRS from Qt Designer. Since we want this to be WGS84 (most coordinates are copied from online map providers such as Google Maps), we have to set that in the code. We add the following line to the first `if` statement in `run(self)`:

```python
if self.first_start == True:
	dlg.crs_input.setCrs(QgsCoordinateReferenceSystem(4326))
```

`crs_input` is the CRS picker GUI object, an instance of `QgsProjectionSelectionWidget`. In its [documentation](https://qgis.org/api/classQgsProjectionSelectionWidget.html#a2af9a2e3aaf29ddbe9a6a9121d9bf505), you'll find all info on its methods, like `setCrs()`. Which expects a `QgsCoordinateReferenceSystem`, which again can be built from a valid EPSG code as integer.

### 1. Process user input

Once the GUI is correctly built, it's shown to the user and it'll be open until the user interacts with its buttons. Now, you can add the logic to read the user input once the OK button was clicked. Also, define the output CRS, which will be WGS84:

```python
if result:
		lineedit_text = dlg.lineedit_xy.value()
		crs_input = dlg.crs_input.crs()
		crs_out = QgsCoordinateReferenceSystem(4326)
```

`lineedit_text` is a string. We need it as coordinate decimal points though:

```python
#if result:
lineedit_yx = [float(coord.strip()) for coord in lineedit_text.split(',')]
```

A lot can go wrong here already: the user doesn't use a comma separator or generally inputs something entirely wrong. To protect against user failure, we add a quick error dialog when there's an error with this function (of course this won't protect for the user swapping X and Y):

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

**DEBUG**: add `print(crs_input.authid(), lineedit_yx)` to the end and reload plugin in QGIS.

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
                                   self.crs_out,
                                   self.project)
    point_transform = xform.transform(point)
    point = point_transform
```

`QgsCoordinateReferenceSystem` comes with `authid`, which returns a string in the form `Provider:ID`, e.g. 'EPSG:4326' for WGS84 Lat/Long. `QgsCoordinateTransform` also expects a `QgsProject.instance()` so that custom project-based transformations can be applied (if set).

**DEBUG**: add `print(point)` before and after the transformation.

### 3. Request Nominatim API

Nominatim expects a GET request, which means parameters are encoded in the URL string, e.g. https://nominatim.openstreetmap.org/reverse?lat=52.098&lon=8.43&format=json. It's best practice to pass a base URL and the parameters separately, not in one huge URL string. Additionally, Nominatim's [usage policy](https://operations.osmfoundation.org/policies/nominatim/) dictates to include a descriptive `User-Agent` in the request header to identify applications.

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
self.project.addMapLayer(layer_out)
```

First, you build a Point object from the response X & Y. A `QgsFeature` is how QGIS understands a single feature entity. It holds information on geometry and attributes, which you'll have to set. Remember, `QgsPointXY` is not a geometry, only a Point object (confusing, really, since `QgsPoint` **is** a geometry), so we'll have to create a geometry from it first.

The layer's attributes (i.e. the field names) are actually not known to the new feature. But you can still pass an ordered list of attribute values, which will have to be in the same order as the layer initialization in the last code block, i.e. first `address`, then `license` and of course hold the same data type.

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
if self.project.crs().authid() != 'EPSG:4326':
	xform = QgsCoordinateTransform(crs_out,
	                               self.project.crs(),
	                               self.project)
	bbox_geom.transform(xform)
self.iface.mapCanvas().zoomToFeatureExtent(QgsRectangle.fromWkt(bbox_geom.asWkt()))
```

First, construct `QgsPointXY`s from the extent of `boundingbox` and add those to `QgsGeometry` to build a Polygon geometry. A geometry object can then be transformed in-place. Finally, the `zoomToFeatureExtent()` method of the map canvas expects a `QgsRectangle`, which can be built from the Well-Known-Text (WKT) string of the polygon geometry.

## Final plugin

When you've gone through all the steps above and your plugin works as expected, it's time to prepare for upload to the QGIS plugin repository.

**NOTE: do not upload this plugin to the QGIS repository!!**

### `metadata.txt`

This is the main source for the plugin repository, but also the QGIS Plugin Manager, which both extract information about author, version etc from here. Generally, you can use this file to store all kinds of meta information, like a help URL or collaborators. The metadata.txt file can be parsed in Python with the native `configparser` library. Just remember, it has to follow [general config guidelines](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure).

Multiline statements (like changelog) must be indented after the first line. Paths are set relatively, e.g. `gui/img/icon.png` if it lives in `quickapi/gui/img`.

Fill out all details accordingly. Find a suitable icon for your plugin and replace `icon.png` (but keep the name for simplicity).

### Zip plugin

For the QGIS plugin repository to accept your plugin, you must zip the whole `quickapi` folder. We recommend to create a `dist` folder top-level:

```bash
mkdir dist/
zip -r dist/quickapi_v0.1.zip quickapi
```

### Upload plugin

The uploading details and more general guidelines can be followed from [the official homepage](https://plugins.qgis.org).

## Bonus

### `resources.qrc`

This is a bit of a strange beast. It's the resource file your plugin depends on to find the icon. It's the recommended way to add static files to plugins. **But note**, it's not inherently necessary.

You will have noted the weird syntax in `quick_api.py`: `icon_path = ':/plugins/quick_api/icon.png'`. The colon tells QGIS Qt framework to look into its `resources` store to find this PNG file. For this to work, `resources.py` has to be imported to the module which holds the `initGui()` function, i.e. `quick_api.py` in your case. The actual icon path is made up of `prefix` and the relative file path of the PNG file, both of which you can see in `resources.qrc`. The prefix is needed, because the Qt resource store works on a application level and this identifies your part of the resource store. If your file is located in `./gui/img`, the icon path would change to `':/plugins/quick_api/gui/img/icon.png'` and in `resources.qrc` you'd have to change the `file` descriptor to `img/gui/icon.png`. Alternatively, you can access and alter the resource file from Qt Designer (*View* ► *Resource Browser*).

Anytime you alter the `resources.qrc` file (either manually or in Qt Designer), you need to re-compile `resources.py`: `pyrcc5 -o resources.py resources.qrc`.

If you don't want this burden, you can also manually locate in classic Python fashion, i.e. `icon_path = os.path.join(self.plugin_dir, 'icon.png')`.
