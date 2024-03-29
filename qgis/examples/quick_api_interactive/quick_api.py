# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickApi
                                 A QGIS plugin
 Query OpenElevation API
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-03-12
        git sha              : $Format:%H$
        copyright            : (C) 2021 by GIS-OPS UG
        email                : info@gis-ops.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import json

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QUrl, QUrlQuery
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QApplication
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsRectangle,
                       QgsPointXY,
                       QgsGeometry,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsNetworkAccessManager, QgsNetworkReplyContent)

# Import the code for the dialog
from .quick_api_dialog import QuickApiDialog
from .maptool import PointTool
import os.path


class QuickApi:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QuickApi_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Quick API')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QuickApi', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, 'icons', 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Query OpenElevation API'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Quick API'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            print("fist")
            self.first_start = False
            self.dlg = QuickApiDialog()
            self.dlg.map_button.setIcon(QIcon(":images/themes/default/cursors/mCapturePoint.svg"))
            self.dlg.finished.connect(self.result)
            self.dlg.crs_input.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
            self.dlg.map_button.clicked.connect(self._on_map_click)  # added line

        self.dlg.open()

    def result(self, result):
        # See if OK was pressed
        if result:
            project = QgsProject.instance()
            # First get all the values of the GUI items
            crs_input = self.dlg.crs_input.crs()
            crs_out = QgsCoordinateReferenceSystem('EPSG:4326')  # we need this to be WGS84 for Nominatim
            lineedit_text = self.dlg.lineedit_xy.value()

            # Protect the free text field for coordinates from generic user failure
            try:
                lineedit_yx = [float(coord.strip()) for coord in lineedit_text.split(',')]
            except:
                QMessageBox.critical(self.iface.mainWindow(),
                                     'QuickAPI error',
                                     "Did you really specify a coordinate in comma-separated Lat/Long?\nExiting...")
                return

            # Create a Point and transform if necessary
            point = QgsPointXY(*reversed(lineedit_yx))
            if crs_input.authid() != 'EPSG:4326':
                xform = QgsCoordinateTransform(crs_input,
                                               crs_out,
                                               project)
                point_transform = xform.transform(point)
                point = point_transform

            # Set up the GET Request to Nominatim
            query = QUrlQuery()
            query.addQueryItem('lat', str(point.y()))
            query.addQueryItem('lon', str(point.x()))
            query.addQueryItem('format', 'json')

            url = QUrl('https://nominatim.openstreetmap.org/reverse')
            url.setQuery(query)

            request = QNetworkRequest(url)
            request.setHeader(QNetworkRequest.UserAgentHeader, 'PyQGIS@GIS-OPS.com')

            nam = QgsNetworkAccessManager()
            response: QgsNetworkReplyContent = nam.blockingGet(request)

            # Only process if HTTP status code is 200
            status_code = response.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if status_code == 200:
                # Get the content of the response and process it
                response_json = json.loads(bytes(response.content()))
                if response_json.get('error'):
                    QMessageBox.critical(self.iface.mainWindow(),
                                         "Quick API error",
                                         "The request was not processed succesfully!\n\n"
                                         "Message:\n"
                                         "{}".format(response_json['error']))
                    return

                x = float(response_json['lon'])
                y = float(response_json['lat'])
                address = response_json['display_name']
                license = response_json['licence']

                # Create the output memory layer
                layer_out = QgsVectorLayer("Point?crs=EPSG:4326&field=address:string&field=license:string",
                                           "Nominatim Reverse Geocoding",
                                           "memory")

                # Create the output feature (only one here)
                point_out = QgsPointXY(x, y)
                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPointXY(point_out))
                feature.setAttributes([address, license])

                # Add feature to layer and layer to map
                layer_out.dataProvider().addFeature(feature)
                layer_out.updateExtents()
                project.addMapLayer(layer_out)

                # build bbox for auto-zoom feature
                bbox = [float(coord) for coord in response_json['boundingbox']]
                min_y, max_y, min_x, max_x = bbox
                bbox_geom = QgsGeometry.fromRect(QgsRectangle(min_x, min_y, max_x, max_y))

                # Transform bbox if map canvas has a different CRS
                if project.crs().authid() != 'EPSG:4326':
                    xform = QgsCoordinateTransform(crs_out,
                                                   project.crs(),
                                                   project)
                    bbox_geom.transform(xform)

                self.iface.mapCanvas().zoomToFeatureExtent(QgsRectangle.fromWkt(bbox_geom.asWkt()))

    def _on_map_click(self):
        self.dlg.hide()
        self.point_tool = PointTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.point_tool)
        self.point_tool.canvasClicked.connect(self._write_line_widget)
        self.point_tool.deactivated.connect(lambda: QApplication.restoreOverrideCursor())
        
    def _write_line_widget(self, point: QgsPointXY):
        self.dlg.lineedit_xy.setText(f"{point.y():.6f}, {point.x():.6f}")
        self.iface.mapCanvas().unsetMapTool(self.point_tool)
        self.dlg.show()
