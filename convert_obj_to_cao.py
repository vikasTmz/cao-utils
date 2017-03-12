"""
Notes:
    - flags
        -i infile.obj           input OBJ file
        -o outfile.cao           output CAO file
        -t p/l                type = points/lines
------
Author
------
Vikas Thamizharasan
"""

import sys
import fileinput
import operator
import random
import os.path
import getopt
import struct
import math
import glob

# #####################################################
# Configuration
# #####################################################

SCALE = 1.0


# #####################################################
# Templates
# #####################################################
TEMPLATE_CAO_FILE = u"""\
{
V1,
#%(objectName)s,
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


# #####################################################
# Utils
# #####################################################
def file_exists(filename):
    """Return true if file exists and is accessible for reading.
    @rtype: boolean
    """

    try:
        f = open(filename, 'r')
        f.close()
        return True
    except IOError:
        return False


def get_name(fname):
    return os.path.splitext(os.path.basename(fname))[0]

def generate_vertices(v):
    return v #TEMPLATE_VERTEX % (v[0], v[1], v[2])

def generate_lines(l):
    return TEMPLATE_LINES % (l[0] ,l[1])    

def generate_facelines(fl):
    return " ".join(map(str,[x for x in fl]))

def generate_faces(v):
    return str(len(v.split(" "))) + " " +  " ".join(map(str,[x-1 for x in map(int,[x.split("/")[0] for x in v.split(" ")])]))
    
# #####################################################
# OBJ parser
# #####################################################


def parse_vertex(text):
    v = 0
    t = 0
    n = 0

    chunks = text.split("/")

    v = int(chunks[0])
    if len(chunks) > 1:
        if chunks[1]:
            t = int(chunks[1])
    if len(chunks) > 2:
        if chunks[2]:
            n = int(chunks[2])

    return { 'v':v, 't':t, 'n':n }

def parse_obj(fname, outfile, method):
    """Parse OBJ file.
    """
    vertices = []
    normals = []
    uvs = []

    faces = []
    lines = []
    facelines = []
    materials = {}
    material = ""
    mcounter = 0
    mcurrent = 0

    mtllib = ""

    # current face state
    group = 0
    object = 0
    smooth = 0
    previous_line = ""
    for line in fileinput.input(fname):
        line = previous_line + line
        if line[-2:-1] == '\\':
            previous_line = line[:-2]
            continue
        previous_line = ""

        chunks = line.split(None, 1)
        if len(chunks) > 0:

            if len(chunks) > 1:
                chunks[1] = chunks[1].strip()

            # Group
            if chunks[0] == "g" and len(chunks) == 2:
                group = chunks[1]

            # Object
            if chunks[0] == "o" and len(chunks) == 2:
                object = chunks[1]

            # Materials definition
            if chunks[0] == "mtllib" and len(chunks) == 2:
                mtllib = chunks[1]

            # Material
            if chunks[0] == "usemtl":
                if len(chunks) > 1:
                    material = chunks[1]
                else:
                    material = ""
                if not material in materials:
                    mcurrent = mcounter
                    materials[material] = mcounter
                    mcounter += 1
                else:
                    mcurrent = materials[material]

            # Split the remaining parameters.
            if len(chunks) > 1:
                chunksvalue = chunks[1];
                chunks = [chunks[0]] + chunks[1].split()

            # Vertices as (x,y,z) coordinates
            if chunks[0] == "v" and len(chunks) == 4:
                x = float(chunks[1])
                y = float(chunks[2])
                z = float(chunks[3])
                vertices.append(chunksvalue)

            # Normals in (x,y,z) form; normals might not be unit
            if chunks[0] == "vn" and len(chunks) == 4:
                x = float(chunks[1])
                y = float(chunks[2])
                z = float(chunks[3])
                normals.append([x,y,z])

            # Texture coordinates in (u,v[,w]) coordinates, w is optional
            if chunks[0] == "vt" and len(chunks) >= 3:
                u = float(chunks[1])
                v = float(chunks[2])
                w = 0
                if len(chunks)>3:
                    w = float(chunks[3])
                uvs.append([u,v,w])

            # Face
            if chunks[0] == "f" and len(chunks) >= 4:
                faces.append(chunksvalue)
                m = map(int,[x.split("/")[0] for x in chunksvalue.split(" ")]);
                initialen = len(lines)
                for i in range(0,len(m)-1):
                    lines.append([m[i]-1,m[i+1]-1])
                lines.append([m[len(m)-1]-1,m[0]-1])

                facelines.append([len(lines)-initialen,list(range(initialen,len(lines)))])
            # Smooth shading
            if chunks[0] == "s" and len(chunks) == 2:
                smooth = chunks[1]

    if method == "p":
        nlines = nfacelines = 0
        npoints = len(vertices)
        nfacepoints = len(faces)
        lines = facelines = []

    elif method == "l":
        nfacepoints = 0
        nlines = len(lines)
        nfacelines = len(facelines)
        npoints = len(vertices)
        faces = []

    text = TEMPLATE_CAO_FILE % {
        "objectName" : outfile.split(".")[0],
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

    out = open(outfile, "a")
    out.write(text)
    out.close()
    os.system("sed -i 's/,//g' " + outfile)
    os.system("sed -i 's/\(\[\|\]\)//g' " + outfile)
    os.system("sed -i 's/{//g' " + outfile)
    os.system("sed -i 's/}//g' " + outfile)
    os.system("sed -i '/^$/d' " + outfile)
    # return faces, vertices, uvs, normals, materials, mtllib


# #############################################################################
# Helpers
# #############################################################################
def usage():
    print "Usage: %s -i filename.obj -o filename.cao -t p/l [3d points or 3d lines]" % os.path.basename(sys.argv[0])

# #####################################################
# Main
# #####################################################
if __name__ == "__main__":

    # get parameters from the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:i:o:t:l", ["help", "input=", "output=", "type=","lines="])

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    method = infile = outfile = ""

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()

        elif o in ("-i", "--input"):
            infile = a

        elif o in ("-o", "--output"):
            outfile = a

        elif o in ("-t", "--type"):
            method = a

    if infile == "" or outfile == "":
        usage()
        sys.exit(2)

    if not file_exists(infile):
        print "Couldn't find [%s]" % infile

    else:
        out = open(outfile, "w")
        out.write("")
        out.close()
        print "Converting [%s] into [%s] ..." % (infile, outfile)
        parse_obj(infile, outfile, method)
 