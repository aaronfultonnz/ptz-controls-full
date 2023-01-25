"""
This is an example of py2app setup.py script for freezing your application

Usage:
    python setup.py py2app
"""

import os
from setuptools import setup


def tree(src):
    return [(root, map(lambda f: os.path.join(root, f), files))
            for (root, dirs, files) in os.walk(os.path.normpath(src))]


ENTRY_POINT = ['controls.py']
DATA_FILES = tree('assets') + tree('wsdl')
OPTIONS = {'argv_emulation': False,
           'strip': True,
           'iconfile': 'assets/AppIcon.icns',
           'packages': ['charset_normalizer'],
           'includes': [],
           'plist': {
               'CFBundleDisplayName': "Camera Controller",
               'CFBundleGetInfoString': "Control PTZ cameras",
               'CFBundleIdentifier': "com.webtolife.osx.cameracontroller",
               'CFBundleVersion': "1.0.1",
               'CFBundleShortVersionString': "1.0.1",
               'NSHumanReadableCopyright': u"Copyright © 2023, webToLife Software Ltd, All Rights Reserved"
           }
           }

setup(
    name="CameraController",
    app=ENTRY_POINT,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
