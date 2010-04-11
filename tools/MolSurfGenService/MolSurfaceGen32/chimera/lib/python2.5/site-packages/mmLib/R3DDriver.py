## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Viewer.py graphics driver for producing a output file
for the Raster3D ray tracer.
"""
import subprocess
import copy
import random
import math

try:
    import numpy
    try:
        from numpy.oldnumeric import linear_algebra as linalg
    except ImportError:
        from numpy.linalg import old as linalg
except ImportError:
    import NumericCompat as numpy
    from NumericCompat import linalg

import ConsoleOutput
import Constants
import Gaussian
import AtomMath

## constants
MARGIN          = 1.15
BASE_LINE_WIDTH = 0.05


class FinishMe(Exception): pass


def matrixmultiply43(M, x):
    """M is a 4x4 rotation-translation matrix, x is a 3x1 vector.  Returns
    the 3x1 vector of x transformed by M.
    """
    return numpy.array((M[0,0]*x[0] + M[0,1]*x[1] + M[0,2]*x[2] + M[0,3],
                        M[1,0]*x[0] + M[1,1]*x[1] + M[1,2]*x[2] + M[1,3],
                        M[2,0]*x[0] + M[2,1]*x[1] + M[2,2]*x[2] + M[2,3]), float)

class TeeWrite(object):
    def __init__(self, *fils):
        self.fils = fils
    def write(self, buff):
        for fil in self.fils:
            fil.write(buff)
    def close(self):
        for fil in self.fils:
            fil.close()

class Raster3DDriver(object):
    """Viewer.py graphics driver for producing a output file
    for the Raster3D ray tracer.
    """
    def __init__(self):
        self.render_program_path = "render"
        self.render_png_path     = "ray.png"
        self.render_stdin        = None
        
        self.glr_init_state()

    def glr_set_render_program_path(self, render_path):
        self.render_program_path = render_path

    def glr_set_render_stdin(self, stdin):
        self.render_stdin = stdin
        
    def glr_set_render_png_path(self, path):
        self.render_png_path  = path

    def glr_init_state(self):
        """Re-initalizes driver state variables.
        """
        self.object_list      = []
        
        self.matrix           = numpy.identity(4, float)
        self.matrix_stack     = []

        self.line_width       = 1.0 * BASE_LINE_WIDTH

        self.normal           = None
        self.normalize        = False

        self.light_two_sides  = False
        
        self.width            = 400
        self.height           = 400
        self.bg_color_rgbf    = (0.0, 0.0, 0.0)
        self.ambient_light    = 0.2
        self.specular_light   = 1.0
        
        self.material_color_r = 1.0
        self.material_color_g = 1.0
        self.material_color_b = 1.0
        self.material_alpha   = 1.0

    def glr_compile_supported(self):
        """Returns True if draw compiling is supported by the driver.
        """
        return False
        
    def glr_render_begin(
        self,
        width              = 200,
        height             = 100,
        zoom               = 50,
        near               = 0,
        far                = 0,
        bg_color_rgbf      = (0.0, 0.0, 0.0),
        ambient_light      = 0.2,
        diffuse_light      = 1.0,
        specular_light     = 1.0,
        **args):
        """Sets up lighting and OpenGL options before scene rendering.
        """
        self.glr_init_state()
        
        self.width            = width
        self.height           = height
        self.zoom             = zoom

        self.front_clip       = near
        self.back_clip        = far

        ## Raster3D assumes r,g,b triplits are squared
        r, g, b = bg_color_rgbf
        r = r*r
        g = g*g
        b = b*b
        self.bg_color_rgbf = (r,g,b)

        ## the lighting model for Raster3D is not quite the same as
        ## OpenGL; this conversion gets it close
        total_light = ambient_light + diffuse_light + specular_light
        
        self.ambient          = ambient_light  / total_light
        self.specular         = specular_light / total_light 
        self.phong            = 3

        ## initial material state
        self.object_list.append((8, 0.0, 0, self.front_clip, self.back_clip))
                
    def glr_construct_header(self):
        """Creates the header for the render program.
        """
        tsz_width   = 16
        tsz_height  = 16
        
        xtiles   = int(round(self.width  / float(tsz_width)))
        ytiles  = int(round(self.height / float(tsz_height)))

        pixel_width  = xtiles * tsz_width
        pixel_height = ytiles * tsz_height

        ## self.zoom is the horizontal number of Angstroms shown in the
        ## image, this must be converted to the Raster3D zoom parameter
        ## which is the number of Angstroms of the shortest dimention
        if pixel_width > pixel_height:
            r = float(pixel_height) / float(pixel_width)
            z = self.zoom * r
        else:
            z = self.zoom

        self.header_list = [
            "mmLib Generated Raster3D Output", 
            "%d %d     tiles in x,y" % (xtiles, ytiles), 
            "%d %d     pixels (x,y) per tile" % (tsz_width, tsz_height),
            "4         anti-aliasing level 4; 3x3->2x2",
            "%4.2f %4.2f %4.2f background(rgb)" % self.bg_color_rgbf,
            "F 	       no shadows cast", 
            "%2d       Phong power" % (self.phong), 
            "0.20      secondary light contribution",
            "%4.2f     ambient light contribution" % (self.ambient),
            "%4.2f     specular reflection component" % (self.specular), 
            "0.0       eye position(no perspective)", 
            "1 1 1     main light source position", 
            "1 0 0 0   4x4 view matrix",
            "0 1 0 0", 
            "0 0 1 0",
            "0 0 0 %f" % (z),
            "3 	       mixed objects", 
            "* 	      (free format triangle and plane descriptors)",
            "* 	      (free format sphere descriptors",
            "* 	      (free format cylinder descriptors)",
            "16",
            "FRONTCLIP %8.3f" % (self.front_clip),
            "16",
            "BACKCLIP  %8.3f" % (self.back_clip),
            ]

    def glr_render_end(self):
        """Write out the input file for the render program.
        """
        ## open r3d file, write header
        pobj = None

        if self.render_stdin is not None:
            stdin = self.render_stdin
        else:
            cmdlist = [self.render_program_path, "-png", self.render_png_path, "-gamma", "1.5"]
            try:
                pobj = subprocess.Popen(cmdlist, 
                                        stdin = subprocess.PIPE,
                                        stdout = subprocess.PIPE,
                                        stderr = subprocess.STDOUT,
                                        close_fds = True,
                                        bufsize = 32768)
            except OSError:
                ConsoleOutput.warning("the render program failed to execute from path: %s" % (
                    self.render_program_path))
                return
                
            stdin = pobj.stdin
            
        ## XXX: debug
        ##r3dfil = open("/tmp/raytrace.r3d","w")
        ##stdin = TeeWrite(stdin)

        ## add required hader for the render program
        self.glr_construct_header()

        try:
            stdin.write("\n".join(self.header_list))
            stdin.write("\n")
            self.glr_write_objects(stdin)
        except IOError, err:
            ConsoleOutput.warning("IOError while executing %s" % (self.render_program_path))
            ConsoleOutput.warning(str(err))
            return

        if self.render_stdin is not None:
            self.render_stdin = None

        if pobj is not None:
            pobj.stdin.close()
            pobj.wait()

    def glr_write_objects(self, stdin):
        """Write the graphic objects to the stdin file.
        """
        ## write objects
        for gob in self.object_list:
            gob_type = gob[0]

            ## triangle
            if gob_type==1:
                stdin.write(
                    "1\n"\
                    "%8.3f %8.3f %8.3f "\
                    "%8.3f %8.3f %8.3f "\
                    "%8.3f %8.3f %8.3f "\
                    "%4.2f %4.2f %4.2f\n" % (
                    gob[1][0], gob[1][1], gob[1][2],
                    gob[2][0], gob[2][1], gob[2][2],
                    gob[3][0], gob[3][1], gob[3][2],
                    gob[4], gob[5], gob[6]))

            ## sphere
            elif gob_type==2:
                stdin.write(
                    "2\n"\
                    "%8.3f %8.3f %8.3f %8.3f %4.2f %4.2f %4.2f\n" % (
                    gob[1][0], gob[1][1], gob[1][2],
                    gob[2],
                    gob[3], gob[4], gob[5]))

            ## round-ended cylinder
            elif gob_type==3:
                stdin.write(
                    "3\n"\
                    "%8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f 0 "\
                    "%4.2f %4.2f %4.2f\n" % (
                    gob[1][0], gob[1][1], gob[1][2],
                    gob[3],
                    gob[2][0], gob[2][1], gob[2][2],
                    gob[4], gob[5], gob[6]))

            ## flat-ended cylinder
            elif gob_type==5:
                stdin.write(
                    "5\n"\
                    "%8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f 0 "\
                    "%4.2f %4.2f %4.2f\n" % (
                    gob[1][0], gob[1][1], gob[1][2],
                    gob[3],
                    gob[2][0], gob[2][1], gob[2][2],
                    gob[4], gob[5], gob[6]))

            ## normal
            elif gob_type==7:
                stdin.write(
                    "7\n"\
                    "%8.3f %8.3f %8.3f "\
                    "%8.3f %8.3f %8.3f "\
                    "%8.3f %8.3f %8.3f\n" % (
                    gob[1][0], gob[1][1], gob[1][2],
                    gob[2][0], gob[2][1], gob[2][2],
                    gob[3][0], gob[3][1], gob[3][2] ))

            ## material properties
            elif gob_type==8:

                stdin.write(
                    "%d\n"\
                    "-1 -1  -1 -1 -1  %4.2f  %1d 0 0 2\n"\
                    "FRONTCLIP %8.3f\n"\
                    "BACKCLIP  %8.2f\n" % gob)

            ## ellipse
            elif gob_type==14:                
                q = gob[6]
                
                stdin.write(
                    "14\n"\
                    "%8.3f %8.3f %8.3f "\
                    "%8.3f "\
                    "%4.2f %4.2f %4.2f "\
                    "%8.3f %8.3f %8.3f %8.3f %8.3f %8.3f 0 0 0 %8.3f\n" % (
                    gob[1][0], gob[1][1], gob[1][2], 
                    gob[2],
                    gob[3], gob[4], gob[5],
                    q[0,0], q[1,1], q[2,2], q[0,1], q[1,2], q[0,2],
                    gob[7]))

    def glr_push_matrix(self):
        """
        """
        assert len(self.matrix_stack)<=25
        self.matrix_stack.append(self.matrix.copy())

    def glr_pop_matrix(self):
        """
        """
        self.matrix       = self.matrix_stack[-1]
        self.matrix_stack = self.matrix_stack[:-1]
        
    def glr_translate(self, t):
        """Translates the scene by vector t.
        """
        M = numpy.array( [[   1.0,    0.0,    0.0, t[0]],
                          [   0.0,    1.0,    0.0, t[1]],
                          [   0.0,    0.0,    1.0, t[2]],
                          [   0.0,    0.0,    0.0,  1.0]], float)

        self.matrix = numpy.matrixmultiply(self.matrix, M)

    def glr_translate3(self, x, y, z):
        """
        """
        M = numpy.array( [[   1.0,    0.0,    0.0,    x],
                          [   0.0,    1.0,    0.0,    y],
                          [   0.0,    0.0,    1.0,    z],
                          [   0.0,    0.0,    0.0,  1.0]], float)

        self.matrix = numpy.matrixmultiply(self.matrix, M)

    def glr_mult_matrix_Rt(self, R, t):
        """Return the current matrix as a 3x3 rotation matrix R and 3x1
        translation vector t.
        """
        M = numpy.array( [[R[0,0], R[0,1], R[0,2], t[0]],
                          [R[1,0], R[1,1], R[1,2], t[1]],
                          [R[2,0], R[2,1], R[2,2], t[2]],
                          [   0.0,    0.0,    0.0,  1.0]], float)

        self.matrix = numpy.matrixmultiply(self.matrix, M)
        
    def glr_mult_matrix_R(self, R):
        """Multiplies the current matrix by rotation matrix R and translates
        by t
        """
        M = numpy.array( [[R[0,0], R[0,1], R[0,2], 0.0],
                          [R[1,0], R[1,1], R[1,2], 0.0],
                          [R[2,0], R[2,1], R[2,2], 0.0],
                          [   0.0,    0.0,    0.0, 1.0]], float)

        self.matrix = numpy.matrixmultiply(self.matrix, M)
        
    def glr_rotate_axis(self, deg, axis):
        """
        """
        R = AtomMath.rmatrixu(axis, deg*Constants.DEG2RAD)
        self.glr_mult_matrix_R(R)

    def glr_lighting_enable(self):
        """
        """
        pass

    def glr_lighting_disable(self):
        """
        """
        pass

    def glr_set_line_width(self, width):
        """
        """
        self.line_width = width * BASE_LINE_WIDTH
    
    def glr_set_material_rgb(self, r, g, b):
        """Creates a stock rendering material colored according to the given
        RGB values.
        """
        self.material_color_r = r*r
        self.material_color_g = g*g
        self.material_color_b = b*b
        
        if self.material_alpha<1.0:
            self.material_alpha = 1.0

            if self.light_two_sides==True:
                self.object_list.append(
                    (8, 0.0, 2,
                     self.front_clip, self.back_clip))
            else:
                self.object_list.append(
                    (8, 0.0, 0,
                     self.front_clip, self.back_clip))

    def glr_set_material_rgba(self, r, g, b, a):
        """Creates a stock rendering material colored according to the given
        RGB values.
        """
        self.material_color_r = r*r
        self.material_color_g = g*g
        self.material_color_b = b*b

        if self.material_alpha!=a:
            self.material_alpha = a

            if self.light_two_sides==True:
                self.object_list.append(
                    (8, 1.0 - self.material_alpha, 2,
                     self.front_clip, self.back_clip))
            else:
                self.object_list.append(
                    (8, 1.0 - self.material_alpha, 0,
                     self.front_clip, self.back_clip))

    def glr_vertex(self, vertex):
        """
        """
        self.glr_vertex_func(vertex)
        
    def glr_vertex3(self, x, y, z):
        """
        """
        self.glr_vertex_func((x,y,z))

    def glr_begin_lines(self):
        """
        """
        raise FinishMe()

    def glr_begin_triangles(self):
        """
        """
        raise FinishMe()

    def glr_begin_quads(self):
        self.glr_vertex_func  = self.glr_vertex_quads_1
        self.glr_end          = self.glr_end_quads
        self.vertex_1         = None
        self.normal_1         = None
        self.vertex_2         = None
        self.normal_2         = None
        self.vertex_3         = None
        self.normal_3         = None

    def glr_end_quads(self):
        del self.glr_vertex_func
        del self.glr_end
        del self.vertex_1
        del self.normal_1
        del self.vertex_2
        del self.normal_2
        del self.vertex_3
        del self.normal_3

    def glr_vertex_quads_1(self, vertex):
        self.glr_vertex_func = self.glr_vertex_quads_2
        self.normal_1        = self.normal
        self.vertex_1        = matrixmultiply43(self.matrix, vertex)

    def glr_vertex_quads_2(self, vertex):
        self.glr_vertex_func = self.glr_vertex_quads_3
        self.normal_2        = self.normal
        self.vertex_2        = matrixmultiply43(self.matrix, vertex)
        
    def glr_vertex_quads_3(self, vertex):
        self.glr_vertex_func = self.glr_vertex_quads_4
        self.normal_3        = self.normal
        self.vertex_3        = matrixmultiply43(self.matrix, vertex)

    def glr_vertex_quads_4(self, vertex):
        self.glr_vertex_func = self.glr_vertex_quads_1

        normal_4 = self.normal
        vertex_4 = matrixmultiply43(self.matrix, vertex)

        self.object_list.append(
            (1,
             self.vertex_1,
             self.vertex_2,
             self.vertex_3,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b))

        self.object_list.append(
            (7,
             self.normal_1,
             self.normal_2,
             self.normal_3))
        
        self.object_list.append(
            (1,
             self.vertex_1,
             self.vertex_3,
             vertex_4,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b))
        
        self.object_list.append(
            (7,
             self.normal_1,
             self.normal_3,
             normal_4))
        
    def glr_begin_triangle_fan(self):
        """
        """
        self.glr_vertex_func  = self.glr_vertex_triangle_fan_1
        self.glr_end          = self.glr_end_triangle_fan
        self.vertex_1         = None
        self.vertex_2         = None
        self.normal_1         = None
        self.normal_2         = None
    
    def glr_end_triangle_fan(self):
        """
        """
        del self.glr_vertex_func
        del self.glr_end
        del self.vertex_1
        del self.vertex_2
        del self.normal_1
        del self.normal_2
        
    def glr_vertex_triangle_fan_1(self, vertex):
        """Get (first) common fan vertex.
        """
        self.glr_vertex_func = self.glr_vertex_triangle_fan_2
        
        self.vertex_1 = matrixmultiply43(self.matrix, vertex)
        self.normal_1 = self.normal

    def glr_vertex_triangle_fan_2(self, vertex):
        """Get second vertex.
        """
        self.glr_vertex_func = self.glr_vertex_triangle_fan_3

        self.vertex_2 = matrixmultiply43(self.matrix, vertex)
        self.normal_2 = self.normal

    def glr_vertex_triangle_fan_3(self, vertex):
        """Get third vertex and beyond: construct triangles.
        """
        vertex_3 = matrixmultiply43(self.matrix, vertex)
        normal_3 = self.normal

        self.object_list.append(
            (1,
             self.vertex_1,
             self.vertex_2,
             vertex_3,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b) )

        self.object_list.append(
            (7,
             self.normal_1,
             self.normal_2,
             normal_3) )

        self.vertex_2 = vertex_3
        self.normal_2 = normal_3

    def glr_normalize_enable(self):
        """
        """
        self.normalize = True

    def glr_normalize_disable(self):
        """
        """
        self.normalize = False

    def glr_normal(self, n):
        """
        """
        ## just rotate the normal
        R  = self.matrix[:3,:3]
        nr = numpy.matrixmultiply(R, n)

        if self.normalize==True:
            self.normal = AtomMath.normalize(nr)
        else:
            self.normal = nr

    def glr_normal3(self, x, y, z):
        """
        """
        ## just rotate the normal
        R  = self.matrix[:3,:3]
        n = numpy.array([x, y, z], float)
        nr = numpy.matrixmultiply(R, n)

        if self.normalize==True:
            self.normal = AtomMath.normalize(nr)
        else:
            self.normal = nr
        
    def glr_light_two_sides_enable(self):
        """
        """
        self.light_two_sides = True
        self.object_list.append(
            (8,  1.0 - self.material_alpha, 2,
             self.front_clip, self.back_clip))
        
    def glr_light_two_sides_disable(self):
        """
        """
        self.light_two_sides = False
        self.object_list.append(
            (8,  1.0 - self.material_alpha, 0,
             self.front_clip, self.back_clip))
        
    def glr_line(self, position1, position2):
        """Draws a single line.
        """
        self.object_list.append(
            (3,
             matrixmultiply43(self.matrix, position1),
             matrixmultiply43(self.matrix, position2),
             self.line_width,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b))
            
    def glr_text(self, text, scale):
        """Renders a text string.
        """
        pass
            
    def glr_axis(self, position, axis, radius):
        """Draw a vector axis using the current set material at position
        with the given radius.
        """
        ## don't bother redering small axes -- they look like junk
        if numpy.allclose(AtomMath.length(axis), 0.0):
            return
        
        self.object_list.append(
            (5,
             matrixmultiply43(self.matrix, position),
             matrixmultiply43(self.matrix, position + axis),
             radius,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b))

    def glr_tube(self, position1, position2, radius):
        """Draws a hollow tube beginning at pos1, and ending at pos2.
        """
        self.object_list.append(
            (5,
             matrixmultiply43(self.matrix, position1),
             matrixmultiply43(self.matrix, position2),
             radius,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b))

    def glr_sphere(self, position, radius, quality):
        """Draw a atom as a CPK sphere.
        """
        self.object_list.append(
            (2,
             matrixmultiply43(self.matrix, position),
             radius,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b))

    def glr_cross(self, position, color, line_width):
        """Draws atom with a cross of lines.
        """
        pass

    def glr_Uaxes(self, position, U, prob, color, line_width):
        """Draw the anisotropic axies of the atom at the given probability.
        """
        ## rotate U
        R  = self.matrix[:3,:3]
        Ur = numpy.matrixmultiply(numpy.matrixmultiply(R, U), numpy.transpose(R))

        evals, evecs = linalg.eigenvectors(Ur)
        
    def glr_Uellipse(self, position, U, prob):
        """Renders the ellipsoid enclosing the given fractional probability
        given the gaussian variance-covariance matrix U at the given position.
        C=1.8724 = 68%
        """
        ## rotate U
        R  = self.matrix[:3,:3]
        Ur = numpy.matrixmultiply(numpy.matrixmultiply(R, U), numpy.transpose(R))

        Umax = max(linalg.eigenvalues(Ur))
        try:
            limit_radius = Gaussian.GAUSS3C[prob] * MARGIN * math.sqrt(Umax)
        except ValueError:
            limit_radius = 2.0

        try:
            Q = linalg.inverse(Ur)
        except linalg.LinAlgError:
            return
        
        self.object_list.append(
            (14,
             matrixmultiply43(self.matrix, position),
             limit_radius,
             self.material_color_r,
             self.material_color_g,
             self.material_color_b,
             Q,
             -Gaussian.GAUSS3C[prob]**2))
    
    def glr_Urms(self, position, U):
        """Renders the root mean square (one standard deviation) surface of
        the
        gaussian variance-covariance matrix U at the given position.  This
        is a peanut-shaped surface. (Note: reference the peanut paper!)
        """
        pass

