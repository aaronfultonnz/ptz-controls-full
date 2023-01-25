import os.path
import plistlib

#
# Example settings file for dmgbuild
#

# Use like this: dmgbuild -s settings.py "Test Volume" test.dmg

# You can actually use this file for your own application (not just TextEdit)
# by doing e.g.
#
#   dmgbuild -s settings.py -D app=/path/to/My.app "My Application" MyApp.dmg

# .. Useful stuff ..............................................................

application = defines.get("app", "dist/CameraController.app")  # noqa: F821
appname = os.path.basename(application)


def icon_from_app(app_path):
    plist_path = os.path.join(app_path, "Contents", "Info.plist")
    with open(plist_path, "rb") as f:
        plist = plistlib.load(f)
    icon_name = plist["CFBundleIconFile"]
    icon_root, icon_ext = os.path.splitext(icon_name)
    if not icon_ext:
        icon_ext = ".icns"
    icon_name = icon_root + icon_ext
    return os.path.join(app_path, "Contents", "Resources", icon_name)


format = defines.get("format", "UDBZ")  # noqa: F821
size = defines.get("size", None)  # noqa: F821
files = [application]
symlinks = {"Applications": "/Applications"}
badge_icon = icon_from_app(application)
icon_locations = {appname: (140, 120), "Applications": (500, 120)}
