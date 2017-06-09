import bpy
from bpy.props import IntProperty, CollectionProperty #, StringProperty 
from bpy.types import Panel, UIList


# return name of selected object
def get_activeSceneObject():
    return bpy.context.scene.objects.active.name


# ui list item actions
class Uilist_actions_circle(bpy.types.Operator):
    bl_idname = "customcircle.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", "")
            # ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.custom_circle_index

        try:
            item = scn.custom_circle[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(scn.custom_circle) - 1:
                item_next = scn.custom_circle[idx+1].name
                scn.custom_circle_index += 1
                info = 'Item %d selected' % (scn.custom_circle_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom_circle[idx-1].name
                scn.custom_circle_index -= 1
                info = 'Item %d selected' % (scn.custom_circle_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item %s removed from list' % (scn.custom_circle[scn.custom_circle_index].name)
                scn.custom_circle_index -= 1
                self.report({'INFO'}, info)
                scn.custom_circle.remove(idx)

        return {"FINISHED"}

# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

# custom list
class UL_items_circle(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.label("Index: %d" % (index))
        split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass   

# draw the panel
class UIListPanelExample_circle(Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = 'OBJECT_PT_my_panel_circle'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "3D Circles"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("UL_items_circle", "", scn, "custom_circle", scn, "custom_circle_index", rows=rows)

        col = row.column(align=True)
        col.operator("customcircle.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("customcircle.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("customcircle.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        row = layout.row()
        col = row.column(align=True)
        col.operator("customcircle.select_item", icon="UV_SYNC_SELECT")
        col.operator("customcircle.clear_list", icon="X")

# select button
class Uilist_selectAllItems_circle(bpy.types.Operator):
    bl_idname = "customcircle.select_item"
    bl_label = "Select List Item"
    bl_description = "Select Item in scene"

    def __init__(self):
        self._ob_select = None

    def execute(self, context):
        scn = context.scene
        bpy.ops.object.select_all(action='DESELECT')
        idx = scn.custom_circle_index
        try:
            item = scn.custom_circle[idx]
        except IndexError:
            pass
        else:
            self._ob_select = bpy.data.objects[scn.custom_circle[scn.custom_circle_index].name]
            self._ob_select.select = True
            scn.ignit_panel.vp_model_types = self._ob_select["vp_model_types"]

            scn.ignit_panel.vp_obj_Point1 = self._ob_select["vp_obj_Point1"]
            scn.ignit_panel.vp_obj_Point2 = self._ob_select["vp_obj_Point2"]
            scn.ignit_panel.vp_obj_Point3 = self._ob_select["vp_obj_Point3"]
            scn.ignit_panel.vp_radius = self._ob_select["vp_radius"]

        return{'FINISHED'}

# clear button
class Uilist_clearAllItems_circle(bpy.types.Operator):
    bl_idname = "customcircle.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items in the list"

    def execute(self, context):
        scn = context.scene
        lst = scn.custom_circle
        current_index = scn.custom_circle_index

        if len(lst) > 0:
             # reverse range to remove last item first
            for i in range(len(lst)-1,-1,-1):
                scn.custom_circle.remove(i)
            self.report({'INFO'}, "All items removed")

        else:
            self.report({'INFO'}, "Nothing to remove")   

        return{'FINISHED'}

# Create custom property group
class CustomProp_circle(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    id = IntProperty()

# -------------------------------------------------------------------
# register
# -------------------------------------------------------------------
classes = (
    CustomProp_circle,
    Uilist_actions_circle,
    Uilist_clearAllItems_circle,
    Uilist_selectAllItems_circle,
    UIListPanelExample_circle,
    UL_items_circle
)

if __name__ == "__main__":
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
