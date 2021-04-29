import json
from typing import List, Tuple, Optional

from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrlQuery, QUrl
from qgis.core import QgsNetworkAccessManager, QgsPointXY


class Nominatim:
    URL = "https://nominatim.openstreetmap.org/reverse"

    def __init__(self):
        self.nam = QgsNetworkAccessManager()

        # has public access methods
        self._status_code = 0
        self._error_string = ""

        # completely private
        self._content = dict()

    def do_request(self, point: QgsPointXY) -> None:
        query = QUrlQuery()
        query.addQueryItem("lat", str(point.y()))
        query.addQueryItem("lon", str(point.x()))
        query.addQueryItem("format", "json")

        url = QUrl(self.URL)
        url.setQuery(query)

        request = QNetworkRequest(url)
        request.setHeader(
            QNetworkRequest.UserAgentHeader, "PyQGIS@GIS-OPS.com"
        )

        response = self.nam.blockingGet(request)
        self._status_code = response.attribute(
            QNetworkRequest.HttpStatusCodeAttribute
        )
        self._content = json.loads(bytes(response.content()))
        if self._content.get("error"):
            self._error_string = self._content["error"]
            return

    def get_point(self) -> Optional[QgsPointXY]:
        if self._error_string:
            return None
        return QgsPointXY(
            float(self._content["lon"]), float(self._content["lat"])
        )

    def get_bbox_points(self) -> Optional[Tuple[QgsPointXY, QgsPointXY]]:
        if self._error_string:
            return None
        res_bbox: List[float] = [
            float(coord) for coord in self._content["boundingbox"]
        ]
        min_y, max_y, min_x, max_x = res_bbox

        return QgsPointXY(min_x, min_y), QgsPointXY(max_x, max_y)

    def get_attributes(self) -> Optional[Tuple[str, str]]:
        if self._error_string:
            return None
        return self._content["display_name"], self._content["licence"]

    @property
    def status_code(self):
        return self._status_code

    @property
    def error_string(self):
        return self._error_string
