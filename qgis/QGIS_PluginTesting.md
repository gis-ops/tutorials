### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer Explained](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained/)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 1](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-1/) (First Steps)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 2](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-2/) (Interactivity)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 3](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-3/) (Best Practices)
- [QGIS 3 Plugins - Geocoding with Nominatim Part 4](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-4/) (Tests & CI)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)
- [QGIS 3 Plugins - Background Tasks](https://gis-ops.com/qgis-3-plugin-tutorial-background-tasks-explained/)

---

[![Test plugin](https://github.com/gis-ops/tutorials/actions/workflows/test_qgis_plugin.yml/badge.svg)](https://github.com/gis-ops/tutorials/actions/workflows/test_qgis_plugin.yml)


# QGIS 3 Plugins - Geocoding with Nominatim Part 4

This tutorial is for now the last one in this series.

You'll follow up on the previous [part](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-3/), which introduced some best practices for QGIS plugin development and development in general. You can get the last tutorial's [plugin code](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive_proper) to follow along here, if you didn't actually go through it.

So, the final topic will be **testing**. Specifically we'll be looking at:
- unit
- e2e/integration tests
- set up _Continuous Integration_ (CI) on GitHub

We'll go over the few different concepts over the course of writing tests. The final plugin can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive_proper_testing).

Big kudos to Mattheo Ghetta from [Faunalia](www.faunalia.eu) and Nyall Dawson from [North Road](https://north-road.com/) for the testing setup of [DataPlotly](https://github.com/ghtmtt/DataPlotly), where this tutorial got most of its inspiration from.

## Motivation

It can not be stressed enough: code breaks. It just does. With you, without you, even with _and_ without you (the Schrödinger's you). QGIS evolves rapidly and sometimes deprecates existing functionality your code depends on. And of course you're human, so you actually do mistakes here and there. When you implement new features, there's no way you want to (or even can) test every single combination of user behavior. And you never _really_ know what sort of side effects your changes might have on the rest of the code. This is where automated tests save the day (plus valuable developer time in the long run, horrible debugging pain and overwhelming user frustration).

Once you dig in you'll notice that the vast majority of QGIS plugins **do not** have automated test suites. (sad) _Disclaimer_: I'm part of this vast majority too and this tutorial is a way out for me, and I hope provides some insight for you as well.

Having little test coverage on plugins should be a reason for concern, as bad user experience from buggy plugins could stain QGIS' reputation as a whole. I can't speak for the majority of plugin developers, but talking from my own experience this might be a result of:

- Little community guidelines
- Few properly implemented test suites in other plugins "to see how it's done"
- Sometimes authors are not professional developers and/or the plugin is a side project gone public with very limited time budgets (and testing is often lowest priority in that context)
- and last but not least: QGIS Plugins are hard(er) to test in all their components (GUI, processing, some async features etc)

In any case: this is a good example where majority behavior shouldn't be your guide. Dig in with us, it won't hurt (or not as much as you might fear ;) I, for one, was very positively surprised!).

**Goals**:

- introduce basic unit tests
- learn e2e testing: how to test the UI the way a user interacts with the plugin
- set up a Github Actions workflow for the QGIS plugin so your code is tested when you push

> **Disclaimer**
>
> Validity only confirmed for **Linux** and **QGIS v3.18**

## Prerequisites

### Hard prerequisites

- Basic understanding of Python
- QGIS v3.x
- **[Previous tutorial(s)](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-3/)** or alternatively the **[prepared plugin](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive_proper)**
- [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin installed
- Python >= 3.6 (should be your system Python3)

## 1 - Terminology

As always in software development there are certain terms you should be familiar with  (sigh..):

**Unit** testing ideally isolates each method to be tested individually, meaning no (or as little as possible) side effects from other parts of the code.<br/>**Integration** tests ensure that the individual components work well together, e.g. the output of one function works as input to another function. <br/>**e2e** tests imitate an actual user using the application for entire workflow start to finish.<br/>**CI** stands for **C**ontinuous **I**ntegration and actually describes the behavior of merging code from several contributors on a regular basis. It's mostly synonymous today for running automated tests on a remote infrastructure. Here we'll use Github Actions.

Integration and e2e tests will be pretty much the same here, the lines are pretty blurry often anyways.

## 2 - Preparation

First we'll prepare our project. In the last tutorial we already took some measures to make the test-writing part a smooth(er) journey, so we don't actually have to touch any of the plugin code.

To not complicate things further we'll write our tests with Python's built-in `unittest` framework. In bigger projects, we usually prefer to use [`pytest`](https://docs.pytest.org/en/6.2.x/), which uses an entirely different, more scalable approach.

We _actually_ prefer to have out-of-source tests (i.e. in a root `tests` folder, so we don't have to ship irrelevant tests to users). However, the CI setup we'll come to later will depend on in-source tests. So create a folder called `tests` in `quick_api/`.

As a first action you'll copy/paste the code from smarter people than us, which will make the whole thing much easier.

Some background to that: One issue which makes testing QGIS plugins a little alien is the fact that we need to test software which _is expecting to run_ within a QGIS application, but _are run_ in isolated tests, i.e. not within the QGIS environment. You typically invoke `unittest` suites with `python -m unittest` from the command line. But then your code very much depends on a living QGIS environment, so you need a way to initialize one.

So, we copy some code from [DataPlotly](https://github.com/ghtmtt/DataPlotly), which will set up QGIS and it's heavier components:

### [`qgis_interface.py`](https://github.com/ghtmtt/DataPlotly/blob/master/DataPlotly/test/qgis_interface.py) by [Tim Sutton](https://kartoza.com/en/)

This one has been going around since the dawn of ages apparently (< QGIS v2) and is still highly useful.

It "mocks" (i.e. pretends to be) a `QgisInterface`. The real `QgisInterface` object is normally passed to your plugin in the root `__init__.py` by QGIS and can't be simply constructed in Python code to be usable. The mock defines a few stubs so that our plugin tests can use the "normal" QGIS functionality offered by `QgisInterface`, like adding toolbars, getting the `QgsMapCanvas` and so on.

Create this file in the `quick_api/tests` folder and copy the contents of the header link, we'll need it soon.

### [`utilities.py`](https://github.com/ghtmtt/DataPlotly/blob/master/DataPlotly/test/qgis_interface.py)

Only exposes a single function: `get_qgis_app()`. When called from outside a QGIS environment (as we do from our tests), this will set up and initialize a QGIS instance programmatically, so we can expect our plugin to work as expected.

It returns a tuple of:
- `QGISAPP`: The actual application object, i.e. a `QgsApplication` instance
- `CANVAS`: A clean `QgsMapCanvas` object initialized with size 400 x 400 px
- `IFACE`: The "mock" `QgisInterface` (see above)
- `PARENT`: A dummy `QWidget()` to act as parent for other widgets (not very useful)

With those objects we'll get very close to an actual QGIS environment. Close enough that our tests will succeed anyways.

So, create this file in the `quick_api/tests` folder and copy the contents of the header link, we'll need it soon.

## 3 - Simple unit tests

In general, you'd want to have one test file per source file and test every single line/condition etc. It's important that you know what exactly to test for. You can get great test coverage yet not test a single important thing.

Let's first do the easy part and write a few tests for `core/utils.py`. Here we only have one single function, which serves two purposes: transforming a coordinate either _from_ or _to_ WGS84. However, in the case where our project CRS is also WGS84, it shouldn't do anything and simply return the input point.

Create a file `test_utils.py` in `quick_api/tests` and paste the following:

```python
import unittest

from qgis.core import QgsCoordinateReferenceSystem, QgsPointXY, QgsCoordinateTransform

from quick_api.core.utils import maybe_transform_wgs84


class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.WGS = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        cls.PSEUDO = QgsCoordinateReferenceSystem.fromEpsgId(3857)

    def test_to_wgs_pseudo(self):
        point = QgsPointXY(1493761.05913532, 6890799.81730105)
        trans_point = maybe_transform_wgs84(point, self.PSEUDO, QgsCoordinateTransform.ForwardTransform)
        self.assertEqual(trans_point, QgsPointXY(13.41868390243822162, 52.49867709045137332))

    def test_to_wgs_same_crs(self):
        point = QgsPointXY(13.41868390243822162, 52.49867709045137332)
        trans_point = maybe_transform_wgs84(point, self.WGS, QgsCoordinateTransform.ForwardTransform)
        self.assertEqual(trans_point, point)
```

It's conventional to prefix your test names with `test_`. In fact `unittest` will use this pattern to auto-discover your tests.

Here, we use the `setUpClass()` class method to initialize a few objects we'll need in the individual tests. This method will only run **once before all** its tests are executed and is often used to set up stuff like database connections etc. It has a counterpart called `tearDownClass()` which is run **once after all** its tests are executed. There's also `setUp()` and `teardown()` which are run **before** and **after every** test function, respectively.

Finally each test does some `assert`, which is the actual test. We advise you to use the `unittest` abstractions around `assert` (e.g. `self.assertEqual()`), otherwise the error messages on failures will be very non-descriptive.

Now you can run it with `python -m unittest discover`.

We "only" tested the cases for forward transformation, i.e. from `EPSG:3857` to `EPSG:4326`. You can quickly make this more robust and test for the reverse transformations as well. Double-check with [our solution](https://github.com/gis-ops/tutorials/blob/qgis-testing/qgis/examples/quick_api_interactive_proper_testing/quick_api/tests/test_utils.py).

## 4 - Unit tests involving QGIS

Often you'll get away without initializing a full QGIS environment and can test just like we did above. However, sometimes you need to test code which relies on a QGIS environment and it's not always super obvious when that's the case.

To exemplify, let's test the Nominatim client in `core/query.py`. In the end there are only two scenarios we need to test here: a successful geocoding request and a failed one. So let's get to it:

```python
import unittest

from qgis.core import QgsPointXY

from ..core.query import Nominatim


class TestNominatim(unittest.TestCase):
    """
    Test that Nominatim is returning valid results.
    """

    def _assertCoordsAlmostEqual(self, pt1: QgsPointXY, pt2: QgsPointXY, places=6):
        """Assert coordinates are the same within 0.000005 degrees"""
        self.assertAlmostEqual(pt1.x(), pt2.x(), places=places)
        self.assertAlmostEqual(pt1.y(), pt2.y(), places=places)

    def test_success(self):
        in_pt = QgsPointXY(13.395317, 52.520174)
        clnt = Nominatim()
        clnt.do_request(in_pt)

        self._assertCoordsAlmostEqual(in_pt, clnt.get_point(), places=4)

        expected_bbox = (QgsPointXY(13.3952203, 52.5201355), QgsPointXY(13.3953203, 52.5202355))
        list(map(lambda pts: self._assertCoordsAlmostEqual(*pts, places=4), zip(clnt.get_bbox_points(), expected_bbox)))

        address, license = clnt.get_attributes()
        self.assertIn('Am Kupfergraben', address)
        self.assertIn('OpenStreetMap contributors', license)

        self.assertEqual(clnt.status_code, 200)
        self.assertEqual(clnt.error_string, '')

    def test_failure(self):
        # test point in the Northern Sea
        in_pt = QgsPointXY(5.822754, 54.889246)
        clnt = Nominatim()
        clnt.do_request(in_pt)

        self.assertEqual(clnt.status_code, 200)  # Nominatim weirdness
        self.assertNotEqual(clnt.error_string, '')
        self.assertEqual(clnt.get_point(), None)
        self.assertEqual(clnt.get_bbox_points(), None)
        self.assertEqual(clnt.get_attributes(), None)
```

The tests should be pretty self-explanatory.

One problem with testing HTTP APIs like this is that we heavily rely on the actual response from Nominatim. That can be problematic because we don't have control over Nominatim's query results. Our test request might return a different response sometime in the future: the underlying OSM data could change, Nominatim could change its format etc. We do try to circumvent this issue a little by only comparing coordinates to 4 decimal places in `self._assertCoordsAlmostEqual()`. Often people "mock" HTTP API responses with e.g. [`responses`](https://pypi.org/project/responses/). However, then the problem is again that we _wouldn't_ be notified if Nominatim changes its request/response format which is even worse than a failing test here and there which we can easily correct when it happens.

If you run the tests now you should get an error along the lines of
```
[1]    43266 segmentation fault (core dumped)  python -m unittest`
```
What a useful error message.. So, what happened?

The issue is that the `Nominatim` class uses the `QgsNetworkAccessManager` class to make the request. And that one _does_ depend on a QGIS environment: you can pass authentication strings from QGIS' auth database and it uses QGIS built-in proxy details if needed.

The solution couldn't be easier thanks to the effort of others: we simply have to import the `get_qgis_app()` function from `quick_api/tests/utitlities` and execute it at the top of the file which will initialize a QGIS instance and `QgsNetworkAccessManager` will have something to hold on to:

```python
import unittest

from qgis.core import QgsPointXY

from ..core.query import Nominatim
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class TestNominatim(unittest.TestCase):
  ...
```

Now a `python -m unittest discover` will work!

## 5 - e2e tests

This is much more interesting. Now we want to simulate a user's behavior and make sure the plugin reacts as intended. These sort of tests are often much more involved, because you often encounter parts of the Qt/QGIS API which are harder to test, such as modal dialogs, signals/slots etc.

For our little plugin, we have two e2e tests in mind:

1. The user has a project in a CRS different from WGS84, opens the plugin dialog, clicks in the map where Nominatim can find an address and the result will be dumped to a layer and added to the canvas.
2. The user does the same as in 1., but clicks in an area on the map where Nominatim will fail to find an address. In that case we want to make sure the modal error dialog is shown to the user before the plugin exits.

We'll only show the more interesting 2. scenario and you can add another method for yourself testing the 1. scenario (or look at [our solution](https://github.com/gis-ops/tutorials/blob/qgis-testing/qgis/examples/quick_api_interactive_proper_testing/quick_api/tests/test_e2e.py)):

```python
import unittest

from qgis.PyQt.QtTest import QTest
from qgis.PyQt.QtCore import Qt, QEvent, QPoint, QTimer
from qgis.PyQt.QtWidgets import QPushButton, QDialogButtonBox, QMessageBox, QApplication
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRectangle, QgsVectorLayer, QgsFeature, \
    QgsFeatureIterator

from .utilities import get_qgis_app

# 1. Get all relevant QGIS objects
CANVAS: QgsMapCanvas
QGISAPP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFlow(unittest.TestCase):

    def test_full_failure(self):
        """Test failing request"""

        # 2. need to import here so that there's already an initialized QGIS app
        from quick_api.gui.quick_api_dialog import QuickApiDialog
        from quick_api.core.maptool import PointTool

        # 3. first set up a project
        CRS = QgsCoordinateReferenceSystem.fromEpsgId(3857)
        project = QgsProject.instance()
        CANVAS.setExtent(QgsRectangle(258889, 7430342, 509995, 7661955))
        CANVAS.setDestinationCrs(CRS)

        # 4. Create and open the dialog
        dlg = QuickApiDialog(IFACE)
        dlg.open()
        self.assertTrue(dlg.isVisible())

        # 5. Click the map button which should hide the dialog
        map_button: QPushButton = dlg.map_button
        QTest.mouseClick(map_button, Qt.LeftButton)
        self.assertFalse(dlg.isVisible())
        self.assertIsInstance(CANVAS.mapTool(), PointTool)

        # 6. Click in the map canvas, which should return the clicked coord,
        # make the dialog visible again
        map_releases = QgsMapMouseEvent(
            CANVAS,
            QEvent.MouseButtonRelease,
            QPoint(0, 0),  # Relative to the canvas' dimensions
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier
        )
        dlg.point_tool.canvasReleaseEvent(map_releases)
        self.assertRegex(dlg.lineedit_xy.text(), r'^(\d+\.\d+.+\d+\.\d+)$')
        self.assertTrue(dlg.isVisible())

        # 7. Clicking the OK button should result in a QMessageBox.critical dialog
        def handle_msgbox():
            msgbox: QMessageBox = QApplication.activeWindow()
            self.assertIsInstance(msgbox, QMessageBox)
            self.assertIn('Unable to geocode', msgbox.text())
            QTest.mouseClick(msgbox.button(QMessageBox.Ok), Qt.LeftButton)

        # Time the MsgBox test to 7000 ms after clicking
        # the OK button (Nominatim is rate limiting for ~6 secs..)
        QTimer.singleShot(7000, handle_msgbox)
        QTest.mouseClick(dlg.button_box.button(QDialogButtonBox.Ok), Qt.LeftButton)

        # 8. No layers produced
        layers = project.mapLayers(validOnly=True)
        self.assertEqual(len(layers), 0)
```

Let's go through point by point:

1. After all the imports you'll notice we capture all objects returned from `get_qgis_app()`. While the `CANVAS` is a real `QgsMapCanvas` object, `IFACE` is the stub class from `qgis_interface.py` which we'll need to initialize our own plugin dialog.
2. Next you'll see that we have another set of imports _inside_ the test function. The reason here is that `quick_api/core/maptool.py`, from which `PointTool` is imported, defined a `QPixMap` as a static global variable. A `QPixMap` needs a running application apparently. If you stick to normal import patterns, Python would try to evaluate all the global and static stuff in the imported modules first, which is _before_ `get_qgis_app()` is executed and will consequently fail. You can achieve the same if you import those two things _after_ `get_qgis_app()` is called at the top of the file.
3. Then we set up the canvas to have a CRS of `EPSG:3857` and set its extent to be somewhere in the Northern Sea to make sure Nominatim will definitely fail the request.
4. By creating the dialog with the fake `QgisInterface` (remember, we have no access to the real deal) we simulate the user opening the plugin dialog. The fake `QgisInterface` is also the reason why we create a `QuickApiDialog` and not the higher-level `QuickApi` class from `quick_api/quick_api.py`: the latter is only responsible to register some stuff with QGIS, mostly its `iface` member.
5. We can use `QTest` to simulate a left mouse click on the `map_button` (which is the name we gave this button in Qt Designer). `QTest.mouseClick()` will by default simulate the click in the center of the widget it's passed. Now we can test the expected behavior of hiding the plugin dialog and making sure our map tool is active.
6. The next step is a little tricky: We need to simulate that the user clicked (and released the click) on the map canvas. Remember our map tool has the `canvasReleaseEvent()` slot which is called with a `QgsMapMouseEvent` by `QgsMapCanvas` _inside_ QGIS. `QTest.mouseClick()` cannot emit this event, so we have construct it ourselves and pass it to the map tool. That triggers our custom `canvasClicked` signal from `quick_api/core/maptool.py` which emits the transformed clicked point to the plugin dialog's `lineedit_xy` widget. A user would now see the dialog again with the WGS84 coordinates of the clicked point. We're not really caring about the exact Lat/Lon values since we don't have too much control which coordinate was clicked on the canvas, so we test with a simple regex.
7. This is the most interesting part. At this point the simulated user would only need to click "OK" to request Nominatim. But the request will fail, there are [(almost) no addresses](https://en.wikipedia.org/wiki/Principality_of_Sealand) in the Northern Sea. On failure a modal dialog will open warning the user about it. A modal dialog is problematic because it stops code execution until the user interacts with it. However, in an automated test there is no user and once the modal dialog is open no one can push a button and the dialog would never close. To work around that Qt has a `QTimer`, which can schedule a task in the background _before_ the modal dialog is triggered, passing the time in msec it should delay the execution of the passed function. So, 7 seconds after being called the `QTimer.singleShot` calls `handle_msgbox()` which will test that the modal dialog was indeed opened. We delay for 7 seconds because of Nominatim's quite heave rate limiting.
8. Finally we make sure there was no layer created.

When you run this test, don't be surprised when the message box pops up on your screen. It's supposed to. Don't interact with it (or any other window) as that would invalidate the test.

Testing our 1. scenario would look very similar: you'd choose a different area for the canvas' extent and check the created layer and the feature it contains. See [our solution](https://github.com/gis-ops/tutorials/blob/qgis-testing/qgis/examples/quick_api_interactive_proper_testing/quick_api/tests/test_e2e.py)

## 6 - Measure coverage

Running all these tests is great, but how do we know our code was thoroughly tested? That's the job of the `coverage` package. First install it: `pip install coverage`. It's another tool we need to configure a little. In the `pyproject.toml` of the plugin include this section:

```ini
[tool.coverage.run]
branch = true
source = ["quick_api"]
omit = ["*/quick_api_dialog_base.py", "*/quick_api.py", '*/__init__.py', "*/tests/*", "*/test_suite.py"
```

This will only report the coverage of the `quick_api` package and `omit` files we don't want/need to test in that package.

Next we can run `coverage run -m unittest discover && coverage report` to print the coverage report to your console. While this is really helpful, it doesn't yet show you which parts of your code are _not_ covered by tests. A `coverage run -m unittest discover && coverage html` will produce a `htmlcov` folder in your current directory. If you open the `index.html` in your web browser you'll be presented with an informative and interactive trace of your exact code coverage per module.

## 7 - Set up Github Actions CI

Finally we can set up our CI jobs on Github Actions, so you can get the fancy badges like [![Test plugin](https://github.com/gis-ops/tutorials/actions/workflows/test_qgis_plugin.yml/badge.svg)](https://github.com/gis-ops/tutorials/actions/workflows/test_qgis_plugin.yml). We won't give the full overview here for Github Actions as that's waaayyy out-of-scope. But there are a few peculiarities around testing QGIS plugins remotely, so we'll show you a little the ins and outs.

### Overview

First look at the config YAML (needs to be in `.github/workflows/<name>.yml`):

```yaml
name: Test plugin

on:
  push:
    branches:
      - master
    paths:
      - "qgis/examples/quick_api_interactive_proper/**"
      - ".github/workflows/test_qgis_plugin.yaml"
  pull_request:
    branches:
      - master
    paths:
      - "qgis/examples/quick_api_interactive_proper/**"
      - ".github/workflows/test_qgis_plugin.yaml"

env:
  # plugin name/directory where the code for the plugin is stored
  PLUGIN_NAME: quick_api
  PLUGIN_PATH: qgis/examples/quick_api_interactive_proper_testing
  # python notation to test running inside plugin
  TESTS_RUN_FUNCTION: quick_api.test_suite.test_package

jobs:
  Tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        docker_tags: [release-3_16, release-3_18, latest]
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Docker pull and create container
        run: |
          docker pull qgis/qgis:${{ matrix.docker_tags }}
          docker run -d --name qgis-testing-environment -v "${GITHUB_WORKSPACE}/${PLUGIN_PATH}":/tests_directory -e DISPLAY=:99 qgis/qgis:${{ matrix.docker_tags }}
      - name: Docker set up QGIS
        run: |
          docker exec qgis-testing-environment sh -c "qgis_setup.sh $PLUGIN_NAME"
          docker exec qgis-testing-environment sh -c "rm -f /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$PLUGIN_NAME"
          docker exec qgis-testing-environment sh -c "ln -s /tests_directory/$PLUGIN_NAME /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$PLUGIN_NAME"
          docker exec qgis-testing-environment sh -c "pip3 install -r /tests_directory/requirements-tests.txt"
      - name: Docker run plugin tests
        run: |
          docker exec qgis-testing-environment sh -c "qgis_testrunner.sh $TESTS_RUN_FUNCTION"
```

One of the most important things to note here is the `strategy` matrix which defines docker tags for the relevant QGIS releases: LTR (3.16), stable (3.18) and `latest` (which is the `master` branch of QGIS). This strategy ensures that your plugin will work in the most relevant QGIS environments. **Note**, this obviously only tests Linux platforms, a setup for CI testing Windows and Mac could be worthwhile in case you include platform-specific stuff (like external, compiled libraries), but we have currently also no idea how to do that (future blog?).

The tests are run in a QGIS docker container, which contains some magic to set up the right environment. Just note for now, that your repository root is mapped to the `/tests_directory` directory inside the container.

### Test suite module

One of the peculiarities with the above approach is that you'll need to provide a programmatic entrypoint for the tests; it can't execute the tests with `python -m unittest`. You can see in the last step it's calling `qgis_testrunner.sh` (provided by the QGIS image) with the argument `$TESTS_RUN_FUNCTION` aka `quick_api.test_suite.test_package`. That function doesn't exist yet, so let's create it in a new `quick_api/test_suite.py` file:

```python
# coding=utf-8
import sys
import unittest
import qgis  # noqa: F401

import coverage
from osgeo import gdal

__author__ = 'Alessandro Pasotti'
__revision__ = '$Format:%H$'
__date__ = '30/04/2018'
__copyright__ = (
    'Copyright 2018, North Road')


def _run_tests(test_suite, package_name):
    """Core function to test a test suite."""
    count = test_suite.countTestCases()
    print('########')
    print('%s tests has been discovered in %s' % (count, package_name))
    print('Python GDAL : %s' % gdal.VersionInfo('VERSION_NUM'))
    print('########')

    cov = coverage.Coverage(
        source=['/tests_directory/quick_api'],
        omit=["*/quick_api_dialog_base.py", "*/quick_api.py", '*/__init__.py', "*/tests/*", "*/test_suite.py"],
    )
    cov.start()

    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)

    cov.stop()
    cov.save()
    cov.report(file=sys.stdout)


def test_package(package='quick_api'):
    """Test package.
    This function is called by travis without arguments.

    :param package: The package to test.
    :type package: str
    """
    test_loader = unittest.defaultTestLoader
    try:
        test_suite = test_loader.discover(package)
    except ImportError:
        test_suite = unittest.TestSuite()
    _run_tests(test_suite, package)


if __name__ == '__main__':
    test_package()
```

Now the CI command will programmatically invoke `unittest` and `coverage`, and print the report to the console.

### Linting

Remember how we set up a linter (`flake8`) and style checker (`black`) in the [last tutorial](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-3/)? Even though we already have a `pre-commit` hook to not push anything unlinted, we want to make sure any contributor's PR's are linted as well before merging them into `master`.

Add this section to your CI config yaml:

```yaml
#jobs:
  ...

  Lint:
    runs-on: ubuntu-latest
    steps:

      - name: Install Python
        uses: actions/setup-python@v1
        with:
          python-version: '3.9'
          architecture: 'x64'

      - name: Checkout
        uses: actions/checkout@v2

      - name: Install packages
        run: |
          cd "${GITHUB_WORKSPACE}/${PLUGIN_PATH}" && pip install -r requirements-tests.txt

      - name: Flake8
        run: cd "${GITHUB_WORKSPACE}/${PLUGIN_PATH}" && flake8 .

      - name: Black
        run: cd "${GITHUB_WORKSPACE}/${PLUGIN_PATH}" && black . --check
```

Now the `Lint` job will fail if a PR or commit to `master` is not adhering to the project's style & lint constraints.

### requirements-test.txt

Now we have a couple of packages which our tests expect. These will have to be installed on the vanilla Python distribution that's typically installed on fresh Ubuntu CI machines.

Create the `requirements-tests.txt` file at the top level with the following:

```
coverage
black
flake8
```

The CI jobs we registered already take this requirements file into account.

### Test CI configuration

Before pushing the new CI config YAML, make sure you test locally with one QGIS docker image. You can take most of the commands from the YAML as they are, but change the bits that need changing (e.g. environment variables).

Then you can finally push it and watch how CI is running your builds! Don't feel bad if you don't get it right on the first try. When I wrote this tutorial it took a solid 6 commits.
