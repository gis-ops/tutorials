from qgis.core import QgsMessageLog
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import  QNetworkAccessManager, QNetworkRequest
import json

def do_request(manager, lat, lng, api_key):
    
    url = f'https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json?prox={lat}%2C{lng}%2C250&mode=retrieveAddresses&maxresults=1&gen=9&apiKey={api_key}'
    QgsMessageLog.logMessage(f'Making a request to {url}')
    req = QNetworkRequest(QUrl(url))
    manager.get(req)

def handle_response(resp):
    
    QgsMessageLog.logMessage(f'Err ? {resp.error()}. Response message : {resp}')
    
    response_data = json.loads(bytes(resp.readAll()))
    QgsMessageLog.logMessage(f'Response {response_data}')
    
    address = response_data["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"]

    our_layer.startEditing()    
    address_col= our_layer.dataProvider().fieldNameIndex("address")
    our_layer.changeAttributeValue(fid, address_col, address)
    our_layer.commitChanges()

    QtWidgets.QMessageBox.information(None, "Success", "Location has been reverse geocoded: {}".format(address))


here_api_key = 'insert_your_here_api_key_here'

our_layer = '[% @layer_id %]'
QgsMessageLog.logMessage("Selected layer ID is {}".format(str(our_layer)))

our_layer = QgsProject.instance().mapLayer(our_layer)

fid = [% $id %]
QgsMessageLog.logMessage("Selected feature ID is {}".format(str(fid)))

feature = our_layer.getFeature(fid)
point = feature.geometry().asPoint()
lat, lng = point.y(), point.x()
QgsMessageLog.logMessage("Selected coordinates are {}, {}".format(lat, lng))

manager = QNetworkAccessManager()
manager.finished.connect(handle_response)


do_request(manager, lat, lng, here_api_key)