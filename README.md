# cao-utils
Convert .obj/.blend files to .cao

**Usage**:

For OBJ to CAO

      `python convert_obj_to_cao.py -i cubesat1b.obj -o new_cubesat1b.cao -t p` *(for 3d points)*
  
     `python convert_obj_to_cao.py -i cubesat1b.obj -o new_cubesat1b.cao -t l` *(for 3d lines)*
  
  For BLEND to CAO
  
      `blender test.blend --background --python convert_blend_to_cao.py -- new_cubesat1b.cao p` *(for 3d points)*
      
      `blender test.blend --background --python convert_blend_to_cao.py -- new_cubesat1b.cao l` *(for 3d lines)*
      
