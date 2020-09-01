### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer Explained](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained/)
- [QGIS 3 Plugins - Plugin Development Part 1](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-1/)
- [QGIS 3 Plugins - Plugin Development Part 2](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-2/)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)

---

# QGIS 3 Plugins - Plugin 101

This blog is a reference guide to QGIS 3 plugin lingo and explains important concepts. It's mostly based on output of [Plugin Builder 3](https://plugins.qgis.org/plugins/pluginbuilder/), which is very useful for generating the necessary boiler plate code. However, it's hard to decipher all the hidden meanings of the code it supplies.

If you miss documentation of some methods or concepts, please open an [issue on GitHub](https://github.com/gis-ops/tutorials/issues) or create a [pull request](https://github.com/gis-ops/tutorials/pulls) with your enhancement.

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **QGIS v3.4**
> Occassionally, the author might choose to give hints on Windows-specific setups. `Ctrl+F` for WINDOWS flags. Mac OS users should find the instructions reasonably familiar.

**Basic vocabulary**
-   `IDE` means `integrated developer environment`
-   `UI` means `user interface`
-   `GUI` means `graphical user interface`

## Development environment

QGIS generally ships with the official [Python distribution](https://www.python.org/downloads/release/python-360/), which is fairly slim with regards to included packages. Additionally, it ships multiple convenience packages, like **`requests`**, **`matplotlib`**, **`SciPy`** and **`NumPy`**. Feel free to extend this list in a PR, since there doesn't seem to be extensive documentation.

Under Linux (and presumably Mac OS), QGIS 3 utilizes the **system Python3** executable and installs all needed libraries in its `PYTHONPATH`. Usually, it's not practical to use virtual environments for QGIS plugins. **WINDOWS** users are not so lucky: they will have to use the OSGeo4W Python executable or modify their `PYTHONPATH` to reflect QGIS native Python libraries.

So, for Linux/Mac users it's straight forward to use an IDE, like [Sypder](https://www.spyder-ide.org) or [PyCharm](https://www.jetbrains.com/pycharm/) and enjoy the benefit of code completion and inline documentation.

## Plugin system paths

QGIS will look for external plugins in these paths :

- Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`

- Windows: `C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`

- Mac OS: `Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`

## Deploy plugin to QGIS

Since you usually won't work in the native QGIS plugin path, there's a few extra steps to deploy the plugin so that QGIS recognizes it and you see changes you make along the development.

It's enough to create a symbolic link from your dev environment to the QGIS Python Plugin directory:

```bash
pyrcc5 -o resources.py resources.qrc

ln -s myplugin/ ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
```

Then, use the [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin to reload your modified code on-the-fly from within QGIS, without restarting QGIS. **Note**, that this only works if you didn't modify any methods which are **only** loaded on QGIS startup, like the root's `__init__.py` or the `initGui()` method.

## `metadata.txt`

This is the main source for the plugin repository, but also the QGIS Plugin Manager, which both extract information about author, version etc from here. Generally, you can use this file to store all kinds of meta information, like a help URL or collaborators. It's a standard INI structured file with sections and `key=value` pairs. Hence, it can be parsed with Python's native `configparser` library. It makes sense to keep `metadata.txt` as the only entry point for meta information and, when needed in the code base, import the configuration from it (like `version`).

Multiline statements (like in changelogs) must be indented after the first line. Paths are set relatively, e.g. `gui/img/icon.png` if it lives in `<plugin_root>/gui/img`.

## Detailed module and method description

QGIS Python plugins need a few mandatory modules and methods so they work smoothly with QGIS.

Consider the name of your plugin 'MyPlugin', whose boiler plate code was generated with [Plugin Builder 3](https://plugins.qgis.org/plugins/pluginbuilder/).

The minimum tree for a functioning output of Plugin Builder 3 would look like:

```
├──myplugin
   ├──icon.png
   ├──__init__.py
   ├──metadata.txt
   ├──my_plugin.py
   ├──my_plugin_dialog.py
   ├──my_plugin_dialog_base.ui
   └──resources.qrc
```

- `icon.png`: the default icon for the plugin. Change this file to reflect your own icon.

- `__init__.py`: contains the function which will initialize the plugin on QGIS startup and register it with QGIS, so it knows about this plugin.

- `metadata.txt`: contains information about the plugin, which will be used by the official QGIS plugin repository and the QGIS Plugin Manager to display information about your plugin, e.g. description, version, author, URL etc. See [metadata section](#metadatatxt)

- `my_plugin.py`: contains the heart of the plugin: custom functionality will go into this file.

- `my_plugin_dialog.py`: loads the plugin User Interface (UI), when QGIS starts up

- `my_plugin_dialog_base.ui`: this is the Qt Designer file to style and build the UI, i.e. plugin window.

- `resource.qrc`: contains the resources for Qt. You will only edit this file when you rename the plugin icon or you want to add additional icons. **Needs to be compiled to resources.py**.

Find a more detailed description below.

### `resources.qrc`

That's a Qt resource file. Basically, it contains instructions for the Qt framework where to find which resources, e.g. plugin icons. Find a more detailed discussion [here](https://github.com/gis-ops/tutorials/blob/master/qgis/QGIS_QtDesigner.md#qt-resourcesqrc). It needs to be compiled to `resources.py` and imported in `my_plugin.py`.

### `__init__.py`

It's responsible to make QGIS aware of the plugin's existence. Which is what the `classFactory()` class does by instantiating your plugin's main class from `my_plugin.py`. More on that further down.

**Don't alter the classFactory() class!** It's implicitly expected by QGIS. Which you'll find is a common thing in QGIS' Python API.

### `my_plugin_dialog.py`

This file only contains a single class: `MyPluginDialog`, which sub-classes `QDialog` and `FORM_CLASS`, hence inherits all methods of both classes.

- `QDialog`: a `QWidget` which will represent your plugin window (**not** the UI elements themselves).

- `FORM_CLASS`: loads your UI file into a class.

The `MyPluginDialog` class will be instantiated in the main `my_plugin.py` module. The main line to note here is:

```python
self.setupUi(self)
```

`setupUi()` is a method of `FORM_CLASS`, which will set up your UI elements in your `QDialog` plugin window. What is highly confusing here: the caller's `self` refers to `FORM_CLASS`, the argument `self` refers to `QDialog` (as `setupUi()` takes a `QWidget` as argument). That's entirely valid, since `QuickApiDialg` sub-classes both classes, but it sure is confusing to any newcomers.

### `my_plugin.py`

This is a bigger beast and you'll spend most time here. It looks scary at first, but trust us, there's a lot of unnecessary boiler plate code here (at least for your current purposes). Instead of stripping it down to the most essential parts, we'll explain all methods. But you will only work with the most important ones. \[**required**\] methods are implicitly expected and called by the main QGIS application, so don't alter their name or input parameters!

It only contains a single class `MyPlugin`. This class will be instantiated by the plugin's `__init__.py`'s `classFactory` class, which in turn is called by QGIS on startup to make your plugin known to QGIS. So, really, this is the heart of the plugin.

#### `def __init__(self, iface)` \[**required**\]

The `MyPlugin` class is passed the `iface` parameter, which is a `QgisInterface` and lets you interact with the QGIS GUI.

We'll go through the lines in order:

- `self.iface`: saves a reference to the QGIS GUI interface (`qgis.gui.QgisInterface`)

- `locale`: all code lines concerning locales, you can (more or less) safely ignore for now. They mostly deal with 
s and internationalization.

- `self.actions`: a container for `QAction`s, which we'll explain a little later.

- `self.menu`: the name which will appear in the menu bar for this plugin.

#### `def tr(self, message)`

If your plugin makes use of translations, this method will handle it. You can read more about it [here](https://docs.qgis.org/3.10/en/docs/pyqgis_developer_cookbook/plugins/plugins.html#translation).

#### `def add_action(self, ...)`

It's creating a `QAction` object, which can be used to instruct QGIS to add icons to a menu, toolbar etc. What it only does, is:

- add icon to Plugin Toolbar
- add entry to QGIS 'Vector' menu list
- set help texts if specified (`setStatusTip`, `setWhatsThis`)
- add a callback to the action, which is executed when either the icon or the menu item are clicked (`action.triggered.connect(callback)`)

#### `def initGui(self)` \[**required**\]

This method is called by QGIS when the main GUI starts up or when the plugin is enabled in the Plugin Manager.

Usually, you only want to register the menu items and toolbar buttons here. Which is what the default `self.add_action()` does. You can add additional parameters to the call like `whats_this` or `status_tip`, which give some help to the plugin user.

**Note the `callback` paramter** is set to `self.run`. Meaning, the `self.run()` will be executed once the user clicks on the plugin menu item or on the toolbar icon. So, you can already guess, that that's the most important function in this class.

Also note the icon path: `':/plugins/my_plugin/icon.png'`. The colon instructs QGIS to use the compiled `resources.py` file to locate the icon. Open the original `resources.qrc` file and you'll see the connection. A more detailed discussion of the resource file is given [here]().

Also, we state here that the plugin is started for the first time during the lifetime of a running QGIS session.

#### `def unload(self)` \[**required**\]

Will be executed when the plugin is disabled. Either in the Plugin Manager or when QGIS shuts down.

It only removes the previously defined `QAction` object from the menu and remove the plugin icon from the toolbar.

#### `def run(self)`

This code block executes the custom plugin functionality. This method is called by the previously defined `QAction` object, which went into the toolbar icon and the menu entry.

Really, this function could be called anything you'd like. There's no hidden meaning to it, as there is for `unload(self)` or `initGui(self)`. You could even have multiple callbacks like `run(self)` connected to a `QAction`.

First thing it does here: check if this is the first time the plugin is called. Remember, this function is called every time the user clicks on the plugin toolbar button/menu entry. Only if it's the first start, it'll build the GUI by instantiating the `QuickApiDialog` class (which calls its `setupUi()` in its `__init__()`) and assigning it to `dlg`. If the GUI would be freshly built every time the user calls the plugin, all previous GUI settings would be lost. `dlg` now holds all plugin GUI objects, which can be accessed by the names you gave them in Qt Designer.

`dlg.show()` shows the GUI modeless, i.e. the user can interact with QGIS main window while the plugin GUI is open.

`dlg.exec_()` shows the GUI modal, i.e. the user can't interact with QGIS main window while the plugin is open. When the user presses a button to close the plugin, this function will return a code, which is `1` if the user pressed _OK_ and `0` if the user pressed _Cancel_. Usually one would either use `show()` **or** `exec_()`.

*BTW*: `exec_()` is equivalent to `exec()` and was introduced by `PyQt`, since `exec` was a reserved keyword until Python 3.

So, if `result` is `1`, meaning the user clicked OK, we want the plugin to execute its costum code. This is finally where the boiler plate ends and the action starts.

## Documentation Stores

### PyQt5

PyQt5 (and its C++ parent Qt) is the GUI framework QGIS relies on. Most UI related objects, methods and properties can be found in this library. Mostly, you'll deal with `PyQt5.QWidgets` and `PyQt5.QtGui`.

Unfortunately, the direct code documentation of PyQt5 provided by Riverside is non-existing. However, there are a few ways to help yourself here:

- you're using an IDE? Great! If you're lucky, `Ctrl+Q` in PyCharm (`Ctrl+I` in Spyder) will show input and output parameters of the selected function.

- the main documentation is [here](http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets). However, it usually only refers you to the C++ documentation of the Qt library, which PyQt5 wraps for Python. That documentation can be slightly overwhelming. You'll get through it though, just consider these few guidelines (taking `QLineEdit` as reference):
	- in [Functions](https://doc.qt.io/qt-5/qlineedit.html#public-functions) description, the first column tells you which object type is returned. `void` does not return anything. `QString` is implemented as a simple Python `str`. The first few rows let you know how to construct an instance of the widget.
	- the Properties are implemented as methods, not attributes, i.e. in [`QLineEdit`](https://doc.qt.io/qt-5/qlineedit.html#properties), `text` is implemented in `PyQt5` as `<some QLineEdit widget>.text()`, which will give you the current text of the widget
	- we will deal with Signals and Slots later

- to lookup properties of a specific widget, use Qt Creator's [Properties](#3-property-editor) panel

### PyQGIS

PyQGIS is the standard synonym for the `qgis` Python library (which will help you a lot when googling solutions). For Linux users (with IDE's), documentation is fairly straight forward, as they benefit from auto-completion and inline documentation. **WINDOWS** users who did not manually change their Python executable to QGIS' one (or include the appropriate directories in their PYTHONPATH), won't be as lucky.

- main documentation is here: [https://www.qgis.org/pyqgis/master/](https://www.qgis.org/pyqgis/master/). From QGIS v3.x on, the documentation improved A LOT! If you ever wonder how to access certain QGIS related properties or methods, either use the search box. Or drill down manually. Basically, the (commonly) 2 most important modules in PyQGIS are `gui` and `core`. The classes are ordered by broader GIS topics (Attributes, Fields and so on) and class names are very descriptive, so you should find your way easily. **Note**, that some class names are prefixed by `Qgs`, some are prefixed by `Qgis` (no, that's not confusing at all...). Occassionally, you'll find that the [C++ documentation](https://qgis.org/api/) is more descriptive than the Python one.

- the main online platform for questions is [Stack Exchange](https://gis.stackexchange.com). All the great QGIS goddesses and gods frequently visit and can help you out of your misery. Apply common sense before asking questions though, i.e. research for at least 20 mins. It really boosts your understanding if you solve problems on your own. Also, your question might have been asked before.

- For more general questions which could be interesting for the whole community, subscribe to the QGIS developer [mailing list](https://lists.osgeo.org/mailman/listinfo/qgis-developer)
