from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import QApplication

from qgis.gui import QgsMapToolEmitPoint, QgsMapMouseEvent
from qgis.core import QgsCoordinateTransform

from ..core.utils import maybe_transform_wgs84

CURSOR_ICON = QIcon(":images/themes/default/cursors/mCapturePoint.svg")
CUSTOM_CURSOR = QCursor(CURSOR_ICON.pixmap(48, 48))


class PointTool(QgsMapToolEmitPoint):

    canvasClicked = pyqtSignal("QgsPointXY")

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        # Get the click and emit a transformed point
        crs_canvas = self.canvas().mapSettings().destinationCrs()
        self.canvasClicked.emit(
            maybe_transform_wgs84(
                event.mapPoint(),
                crs_canvas,
                QgsCoordinateTransform.ForwardTransform,
            )
        )

    def activate(self):
        super().activate()
        QApplication.setOverrideCursor(CUSTOM_CURSOR)
