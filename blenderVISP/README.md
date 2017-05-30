# Blender Export Addon for ViSP CAD file (.cao)

**Installation**:
  
  1) Run `blender --background --python setup.py` in project directory.
  2) Launch Blender and open User Preferences (**Ctrl+Atl+U**)
  3) Search for "visp" in Addons section and enable the plugin called "Export: ViSP CAO".

**Usage**

  1) In the **ViSP CAD Properties Panel** under the Tools menu of blender, the user can set the model export type (default is 3D Points), create heirarchial models and also enter point coordinates for cylinder and circle exports.
  2) To set these properties for model(s), select the model(s) and hit `Set Properties`.
  3) If `Type == "3D Cylinders" || "3D Circles"`, then switch to `Edit Mode` and hit `Calculate Radius`. Enter the necessary points coordinates. These coordinates can be found by right clicking on vertex and then hitting `N`. 
  4) To export the objects in the scene in a heirarchial manner (modular files), check the `Heirarchy button`.
  5) Go to `File > Export > ViSP .cao` to export to .cao format. 
