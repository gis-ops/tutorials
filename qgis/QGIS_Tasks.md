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
