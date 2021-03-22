from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import QApplication

from qgis.gui import QgsMapToolEmitPoint, QgsMapMouseEvent
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
)

from ..core.utils import maybe_transform_point_to_wgs

WGS = QgsCoordinateReferenceSystem("EPSG:4326")
CUSTOM_CURSOR = QCursor(
    QIcon(":images/themes/default/cursors/mCapturePoint.svg").pixmap(48, 48)
)


class PointTool(QgsMapToolEmitPoint):

    canvasClicked = pyqtSignal("QgsPointXY")

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        # Get the click and emit a transformed point
        crs_canvas = self.canvas().mapSettings().destinationCrs()
        self.canvasClicked.emit(
            maybe_transform_point_to_wgs(
                event.mapPoint(), crs_canvas, QgsProject.instance()
            )
        )

    def activate(self):
        super().activate()
        QApplication.setOverrideCursor(CUSTOM_CURSOR)
