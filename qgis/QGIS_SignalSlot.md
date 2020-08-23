### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer Explained](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained/)
- [QGIS 3 Plugins - Plugin Development Part 1](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-1/)
- [QGIS 3 Plugins - Plugin Development Part 2](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-2/)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)

# QGIS 3 Plugins - Signals and Slots in PyQt

This is a brief explanation of the concept of `signal` and `slot` in PyQt5, which is the GUI framework for QGIS plugins.

In summary, this very much resembles events and callbacks in JavaScript. It's an asynchronous mechanism to let one part of a program know when another part of a program was updated, which is a most crucial concept in GUI programming. You master `signal`/`slot`, you master a whole lot about plugin development in QGIS.

## General concept

Generally a `signal` is a trigger which can be emitted (hence the term *signal*) and carry an arbitrary amount of information when it is emitted.

The `signal` can be connected to a `slot`, which needs to be Python callable (in other words, a method or a class, anything implementing the `__call__` magic), which can be any arbitrary function. The `slot` can accept the information which is emitted by the signal to process it further.

This is useful when one object needs to know about the actions of another object. For instance, if your plugin features a button that should paste the clipboard contents into a text field, then your plugin would need to know which function to call once the button is clicked. This is typically done via `signal` and `slot`.

## Signal

A `signal` **has to be a class attribute of a descendant of `QObject`**. **Any** QGIS widget and almost all GUI classes are descendants of `QObject` (i.e. have `QObject` as the very basic parent class) and they all come with predefined signals, such as [`QgsFilterLineEdit`](https://qgis.org/api/classQgsFilterLineEdit.html)'s `valueChanged` signal, which is triggered when a user changes the text of the widget.

### Definition

A `signal` has the general definition of `PyQt5.QtCore.pyqtSignal(types)`, where `types` will be the data type(s) a `signal` can emit:

- any basic Python data type (`int`, `str`, `list` etc.) or C++ type. In the latter case it needs to be defined as a string, e.g. `pyqtSignal(int)` or `pyqtSignal('QgsPointXY')`
- multiple Python or C++ types, which will emit several values, e.g. `pyqtSignal(int, str)` will take two arguments
- multiple sequences, which will create multiple versions of the signal, i.e. signal overloads, e.g. `pyqtSignal([int], ['QgsPointXY'])`

The first two options are fairly easy to grasp. However, the latter is a little more mysterious. Basically, overloaded signatures are a way to define the same object or class in multiple ways (you might call it Schrödinger's `signal`). The concept of overloaded class definitions is not really a thing in Python, though it can be done. If you define a signal with overloaded signatures, it's like you're creating the same object multiple times with different arguments, e.g. the example above would translate to:

```python
x = pyqtSignal([int], ['QgsPointXY'])

# can be read as:
x = pyqtSignal(int) AND pyqtSignal('QgsPointXY')
```

This method to define a `signal` is a little more elaborate as we'll [see soon](#overloaded-signal-example), but very handy.

### Methods

#### `connect()`

This method connects the signal to a slot. I.e. the signal can connect to a function, which takes its arguments and does something with them. For all practical purposes, you'll only need to pass the slot function to `connect()`. Each `signal` can connect to an arbitrary amount of slot functions.

### `disconnect()`

Often you want to disconnect a slot from its signal to control whether the slot function should still be executed when the signal is triggered. You can either pass the specific slot function or nothing, in which case all slots for the signal will be disconnected.

### `emit()`

When called, it emits values of the data types you specified when defining the `signal` (if any). These values have to be in the same order as in the definition, i.e. if `pyqtSignal(int, str)` was the definition, the `signal` needs to e.g. `emit(4, 'blabla')`, not `emit('blabla', 4)`.

## Examples

Let's see how this would work with more practical examples. To more relate to QGIS plugins, I'll use a similar (harshly abstracted) barebone structure as in our [Interactive QGIS Plugin tutorial](https://gis-ops.com/qgis-3-plugins-use-interactive-mapping/#4-pyqgis-set-up-map-tool-and-signal) to depict the general usage when e.g. defining a new Map Tool ([`QgsMapTool`](https://qgis.org/api/classQgsMapTool.html)).

### Simple Example

This is only non-working pseudo-code, which will just demonstrate the general usage. A map tool is created which implements a `canvasReleaseEvent` event emitting a custom `signal` when triggered. This `signal` connects to a custom `slot` function in the main plugin code.

```python
# First a generic Map Tool
class NewMapTool(QgsMapToolEmitPoint):

    # Define the custom signal this map tool will have
    # Always needs to be implemented as a class attributes like this
    canvasClicked = pyqtSignal('QgsPointXY')

    def __init__(self, canvas):
        super(self, QgsMapTool).__init__(self, canvas)
        #... and so on

    # This is the event triggered when the mouse button is released over the map canvas
    # Then the captured point will be emitted by the custom signal
    def canvasReleaseEvent(self, event):
        point_canvas_crs = event.mapPoint()

        self.canvasClicked.emit(point_canvas_crs)

# This is the main plugin code initiating the GUI etc
class QuickApi:
    def __init__(self, iface):
      self.iface = iface
      #... and so on

    ...

    # when this method is called by the plugin it loads our NewMapTool
    # and connect its canvasClicked signal to our custom slot function
    def connect_tool(self):
        self.point_tool = NewMapTool(self.iface.mapCanvas())
        self.point_tool.canvasClicked.connect(self.print_wkt)

    # our custom slot function needs to accept the QgsPointXY the signal emits
    def print_wkt(point):
        print(point.asWkt())
```

So, this hypothetical plugin would capture the point clicked by a user upon releasing the mouse button and print the WKT (Well Known Text) representation of that point to the Python console. Not very useful, I know, but I hope it gets the point across.

### Overloaded signal example

Let's get a little fancier and say we want to print the distance of that point to our location when we **click** the mouse, but the WKT representation when we **release** the mouse button.

We can achieve this with the exact same `signal` if we define it with an overloaded signature. Yep, finally seeing how a Schrödinger's signal can work:

```python
# First a generic Map Tool
class NewMapTool(QgsMapToolEmitPoint):

    # Define the custom signal this map tool will have
    # Always needs to be implemented as a class attributes like this
    canvasClicked = pyqtSignal([int], ['QgsPointXY'])

    def __init__(self, canvas):
        super(self, QgsMapTool).__init__(self, canvas)
        #... and so on

    # This is the event triggered when the mouse button is released over the map canvas
    # Then the captured point will be emitted by the custom signal
    def canvasReleaseEvent(self, event):
        point_canvas_crs = event.mapPoint()

        # you need to specifically emit the right signal signature
        self.canvasClicked['QgsPointXY'].emit(point_canvas_crs)

    # This event is triggered when the mouse button is pressed over the map canvas
    # Then the distance to an arbitrary point is calculated and returned
    def canvasPressEvent(self, event):
        point_canvas_crs = event.mapPoint()

        # you need to specifically emit the right signal signature
        self.canvasClicked[int].emit(int(point_canvas_crs.distance(13.413513, 52.491019)))        

# This is the main plugin code initiating the GUI etc
class QuickApi:
    def __init__(self, iface):
      self.iface = iface
      #... and so on

    ...

    # when this method is called by the plugin it loads our NewMapTool
    # and connect its canvasClicked signal to our custom slot function
    def connect_tool(self):
        self.point_tool = NewMapTool(self.iface.mapCanvas())

        # Again: you need to connect to the specific signal signatures
        # for the different desired outcomes
        self.point_tool.canvasClicked['QgsPointXY'].connect(self.print_wkt)
        self.point_tool.canvasClicked[int].connect(self.print_distance)

    # the one custom slot function needs to accept the QgsPointXY the signal emits
    def print_wkt(point):
        print(point.asWkt())

    # the other custom slot function needs to accept the integer distance the signal emits
    def print_distance(distance):
        print(distance)
```

We now defined another `canvasPressEvent`, which will be triggered if the user presses the map canvas while the `NewMapTool` is active.

Since we defined our `canvasClicked` event now with the overloaded signature `pyqtSignal([int], ['QgsPointXY'])`, we need to watch out that we only call the right signature for `connect()` and `emit()`. If we would omit the specific signature when calling these functions, they would use the first signature they find, which would be `int` in this case.

We connected both signatures to separate functions. Now, when the user clicks in the map canvas, the distance of the point to *13.413513, 52.491019* will be printed (\*), when he releases the mouse button, the point's WKT representation will be printed.

**Be aware** however, that overloaded signatures have a catch: the **Python** data types in the `pyqtSignal` definition are converted to C++ types and some combinations can lead to undesired outcomes. E.g. `pyqtSignal([list], [dict])` will be converted to the **same C++ data type**. Calling `emit()` or `connect()` on the `dict` signature will be interpreted as calling the method on the `list` signature instead.

(\*) Note, that those coordinates are in X, Y WGS84. The point captured by the `canvasPressEvent` depends on the map canvas CRS which is likely different, so you'd need to transform. Even if it were WGS84, the distance would be in degrees.
