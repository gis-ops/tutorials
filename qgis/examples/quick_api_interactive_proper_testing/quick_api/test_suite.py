# coding=utf-8
"""
Test Suite.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import sys
import unittest
import qgis  # noqa: F401

import coverage
from osgeo import gdal

__author__ = "Alessandro Pasotti"
__revision__ = "$Format:%H$"
__date__ = "30/04/2018"
__copyright__ = "Copyright 2018, North Road"


def _run_tests(test_suite, package_name):
    """Core function to test a test suite."""
    count = test_suite.countTestCases()
    print("########")
    print("%s tests has been discovered in %s" % (count, package_name))
    print("Python GDAL : %s" % gdal.VersionInfo("VERSION_NUM"))
    print("########")

    cov = coverage.Coverage(
        source=["/tests_directory/quick_api"],
        omit=[
            "*/quick_api_dialog_base.py",
            "*/quick_api.py",
            "*/__init__.py",
            "*/tests/*",
            "*/test_suite.py",
        ],
    )
    cov.start()

    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)

    cov.stop()
    cov.save()
    cov.report(file=sys.stdout)


def test_package(package="quick_api"):
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


if __name__ == "__main__":
    test_package()
