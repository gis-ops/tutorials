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


---

# QGIS 3 Plugins - Geocoding with Nominatim Part 3

This tutorial follows up on the [second QGIS plugin development tutorial](https://gis-ops.com/qgis-simple-plugin/), which built an interactive plugin where a user could reverse geocode via [Nominatim](https://wiki.openstreetmap.org/wiki/Nominatim) by clicking a point in the map canvas. If you have no idea what I'm talking about, go through the last [tutorial](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-2/) or get the previously prepared plugin from our [repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive).

In this tutorial we won't introduce a lot of new functionality, but rather focus on things that'll make our live a lot easier going forward developing a plugin: apply a better code/module structure, learn some tricks like IntelliSense autocompletion in your IDE and introduce quality features like code linting. So far (almost) everything lived in a single file. Which is totally fine for the limited functionality we have up to now. But suppose you'd want to offer another geocoding provider, such as [OpenCage Geocoder](https://opencagedata.com/) or integrate more plugin dialogs. You'd have to refactor a lot and you'd soon notice that one file is not enough to hold the entire logic. After describing some of those principles & tips, we'll apply them in the last chapter to the interactive plugin you developed in the [last tutorial](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-2/). In the next tutorial we'll go one step further and introduce automated testing.

The final restructured plugin can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive_proper).

**Goals**:

- learn some useful tips around plugin development
- refactor code for maintainability & extensibility
- introduce quality assurance features like linting

> **Disclaimer**
>
> Validity only confirmed for **Linux** and **QGIS v3.18**
> Occassionally, the author might choose to give hints on Windows-specific setups. `Ctrl+F` for WINDOWS flags. Mac OS users should find the instructions reasonably familiar.

## Prerequisites

### Hard prerequisites

- Basic understanding of Python
- QGIS v3.x
- **[Previous tutorial(s)](https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-2/)** or alternatively the **[prepared plugin](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive)**
- [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin installed
- Python >= 3.6 (should be your system Python3)

### Recommendations

- Basic Python knowledge
- Familiarity with
	- Qt Designer application, see [our tutorial](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
	- Python Plugin Basics, see [our tutorial](https://gis-ops.com/qgis-3-plugin-development-reference-guide/)

## 1 - Licensing

This is not making your life easier exactly, but is one of the most important points when dealing with open-source software development in general and QGIS in particular.

QGIS is licensed under the [GNU Public License (GPL) version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html). GPL is a copyleft license which mandates that your code must be licensed under the same (or very similar) license if you use any functionality/code of GPL software. The main point of GPL is that any recipient of GPL licensed software **must have access to the source code**. That sounds harsh, but is (in theory) a good protection for the many volunteer hours of amazing QGIS development (isn't it ESRI?).

In practice that means QGIS plugins are implicitly GPL licensed and **if** you distribute QGIS plugins to anyone you **have to** give them easy access to the source code (commonly put it on Gitlab/-hub). You **don't have to** if you're the only plugin user.

Do note, that usually a copyleft license is kinda meaningless to Python code, as it's an interpreted language where source code == compiled code. The point for GPL licensed Python code would rather be: don't obfuscate your code or deliver packaged (e.g. `.exe`) files.

## 2 - Enable IntelliSense

Let's continue with the most gratifying and useful tip: enable your IDE to provide you with intelligent code completion. This will save you tons of time grooming through QGIS and Qt documentation. While QGIS [docstrings](https://en.wikipedia.org/wiki/Docstring#:~:text=In%20programming%2C%20a%20docstring%20is,a%20specific%20segment%20of%20code.) are outstanding, PyQt pretty much has zero docstrings though (but you still see which functions are even available for a module/class).

The exact method depends a lot on the IDE and platform (Linux, MacOS, Win), but the general idea is always the same: you have to tell your IDE where the QGIS packages are located. The process of doing that obviously also depends on your IDE; for PyCharm see [this SO thread](https://stackoverflow.com/questions/48947494/add-directory-to-python-path-in-pycharm).

To really understand what's going on, there's a couple of gotcha's in the way QGIS and Python interact:

- On Linux and MacOS QGIS uses the system Python3, on Win it ships with its own Python installation
- QGIS provides the system python only with the `qgis` namespace, things like `processing` (for processing functionality like running algorithms) are missing
- QGIS will augment the paths Python uses to locate packages & modules with the relevant directories **on startup** (meaning when QGIS is initialized and running, it knows where all packages are even if your IDE has no clue about it)

The last point means that a QGIS Python console can give you the clue where all the relevant packages are installed: open the QGIS Python console and do a `import sys; print(sys.path)`. On Linux these are:

- `/usr/lib/python3.<minor_version>/site-packages`: holds the entire `qgis` namespace (includes its own `PyQt` namespace) and all system-wide packages (does not need to be added to IDE settings)
- `/usr/share/qgis/python`: holds access to `pyplugin_installer` (interacting with plugin (un)installation, rarely useful) and `console` package
- `/usr/share/qgis/python/plugins`: holds the `processing` (useful to interact with processing algorithms) and `db_manager` (very useful if you ever need classes interacting with databases)
- `/home/<user>/.local/share/QGIS/QGIS3/profiles/default/python/plugins`: the location for user-installed plugins, also rarely useful

So, add the 2. and 3. path to your IDE's Python interpreter paths and make sure you it understands `import processing`. Congrats, now you got the QGIS documentation at your fingertips.

**Bonus Points**: Now you got access to all definitions of _your current_ QGIS version. For developers that's often the latest version. However, most commonly you'd at least like to support the current _LTS_ version, which is mostly a few versions ago. To make sure you're not using undefined classes/methods, you can compile the QGIS LTS version from source following the [compilation manual](https://github.com/qgis/QGIS/blob/master/INSTALL.md) and more [official tips for IDE integration](https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/plugins/ide_debugging.html#debugging-with-pycharm-on-ubuntu-with-a-compiled-qgis).

## 3 - Compile your .ui files

One of the most annoying things for us when developing plugins in the "classical" way (meaning the output of `Plugin Builder` plugin) is the lack of IntelliSense for the UI files from Qt Designer. Here's a way how your IDE knows the UI objects you created:

1. Use `pyuic5` to compile the `.ui` files to Python files which can be imported:
```
pyuic5 <input_file> > <output_file>
# e.g.
pyuic5 quick_api_dialog_base.ui > quick_api_dialog_base.py
```
2. Import the automatically created class from `quick_api_dialog_base.py` where you need it; `quick_api_dialog_base.py` in this case
3. Subclass your existing dialog class from the newly imported class instead of `FORM_CLASS`, e.g.:
```python
from ..ui.quick_api_dialog_base import Ui_QuickApiDialogBase

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/quick_api_dialog_base.ui'))


class QuickApiDialog(QtWidgets.QDialog, Ui_QuickApiDialogBase):
    def __init__(self, iface: QgisInterface, parent=None):
        """Constructor."""
        super(QuickApiDialog, self).__init__(parent)
        self.setupUi(self)
```

Now you have all the objects you created in Qt Designer available for IntelliSense in your IDE! **Note**, the downside of this approach is you'll **have to compile the UI file(s) every time they change**. We commonly add a PyCharm configuration with a shell script containing all the `pyuic5` commands to re-compile the UI files to Python files.

## 4 - Best practices

While it's totally fine to have a flat file structure for small plugins/code bases in general, there are many reasons to apply common software development principles also to plugins, e.g.:

- **Logical naming & namespacing**: Imagine your code base was a shelf with drawers with labels to indicate what's inside: you want to navigate your way easily when looking for a particular functionality. Names should be rather explicit and long(er) than implicit and short(er).
- **Separation of concerns**: Break your code into smaller, encapsulated chunks (i.e. methods) with a single purpose and as little side effects as possible. This ensures easy testability and bug tracing.
- **Defensive coding**: Meaning, always think what could go wrong when executing your code and properly guard against user-induced errors. This is very important for QGIS plugin development as users are often technically rather casual
- **Unit and e2e testing**: Unit testing makes sure single methods are doing what they're supposed to, while e2e (or integration) tests rather test an entire workflow start to finish. In our case an e2e test would be to test whether a layer was created after the user hit OK with valid coordinates.

As most QGIS plugins are openly accessible, a smart plugin maintainer would like community contributions for bug fixes or new features. Following best practices like the ones above makes community contribution much more likely. No one wants to dive into spaghetti code.

## 5 - Project structure

In terms of QGIS plugins, a sensible project structure usually emulates QGIS' own package structure, where you'd end up with something like this:

```
quick_api_interactive_proper
├── .git/
├── dist/
├── quick_api/
│   ├── core/
│   ├── gui/
│   ├── icons/
│   ├── ui/
│   ├── __init__.py
│   ├── metadata.txt
│   └── quick_api.py
├── tests/
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
└── setup.cfg
```

First, the actual plugin code should live as a package in your Git folder and it's common to give it the same name as the plugin, i.e. `quick_api/`. That way you'll only package relevant files for the plugin and can omit project/development files like README and dev setup files (e.g. `setup.cfg`). When you package your plugin for QGIS (i.e. zip it up), you can put the ZIP(s) in the `dist/` folder.

The code inside the plugin package is commonly leaning towards QGIS own logic:
- `core/`: Contains the business logic of your plugin, mostly functionality that doesn't depend on the rest of your plugin like the UI. In our case that'd would the logic to request Nominatim and the map tool capturing clicked points.
- `gui`: Contains the logic around your dialogs, which will make use of the `core/` functionality.
- `icons`: A place to hold your plugin-specific icons, doesn't need to be a Python package (i.e. no need for a `__init__.py`).
- `ui`: Contains the raw and/or compiled UI files.
- `processing` (if needed): Contains the modules used to integrate with QGIS Processing framework.
- `__init__.py`: **Only** contains the `classFactory()` QGIS expects every plugin to have.
- `quick_api.py`: The class QGIS uses to instantiate the plugin. This should only contain functionality which is important to the **main** QGIS app, such as adding toolbars/menus (e.g. in `initGui()`) or the `unload()` function. See our [QGIS Plugin 101 tutorial](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/) for more info.

## 6 - Linters

Linters deal with ensuring best development practices (e.g. flagging unused variables) and can also be used to ensure a consistent style across the code base. Style and best practice conformance will help you write better code and make it much easier for external contributors.

There's tons of options for Python, we'll use `flake8`, a wrapper around multiple related projects, which will report any violations of registered style/programming guides (check the [documentation](https://flake8.pycqa.org/en/latest/user/configuration.html) on how to ignore certain violations like maximum line length). For style formatting we'll use `black`, the ["_uncompromising Python code formatter_"](https://github.com/psf/black).

#### Configuration

After installing both via `pip`, you can configure `flake8` and `black` project-wide. Unfortunately, both packages support different configuration files (Python really has an infrastructure problem...): `black` wants its config in `pyproject.toml` while `flake8` expects its configuration in `setup.cfg`. Our configuration for this project looks like this:

##### `setup.cfg`
```ini
[flake8]
# ignore some errors to play nicely with black
ignore = E203,E266,E501,W503,F403,E722
max-complexity = 10
max-line-length = 88
exclude = quick_api_dialog_base.py
```
##### `pyproject.toml`
```ini
[tool.black]
line-length = 79
exclude = '''
/(
    \.git
  | \.venv
  | quick_api_dialog_base.py
  | dist
)/
'''
```

#### pre-commit

Your IDE likely already flags certain style or best practice violations. Linters are supposed to make sure that you don't _commit_ any code not following the guidelines. Hence it's most useful to add linter checks as a [`pre-commit` hook](https://towardsdatascience.com/getting-started-with-python-pre-commit-hooks-28be2b2d09d5), where a small script is registered with your local `.git` repository and runs _before_ every commit. And of course there's a convenient package for this as well: [`pre-commit`](https://pre-commit.com). This will set you up:

1. `pip install pre-commit`
2. Add a `.pre-commit-config.yaml` to your project at the top level with e.g.:
```yaml
repos:
- repo: https://github.com/ambv/black
  rev: stable
  hooks:
  - id: black
    language_version: python3.9
- repo: https://gitlab.com/pycqa/flake8
  rev: 3.8.4  # pick a git hash / tag to point to
  hooks:
  - id: flake8
```
3. Install the commit hook: `pre-commit install`

Now the `flake8` and `black` checks will run every time you commit to the repository. If the check fails you won't be able to commit. So it's really important you configure the tools in a way that it only captures stuff you want to comply with (e.g. `E722`, I sometimes like using a bare `except`).

## 7 - Restructure the plugin

Finally we got to the stage where we'll refactor the current plugin and apply some of the best practices we've been describing.

It hardly makes sense to discuss every changed line, so I'll keep it rather abstract and point out a few thought processes behind the new layout. Best you follow along looking at the new plugin code from the [repository](https://github.com/gis-ops/tutorials/tree/master/qgis/examples/quick_api_interactive_proper).

#### Strip `quick_api.py`

We start off by stripping down QGIS' entrypoint to our plugin, i.e. `quick_api.py`, to the most essential information. This is the class that QGIS loads when you're plugin is activated (from the `__init__.py`'s `classFactory` method) and here you only need to tell QGIS what needs to be done to load the plugin:
- register the relevant `QAction`(s) to QGIS toolbar(s)/menu(s), so the plugin's dialogs can be started
- register a callback to the `QAction`(s) so QGIS knows what to do when those toolbar buttons or menu entries are clicked

Also we get rid of most of the irrelevant (in this context) boilerplate code from the initial `Plugin Builder 3` setup.

In the end you'll have a very slim `run()` callback which does nothing else than opening the dialog. All other logic moved into the dialog class.

#### Extend the responsibility of the main plugin dialog

The `quick_api_dialog.py` moved to `gui/`, still holds the main plugin dialog, but also contains the logical flow what happens once OK is clicked. Because this is the place it belongs: you just separated the concerns of the QGIS main app (simply (un)-registering your plugin) from the actual plugin dialog & functionality.

The first thing to note: we compiled the `.ui` file to a `.py` file which we import from the `ui/` package and use as a base class for our dialog. As discussed in [chapter 3](#user-content-3-compile-your-ui-files), this allows us to inspect dialog objects in our IDE. We could delete the `FORM_CLASS` statement, but we keep it in there for now.

Generally you register all signal/slot callback in the dialog's `__init__()` function and set up all other things which need a one-time setup (setting icons, UI element defaults etc).

You'll also notice that our main callback (invoked when OK is clicked) is slimmer. A lot of the business logic is placed in other modules and we're only left with the main flow and GUI-related stuff.

#### Breaking out request logic

The main logic I wanted to outsource is the way we request reverse geocoding from Nominatim. For a few reasons:

- have a class encapsulating the requesting logic, so it'll be easier to test & maintain
- make it easier to support other geocoders
- shorten the main plugin flow in `quick_api_dialog.py`

If you look at the code in `core/query.py`, it's very easy to see what needs to be provided to have a working geocoder in the context of this plugin: get the reverse geocoded point, a bbox for zooming, attributes for the resulting layer, a HTTP status code and an error message if there was one.

So if you'd want to change the geocoder to e.g. [OpenCage Geocoder](https://opencagedata.com/), you could do so by only changing the bodies of these methods and without touching anything in the main dialog `quick_api_dialog.py`.

You could even define an abstract base class which defines abstract methods which **need to be implemented** by any inheriting class. Then `Nominatim()` and other geocoder classes could sub-class the base class and implement their own logic.

That's a fairly object-oriented way and unfortunately Python is not perfectly well suited to enforce some object-oriented programming paradigms, at least out-of-the-box. However, it's possible, and separation of concerns and single responsibility for classes is very important for maintainability, extensibility, testability and ease of on-boarding new developers.

## Next steps

Our next tutorial in this series will be all about setting up automated tests for QGIS plugins, an often overlooked part of plugin development. We'll briefly go over important testing concepts (unit & e2e) and show you how to implement them with the example of this plugin. Additionally we'll showcase an example configuration for Github Actions to run your new test suite on every push & pull request. Try it out: https://gis-ops.com/qgis-3-plugin-tutorial-geocoding-with-nominatim-part-4/.
