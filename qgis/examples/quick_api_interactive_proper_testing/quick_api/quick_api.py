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

import os.path

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDialog
from qgis.gui import QgisInterface

# Import the code for the dialog
from quick_api.gui.quick_api_dialog import QuickApiDialog


class QuickApi:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        # Save reference to the QGIS interface
        self.iface = iface

        # Declare instance attributes
        self.dlg = QDialog()
        self.actions = []
        self.menu_item = "&Quick API"

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "icons", "icon.png")

        icon = QIcon(icon_path)
        action = QAction(
            icon, "Query OpenElevation API", self.iface.mainWindow()
        )
        action.triggered.connect(self.run)
        self.actions.append(action)

        self.iface.addToolBarIcon(action)
        self.iface.addPluginToWebMenu(self.menu_item, action)

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(u"&Quick API", action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Opens the dialog."""
        if self.first_start:
            self.first_start = False
            self.dlg = QuickApiDialog(self.iface)

        self.dlg.open()
