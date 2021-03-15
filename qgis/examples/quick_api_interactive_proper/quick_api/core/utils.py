from qgis.core import QgsCoordinateReferenceSystem, QgsPointXY, QgsProject, QgsCoordinateTransform

WGS84 = QgsCoordinateReferenceSystem('EPSG:4326')


def maybe_transform_point_to_wgs(point: QgsPointXY, crs_from: QgsCoordinateReferenceSystem, project: QgsProject) -> QgsPointXY:
    return _transform(point, crs_from, WGS84, project)


def maybe_transform_point_from_wgs(point: QgsPointXY, crs_to: QgsCoordinateReferenceSystem, project: QgsProject) -> QgsPointXY:
    return _transform(point, WGS84, crs_to, project)


def _transform(point: QgsPointXY,
               crs_from: QgsCoordinateReferenceSystem,
               crs_to: QgsCoordinateReferenceSystem,
               project: QgsProject) -> QgsPointXY:
    out_point = point
    if crs_from != crs_to:
        xform = QgsCoordinateTransform(crs_from,
                                       crs_to,
                                       project)
        point_transform = xform.transform(point)
        out_point = point_transform

    return out_point
