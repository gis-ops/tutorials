import unittest

from qgis.core import QgsPointXY

from ..core.query import Nominatim
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class TestNominatim(unittest.TestCase):
    """
    Test that Nominatim is returning valid results.

    TODO: make the test independent of nominatim results, i.e. provide a mock
    """

    def _assertCoordsAlmostEqual(
        self, pt1: QgsPointXY, pt2: QgsPointXY, places=6
    ):
        """Assert coordinates are the same within 0.000005 degrees"""
        self.assertAlmostEqual(pt1.x(), pt2.x(), places=places)
        self.assertAlmostEqual(pt1.y(), pt2.y(), places=places)

    def test_success(self):
        in_pt = QgsPointXY(13.395317, 52.520174)
        clnt = Nominatim()
        clnt.do_request(in_pt)

        self._assertCoordsAlmostEqual(in_pt, clnt.get_point(), places=4)

        expected_bbox = (
            QgsPointXY(13.3952203, 52.5201355),
            QgsPointXY(13.3953203, 52.5202355),
        )
        list(
            map(
                lambda pts: self._assertCoordsAlmostEqual(*pts, places=4),
                zip(clnt.get_bbox_points(), expected_bbox),
            )
        )

        address, license = clnt.get_attributes()
        self.assertIn("Am Kupfergraben", address)
        self.assertIn("OpenStreetMap contributors", license)

        self.assertEqual(clnt.status_code, 200)
        self.assertEqual(clnt.error_string, "")

    def test_failure(self):
        in_pt = QgsPointXY(5.822754, 54.889246)
        clnt = Nominatim()
        clnt.do_request(in_pt)

        # Nominatim weirdness
        self.assertEqual(clnt.status_code, 200)
        self.assertNotEqual(clnt.error_string, "")
        self.assertEqual(clnt.get_point(), None)
        self.assertEqual(clnt.get_bbox_points(), None)
        self.assertEqual(clnt.get_attributes(), None)
