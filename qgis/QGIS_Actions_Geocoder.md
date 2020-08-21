### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer](https://gis-ops.com/qgis-3-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugins-pyqt-signals-slots/)
- [QGIS 3 Plugins - Plugin Development Part 1](https://gis-ops.com/qgis-simple-plugin/)
- [QGIS 3 Plugins - Plugin Development Part 2](https://gis-ops.com/qgis-3-use-interactive-mapping/)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)

---

# QGIS 3 Actions - Reverse Geocode Point Data with the HERE Maps API

This tutorial follows you through the development process of a simple QGIS 3 Action.

**Goals**:

- Get more familiar with `QGIS3 Actions` and the `HERE Maps Geocoder API`
- Extend your table with additional columns and populate them programmatically
- Generate random points in polygon
- Upon executing the custom QGIS action a request is made to the HERE Maps API to reverse geocode the point data

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **QGIS <= v3.6.3**
> Occassionally, the author might choose to give hints on Windows-specific setups. `Ctrl+F` for WINDOWS flags. Mac OS users should find the instructions reasonably familiar.

## Prerequisites

- Basic understanding of Python
- Experience with QGIS v3.x
- Python >= 3.6 (should be your system Python3)
- A freemium [HERE Maps Developer Account](https://developer.here.com/sign-up?create=Freemium-Basic&keepState=true&step=account) to create your own API Key

## 1. Prepare your QGIS3 Environment

![Melbourne Polygon with Random Points](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/actions_img1.jpg)

Once you have opened your QGIS3 environment add a basemap of your choice (we recommend [QuickMapServices](https://plugins.qgis.org/plugins/quick_map_services/)). 
Afterwards select EPSG:4326 as your project coordinate reference system and drag and drop the provided [melbourne.geojson](https://github.com/gis-ops/tutorials/raw/master/qgis/data/melbourne.geojson) file into your map.
Note: You obviously could use any other polygon here.

Up next we will need to generate some random points in our polygon which we will use to reverse geocode in our QGIS action later on:

a. Go to Vector / Research Tools / Random Points inside Polygons.
b. Select your input polygon layer (e.g. the melbourne polygon)
c. Input your point count (e.g. 200) / you don't have to set the minimum distance between points
d. We will save the output to a temporary layer

A temporary layer called "Random Points" should have been generated and you will be seeing the amount of points you selected in c. in your polygon on the map.
Our QGIS action will be created in a way which will consume the point data and send it to the HERE Maps Geocoder. 
The response will be an address at that location which we want to save to our temporary table.
To this end, we will have to add one additional column to this table:

a. Right click the Random Points layer and select "Properties"
b. Find the tab "Fields" and add a new field by clicking "toggle editing mode".
c. Then select "new field" and in the dialogue you will have to give it a name, e.g. "address" and the type which in this case should be "Text, unlimited length". 
d. Afterwards hit "toggle editing mode" again and confirm your changes to be saved.


## 2. QGIS3 Action Code

**We only will require one python script. Let's name it `action_geocoder.py`.**

The logic of this script will be invoked once a user has either selected the action in the main toolbor and clicked a specific point feature in the layer or when a feature has been identified and the action has been clicked in the "Identify Results" tab.

1. It will derive the features point geometry
2. Then it will use the latitude and longitude to construct a request which will be fired against there HERE Geocoder Service
3. The service will reverse the coordinates into an address which we will use to save in our temporary points table address column


### Create a new Action

Right click the points layer and select "Properties".
Once opened, navigate to "Actions" and add a new action of type "Python" with a short description. 
The scopes of the action to be selected are "Feature Scope" and "Canvas" which define where and how this specific action can be invoked.

![Create the QGIS Action](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/actions_img2.jpg)


### Action Text

The script consists of multiple parts which we will break down for you in the following.

#### Imports and Programmatically Derive Feature Geometry

The "Action Text" is where we will write our Python code which handle the aforementioned logic (or into a python file in your favourite text editor which you can dynamically load later).
First of all please paste the following into your import statements. 

```python
from PyQt5.QtNetwork import  QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl
from qgis.core import QgsMessageLog
from qgis.PyQt import QtWidgets
import json
```

To make certain we have everything prepared and ready to make a request against the HERE Maps API please paste the following code into the "Action Text" input field.

```python

here_api_key = 'insert_your_here_maps_api_key_here'

our_layer = '[% @layer_id %]'
QgsMessageLog.logMessage("Selected layer ID is {}".format(str(our_layer)))

our_layer = QgsProject.instance().mapLayer(our_layer)

fid = [% $id %]
QgsMessageLog.logMessage("Selected feature ID is {}".format(str(fid)))

feature = our_layer.getFeature(fid)
geom = feature.geometry()
lat, lng = geom.asPoint().y(), geom.asPoint().x()
QgsMessageLog.logMessage("Selected coordinates are {}, {}".format(lat, lng))

manager = QNetworkAccessManager()
manager.finished.connect(handle_response)
```

We can make use of some nifty QGIS features here, namely some built-in functions to derive information of layers and features.
With `@layer_id` we can grab the layer id we are currently working in which is holding our points. 
`$id` on the other hand provides us with the ID of the feature which was clicked to invoke this script.
We bring these 2 variables together and access the feature from the current layer which we then can use to extract the geometry.
Now and then we have added some log messages to help us debug which you can see when the script successfully runs (View > Panels > Log Messages).

We will make use of the handy `QNetworkAccessManager()` which we will make our actual HTTP request.
The handy thing here is that by design it works asynchronously and doesn't run in the main thread, thus it won't block any other operation going on.
With the `connect` function we finally have to make sure the network manager knows which method should be called once the response is returned successfully (this is referred to as the callback function).

Until this point we have the selected feature and its coordinates.
We have also set up the network manager but what is missing is the actual request logic.


### Requesting the HERE Geocoder Service

Let's append a line at the very end...

```python
do_request(manager, lat, lng, here_api_key)
```

And declare this new method which can sit right after the imports.

```python
def do_request(manager, lat, lng, api_key):

  url = f'https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json?prox={lat}%2C{lng}%2C250&mode=retrieveAddresses&maxresults=1&gen=9&apiKey={api_key}'
  QgsMessageLog.logMessage(f'Making a request to {url}')

  req = QNetworkRequest(QUrl(url))
  manager.get(req)
```

Here we set the url for the [HERE Maps geocoding service](https://developer.here.com/documentation/geocoder/dev_guide/topics/what-is.html) which uses our `lat` and `lng` variables as well as the `api_key`.
The request is created as a `QNetworkRequest` which takes the `QUrl` consuming our `url` as input.
Finally the manager makes the HTTP GET request to the REST service.


### Handling the Response

If you have followed carefully you will have noticed at this point that the `handle_response` function is missing.
Try to execute the action in its current form and you will see that the request will be made.
However, the callback method won't be called because it doesn't exist yet.
So let's add it.


```python

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

```

A successful response with a coordinate reverse geocoded will yield a json object from HERE containing all different kinds of interesting information corresponding to these coordinates. 
To keep this tutorial simple, we are only interested in the full text address which HERE Maps provides in the `Label` object of the response.
The response object holding this information is a `QByteArray` which we have to cast to bytes to make sure we can load it into a json object which we can access.

At long last we would like to save the result in our tempory table in the address column we added in the beginning.
To do so we have toggle the selected layer `our_layer` to make it editable and look for the index of the address column which we save to the variable `address_col`.
This will help us make sure we are changing the attribute for this column with the address the geocoding service returned.
After the changes have been commited to the layer with `commitChanges()` a display box will open with the address from the service.

![Select the QGIS Action](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/actions_img3.jpg)

## Wrapping it up

This action can now be invoked once a user selects it either in the canvas or in the feature. 
You will see the QGIS actions icon in the top bar usually located next to the selection features.
If you want to invoke the action from a feature you will be able to if you select a feature and look for the "Actions" entry in the "Identify Feature" tab.

When you've gone through all the steps above, you should be able to see something like this:

![The Geocoded Point](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/actions_img4.jpg)

The final plugin can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/QGIS_Actions_Geocoder.py). 
Feel free to clone it and compare.
