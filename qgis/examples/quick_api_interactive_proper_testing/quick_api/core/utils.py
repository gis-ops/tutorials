from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsPointXY,
    QgsProject,
    QgsCoordinateTransform,
)

WGS84 = QgsCoordinateReferenceSystem.fromEpsgId(4326)


def maybe_transform_wgs84(
    point: QgsPointXY,
    own_crs: QgsCoordinateReferenceSystem,
    direction: int
) -> QgsPointXY:
    """
    Transforms the ``point`` to (``direction=ForwardTransform`) or from
    (``direction=ReverseTransform`) WGS84.
    """
    project = QgsProject.instance()
    out_point = point
    if own_crs != WGS84:
        xform = QgsCoordinateTransform(own_crs, WGS84, project)
        point_transform = xform.transform(point, direction)
        out_point = point_transform

    return out_point
