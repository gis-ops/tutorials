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

# QGIS Tasks – background processing

In this tutorial you'll buid a plugin which downloads and displays [Mapzen Terrain Tiles](https://registry.opendata.aws/terrain-tiles/), within the extents of a user-defined polygon layer. This download task can be enormous: the planet-wide dataset weighs \~ 1.5 TB. If the main plugin code simply calls a download function, QGIS would freeze for multiple minutes. This is where the QGIS background tasks (`QgsTask`) come in very handy. You can start a `QgsTask` which will run in another thread, keeping the main thread with QGIS reactive for the user.

The final plugin code can be found [here](https://github.com/gis-ops/tutorials/qgis/examples/elevation_tile_downloader). We assume that you are familiar with PyQGIS and the basics of plugin development in QGIS. In case you want to catch up on the latter, please refer to our [QGIS plugin development guide](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/).

**Goals:** 
- become familiar with the concept of background tasks in PyQGIS
- communicating a background task's progress to the user

> **Disclaimer**
>
> Validity only confirmed for **Linux**, **Mac OS** and **QGIS v3.20.2**

## Prerequisites

### Hard prerequisites

- Good understanding of Python
- Basic understanding of QGIS plugin development
- QGIS v3.x
- [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin installed
- Python >= 3.6 (should be your system Python3)

### Recommendations

- Good Python knowledge
- Familiarity with
	- Qt Designer application, see [our tutorial](https://gis-ops.com/qgis-3-qt-designer-explained/)
	- Python Plugin Basics, see [our tutorial](https://gis-ops.com/qgis-3-plugin-development-reference-guide/)

## 1 Build UI

First we need to build the UI with Qt Designer. We won't cover any of the basics here, refer to our [Qt Designer tutorial](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/) if you need a refresher. 

The final plugin will look something like this:

<closeup of Qt Designer window>

To make sure we're on the same page along the code examples:
- the layer widget is a `QgsMapLayerComboBox`, which we named `layer_choice` and will be the polygon layer selector
- the folder picker is a `QgsFileWidget`, which we named `output_dir` and will be the user-defined output directory for the downloaded terrain tiles

You can go ahead, create the UI file in Qt Designer, convert it to a Python file with `pyuic5` and do the usual boilerplate code to get the plugin loadable by QGIS. You can always double-check with [our solution](https://github.com/gis-ops/tutorials/qgis/examples/elevation_tile_downloader) when in doubt. Our minimal layout looks like this, with `plugin.py` holding our plugin's main class and `gui` and `core` being packages we'll add further files to further down:

```
├── core
├── gui
│   ├── __init__.py
│	├── tile_downloader_dlg_base.py
│	└── tile_downloader_dlg_base.ui
├── __init__.py
├── __pycache__
├── icon.png
├── __init__.py
├── metadata.txt
├── plugin.py
├── README.html
└── README.txt


```

Our `plugin.py` is pretty standard:

```python
from pathlib import Path
from typing import Optional

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.gui import QgisInterface

from .gui.tile_downloader_dlg import ElevationTileDownloaderDialog


class ElevationTileDownloader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        """Constructor."""
        self.iface = iface

        self.dlg: Optional[ElevationTileDownloaderDialog] = None
        self.action: Optional[QAction] = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon = QIcon(str(Path(__file__).parent.joinpath("icon.png")))
        self.action = QAction(
            icon, "Download elevation tiles", self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        # add action to the raster menu and the default plugin toolbar
        self.iface.addPluginToRasterMenu(
            "Elevation Tile Downloader", self.action
        )
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginRasterMenu(
            self.action.objectName(), self.action
        )
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Run method that performs all the real work"""

        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if not self.dlg:
            self.dlg = ElevationTileDownloaderDialog(self.iface)

        # show the dialog
        self.dlg.open

```

## 2 Collect the input

### 2.1 Make the UI usable

Before we start off with the more interesting part of designing the background task, we first have to know which elevation tiles we actually need to download. So we'll have to add some logic to the UI we just built.

Create a file `gui/tile_elevation_dlg.py` to hold that logic. As always we need a class which subclasses what we import from the output of `pyuic5`. Don't be suprised by all the imports, we'll need them along the way:

```python
from pathlib import Path
from math import floor, ceil
from typing import List, Optional, Set

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialogButtonBox, QProgressBar, QDialog
from qgis.gui import QgisInterface, QgsMessageBarItem
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsGeometry,
    QgsMapLayerProxyModel,
    QgsApplication,
    QgsRectangle,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    Qgis,
    QgsTask,
)

from ..gui.tile_downloader_dlg_base import Ui_ElevationTileDownloaderDialogBase

class ElevationTileDownloaderDialog(QDialog, Ui_ElevationTileDownloaderDialogBase):
    def __init__(self, iface: QgisInterface, parent=None):
        """Constructor."""
        super(ElevationTileDownloaderDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        # we only allow polygon layers
        self.layer_choice.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.accepted.connect(self.download_tiles)

        # change the text of the "Ok" button
        self.button_box.button(QDialogButtonBox.Ok).setText("Download")

```

This should be quite self-explanatory: when the user hits the "Download" button it will invoke the `download_tiles()` function, which we still need to define.

### 2.2 Collecting tiles to download

Before we start out, we have to know how those terrain tiles can be actually accessed. They're hosted on AWS Open Data infrastructure (the only thing you should use AWS for!), an example URL is http://s3.amazonaws.com/elevation-tiles-prod/skadi/N49/N49W097.hgt.gz. The tiles' size is 1° x 1° in WGS84. The base URL is http://s3.amazonaws.com/elevation-tiles-prod/skadi, then a folder collects all 360 longitudinal tiles for that latitude (here `N49`), while the file name denotes the lat/lon of the lower-left corner of the tile. 

We'll want to collect all tiles which are covered by input polygon features, so let's see what that'd look like:

```python
def to_wgs84(geometry: QgsGeometry, own_crs: QgsCoordinateReferenceSystem) -> QgsGeometry:
    """
    Transforms the ``point`` to (``direction=ForwardTransform``) or from
    (``direction=ReverseTransform``) WGS84.
    """
    wgs84 = QgsCoordinateReferenceSystem.fromEpsgId(4326)
    if own_crs != wgs84:
        xform = QgsCoordinateTransform(own_crs, wgs84, QgsProject.instance())
        geometry.transform(xform)

    return geometry


def create_grid_from_bounds(bounds: QgsRectangle) -> List[QgsGeometry]:
    """Creates a regular grid of size 1x1 within specified bounds"""
    grid_bboxes = []

    # loop through x and y range and create the grid
    min_x, min_y = [floor(x) for x in (bounds.xMinimum(), bounds.yMinimum())]
    max_x, max_y = [ceil(x) for x in (bounds.xMinimum() + bounds.width(), bounds.yMinimum() + bounds.height())]
    for x in range(min_x, max_x):
        for y in range(min_y, max_y):
            grid_bboxes.append(QgsGeometry.fromRect(QgsRectangle(x, y, x + 1, y + 1)))

    return grid_bboxes


class ElevationTileDownloaderDialog(QDialog, Ui_ElevationTileDownloaderDialogBase):
	...
    def download_tiles(self) -> None:
        """
        The plugin's main method; constructs the grid from selected input features,
        creates and starts the download task and connects the plugin to task signals.
        """
        poly_layer: QgsVectorLayer = self.layer_choice.currentLayer()
        out_dir = Path(self.output_dir.filePath())

        # Collect the tile bounding boxes covering the input polygons
        grid: Set[QgsGeometry] = set()
        for feature in poly_layer.getFeatures():
            # transform the feature's bounding box and create a 1 x 1 degree tile grid from it
            feature_geom = to_wgs84(feature.geometry(), poly_layer.crs())
            grid_bboxes = create_grid_from_bounds(feature_geom.boundingBox())
            for grid_bbox in grid_bboxes:
                if feature_geom.intersects(grid_bbox):
                    grid.add(grid_bbox)

        self.total = len(grid)
        if not self.total:
            self.iface.messageBar().pushMessage(
                "No tiles",
                f"Layer {poly_layer.name()} does not intersect any tiles",
            )
            return

```

For all user-defined polygon features, we transform them to WGS84 and collect a `set` (to avoid duplicates) of all tiles whose bounding box intersect with the polygons' bounding boxes. If we couldn't find any intersecting tiles we notify the user and abort.

### 2.3 User feedback

Since the download could be potentially huge, we'd like to inform the user about the progress. The best communication way is via fairly unobtrusive messages in the pop-up message bar on top of the map canvas. That message bar does not only accept text to display but even other widgets, such as a progress bar:

```python

class ElevationTileDownloaderDialog(QDialog, Ui_ElevationTileDownloaderDialogBase):
	...
    def download_tiles(self) -> None:
    	...
        # Create a progress bar in the QGIS message bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        progress_msg: QgsMessageBarItem = (
            self.iface.messageBar().createMessage("Download Progress: ")
        )
        progress_msg.layout().addWidget(self.progress_bar)
        self.iface.messageBar().pushWidget(progress_msg, Qgis.Info)

```

Before we show you how we'll update the progress bar, we'll first create our `QgsTask`.

## 3 The `QgsTask`

Generally, there are three ways in which tasks can be created:

- creating it directly from a function,
- from a processing algorithm,
- or by extending `QgsTask`

Our task is a little bigger and we like things to be encapsulated, so we chose to extend `QgsTask`. There is a bunch of functions you will need to override/implement when subclassing `QgsTask`:
- `run()`: this is where the real work will happen in a separate thread, similar to a `QgsProcessingAlgorithm::processAlgorithm`. This method must not call any UI related functions or interact with the main QGIS interface at all or crashes will occur
- `finished()`: will be called after the `run()` method is finished. It's safe to call UI functions here e.g. to inform the user about success or errors.

### 3.1 Extending `QgsTask`
We start by creating a new Python module `task.py` inside a new package called `core`. Here, we subclass `QgsTask`:
```python
from typing import List, Optional, Set
from pathlib import Path
import gzip
from io import BytesIO

from qgis.gui import QgisInterface
from qgis.core import (
    QgsTask,
    QgsMessageLog,
    Qgis,
    QgsRasterLayer,
    QgsProject,
    QgsNetworkAccessManager,
    QgsNetworkReplyContent,
    QgsGeometry,
)
from qgis.utils import iface
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtNetwork import QNetworkRequest

iface: QgisInterface


class DownloadTask(QgsTask):
    def __init__(self, grid: Set[QgsGeometry], output_dir: Path):
        super().__init__("Tile download task", QgsTask.CanCancel)
        self.grid = grid
        self.output_dir = output_dir

        self.exception: Optional[Exception] = None
        self.tiles: List[Path] = []
```

The `__init__` is simple: we initialize the parent and assign the grid and the output directory as instance attributes. Note the exception attribute here: since it's not safe to raise exceptions in a background task (this will crash QGIS), we initialize an empty `exception` instance attribute here, where we will store any exception that we catch in `run()`. 
	
Now we can get to the actual task logic, implemented inside `run()`:
```python
class DownloadTask(QgsTask):
    ...
    def run(self):
        """Do the work."""
        nam = QgsNetworkAccessManager()

        # Don't raise any error during processing, relay error reporting to self.finished()
        try:
            for i, bbox in enumerate(self.grid):
                if self.isCanceled():
                    return False

                # Get the filepath and create the output directory (if necessary)
                x, y = (
                    bbox.boundingBox().xMinimum(),
                    bbox.boundingBox().yMinimum(),
                )
                hemisphere = "S" if y < 0 else "N"
                dir_name = "%s%02d" % (hemisphere, abs(y))
                directory = self.output_dir.joinpath(dir_name)
                directory.mkdir(exist_ok=True)
                tile_name = "%s%02d%s%03d.hgt" % (
                    hemisphere,
                    abs(y),
                    "W" if x < 0 else "E",
                    abs(x),
                )
                filepath = self.output_dir.joinpath(dir_name, tile_name)
                self.tiles.append(filepath)
                if filepath.is_file():
                    QgsMessageLog.logMessage(
                        message=f"Already downloaded tile {tile_name}",
                        level=Qgis.Info,
                    )
                    continue

                # get the new tile if it didn't exist
                url = QUrl(
                    f"http://s3.amazonaws.com/elevation-tiles-prod/skadi/{dir_name}/{tile_name}.gz"
                )
                request = QNetworkRequest(url)
                reply: QgsNetworkReplyContent = nam.blockingGet(request)
                # turn the reply into a file object and write the decompressed file to disk
                with gzip.GzipFile(
                    fileobj=BytesIO(reply.content()), mode="rb"
                ) as gz:
                    with open(filepath, "wb") as f:
                        f.write(gz.read())

                self.setProgress((i / len(self.grid)) * 100)

            return True
        except Exception as e:
            self.exception = e
            return False
```
The `run()` method of a `QgsTask` always needs to return a boolean value, which is used in `finished()` to evaluate whether the task ran successfully. After initializing the network access manager, which is used for handling the http requests, we wrap the remainder of the method inside a `try`/`except` block to prevent exceptions from being raised. If an exception is caught, we save it and return `False`. In order to give the user control over cancelling the download, we check for this after each iteration by calling `self.isCanceled()`, and return False if the user has canceled the task.

The logic of the actual heavy lifting inside `run()` works as follows: for every box in the grid, we get the southwesternmost coordinates, from wich the directory and tile names are created, as well as the URL to download the tile from. If the file does not exist yet, we download it, extract the `.gz`file and save the result into the respective directory.
	
Next up is the `finished()` method:
```python
class DownloadTask(QgsTask):
    ...
    def finished(self, result):
        """Postprocessing after the run() method."""
        if self.isCanceled():
            # if it was canceled by the user
            QgsMessageLog.logMessage(
                message=f"Canceled download task. {len(self.tiles)} tiles downloaded.",
                level=Qgis.Warning,
            )
            return
        elif not result:
            # if there was an error
            QMessageBox.critical(
                iface.mainWindow(),
                "Tile download error",
                f"The following error occurred:\n{self.exception.__class__.__name__}: {self.exception}",
            )
            return

        iface.messageBar().pushMessage(
            "Success",
            f"Finished downloading {len(self.tiles)} tiles.",
            level=Qgis.Success,
        )

        # add the rasters to the map canvas
        for tile_path in self.tiles:
            if not tile_path.exists():
                QgsMessageLog.logMessage(
                    message=f"Tile at {tile_path.resolve()} was removed.",
                    level=Qgis.Warning,
                )
                continue
            QgsProject.instance().addMapLayer(
                QgsRasterLayer(str(tile_path.resolve()), tile_path.stem)
            )

```
Here, we want to handle three different cases:
	1. The user canceled the task
	2. An exception occured
	3. The task completed successfully

In the first two cases, we only want to communicate the task outcome to the user. Remember that inside `finished()`, we can access objects from the main thread again, so we can simply push a message to the main interface's message bar. For the third case, we communicate the successful completion of the task to the user and additionally add the downloaded tiles to the map canvas.

### 3.2 Wrap up: user feedback and running the task

Lastly, we want to update the progress bar while the tiles are downloading. Remember that we can't directly access the widget we created earlier in `gui/tile_elevation_dlg.py`, but luckily, `QgsTask` comes with a set of signals we can use to communicate with the user while the background task is running. `progressChanged` is the most important one here: we can emit it by calling `self.setProgress(int)`, where `int` is an integer between 0 - 100, indicating the tasks progress in percent. We connect to the signal in `gui/tile_elevation_dlg.py` right after initializing the task, and to the `taskCompleted` signal to clear the message bar again after the task has run:

```python
def download_tiles(self) -> None:
    ...
    self.task = DownloadTask(grid, out_dir)
    self.task.progressChanged.connect(self.progress_bar.setValue)
    self.task.taskCompleted.connect(self.iface.messageBar().clearWidgets)
    QgsApplication.taskManager().addTask(self.task)
    self.close()
```

> Note that it's vital to assign the task not just to a variable, but to a class attribute. Otherwise, the task will be deleted after `download_tiles()` finishes, but before the task itself finishes.

Finally, the task needs to be run. For this, we use the `QgsTaskManager`, which is a singleton class that takes care of delegating any background tasks. We add the task and the task manager makes sure that the task starts running.

And that's it! We have successfully created a small plugin that downloads SRTM tiles in the background by using `QgsTask`, so that the user can continue interacting with QGIS while the download runs.
