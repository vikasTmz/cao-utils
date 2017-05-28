#----------------------------------------------------------
# File scene_props.py
#----------------------------------------------------------
import bpy
from bpy.props import *
 
#
#    Store properties in the active scene
#
def initSceneProperties(scn):
    bpy.types.Scene.MyInt = IntProperty(
        name = "Integer", 
        description = "Enter an integer")
    scn['MyInt'] = 17
 
    bpy.types.Scene.MyFloat = FloatProperty(
        name = "Float", 
        description = "Enter a float",
        default = 33.33,
        min = -100,
        max = 100)
 
    bpy.types.Scene.MyBool = BoolProperty(
        name = "Boolean", 
        description = "True or False?")
    scn['MyBool'] = True
 
    bpy.types.Scene.MyEnum = EnumProperty(
        items = [('Eine', 'Un', 'One'), 
                 ('Zwei', 'Deux', 'Two'),
                 ('Drei', 'Trois', 'Three')],
        name = "Ziffer")
    scn['MyEnum'] = 2
 
    bpy.types.Scene.MyString = StringProperty(
        name = "String")
    scn['MyString'] = "Lorem ipsum dolor sit amet"
    return
 
initSceneProperties(bpy.context.scene)
 
#
#    Menu in UI region
#
class UIPanel(bpy.types.Panel):
    bl_label = "Property panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.prop(scn, 'MyInt', icon='BLENDER', toggle=True)
        layout.prop(scn, 'MyFloat')
        layout.prop(scn, 'MyBool')
        layout.prop(scn, 'MyEnum')
        layout.prop(scn, 'MyString')
        layout.operator("idname_must.be_all_lowercase_and_contain_one_dot")
 
#
#    The button prints the values of the properites in the console.
#
 
class OBJECT_OT_PrintPropsButton(bpy.types.Operator):
    bl_idname = "idname_must.be_all_lowercase_and_contain_one_dot"
    bl_label = "Print props"
 
    def execute(self, context):
        scn = context.scene
        printProp("Int:    ", 'MyInt', scn)
        printProp("Float:  ", 'MyFloat', scn)
        printProp("Bool:   ", 'MyBool', scn)
        printProp("Enum:   ", 'MyEnum', scn)
        printProp("String: ", 'MyString', scn)
        return{'FINISHED'}    
 
def printProp(label, key, scn):
    try:
        val = scn[key]
    except:
        val = 'Undefined'
    print("%s %s" % (key, val))
 
#    Registration
bpy.utils.register_module(__name__)








# theFloat = 9.8765
# theBool = False
# theString = "Lorem ..."
# theEnum = 'one'
 
# class DialogOperator(bpy.types.Operator):
#     bl_idname = "object.dialog_operator"
#     bl_label = "Simple Dialog Operator"
 
#     my_float = FloatProperty(name="Some Floating Point", 
#         min=0.0, max=100.0)
#     my_bool = BoolProperty(name="Toggle Option")
#     my_string = StringProperty(name="String Value")
#     my_enum = EnumProperty(name="Enum value",
#         items = [('one', 'eins', 'un'), 
#                  ('two', 'zwei', 'deux'),
#                  ('three', 'drei', 'trois')])
 
#     def execute(self, context):
#         message = "%.3f, %d, '%s' %s" % (self.my_float, 
#             self.my_bool, self.my_string, self.my_enum)
#         self.report({'INFO'}, message)
#         print(message)
#         return {'FINISHED'}
 
#     def invoke(self, context, event):
#         global theFloat, theBool, theString, theEnum
#         self.my_float = theFloat
#         self.my_bool = theBool
#         self.my_string = theString
#         self.my_enum = theEnum
#         return context.window_manager.invoke_props_dialog(self)

# bpy.types.Scene.photoPath = StringProperty(
#     name="Path to file",
#     subtype="DIR_PATH",
#     description="Path to the folder containing the .cao file"
#     )


# class OBJECT_PT_Panel(bpy.types.Panel):
#     bl_idname = "mesh.point_cloud_add"
#     bl_label = "Add Point Cloud"
#     bl_description = "Generate a point cloud from photographs"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "TOOLS"

#     def draw(self, context):
#         layout = self.layout
#         global theFloat, theBool, theString, theEnum
#         theFloat = 12.345
#         theBool = True
#         theString = "Code snippets"
#         theEnum = 'two'
#         layout.operator("object.dialog_operator")
#         # layout.prop(context.scene, "photoPath")
#         # layout.label(context.scene.currentStatus)
#         layout.label("Lorem Ips....")
