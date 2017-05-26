import bpy
import sys
import os

argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"

obj_out = argv[0]
method = argv[1]


bpy.ops.export_scene.obj(filepath="temp.obj", axis_forward='-Z', axis_up='Y')

os.system(" python convert_obj_to_cao.py -i temp.obj -o " + obj_out + " -t " + method)


# for ob in bpy.data.objects:
#     if ob.name == "Cylinder 1.001": bpy.data.window_managers["WinMan"].(type) = "3D Cylinders"
#     	print (ob.name,ob.dimensions,ob.location,ob.rotation_euler.z)

# ob = bpy.data.objects["Cube"]
