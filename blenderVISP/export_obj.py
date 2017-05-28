# <pep8 compliant>

import os
import time

import bpy
import mathutils
import bpy_extras.io_utils


# #####################################################
# Templates
# #####################################################

TEMPLATE_CAO_FILE = u"""\
{
V1,
%(nPoints)d,   
# 3D points,
[%(points)s],
# 3D lines,
%(nLines)d,
[%(lines)s],
# Faces from 3D lines,
%(nFacelines)d,
[%(facelines)s],
# Faces from 3D points,
%(nFacepoints)d,
[%(facepoints)s],
# 3D cylinders,
%(nCylinder)d,
[%(cylinders)s],
# 3D circles,
%(nCircles)d,
[%(circles)s]
}
"""

TEMPLATE_LINES = "%d ,%d"

TEMPLATE_VERTEX = "%f %f %f"

# #####################################################
# Utils
# #####################################################

def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

def generate_vertices(v):
    return  TEMPLATE_VERTEX % (v[0], v[1], v[2])

def generate_lines(l):
    return TEMPLATE_LINES % (l[0] ,l[1])    

def generate_facelines(fl):
    return " ".join(map(str,[x for x in fl]))

def generate_faces(v):
    return str(len(v)) + " " + " ".join(map(str,[x-1 for x in v]))


def write_file(MODEL_TYPE, filepath, objects, scene,
               EXPORT_TRI=False,
               EXPORT_EDGES=False,
               EXPORT_NORMALS=False,
               EXPORT_APPLY_MODIFIERS=True,
               EXPORT_GLOBAL_MATRIX=None,
               ):

    if EXPORT_GLOBAL_MATRIX is None:
        EXPORT_GLOBAL_MATRIX = mathutils.Matrix()

    print('CAO Export path: %r' % filepath)

    time1 = time.time()

    file = open(filepath, "w", encoding="utf8", newline="\n")
    fw = file.write

    # Write Header
    fw('# Blender v%s CAO File\n' % (bpy.app.version_string))

    # Initialize totals, these are updated each object
    totverts = 1

    face_vert_index = 1

    copy_set = set()

    vertices = []
    faces = []
    lines = []
    facelines = []

    # Get all meshes
    for ob_main in objects:

        # ignore dupli children
        if ob_main.parent and ob_main.parent.dupli_type in {'VERTS', 'FACES'}:

            print(ob_main.name, 'is a dupli child - ignoring')
            continue

        obs = []
        if ob_main.dupli_type != 'NONE':

            print('creating dupli_list on', ob_main.name)
            ob_main.dupli_list_create(scene)
            obs = [(dob.object, dob.matrix) for dob in ob_main.dupli_list]

            print(ob_main.name, 'has', len(obs), 'dupli children')
        else:
            obs = [(ob_main, ob_main.matrix_world)]

        for ob, ob_mat in obs:

            try:
                me = ob.to_mesh(scene, EXPORT_APPLY_MODIFIERS, 'PREVIEW', calc_tessface=False)
            except RuntimeError:
                me = None

            if me is None:
                continue

            me.transform(EXPORT_GLOBAL_MATRIX * ob_mat)

            if EXPORT_TRI:
                # _must_ do this first since it re-allocs arrays
                mesh_triangulate(me)

            me_verts = me.vertices[:]

            # Make our own list so it can be sorted to reduce context switching
            face_index_pairs = [(face, index) for index, face in enumerate(me.polygons)]

            if EXPORT_EDGES:
                edges = me.edges
            else:
                edges = []

            if not (len(face_index_pairs) + len(edges) + len(me.vertices)):  # Make sure there is somthing to write
                # clean up
                bpy.data.meshes.remove(me)
                continue  # dont bother with this mesh.

            smooth_groups, smooth_groups_tot = (), 0

            # no materials
            if smooth_groups:
                sort_func = lambda a: smooth_groups[a[1] if a[0].use_smooth else False]
            else:
                sort_func = lambda a: a[0].use_smooth

            face_index_pairs.sort(key=sort_func)
            del sort_func

            # fw('# %s\n' % (ob_main.name))

            # Vert
            for v in me_verts:
                # fw('v %.6f %.6f %.6f\n' % v.co[:])
                vertices.append(v.co[:])

            for f, f_index in face_index_pairs:

                #f_v = [(vi, me_verts[v_idx]) for vi, v_idx in enumerate(f.vertices)]
                f_v = [(vi, me_verts[v_idx], l_idx) for vi, (v_idx, l_idx) in enumerate(zip(f.vertices, f.loop_indices))]
                tempface = []

                # fw('f')
                for vi, v, li in f_v:
                    # fw(" %d" % (totverts + v.index))
                    tempface.append(totverts + v.index)

                faces.append(tempface)
                # fw('\n')

            # Make the indices global rather then per mesh
            totverts += len(me_verts)

            # clean up
            bpy.data.meshes.remove(me)

        if ob_main.dupli_type != 'NONE':
            ob_main.dupli_list_clear()

    if MODEL_TYPE == "3D Points":
        nlines = nfacelines = 0
        npoints = len(vertices)
        nfacepoints = len(faces)
        lines = facelines = []

    elif MODEL_TYPE == "3D Lines":
        nfacepoints = 0
        nlines = len(lines)
        nfacelines = len(facelines)
        npoints = len(vertices)
        faces = []

    text = TEMPLATE_CAO_FILE % {
        "nPoints"  : npoints,
        "points" : "\n".join(generate_vertices(v) for v in vertices),
        "nLines" : nlines,
        "lines" : "\n".join(generate_lines(l) for l in lines),
        "nFacelines" : nfacelines,
        "facelines" : "\n".join(generate_facelines(fl) for fl in facelines),
        "nFacepoints" : nfacepoints,
        "facepoints" : "\n".join(generate_faces(f) for f in faces),
        "nCylinder" : 0,
        "cylinders" : "",
        "nCircles" : 0,
        "circles" : "" 
    }

    fw(text)
    file.close()

    os.system("sed -i 's/,//g' " + filepath)
    os.system("sed -i 's/\(\[\|\]\)//g' " + filepath)
    os.system("sed -i 's/{//g' " + filepath)
    os.system("sed -i 's/}//g' " + filepath)
    os.system("sed -i '/^$/d' " + filepath)
    # copy all collected files.
    bpy_extras.io_utils.path_reference_copy(copy_set)

    print("OBJ Export time: %.2f" % (time.time() - time1))


def _write(context, MODEL_TYPE, filepath,
              EXPORT_TRI,  # ok
              EXPORT_EDGES,
              EXPORT_NORMALS,  # not yet
              EXPORT_APPLY_MODIFIERS,  # ok
              EXPORT_SEL_ONLY,  # ok
              EXPORT_GLOBAL_MATRIX,
              ):  # Not used

    base_name, ext = os.path.splitext(filepath)
    context_name = [base_name, '', '', ext]  # Base name, scene name, frame number, extension
    scene = context.scene

    # Exit edit mode before exporting, so current object states are exported properly.
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    orig_frame = scene.frame_current
    scene_frames = [orig_frame]
    EXPORT_SEL_ONLY = True   # Hard-coded?

    # Loop through all frames in the scene and export.
    for frame in scene_frames:

        scene.frame_set(frame, 0.0)
        if EXPORT_SEL_ONLY:
            objects = context.selected_objects
        else:
            objects = scene.objects
        
        full_path = ''.join(context_name)

        # erm... bit of a problem here, this can overwrite files when exporting frames. not too bad.
        # EXPORT THE FILE.
        write_file(MODEL_TYPE, full_path, objects, scene,
                   EXPORT_TRI,
                   EXPORT_EDGES,
                   EXPORT_NORMALS,
                   EXPORT_APPLY_MODIFIERS,
                   EXPORT_GLOBAL_MATRIX,
                   )

    scene.frame_set(orig_frame, 0.0)

def save(operator, context, model_type, filepath="",
         use_triangles=False,
         use_edges=True,
         use_normals=False,
         use_mesh_modifiers=True,
         use_selection=True,
         global_matrix=None,
         ):

    _write(context, model_type, filepath,
           EXPORT_TRI=use_triangles,
           EXPORT_EDGES=use_edges,
           EXPORT_NORMALS=use_normals,
           EXPORT_APPLY_MODIFIERS=use_mesh_modifiers,
           EXPORT_SEL_ONLY=use_selection,
           EXPORT_GLOBAL_MATRIX=global_matrix,
           )

    return {'FINISHED'}
