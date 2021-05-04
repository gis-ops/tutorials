import unittest

from qgis.PyQt.QtTest import QTest
from qgis.PyQt.QtCore import Qt, QEvent, QPoint, QTimer
from qgis.PyQt.QtWidgets import (
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
    QApplication,
)
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsVectorLayer,
    QgsFeature,
    QgsFeatureIterator,
)

from .utilities import get_qgis_app

CANVAS: QgsMapCanvas
QGISAPP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFlow(unittest.TestCase):
    def tearDown(self) -> None:
        project = QgsProject.instance()
        project.removeAllMapLayers()

    def test_full_success(self):
        """Test the full workflow from opening the dialog to requesting geocoding"""

        # need to import here so that there's already an initialized QGIS app
        from quick_api.gui.quick_api_dialog import QuickApiDialog
        from quick_api.core.maptool import PointTool

        # first set up a project
        CRS = QgsCoordinateReferenceSystem.fromEpsgId(3857)
        project = QgsProject.instance()
        CANVAS.setExtent(QgsRectangle(1469703, 6870031, 1506178, 6907693))
        CANVAS.setDestinationCrs(CRS)

        # Create and open the dialog
        dlg = QuickApiDialog(IFACE)
        dlg.open()
        self.assertTrue(dlg.isVisible())

        # Click the map button which should hide the dialog
        map_button: QPushButton = dlg.map_button
        QTest.mouseClick(map_button, Qt.LeftButton)
        self.assertFalse(dlg.isVisible())
        self.assertIsInstance(CANVAS.mapTool(), PointTool)

        # Click in the map canvas, which should return the clicked coord,
        # make the dialog visible again
        map_releases = QgsMapMouseEvent(
            CANVAS,
            QEvent.MouseButtonRelease,
            QPoint(0, 0),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        dlg.point_tool.canvasReleaseEvent(map_releases)
        self.assertRegex(dlg.lineedit_xy.text(), r"^(\d+\.\d+.+\d+\.\d+)$")
        self.assertTrue(dlg.isVisible())

        # Clicking the OK button should load the Nominatim result layer
        QTest.mouseClick(
            dlg.button_box.button(QDialogButtonBox.Ok), Qt.LeftButton
        )
        layers = project.mapLayers(validOnly=True)
        self.assertEqual(len(layers), 1)

        result_layer: QgsVectorLayer = list(layers.values())[0]

        # Also should be only one feature
        result_features: QgsFeatureIterator = result_layer.getFeatures()
        feat: QgsFeature = next(result_features)
        self.assertRaises(StopIteration, next, result_features)

        # Test the attributes and geometry
        self.assertIn("Havelland,", feat["address"])
        self.assertIn("OpenStreetMap contributors", feat["license"])
        self.assertAlmostEqual(
            feat.geometry().asPoint().x(), 12.703847, delta=1.0
        )
        self.assertAlmostEqual(
            feat.geometry().asPoint().y(), 52.590965, delta=1.0
        )

    def test_full_failure(self):
        """Test failing request"""

        # need to import here so that there's already an initialized QGIS app
        from quick_api.gui.quick_api_dialog import QuickApiDialog
        from quick_api.core.maptool import PointTool

        # first set up a project
        CRS = QgsCoordinateReferenceSystem.fromEpsgId(3857)
        project = QgsProject.instance()
        project.setCrs(CRS)
        CANVAS.setExtent(QgsRectangle(258889, 7430342, 509995, 7661955))
        CANVAS.setDestinationCrs(CRS)

        # Create and open the dialog
        dlg = QuickApiDialog(IFACE)
        dlg.open()
        self.assertTrue(dlg.isVisible())

        # Click the map button which should hide the dialog
        map_button: QPushButton = dlg.map_button
        QTest.mouseClick(map_button, Qt.LeftButton)
        self.assertFalse(dlg.isVisible())
        self.assertIsInstance(CANVAS.mapTool(), PointTool)

        # Click in the map canvas, which should return the clicked coord,
        # make the dialog visible again
        map_releases = QgsMapMouseEvent(
            CANVAS,
            QEvent.MouseButtonRelease,
            QPoint(0, 0),  # Relative to the canvas' dimensions
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        dlg.point_tool.canvasReleaseEvent(map_releases)
        self.assertRegex(dlg.lineedit_xy.text(), r"^(\d+\.\d+.+\d+\.\d+)$")
        self.assertTrue(dlg.isVisible())

        # Clicking the OK button should result in a QMessageBox.critical dialog
        def handle_msgbox():
            msgbox: QMessageBox = QApplication.activeWindow()
            self.assertIsInstance(msgbox, QMessageBox)
            self.assertIn("Unable to geocode", msgbox.text())
            QTest.mouseClick(msgbox.button(QMessageBox.Ok), Qt.LeftButton)

        # Time the MsgBox test to 7000 ms after clicking
        # the OK button (Nominatim rate limiting for ~6 secs..)
        QTimer.singleShot(7000, handle_msgbox)
        QTest.mouseClick(
            dlg.button_box.button(QDialogButtonBox.Ok), Qt.LeftButton
        )

        # No layers produced
        layers = project.mapLayers(validOnly=True)
        self.assertEqual(len(layers), 0)
