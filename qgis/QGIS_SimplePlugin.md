# Create a quick QGIS 3 Plugin

This tutorial is not intended to be a deep dive into QGIS plugins, but rather a guideline for creating a plugin from available boiler plate code based on the very useful [Plugin Builder](http://g-sherman.github.io/Qgis-Plugin-Builder/).

At the end of this tutorial, you will be able to:

- build a GUI with QGIS native Qt Designer
- connect GUI elements to Python functions
- test the plugin locally and upload to QGIS official plugin repository

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **QGIS v3.x**

## Prerequisites

### Hard prerequisites

- QGIS v3.x
- Python > 3.6 (should be your system Python3)

### Make sure the following works

```bash
python3
# in Python console
import qgis
import PyQt5
```
