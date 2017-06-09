import bpy
import bmesh
from bpy.props import *
from mathutils import Vector

# #####################################################
# ViSP Property Panel
# #####################################################

def update_after_enum(self, context):
    print('self.vp_model_types ---->', self.vp_model_types)

class IgnitProperties(bpy.types.PropertyGroup):
    vp_model_types = bpy.props.EnumProperty(
        name = "Type",
        description = "Model export types",
        items = [
            ("3D Faces" , "3D Faces" , "Export as 3d points"),
            ("3D Lines", "3D Lines", "Export as 3d lines"),
            ("3D Cylinders", "3D Cylinders", "Export as 3d cylinders"),
            ("3D Circles", "3D Circles", "Export as 3d circles")],
        update=update_after_enum
        )

    vp_heirarchy_export = BoolProperty(
        name = "Heirarchy Export", 
        description = "True or False?")

    vp_obj_Point1 = FloatVectorProperty(name = "Point 1 coordinate", description = "Point 1 coordinate", size=3, default=[0.00,0.00,0.00])
    vp_obj_Point2 = FloatVectorProperty(name = "Point 2 coordinate", description = "Point 2 coordinate", size=3, default=[0.00,0.00,0.00])
    vp_obj_Point3 = FloatVectorProperty(name = "Point 3 coordinate", description = "Point 3 coordinate", size=3, default=[0.00,0.00,0.00])

    vp_radius = FloatProperty(name = "", default = 0,description = "Set radius")

class UIPanel(bpy.types.Panel):
    bl_label = "ViSP CAD Properites Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def __init__(self):
        self._ob_select = None

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column()

        if not len(context.selected_objects):
            col.label("Select Object(s) in scene to add properties")

        else:
            self._ob_select = context.selected_objects[0]
            try:
                self._ob_select["vp_model_types"]
            except:
                col.label("Add new property")
                col.operator("my.button", text="+ New").number=5

            else:
                col.operator("refresh.button", text="load previous property") # Load prev. set properties. Button click required to write to panel
                col.prop(scn.ignit_panel, "vp_model_types", expand=False)
                col1 = col.column()
                col1.enabled = False

                if scn.ignit_panel.vp_model_types in ["3D Cylinders","3D Circles"]:
                    if context.active_object.mode == 'EDIT': # enable only in edit mode
                        col1.enabled = True
                    else:
                        col.label("Switch to EDIT MODE to set radius and coordinates")

                    col1.prop(scn.ignit_panel, "vp_obj_Point1")
                    col1.operator("my.button", text="Get Point 1").number=1
                    col1.prop(scn.ignit_panel, "vp_obj_Point2")
                    col1.operator("my.button", text="Get Point 2").number=2
                    if scn.ignit_panel.vp_model_types == "3D Circles":
                        col1.prop(scn.ignit_panel, "vp_obj_Point3")
                        col1.operator("my.button", text="Get Point 3").number=3

                    row = col1.row()
                    row.operator("my.button", text="Calculate Radius").number=4
                    row.prop(scn.ignit_panel, "vp_radius")

                col.label(" ")
                layout.operator("model_types.selection")
 
# #####################################
# BUTTON CALLS
# #####################################

class OBJECT_OT_AddPropsButton(bpy.types.Operator):
    bl_idname = "model_types.selection"
    bl_label = "Add Properites"

    def execute(self, context):
        scn = context.scene
        idx = scn.custom_circle_index
        try:
            item = scn.custom_circle[idx]
        except IndexError:
            pass

        for ob in context.selected_objects:
            ob["vp_model_types"] = scn.ignit_panel.vp_model_types

            if scn.ignit_panel.vp_model_types in ["3D Cylinders","3D Circles"]:
                ob["vp_obj_Point1"] = scn.ignit_panel.vp_obj_Point1
                ob["vp_obj_Point2"] = scn.ignit_panel.vp_obj_Point2
                if scn.ignit_panel.vp_model_types == "3D Circles":
                    ob["vp_obj_Point3"] = scn.ignit_panel.vp_obj_Point3
                    item = scn.custom_circle.add()
                    item.id = len(scn.custom_circle)
                    item.name = ob.name
                    scn.custom_circle_index = (len(scn.custom_circle)-1)
                else:
                    item = scn.custom_cylinder.add()
                    item.id = len(scn.custom_cylinder)
                    item.name = ob.name
                    scn.custom_cylinder_index = (len(scn.custom_cylinder)-1)
                ob["vp_radius"] = scn.ignit_panel.vp_radius
                # info = '%s added to list' % (item.name)
                # self.report({'INFO'}, info)

        return{'FINISHED'}

class OBJECT_OT_RefreshButton(bpy.types.Operator):
    bl_idname = "refresh.button"
    bl_label = "Button"

    def __init__(self):
        self._ob_select = None

    def execute(self, context):
        scn = context.scene
        self._ob_select = context.selected_objects[0]
        scn.ignit_panel.vp_model_types = self._ob_select["vp_model_types"]
        if self._ob_select["vp_model_types"] in ["3D Cylinders","3D Circles"]:
            try:
                self._ob_select["vp_obj_Point1"]
            except:
                pass
            else:
                scn.ignit_panel.vp_obj_Point1 = self._ob_select["vp_obj_Point1"]
                scn.ignit_panel.vp_obj_Point2 = self._ob_select["vp_obj_Point2"]
                if self._ob_select["vp_model_types"] == "3D Circles":
                    scn.ignit_panel.vp_obj_Point3 = self._ob_select["vp_obj_Point3"]

                scn.ignit_panel.vp_radius = self._ob_select["vp_radius"]

        return{'FINISHED'}

class OBJECT_OT_Button(bpy.types.Operator):
    bl_idname = "my.button"
    bl_label = "Button"
    number = bpy.props.IntProperty()

    def __init__(self):
        self._ob_select = None

    # @classmethod
    # def poll(cls, context):
    #     return (True)

    def execute(self, context):
        scn = context.scene

        if self.number == 5:
            self._ob_select = context.selected_objects[0]
            self._ob_select["vp_model_types"] = "3D Faces"

        else:
            for ob in context.selected_objects:
                if scn.ignit_panel.vp_model_types in ["3D Cylinders","3D Circles"]:
                    ob_edit = context.edit_object # check if in edit mode
                    me = ob_edit.data
                    bm = bmesh.from_edit_mesh(me)
                    selected = [v for v in bm.verts if v.select]
                    # Calculate Radius
                    if self.number == 4:    
                        vsum = Vector()
                        for v in selected:
                            vsum += v.co
                        midPoint = vsum/len(selected)
                        distances = [(v.co-midPoint).length for v in selected]
                        radius = sum(distances)/len(distances)
                        ob["vp_radius"] = radius
                        scn.ignit_panel.vp_radius = radius
                    else: #Get coordinates of selected vertex
                        v = selected[0]
                        if self.number == 1:
                            scn.ignit_panel.vp_obj_Point1 = v.co
                        elif self.number == 2:
                            scn.ignit_panel.vp_obj_Point2 = v.co
                        elif self.number == 3:
                            scn.ignit_panel.vp_obj_Point3 = v.co
        return{'FINISHED'}

classes = (
    IgnitProperties,
    UIPanel,
    OBJECT_OT_Button,
    OBJECT_OT_RefreshButton,
    OBJECT_OT_AddPropsButton
)

if __name__ == "__main__":
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
