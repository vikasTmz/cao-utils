
bl_info = {
    "name": "ViSP CAO",
    "author": "Vikas Thamizharasan",
    "blender": (2, 6, 9),
    "location": "File > Export",
    "description": "Export CAO",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Export"}


if "bpy" in locals():
    import imp
    if "export_cao" in locals():
        imp.reload(export_cao)

import bpy
from bpy.props import *
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )

# #####################################################
# UI Panel
# #####################################################

def initSceneProperties(scn):
    bpy.types.Scene.MyInt = IntProperty(
        name = "Integer", 
        description = "Enter an integer")
 
    bpy.types.Scene.MyFloat = FloatProperty(
        name = "Float", 
        description = "Enter a float",
        default = 33.33,
        min = -100,
        max = 100)
 
    bpy.types.Scene.MyBool = BoolProperty(
        name = "Boolean", 
        description = "True or False?")
 
    bpy.types.Scene.MyEnum = EnumProperty(
        items = [('Eine', 'Un', 'One'), 
                 ('Zwei', 'Deux', 'Two'),
                 ('Drei', 'Trois', 'Three')],
        name = "Ziffer")
 
    bpy.types.Scene.MyString = StringProperty(
        name = "String")
    return
 
class IgnitProperties(bpy.types.PropertyGroup):
    model_types = bpy.props.EnumProperty(
        name = "Model export types",
        description = "Model export types",
        items = [
            ("3D Points" , "3D Points" , "Description..."),
            ("3D Lines", "3D Lines", "other description"),
            ("3D Cylinders", "3D Cylinders", "Some other description")])

class UIPanel(bpy.types.Panel):
    bl_label = "ViSP CAD Properites Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        row = layout.row()
        row.prop(scn.ignit_panel, "model_types", expand=False)
        # layout.prop(scn, 'MyInt', icon='BLENDER', toggle=True)
        layout.operator("model_types.selection")
 
# #####################################################
# Button to Set Properites
# #####################################################

MType = "3D Points" 

class OBJECT_OT_PrintPropsButton(bpy.types.Operator):
    bl_idname = "model_types.selection"
    bl_label = "Set Properites"
 
    def execute(self, context):
        global MType
        scn = context.scene
        MType = scn.ignit_panel.model_types
        # print(scn.ignit_panel.model_types)
        return{'FINISHED'}

# #####################################################
# ExportCAO
# #####################################################

class ExportCAO(bpy.types.Operator, ExportHelper):

    bl_idname = "export_scene.cao"
    bl_label = 'Export .cao'
    bl_options = {'PRESET'}

    filename_ext = ".cao"
    filter_glob = StringProperty(
            default="*.cao",
            options={'HIDDEN'},
            )

    # context group
    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    # object group
    use_mesh_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Apply modifiers (preview resolution)",
            default=True,
            )

    # extra data group
    use_edges = BoolProperty(
            name="Include Edges",
            description="",
            default=True,
            )

    use_normals = BoolProperty(
            name="Include Normals",
            description="",
            default=False,
            )

    use_triangles = BoolProperty(
            name="Triangulate Faces",
            description="Convert all faces to triangles",
            default=False,
            )

    axis_forward = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='-Z',
            )
    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Y',
            )
    global_scale = FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            default=1.0,
            )


    check_extension = True

    def execute(self, context):
        from . import export_cao

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
        keywords["global_matrix"] = global_matrix

        return export_cao.save(self, context, MType, **keywords)

def menu_func_export(self, context):
    self.layout.operator(ExportCAO.bl_idname, text="ViSP .cao")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.Scene.ignit_panel = bpy.props.PointerProperty(type=IgnitProperties)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    del bpy.types.Scene.ignit_panel

if __name__ == "__main__":
    register()
