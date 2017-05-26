import bpy
import sys
import os

print("BLENDER VERSION : " + bpy.app.version_string)
ADDON_PATH = (bpy.utils.user_resource('SCRIPTS', "addons"))
print(ADDON_PATH)

os.system("cp -r ../blenderVISP " + ADDON_PATH)
# bpy.utils.script_paths()