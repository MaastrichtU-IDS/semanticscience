## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Visualization system for Structure objects.
"""
from __future__  import generators

import copy
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

import Library
import GeometryDict
import AtomMath
import Structure
import Gaussian
import Colors


## MISC Constents
PROP_OPACITY_RANGE    = "0.0-1.0,0.1"
PROP_LINE_RANGE       = "1.0-10.0,1.0"
PROP_PROBABILTY_RANGE = "1-99,1"
PROP_FRAC_RANGE       = "0-100,1"


class GLPropertyDict(dict):
    """Property cache/routing dictionary
    """
    def __init__(self, gl_object):
        self.gl_object = gl_object

    def update(self, **args):
        self.gl_object.glo_update_properties(**args)


class GLPropertyDefault(object):
    """This value means a property should use its default value.
    """
    pass


class GLObject(object):
    """Base class for all OpenGL rendering objects.  It combines a
    composite-style tree structure with a system for setting properties.
    The properties are used for the specific OpenGL drawing objects
    to control color, position, line width, etc...  Implementing properties
    requres the GLProperties object which is the access object for the
    properties.
    """
    
    PropertyDefault = GLPropertyDefault()

    def __init__(self, **args):
        object.__init__(self)

        self.__globject_parent               = None
        self.__globject_children             = []

        self.properties                      = GLPropertyDict(self)
        self.__globject_properties_id        = str(id(self))
        self.__globject_properties_name      = None
        self.__globject_properties           = []
        self.__globject_properties_callbacks = []

        self.glo_install_properties()

    def glo_name(self):
        """Returns the GLObject name.
        """
        if self.__globject_properties_name is not None:
            return self.__globject_properties_name
        elif self.__globject_properties_id is not None:
            return "%s(%s)" % (self.__class__.__name__, self.__globject_properties_id)
        else:
            return self.__class__.__name__

    def glo_set_name(self, name):
        """Sets the GLObject name.
        """
        self.__globject_properties_name = name

    def glo_add_child(self, child):
        assert isinstance(child, GLObject)
        assert child!=self
        assert self.glo_is_descendant_of(child) is False
        assert child.__globject_parent is None
        child.__globject_parent = self
        self.__globject_children.append(child)

    def glo_prepend_child(self, child):
        """Adds a child GLObject to the beginning of the GLObject's
        child list.
        """
        assert isinstance(child, GLObject)
        assert child!=self
        assert self.glo_is_descendant_of(child) is False
        assert child.__globject_parent is None
        child.__globject_parent = self
        self.__globject_children.insert(0, child)
            
    def glo_append_child(self, child):
        """Adds a child GLObject to the end of the GLObject's child list.
        """
        assert isinstance(child, GLObject)
        assert child!=self
        assert self.glo_is_descendant_of(child) is False
        assert child.__globject_parent is None
        child.__globject_parent = self
        self.__globject_children.append(child)
        
    def glo_remove_child(self, child):
        """Removes the child GLObject.
        """
        assert isinstance(child, GLObject)
        assert child.__globject_parent==self
        child.__globject_parent = None
        self.__globject_children.remove(child)

    def glo_remove(self):
        """The GLObject removes itself from its parent.
        """
        parent = self.__globject_parent
        if parent is None:
            return
        parent.glo_remove_child(self)
        
    def glo_iter_children(self):
        """Iterate immediate children.
        """
        return iter(self.__globject_children)

    def glo_iter_preorder_traversal(self):
        """Preorder Traversal for GLObject composite.
        """
        for child1 in self.__globject_children:
            yield child1
            for child2 in child1.glo_iter_preorder_traversal():
                yield child2

    def glo_get_depth(self):
        """Returns the depth, the root composite is depth 0.
        """
        depth = 0
        ancestor = self.__globject_parent
        while ancestor:
            depth += 1
            ancestor = ancestor.parent
        return depth

    def glo_get_degree(self):
        """Returns the number of children (degree).
        """
        return len(self.__globject_children)

    def glo_count_descendants(self):
        """Counts all decendant GLObjects.
        """
        n = self.glo_get_degree()
        for child in self.__globject_children:
            n += child.glo_count_descendants()
        return n

    def glo_get_root(self):
        """Returns the root GLObject.
        """
        gl_object = self
        while gl_object.__globject_parent:
            gl_object = gl_object.__globject_parent
        return gl_object

    def glo_get_parent(self):
        """Returns the parent GLObject.
        """
        return self.__globject_parent

    def glo_get_path(self):
        """Returns the tree-path to the composite as a list of its
        parent composites.
        """
        path_list = [self]
        parent = self.__globject_parent
        while parent:
            path_list.insert(0, parent)
            parent = parent.__globject_parent
        return path_list

    def glo_get_index_path(self):
        """Returns the tree-path to the GLObject as a list of its
        integer indexes.
        """
        ipath_list = []
        child = self
        parent = child.__globject_parent
        while parent:
            ipath_list.insert(0, parent.__globject_children.index(child))
            child = parent
            parent = parent.__globject_parent
        return ipath_list

    def glo_get_parent_list(self):
        """Returns a list of the parent GLObjects back to the root.
        """
        parent_list = []
        composite = self
        while composite.__globject_parent:
            composite = composite.__globject_parent
            parent_list.append(composite)
        return parent_list

    def glo_get_lowest_common_ancestor(self, gl_object):
        """Returns the lowest common ancesotry of self and argument
        composite.
        """
        assert isinstance(gl_object, GLObject)

        pl1 = self.glo_get_parent_list()
        pl2 = gl_object.getParentList()
        pl1.reverse()
        pl2.reverse()

        ancestor = None
        for i in xrange(min(len(pl1), len(pl2))):
            if pl1[i] == pl2[i]:
                ancestor = pl1[i]
            else:
                break

        return ancestor

    def glo_is_descendant_of(self, gl_object):
        """Returns true if self composite is a decent of argument GLObject.
        """
        assert isinstance(gl_object, GLObject)
        
        ancestor = self.__globject_parent
        while ancestor:
            if ancestor==gl_object:
                return True
            ancestor = ancestor.__globject_parent
        return False

    def glo_set_properties_id(self, gl_object_id):
        """Set the property name for this GLObject.
        """
        self.__globject_properties_id = gl_object_id

    def glo_get_properties_id(self):
        """Returns the properties ID of this object.
        """
        return self.__globject_properties_id

    def glo_install_properties(self):
        """Called by GLObject.__init__ to install properties.
        """
        pass

    def glo_add_property(self, prop_desc):
        """Adds a new property to the GLObject.  The prop_desc is a dictionary
        with attributes describing the property.  See comments in source code
        for a description of the key values for property descriptions.
        """
        assert prop_desc["name"] not in self.properties

        ## is the proprty marked read-only, this is only a hint to
        ## the user interface, not a actual read-only property
        prop_desc["read_only"] = prop_desc.get("read_only", False)

        ## the property triggers update callbacks when the
        ## value is changed
        prop_desc["update_on_changed"] = prop_desc.get("update_on_changed", True)

        ## the property triggers update callbacks when the
        ## property is set with comparison to the old value
        prop_desc["update_on_set"] = prop_desc.get("update_on_set", False)

        ## the property triggers update callbacks on initalization
        prop_desc["update_on_init"] = prop_desc.get("update_on_init", True)

        self.__globject_properties.append(prop_desc)

    def glo_iter_property_desc(self):
        """Iterates over all property descriptions.
        """
        return iter(self.__globject_properties)
        
    def glo_get_property_desc(self, name):
        """Return the property description dictionary for the given
        property name.
        """
        for prop_desc in self.__globject_properties:
            if prop_desc["name"]==name:
                return prop_desc
        return None

    def glo_link_child_property(self, name, child_gl_object_id, child_name):
        """Link the value of the GLObject's property to the value of
        a child property.
        """
        prop_desc = self.glo_get_property_desc(name)
        if prop_desc is None:
            raise ValueError, "GLObject.glo_link_child_property(x, y, z) parent has no property: %s" % (name)

        link_dict = {"gl_object": child_gl_object_id,
                     "name":      child_name}

        try:
            prop_desc["link"].append(link_dict)
        except KeyError:
            prop_desc["link"] = [link_dict]

    def glo_get_child(self, gl_object_id):
        """Returns the child GLObject matching the given gl_object_id.
        """
        for gl_object in self.glo_iter_children():
            if gl_object.__globject_properties_id==gl_object_id:
                return gl_object
        return None

    def glo_get_child_path(self, glo_id_path):
        """Returns the object at the given path, or None if the object does
        not exist.
        """
        child = self

        for glo_id in glo_id_path.split("/"):
            parent = child
            child = parent.glo_get_child(glo_id)
            if child is None:
                return False
            
        return child

    def glo_init_properties(self, **args):
        """This is a special form of update which propagates all linked
        values, not just the changed ones.
        """
        updates = {}
        actions = []

        for prop_desc in self.__globject_properties:
            name = prop_desc["name"]

            ## set the property value
            if args.has_key(name):
                if isinstance(args[name], GLPropertyDefault):
                    self.properties[name] = prop_desc["default"]
                else:
                    self.properties[name] = args[name]
            else:
                self.properties[name] = prop_desc["default"]

            ## if the update callbacks are to be triggered on initialization
            if prop_desc["update_on_init"] is True:
                 updates[name] = self.properties[name]

                 ## add changes to actions list
                 ## case 1: action is a string
                 if isinstance(prop_desc["action"], str):
                     if prop_desc["action"] not in actions:
                         actions.append(prop_desc["action"])
                 ## case 2: action is a list of strings
                 elif isinstance(prop_desc["action"], list):
                     for prop_action in prop_desc["action"]:
                         if prop_action not in actions:
                             actions.append(prop_action)

            ## propagate linked values
            try:
                linked_props = prop_desc["link"]
            except KeyError:
                pass
            else:
                for linked_prop in linked_props:
                    child = self.glo_get_child(linked_prop["gl_object"])
                    child_name = linked_prop["name"]
                    child.glo_update_properties(**{ child_name: self.properties[name] })
                    
        if len(updates)>0:
            for func in self.__globject_properties_callbacks:
                func(updates, actions)
                
    def glo_update_properties(self, **args):
        """Update property values and trigger update callbacks.
        """        
        updates = {}
        actions = []

        ## update properties
        for prop_desc in self.__globject_properties:
            name = prop_desc["name"]

            ## continue if this property is not being updated
            if args.has_key(name) is False:
                continue

            ## update_on_set:
            ##     If True, always trigger update callbacks when
            ##     the value is set.
            ## update_on_changed:
            ##     If true, trigger update callbacks when a value
            ##     is changed.
            do_update = False

            if prop_desc["update_on_set"] is True:
                do_update = True

            elif prop_desc["update_on_changed"] is True:

                ## special handling for Numeric/Numarray types
                if isinstance(self.properties[name], numpy.ArrayType):
                    if not numpy.allclose(self.properties[name], args[name]):
                        do_update = True

                elif self.properties[name]!=args[name]:
                    do_update = True
            
            if do_update is True:
                
                if isinstance(args[name], GLPropertyDefault):
                    self.properties[name] = prop_desc["default"]
                else:
                    self.properties[name] = args[name]
                    
                updates[name] = self.properties[name]

                ## now update the actions taken when a property changes
                ## case 1: action is a string
                if isinstance(prop_desc["action"], str):
                    if prop_desc["action"] not in actions:
                        actions.append(prop_desc["action"])
                ## case 2: action is a list of strings
                elif isinstance(prop_desc["action"], list):
                    for prop_action in prop_desc["action"]:
                        if prop_action not in actions:
                            actions.append(prop_action)

            if do_update is True:
                ## propagate updates for linked properties
                try:
                    linked_props = prop_desc["link"]
                except KeyError:
                    pass
                else:
                    for linked_prop in linked_props:
                        child = self.glo_get_child(linked_prop["gl_object"])
                        child_name = linked_prop["name"]                    
                        child.glo_update_properties(**{ child_name: self.properties[name] })

        if len(updates)>0:
            for func in self.__globject_properties_callbacks:
                func(updates, actions)

    def glo_update_properties_path(self, glo_id_path, value):
        """
        """
        path = glo_id_path.split("/")
        prop_name = path[-1]
        path = path[:-1]

        ## get the child to update
        child = self
        for glo_id in path:
            parent = child
            child = parent.glo_get_child(glo_id)
            if child is None:
                break
        if child is None:
            return False

        child.glo_update_properties(**{prop_name: value})

    def glo_add_update_callback(self, func):
        """Adds a function which is called whenever property values change.
        The function is called with two arguments: a updates dictionary
        containing all updated properties and the values they were changed
        to, and a actions list which contains a unique list of action
        key words forme self.prop_list = []
        self.callback_list = [] from the action fields of the updated
        properties.
        """
        self.__globject_properties_callbacks.append(func)

    def glo_remove_update_callback(self, func):
        """Removes the update callback.
        """
        self.__globject_properties_callbacks.remove(func)

    def glo_get_glstructure(self):
        """Returns the parent GLStructure object, or None if the GLObject
        is not a child of a GLStructure.
        """
        gl_object = self
        while gl_object is not None and not isinstance(gl_object, GLStructure):
            gl_object = gl_object.__globject_parent
        return gl_object


class GLDrawList(GLObject):
    """Fundamental OpenGL rigid entity.
    """

    gldl_color_list = Colors.COLOR_NAMES_CAPITALIZED[:]
    
    def __init__(self, **args):
        self.driver                = None
        self.gldl_draw_method_list = []
        
        GLObject.__init__(self, **args)
        self.glo_add_update_callback(self.gldl_update_cb)
        self.glo_init_properties(**args)

        self.gldl_install_draw_methods()

    def glo_remove_child(self, child):
        """Override GLObject's remove to also delete the compiled OpenGL
        draw lists.
        """
        for chd in child.glo_iter_preorder_traversal():
            if isinstance(chd, GLDrawList):
                chd.gldl_draw_method_delete_compiled_all_drivers()
        GLObject.glo_remove_child(self, child)

    def glo_remove(self):
        """Override GLObject's remove to also delete the compiled OpenGL
        draw lists.
        """
        for child in self.glo_iter_preorder_traversal():
            if isinstance(child, GLDrawList):
                child.gldl_draw_method_delete_compiled_all_drivers()
        GLObject.glo_remove(self)

    def glo_install_properties(self):
        self.glo_add_property(
            { "name" :      "visible",
              "desc":       "Visible",
              "catagory":   "Show/Hide",
              "type":       "boolean",
              "default":    True,
              "action":     "redraw" })
        self.glo_add_property(
            { "name" :      "origin",
              "desc":       "Origin",
              "type":       "array(3)",
              "hidden":     True,
              "default":    numpy.zeros(3, float),
              "action":     "redraw" })
        self.glo_add_property(
            { "name" :      "axes",
              "desc":       "Rotation Axes",
              "type":       "array(3,3)",
              "hidden":     True,
              "default":    numpy.identity(3, float),
              "action":     "redraw" })
        self.glo_add_property(
            { "name" :      "rot_x",
              "desc":       "Degrees Rotation About X Axis",
              "type":       "float",
              "hidden":     True,
              "default":    0.0,
              "action":     "redraw" })
        self.glo_add_property(
            { "name" :      "rot_y",
              "desc":       "Degrees Rotation About Y Axis",
              "type":       "float",
              "hidden":     True,
              "default":    0.0,
              "action":     "redraw" })
        self.glo_add_property(
            { "name" :      "rot_z",
              "desc":       "Degrees Rotation About Z Axis",
              "type":       "float",
              "hidden":     True,
              "default":    0.0,
              "action":     "redraw" })
        self.glo_add_property(
            { "name" :      "visible_distance",
              "desc":       "",
              "type":       "float",
              "hidden":     True,
              "default":    0.0,
              "action":     "redraw" })

    def gldl_update_cb(self, updates, actions):
        """Properties update callback.
        """
        ## recompile action recompiles all OpenGL draw lists
        if "recompile" in actions:
            self.gldl_draw_method_delete_compiled_all_drivers()
            self.gldl_redraw()

        ## redraw action redraws all OpenGL draw lists
        elif "redraw" in actions:
            self.gldl_redraw()

        ## go through the draw method definitions and trigger
        ## fine-grained redraw/recompile actions for specific
        ## draw methods
        for draw_method in self.gldl_draw_method_list:
            if draw_method["recompile_action"] in actions:
                self.gldl_redraw()
                
                draw_method["expiration_id"] += 1

                ## check if the opacity flag of the draw list changed
                op = draw_method["opacity_property"]
                if op is not None:
                    draw_method["transparent"] = self.properties[op]<1.0

    def gldl_redraw(self):
        """Triggers a redraw of the GLViewer
        """
        gl_viewer = self.glo_get_root()
        if isinstance(gl_viewer, GLViewer):
            gl_viewer.glv_redraw()

    def gldl_get_glviewer(self):
        """Returns the root GLViewer object.
        """
        return self.glo_get_root()

    def gldl_property_color_rgbf(self, prop_name):
        """Returns the property value as a RGBF triplet.
        """
        try:
            colorx = self.properties[prop_name]
        except KeyError:
            raise KeyError, "gldl_property_color_rgbf: bad prop_name %s" % (prop_name)
        
        try:
            return Colors.COLOR_RGBF[colorx.lower()]
        except KeyError:
            pass

        try:
            r, g, b = colorx.split(",")
        except ValueError:
            pass
        else:
            try:
                return (float(r), float(g), float(b))
            except ValueError:
                return (1.0, 0.0, 0.0)

        raise TypeError, "gldl_property_color_rgbf: bad colorx %s" % (str(colorx))

    def gldl_install_draw_methods(self):
        """Override in children to install draw methods for a GLDrawList.
        """
        pass

    def gldl_draw_method_install(self, draw_method):
        """Installs a draw method to compile and render a OpenGL draw listlist.
        keys:
           name:       text description of the method
           func:       the method to invoke to render the draw list
           tranparent: True if the draw list is drawing transparent

        private values:
           gl_draw_list_id: OpenGL Drawlist ID
        """
        assert draw_method.has_key("name")
        assert draw_method.has_key("func")

        draw_method["transparent"] = draw_method.get("transparent", False)
        draw_method["no_gl_compile"] = draw_method.get("no_gl_compile", False)
        draw_method["visible_property"] = draw_method.get("visible_property", None)
        draw_method["recompile_action"] = draw_method.get("recompile_action", None)
        draw_method["opacity_property"] = draw_method.get("opacity_property", None)
        draw_method["multidraw_iter"] = draw_method.get("multipdraw_iter", None)
        draw_method["multidraw_all_iter"] = draw_method.get("multipdraw_all_iter", None)

        ## the state_id gets incrimented whever compiled draw methods
        ## need to be recompiled
        draw_method["expiration_id"] = 1

        ## list of drivers with compiled rendering of this draw method
        draw_method["driver_list"] = []

        self.gldl_draw_method_list.append(draw_method)

    def gldl_draw_method_get(self, draw_method_name):
        """Returns the draw metod of the given name or None if not found.
        """
        for draw_method in self.gldl_draw_method_list:
            if draw_method["name"]==draw_method_name:
                return draw_method
        return None

    def gldl_draw_method_compile(self, draw_method):
        """Compiles a draw method.
        """
        assert self.driver is not None
        
        mid = self.driver.glr_compile_start(draw_method)
        draw_method["func"]()
        self.driver.glr_compile_end()
        draw_method["driver_list"].append(self.driver)

    def gldl_draw_method_delete_compiled(self, draw_method):
        """Deletes the compiled draw list in the current driver.
        """
        assert self.driver is not None
        
        if self.driver.glr_compile_exists(draw_method):
            self.driver.glr_compile_delete(draw_method)
            draw_method["driver_list"].remove(self.driver)

    def gldl_draw_method_delete_compiled_all_drivers(self):
        """
        """
        for draw_method in self.gldl_draw_method_list:
            for driver in draw_method["driver_list"]:
                if driver.glr_compile_exists(draw_method):
                    driver.glr_compile_delete(draw_method)

    def gldl_push_matrix(self):
        """Rotate and translate to the correct position for drawing.
        """
        assert self.driver is not None

        self.driver.glr_push_matrix()

        if not numpy.allclose(self.properties["origin"], numpy.zeros(3, float)):
            self.driver.glr_translate(self.properties["origin"])

        axes = self.properties["axes"]
        if not numpy.allclose(axes, numpy.identity(3, float)):
            self.driver.glr_rotate_axis(self.properties["rot_x"], axes[0])
            self.driver.glr_rotate_axis(self.properties["rot_y"], axes[1])
            self.driver.glr_rotate_axis(self.properties["rot_z"], axes[2])
            
    def gldl_pop_matrix(self):
        """Pop the roatated/translated position.
        """
        assert self.driver is not None
        
        self.driver.glr_pop_matrix()

    def gldl_render(self, driver, transparent=False):
        """Compile or force a recompile of this object's gl_draw list, and
        render the scene.  Rendering the scene can be bypassed if
        this method is called with render = False.
        """
        if self.properties["visible"] is False:
            return

        self.driver = driver
        self.gldl_push_matrix()

        ## support multiple rendering images by implementing class
        ## iterators gldl_iter_multidraw_all() for multiple
        ## rendering iterations of the GLDrawList and all its children,
        ## or gldl_iter_multidraw_self() for multiple images of just
        ## this GLDrawList, rendering the children just once
        for draw_flag_multi in self.gldl_iter_multidraw_all():

            for draw_flag_self in self.gldl_iter_multidraw_self():
                self.gldl_render_draw_methods(transparent)

            ## render first-level children of this GLDrawList
            ## which, in turn, will render their children
            for draw_list in self.glo_iter_children():
                if isinstance(draw_list, GLDrawList):
                    draw_list.gldl_render(driver, transparent)

        self.gldl_pop_matrix()
        self.driver = None

    def gldl_render_draw_methods(self, transparent):
        """Render all draw methods.
        """
        for draw_method in self.gldl_draw_method_list:

            ## check if the draw method is currently visible
            ## skip it if it is not visible
            visable_property_name = draw_method["visible_property"]
            if visable_property_name is not None:
                if self.properties[visable_property_name] is False:
                    continue

            ## transparent methods are only drawn when during the second
            ## rednering pass
            if draw_method["transparent"]!=transparent:
                continue

            ## some draw lists may be not be compiled into a OpenGL draw
            ## list, these have to be redrawn every time
            if draw_method["no_gl_compile"] is True or not self.driver.glr_compile_supported():
                draw_method["func"]()

            else:
                if not self.driver.glr_compile_exists(draw_method):
                    self.gldl_draw_method_compile(draw_method)

                elif not self.driver.glr_compile_current(draw_method):
                    self.gldl_draw_method_delete_compiled(draw_method)
                    self.gldl_draw_method_compile(draw_method)

                self.driver.glr_compile_render(draw_method)

    def gldl_iter_multidraw_all(self):
        """When implemented as a iterator in a subclass, each time yield
        is invoked the GLDrawList and all its decendants will be rendered
        from whatever OpenGL coordinate system is set in the iterator.
        """
        yield True

    def gldl_iter_multidraw_self(self):
        """Similar to gldl_iter_multidraw_all, but only this GLDrawList is
        rendered.  The decendant GLDrawLists are rendered normally.
        """
        yield True

    def gldl_draw(self):
        """Implement in subclass to draw somthing.
        """
        pass

    def gldl_draw_transparent(self):
        """Implement in subclass to draw transparent objects.
        """
        pass


class GLAxes(GLDrawList):
    """Draw orthogonal axes in red = x, green = y, blue = z.
    """
    def __init__(self, **args):
        GLDrawList.__init__(self, **args)
        self.glo_set_name("Cartesian Axes")
        self.glo_init_properties(**args)

    def glo_install_properties(self):
        GLDrawList.glo_install_properties(self)

        self.glo_add_property(
            { "name":       "line_length",
              "desc":       "Axis Length",
              "catagory":   "Show/Hide",
              "type":       "float",
              "spin":       "1.0-500.0,10.0",
              "default":    20.0,
              "action":     "recompile" })
        self.glo_add_property(
            { "name":       "line_width",
              "desc":       "Axis Radius",
              "catagory":   "Show/Hide",
              "type":       "float",
              "spin":      "0.0-5.0,0.1",
              "default":    0.1,
              "action":     "recompile" })
        self.glo_add_property(
            { "name":       "color_x",
              "desc":       "X Axis Color",
              "catagory":   "Show/Hide",
              "type":       "enum_string",
              "default":    "Red",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile" })
        self.glo_add_property(
            { "name":       "color_y",
              "desc":       "Y Axis Color",
              "catagory":   "Show/Hide",
              "type":       "enum_string",
              "default":    "Green",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile" })
        self.glo_add_property(
            { "name":       "color_z",
              "desc":       "Z Axis Color",
              "catagory":   "Show/Hide",
              "type":       "enum_string",
              "default":    "Blue",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile" })

    def gldl_install_draw_methods(self):
        self.gldl_draw_method_install(
            { "name":        "axes",
              "func":        self.draw_axes,
              "transparent": False })

    def draw_axes(self):
        line_length = self.properties["line_length"]
        line_width  = self.properties["line_width"]

        r, g, b = self.gldl_property_color_rgbf("color_x")
        self.driver.glr_set_material_rgb(r, g, b)
        self.driver.glr_axis(
            numpy.zeros(3, float),
            numpy.array([line_length, 0.0, 0.0]),
            line_width) 

        r, g, b = self.gldl_property_color_rgbf("color_y")
        self.driver.glr_set_material_rgb(r, g, b)
        self.driver.glr_axis(
            numpy.zeros(3, float),
            numpy.array([0.0, line_length, 0.0]),
            line_width) 

        r, g, b = self.gldl_property_color_rgbf("color_z")
        self.driver.glr_set_material_rgb(r, g, b)
        self.driver.glr_axis(
            numpy.zeros(3, float),
            numpy.array([0.0, 0.0, line_length]),
            line_width) 


class GLUnitCell(GLDrawList):
    """Draw unit cell.
    """
    def __init__(self, **args):
        self.unit_cell = args["unit_cell"]

        GLDrawList.__init__(self, **args)
        self.glo_set_name("Unit Cell")
        
        self.glo_init_properties(
            crystal_system  = self.unit_cell.space_group.crystal_system,
            space_group     = self.unit_cell.space_group.pdb_name,

            a = self.unit_cell.a,
            b = self.unit_cell.b,
            c = self.unit_cell.c,

            alpha = self.unit_cell.calc_alpha_deg(),
            beta  = self.unit_cell.calc_beta_deg(),
            gamma = self.unit_cell.calc_gamma_deg(),

            **args)

    def glo_install_properties(self):
        GLDrawList.glo_install_properties(self)

        self.glo_add_property(
            { "name":       "radius",
              "desc":       "Radius",
              "catagory":   "Show/Hide",
              "type":       "float",
              "default":    0.25,
              "action":     "recompile" })
        
        self.glo_add_property(
            { "name":       "a_color",
              "desc":       "a Cell Divider Color",
               "catagory":   "Show/Hide",
              "type":       "enum_string",
              "default":    "Red",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile" })
        self.glo_add_property(
            { "name":       "b_color",
              "desc":       "b Cell Divider Color",
               "catagory":   "Show/Hide",
              "type":       "enum_string",
              "default":    "Green",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile" })
        self.glo_add_property(
            { "name":       "c_color",
              "desc":       "c Cell Divider Color",
               "catagory":   "Show/Hide",
              "type":       "enum_string",
              "default":    "Blue",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile" })
        
        self.glo_add_property(
            { "name":        "crystal_system",
              "desc":        "Crystal System",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "string",
              "default":     "",
              "action":      "" })
        self.glo_add_property(
            { "name":        "space_group",
              "desc":        "Spacegroup",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "string",
              "default":     "",
              "action":      "" })
        
        self.glo_add_property(
            { "name":        "a",
              "desc":        "a",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "" })
        self.glo_add_property(
            { "name":        "b",
              "desc":        "b",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "" })
        self.glo_add_property(
            { "name":        "c",
              "desc":        "c",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "" })

        self.glo_add_property(
            { "name":        "alpha",
              "desc":        "alpha",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "" })
        self.glo_add_property(
            { "name":        "beta",
              "desc":        "beta",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "" })
        self.glo_add_property(
            { "name":        "gamma",
              "desc":        "gamma",
              "catagory":    "Show/Hide",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "" })

    def gldl_install_draw_methods(self):
        self.gldl_draw_method_install(
            { "name":        "unit_cell",
              "func":        self.draw_unit_cell,
              "transparent": False })

    def draw_unit_cell(self):
        self.draw_cell(-1, -1, -1, 0, 0, 0)

    def draw_cell(self, x1, y1, z1, x2, y2, z2):
        """Draw the unit cell lines in a rectangle starting at fractional
        integer coordinates x1, y1, z1, ending at x2, y2, z2.  The first set of
        coordinates must be <= the second set.
        """
        assert x1<=x2 and y1<=y2 and z1<=z2

        a = self.unit_cell.calc_frac_to_orth(numpy.array([1.0, 0.0, 0.0]))
        b = self.unit_cell.calc_frac_to_orth(numpy.array([0.0, 1.0, 0.0]))
        c = self.unit_cell.calc_frac_to_orth(numpy.array([0.0, 0.0, 1.0]))

        rad = self.properties["radius"]

        rf, gf, bf = self.gldl_property_color_rgbf("a_color")
        self.driver.glr_set_material_rgb(rf, gf, bf)
        for k in xrange(z1, z2+2):
            for j in xrange(y1, y2+2):
                p1 = x1*a + j*b + k*c
                p2 = (x2+1)*a + j*b + k*c
                self.driver.glr_tube(p1, p2, rad)

        rf, gf, bf = self.gldl_property_color_rgbf("b_color")
        self.driver.glr_set_material_rgb(rf, gf, bf)
        for k in xrange(z1, z2+2):
            for i in xrange(x1, x2+2):
                p1 = i*a + y1*b + k*c
                p2 = i*a + (y2+1)*b + k*c
                self.driver.glr_tube(p1, p2, rad)

        rf, gf, bf = self.gldl_property_color_rgbf("c_color")
        self.driver.glr_set_material_rgb(rf, gf, bf)
        for j in xrange(y1, y2+2):
            for i in xrange(x1, x2+2):
                p1 = i*a + j*b + z1*c
                p2 = i*a + j*b + (z2+1)*c
                self.driver.glr_tube(p1, p2, rad)


class GLAtomList(GLDrawList):
    """OpenGL renderer for a list of atoms.  Optional arguments iare:
    color, U, U_color.
    """
    glal_res_type_color_dict = {
        "aliphatic":         (0.50, 0.50, 0.50),
        "aromatic":          (0.75, 0.75, 0.75),
        "sulfer-containing": (0.20, 1.00, 0.20),
        "alchols":           (1.00, 0.60, 0.60),
        "acids":             (1.00, 0.25, 0.25),
        "bases":             (0.25, 0.25, 1.00),
        "amides":            (0.60, 0.60, 1.00)}
    
    def __init__(self, **args):
        
        self.glal_atom_color_opts = [
            "Color By Element",
            "Color By Residue Type",
            "Color By Temp Factor",
            "Color By Anisotropy" ]
        self.glal_atom_color_opts += self.gldl_color_list
        
        self.glal_hidden_atoms_dict  = None
        self.glal_visible_atoms_dict = None
        self.glal_xyzdict            = None

        GLDrawList.__init__(self, **args)
        self.glo_add_update_callback(self.glal_update_properties)
        self.glo_init_properties(**args)

    def glo_install_properties(self):
        GLDrawList.glo_install_properties(self)

        ## Show/Hide
        self.glo_add_property(
            { "name":       "atom_origin",
              "desc":       "Atom Calculation Origin",
              "type":       "array(3)",
              "hidden":     True,
              "default":    None,
              "action":     ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "color",
              "desc":      "Atom Color",
              "catagory":  "Colors",
              "type":      "enum_string",
              "default":   "Color By Element",
              "enum_list": self.glal_atom_color_opts,
              "action":    "" })
        
        self.glo_add_property(
            { "name":      "color_setting",
              "desc":      "Atom Color",
              "catagory":  "Colors",
              "type":      "string",
              "hidden":    True,
              "default":   "Color By Element",
              "action":    "recompile" })
        self.glo_add_property(
            { "name":      "color_blue",
              "desc":      "Color Range Blue",
              "catagory":  "Colors",
              "type":      "float",
              "default":   0.0,
              "action":    "recompile" })
        self.glo_add_property(
            { "name":      "color_red",
              "desc":      "Color Range Red",
              "catagory":  "Colors",
              "type":      "float",
              "default":   1.0,
              "action":    "recompile" })
        
        self.glo_add_property(
            { "name":      "symmetry",
              "desc":      "Show Symmetry Equivelants",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "main_chain_visible",
              "desc":      "Show Main Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "oatm_visible",
              "desc":      "Show Main Chain Carbonyl Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "side_chain_visible",
              "desc":      "Show Side Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "hetatm_visible",
              "desc":      "Show Hetrogen Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "water_visible",
              "desc":      "Show Waters",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "hydrogen_visible",
              "desc":      "Show Hydrogens",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    ["recompile", "recalc_positions"] })

        ## labels
        self.glo_add_property(
            { "name":      "labels",
              "desc":      "Show Atom Lables",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    "recompile_labels" })
        self.glo_add_property(
            { "name":       "label_size",
              "desc":       "Label Size",
              "catagory":   "Labels",
              "type":       "float",
              "default":    5.0,
              "action":     "recompile_labels" })
        self.glo_add_property(
            { "name":       "label_color",
              "desc":       "Label Color",
              "catagory":   "Labels",
              "type":       "enum_string",
              "default":    "White",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile_labels" })
        self.glo_add_property(
            { "name":       "label_style",
              "desc":       "Label Style",
              "catagory":   "Labels",
              "type":       "enum_string",
              "default":    "Residue",
              "enum_list":  ["Residue", "All Atoms", "CA Atoms"],
              "action":     "recompile_labels" })
        
        ## lines
        self.glo_add_property(
            { "name":       "lines",
              "desc":       "Draw Atom Bond Lines",
              "catagory":   "Show/Hide",
              "type":       "boolean",
              "default":    True,
              "action":     "recompile_lines" })
        self.glo_add_property(
            { "name":       "line_width",
              "desc":       "Bond Line Size",
              "catagory":   "Bond Lines",
              "type":       "float",
              "spin":       PROP_LINE_RANGE,
              "default":    1.0,
              "action":     "recompile_lines" })

        ## Ball/Stick
        self.glo_add_property(
            { "name":       "ball_stick",
              "desc":       "Draw Ball/Sticks",
              "catagory":   "Show/Hide",
              "type":       "boolean",
              "default":    False,
              "action":     "recompile_ball_stick" })
        self.glo_add_property(
            { "name":       "ball_radius",
              "desc":       "Atom (Ball) Radius",
              "catagory":   "Ball/Stick",
              "type":       "float",
              "default":    0.1,
              "action":     "recompile_ball_stick" })
        self.glo_add_property(
            { "name":       "stick_radius",
              "desc":       "Bond (Stick) Radius",
              "catagory":   "Ball/Stick",
              "type":       "float",
              "default":    0.1,
              "action":     "recompile_ball_stick" })

        ## cpk
        self.glo_add_property(
            { "name":       "cpk",
              "desc":       "Draw CPK Spheres",
              "catagory":   "Show/Hide",
              "type":       "boolean",
              "default":    False,
              "action":     "recompile_cpk" })
        self.glo_add_property(
            { "name":       "cpk_opacity_occupancy",
              "desc":       "Set Opacity by Atom Occupancy",
              "catagory":   "CPK",
              "type":       "boolean",
              "default":    False,
              "action":     "recompile_cpk" })
        self.glo_add_property(
            { "name":       "cpk_scale_radius",
              "desc":       "Scale CPK Radius",
              "catagory":   "CPK",
              "type":       "float",
              "range":       "0.0-5.0,0.1",
              "default":    1.0,
              "action":     "recompile_cpk" })
        self.glo_add_property(
            { "name":       "cpk_opacity",
              "desc":       "CPK Sphere Opacity",
              "catagory":   "CPK",
              "type":       "float",
              "range":      PROP_OPACITY_RANGE,
              "default":    1.00,
              "action":     "recompile_cpk" })
        self.glo_add_property(
            { "name":       "sphere_quality",
              "desc":       "CPK Sphere Quality",
              "catagory":   "CPK",
              "type":       "integer",
              "range":      "5-36,5",
              "default":    10,
              "action":     "recompile_cpk" })

        ## trace           
        self.glo_add_property(
            { "name":       "trace",
              "desc":       "Draw Backbone Trace",
              "catagory":   "Show/Hide",
              "type":       "boolean",
              "default":    False,
              "action":     "recompile_trace" })
        self.glo_add_property(
            { "name":       "trace_radius",
              "desc":       "Trace Radius",
              "catagory":   "Trace",
              "type":       "float",
              "default":    0.2,
              "action":     "recompile_trace" })
        self.glo_add_property(
            { "name":       "trace_color",
              "desc":       "Trace Color",
              "catagory":   "Trace",
              "type":       "enum_string",
              "default":    "White",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile_trace" })

        ## ADPs
        self.glo_add_property(
            { "name":       "adp_prob",
              "desc":       "Isoprobability Magnitude",
              "catagory":   "ADP",
              "type":       "integer",
              "range":      PROP_PROBABILTY_RANGE,
              "default":    50,
              "action":     ["recompile_Uaxes", "recompile_Uellipse"] })
        self.glo_add_property(
            { "name":      "U",
              "desc":      "Show Thermal Axes",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    "recompile_Uaxes" })
        self.glo_add_property(
            { "name":       "U_color",
              "desc":       "Thermal Axes Color",
              "catagory":   "ADP",
              "type":       "enum_string",
              "default":    "White",
              "enum_list":  self.gldl_color_list,
              "action":     "recompile_Uaxes" })
        self.glo_add_property(
            { "name":       "ellipse",
              "desc":       "Show Thermal Ellipsoids",
              "catagory":   "Show/Hide",
              "type":       "boolean",
              "default":    False,
              "action":     "recompile_Uellipse" })
        self.glo_add_property(
            { "name":       "ellipse_opacity",
              "desc":       "Thermal Ellipsoid Opacity",
              "catagory":   "ADP",
              "type":       "float",
              "range":      PROP_OPACITY_RANGE,
              "default":    1.0,
              "action":     "recompile_Uellipse" })
        self.glo_add_property(
            { "name":       "rms",
              "desc":       "Show Thermal Peanuts",
              "catagory":   "Show/Hide",
              "type":       "boolean",
              "default":    False,
              "action":     "recompile_Urms" })
        self.glo_add_property(
            { "name":       "rms_opacity",
              "desc":       "Peanut Surface Opacity",
              "catagory":   "ADP",
              "type":       "float",
              "range":      PROP_OPACITY_RANGE,
              "default":    1.0,
              "action":     "recompile_Urms" })
        self.glo_add_property(
            { "name":       "show_sig_u",
              "desc":       "Show +/- SIGUIJ Ellipsoids",
              "catagory":   "ADP",
              "type":       "boolean",
              "default":    False,
              "action":     "recompile_Uellipse" })
        self.glo_add_property(
            { "name":       "sig_u_opacity",
              "desc":       "SIGUIJ Ellipsoid Opacity",
              "catagory":   "ADP",
              "type":       "float",
              "range":      PROP_OPACITY_RANGE,
              "default":    0.5,
              "action":     "recompile_Uellipse" })

    def gldl_install_draw_methods(self):
        self.gldl_draw_method_install(
            { "name":                "labels",
              "func":                self.glal_draw_labels,
              "no_gl_compile":       True,
              "transparent":         False,
              "visible_property":    "labels",
              "recompile_action":    "recompile_labels" })
        self.gldl_draw_method_install(
            { "name":                "lines",
              "func":                self.glal_draw_lines,
              "transparent":         False,
              "visible_property":    "lines",
              "recompile_action":    "recompile_lines" })
        self.gldl_draw_method_install(
            { "name":                "trace",
              "func":                self.glal_draw_trace,
              "transparent":         False,
              "visible_property":    "trace",
              "recompile_action":    "recompile_trace" })
        self.gldl_draw_method_install(
            { "name":                "ball_stick",
              "func":                self.glal_draw_ball_stick,
              "transparent":         False,
              "visible_property":    "ball_stick",
              "recompile_action":    "recompile_ball_stick" })
        self.gldl_draw_method_install(
            { "name":                "cpk",
              "func":                self.glal_draw_cpk,
              "visible_property":    "cpk",
              "opacity_property":    "cpk_opacity",
              "recompile_action":    "recompile_cpk" })
        self.gldl_draw_method_install(
            { "name":                "Uaxes",
              "func":                self.glal_draw_Uaxes,
              "transparent":         False,
              "visible_property":    "U",
              "recompile_action":    "recompile_Uaxes" })
        self.gldl_draw_method_install(
            { "name":                "Uellipse",
              "func":                self.glal_draw_Uellipse,
              "visible_property":    "ellipse",
              "opacity_property":    "ellipse_opacity",
              "recompile_action":    "recompile_Uellipse" })
        self.gldl_draw_method_install(
            { "name":                "Urms",
              "func":                self.glal_draw_Urms,
              "visible_property":    "rms",
              "opacity_property":    "rms_opacity",
              "recompile_action":    "recompile_Urms" })

    def glal_update_color_value(self, value):
        """Configure the color_value property from the value argument.
        """
        ## selects one of the named color functions
        if value in self.glal_atom_color_opts:

            if value=="Color By Temp Factor":
                ## calculate the min/max temp factor of the atoms
                ## and auto-set the low/high color range
                min_tf = None
                max_tf = None
                for atm in self.glal_iter_atoms():
                    if min_tf is None:
                        min_tf = atm.temp_factor
                        max_tf = atm.temp_factor
                        continue
                    min_tf = min(atm.temp_factor, min_tf)
                    max_tf = max(atm.temp_factor, max_tf)

                self.properties.update(
                    color_blue    = min_tf,
                    color_red     = max_tf,
                    color_setting = value)
                return
                
            elif value=="Color By Anisotropy":
                self.properties.update(
                    color_blue    = 1.0,
                    color_red     = 0.0,
                    color_setting = value)
                return

            try:
                self.properties.update(color_setting = Colors.COLOR_RGBF[value.lower()])
            except KeyError:
                pass
            else:
                return

            self.properties.update(color_setting=value)

        ## maybe the color is in R,G,B format
        try:
            r, g, b = value.split(",")
        except ValueError:
            pass
        else:
            color_setting = (float(r), float(g), float(b))
            self.properties.update(color_setting=color_setting)
            return

    def glal_update_properties(self, updates, actions):
        ## rebuild visible/hidden dictionaries
        if "recalc_positions" in actions:
             self.glal_hidden_atoms_dict  = None
             self.glal_visible_atoms_dict = None
             self.glal_xyzdict            = None

        ## update color
        if "color" in updates:
            self.glal_update_color_value(updates["color"])
            
    def gldl_iter_multidraw_self(self):
        """Specialized draw list invokation to recycle the draw list for
        symmetry related copies.  Cartesian versions of the symmetry rotation
        and translation operators are generated by GLStructure/UnitCell
        classes.
        """
        if self.properties["symmetry"] is False:
            yield True
            
        else:

            gl_struct = self.glo_get_glstructure()
            if gl_struct is None:
                yield True

            else:
                for symop in gl_struct.iter_orth_symops():
                    self.driver.glr_push_matrix()

                    if self.properties["atom_origin"] != None:
                        self.driver.glr_translate(-self.properties["atom_origin"])

                    self.driver.glr_mult_matrix_Rt(symop.R, symop.t)

                    if self.properties["atom_origin"] != None:
                        self.driver.glr_translate(self.properties["atom_origin"])
                    
                    yield True
                    self.driver.glr_pop_matrix()

    def glal_iter_atoms(self):
        """Implement in a subclass to iterate over all atoms which
        need to be drawn.
        """
        pass

    def glal_iter_fragments(self):
        """Implement in a subclass to iterate one Fragment object
        at a time, in order.  This implementation works with any
        implementation of glal_iter_atoms, but is very inefficent.
        """
        struct = Structure.Structure()
        memo   = {}
        
        for atm in self.glal_iter_atoms():
            struct.add_atom(copy.deepcopy(atm, memo))

        for frag in struct.iter_fragments():
            yield frag

    def glal_iter_chains(self):
        """Implement in a subclass to iterate one Chain object
        at a time, in order.  This implementation works with any
        implementation of glal_iter_atoms, but is very inefficent.
        """
        struct = Structure.Structure()
        memo   = {}
        
        for atm in self.glal_iter_atoms():
            struct.add_atom(copy.deepcopy(atm, memo))

        for chain in struct.iter_chains():
            yield chain

    def glal_iter_models(self):
        """Implement in a subclass to iterate one Model object
        at a time, in order.  This implementation works with any
        implementation of glal_iter_atoms, but is very inefficent.
        """
        struct = Structure.Structure()
        memo   = {}
        
        for atm in self.glal_iter_atoms():
            struct.add_atom(copy.deepcopy(atm, memo))

        for model in struct.iter_models():
            yield model

    def glal_iter_atoms_filtered(self):
        """Iterate all atoms and yield the tuble (atom, visible_flag).
        """
        aa_bb_atoms = ("N", "CA", "C", "O")
        na_bb_atoms = ("P", "O5*", "C5*", "C4*", "C3*", "O3*")

        main_chain_visible = self.properties["main_chain_visible"]
        oatm_visible       = self.properties["oatm_visible"]
        side_chain_visible = self.properties["side_chain_visible"]
        hetatm_visible     = self.properties["hetatm_visible"]
        water_visible      = self.properties["water_visible"]
        hydrogen_visible   = self.properties["hydrogen_visible"]

        for atm in self.glal_iter_atoms():
            if hydrogen_visible is False:
                if atm.element=="H":
                    yield atm, False
                    continue

            frag = atm.get_fragment()
            
            if frag.is_amino_acid():
                if oatm_visible is False and atm.name == "O":
                    yield atm, False                    
                    continue
                
                elif main_chain_visible and side_chain_visible:
                    yield atm, True
                    continue
                
                elif main_chain_visible and not side_chain_visible:
                    if atm.name in aa_bb_atoms:
                        yield atm, True
                        continue
                    
                elif not main_chain_visible and side_chain_visible:
                    if atm.name not in aa_bb_atoms:
                        yield atm, True
                        continue
                    
                yield atm, False
                continue

            elif frag.is_nucleic_acid():
                if main_chain_visible and side_chain_visible:
                    yield atm, True
                    continue
                
                elif main_chain_visible and not side_chain_visible:
                    if atm.name in na_bb_atoms:
                        yield atm, True
                        continue
                    
                elif not main_chain_visible and side_chain_visible:
                    if atm.name not in na_bb_atoms:
                        yield atm, True
                        continue
                    
                yield atm, False
                continue

            elif frag.is_water() is True:
                if water_visible is True:
                    yield atm, True
                    continue
                
                yield atm, False
                continue

            elif hetatm_visible is True:
                yield atm, True
                continue

            else:
                yield atm, False
                continue

    def glal_rebuild_atom_dicts(self):
        """When a atom selection setting or origin changes, the atom
        dictionaries need to be rebuilt.
        """
        self.glal_hidden_atoms_dict  = {}
        self.glal_visible_atoms_dict = {}
        self.glal_xyzdict = GeometryDict.XYZDict(5.0)

        for atm, visible in self.glal_iter_atoms_filtered():
            pos = self.glal_calc_position(atm.position)

            if visible is True:
                self.glal_visible_atoms_dict[atm] = pos
                self.glal_xyzdict.add(pos, atm)
            else:
                self.glal_hidden_atoms_dict[atm] = pos

    def glal_iter_visible_atoms(self):
        """Iterate over all visible atoms yielding the 2-tuple (atm, position).
        """
        if self.glal_visible_atoms_dict is None:
            self.glal_rebuild_atom_dicts()

        for atm, pos in self.glal_visible_atoms_dict.iteritems():
            yield atm, pos
                    
    def glal_calc_position(self, position):
        """Calculate a position vector with respect to the
        proeprty: atom_origin.
        """
        if self.properties["atom_origin"] is not None:
             return position - self.properties["atom_origin"]
        return position
    
    def glal_calc_color_range(self, value):
        """Return a RGBF 3-tuple color of a color gradient for value.
        """
        blue  = self.properties["color_blue"]
        red   = self.properties["color_red"]
        width = abs(red - blue)

        if red>blue:
            if value>=red:
                return (1.0, 0.0, 0.0)
            elif value<=blue:
                return (0.0, 0.0, 1.0)
            
            b = 1.0 - ((value - blue) / width)
            return (1.0-b, 0.0, b)
        
        else:
            if value<=red:
                return (1.0, 0.0, 0.0)
            elif value>=blue:
                return (0.0, 0.0, 1.0)

            b = 1.0 - ((value - red) / width)
            return (b, 0.0, 1.0-b)

    def glal_calc_color(self, atom):
        """Sets the open-gl color for the atom.
        """
        ## individual atom colors
        if hasattr(atom, "glal_color"):
            return atom.glal_color

        setting = self.properties["color_setting"]
        if isinstance(setting, tuple):
            return setting

        if setting=="Color By Element":
            element = Library.library_get_element_desc(atom.element)
            try:
                return element.color_rgbf
            except AttributeError:
                return Colors.COLOR_RGBF["white"]

        elif setting=="Color By Residue Type":
            monomer = Library.library_get_monomer_desc(atom.res_name)
            try:
                return self.glal_res_type_color_dict[monomer.chem_type]
            except KeyError:
                return Colors.COLOR_RGBF["white"]

        elif setting=="Color By Temp Factor":
            return self.glal_calc_color_range(atom.temp_factor)

        elif setting=="Color By Anisotropy":
            return self.glal_calc_color_range(atom.calc_anisotropy())

        raise ValueError, "glal_calc_color: bad color setting %s" % (str(setting))

    def glal_calc_color_label(self):
        """Returns the label color.
        """
        return self.gldl_property_color_rgbf("label_color")
    
    def glal_calc_color_trace(self):
        """Returns the trace color.
        """
        return self.gldl_property_color_rgbf("trace_color")

    def glal_calc_color_Uaxes(self, atom):
        """Return the color to be used for thermal axes.
        """
        return self.gldl_property_color_rgbf("U_color")
    
    def glal_calc_color_Uellipse(self, atom):
        """Return the color to be used for thermal ellipse.
        """
        return self.glal_calc_color(atom)

    def glal_calc_color_Urms(self, atom):
        """Return the color to be used for thermal peanuts.
        """
        return self.glal_calc_color(atom)
        
    def glal_calc_U(self, atom):
        """Return the ADP U tensor for the atom
        """
        return atom.get_U()

    def glal_draw_labels(self):
        """Draws atom lables.
        """
        ## driver optimization
        glr_push_matrix    = self.driver.glr_push_matrix
        glr_pop_matrix     = self.driver.glr_pop_matrix
        glr_mult_matrix_R  = self.driver.glr_mult_matrix_R
        glr_translate      = self.driver.glr_translate
        glr_text           = self.driver.glr_text
        ##
        
        style = self.properties["label_style"].lower()
        scale = self.properties["label_size"]
        self.driver.glr_set_material_rgb(*self.glal_calc_color_label())

        viewer = self.gldl_get_glviewer()
        R  = viewer.properties["R"]
        Ri = numpy.transpose(R)

        ## this vecor is needed to adjust for origin/atom_origin
        ## changes, but it does not account for object rotation yet
        cv = self.properties["origin"]

        ## shift back to the view window coordinate system so the
        ## labels can be drawn in the plane perpendicular to the viewer's
        ## z axis
        glr_push_matrix()
        glr_mult_matrix_R(Ri)

        for atm, pos in self.glal_iter_visible_atoms():

            ## amino acid residues
            if atm.get_fragment().is_amino_acid():

                ## just label chain/residue
                if style=="residue":
                    if atm.name!="CA":
                        continue
                    text = "%s%s" % (atm.chain_id, atm.fragment_id)

                ## full lables for CA atoms only
                elif style=="ca atoms":
                    if atm.name!="CA":
                        continue

                    if atm.alt_loc=="":
                        text = "%s %s %s %s" % (
                            atm.name,
                            atm.res_name,
                            atm.fragment_id,
                            atm.chain_id)
                    else:
                        text = "%s(%s) %s %s %s" % (
                            atm.name,
                            atm.alt_loc,
                            atm.res_name,
                            atm.fragment_id,
                            atm.chain_id)

                ## labels for all atoms
                elif atm.name=="CA":
                    if atm.alt_loc=="":
                        text = "%s %s %s %s" % (
                            atm.name,
                            atm.res_name,
                            atm.fragment_id,
                            atm.chain_id)
                    else:
                        text = "%s(%s) %s %s %s" % (
                            atm.name,
                            atm.alt_loc,
                            atm.res_name,
                            atm.fragment_id,
                            atm.chain_id)
                else:
                    if atm.alt_loc=="":
                        text = atm.name
                    else:
                        text = "%s(%s)" % (atm.name, atm.alt_loc)

            ## all other residues
            else:
                 if atm.alt_loc=="":
                     text = "%s %s %s %s" % (
                         atm.name,
                         atm.res_name,
                         atm.fragment_id,
                         atm.chain_id)
                 else:
                     text = "%s(%s) %s %s %s" % (
                         atm.name,
                         atm.alt_loc,
                         atm.res_name,
                         atm.fragment_id,
                         atm.chain_id)

            relative_pos = numpy.matrixmultiply(R, pos + cv)
            glr_push_matrix()
            glr_translate(relative_pos + numpy.array([0.0, 0.0, 2.0]))
            glr_text(text, scale)
            glr_pop_matrix()

        glr_pop_matrix()

    def glal_draw_cpk(self):
        """Draw a atom as a CPK sphere.
        """
        ## driver optimization
        glr_set_material_rgba = self.driver.glr_set_material_rgba
        glr_sphere            = self.driver.glr_sphere
        ##
        
        for atm, pos in self.glal_iter_visible_atoms():
            edesc = Library.library_get_element_desc(atm.element)
            if edesc is not None:
                radius = edesc.vdw_radius
            else:
                radius = 2.0

            r, g, b = self.glal_calc_color(atm)
            glr_set_material_rgba(r, g, b, self.properties["cpk_opacity"])

            glr_sphere(
                pos,
                self.properties["cpk_scale_radius"] * radius,
                self.properties["sphere_quality"])

    def glal_draw_Uaxes(self):
        """Draw thermal axes at the given ADP probability level.
        """
        ## driver optimization
        glr_Uaxes = self.driver.glr_Uaxes
        ##
        
        prob = self.properties["adp_prob"]
        
        for atm, pos in self.glal_iter_visible_atoms():
            rgb = self.glal_calc_color_Uaxes(atm)
            U = self.glal_calc_U(atm)
            if U is None:
                continue
            glr_Uaxes(pos, U, prob, rgb, 1.0)

    def glal_draw_Uellipse(self):
        """Draw the ADP determined probability ellipsoid.
        """
        ## driver optimization
        glr_set_material_rgba = self.driver.glr_set_material_rgba
        glr_Uellipse          = self.driver.glr_Uellipse
        ##
        
        opacity = self.properties["ellipse_opacity"]
        prob    = self.properties["adp_prob"]

        show_sig_u    = self.properties["show_sig_u"]
        sig_u_opacity = self.properties["sig_u_opacity"]
        
        for atm, pos in self.glal_iter_visible_atoms():
            U = self.glal_calc_U(atm)
            if U is None:
                continue

            r, g, b = self.glal_calc_color_Uellipse(atm) 
            
            if show_sig_u is True and atm.sig_U is not None:
                glr_set_material_rgba(r, g, b,sig_u_opacity)
                glr_Uellipse(pos, U - atm.sig_U, prob)

            glr_set_material_rgba(r, g, b, opacity)
            glr_Uellipse(pos, U, prob)

            if show_sig_u is True and atm.sig_U is not None:
                glr_set_material_rgba(r, g, b,sig_u_opacity)
                glr_Uellipse(pos, U + atm.sig_U, prob)

    def glal_draw_Urms(self):
        """Draw the ADP determined RMS displacement surface.
        """
        ## driver optimization
        glr_set_material_rgba = self.driver.glr_set_material_rgba
        glr_Urms              = self.driver.glr_Urms
        ##

        opacity = self.properties["rms_opacity"]

        for atm, pos in self.glal_iter_visible_atoms():
            U = self.glal_calc_U(atm)
            if U is None:
                continue

            r, g, b = self.glal_calc_color_Urms(atm)        
            glr_set_material_rgba(r, g, b, opacity)
            glr_Urms(pos, U)

    def glal_draw_lines(self):
        """Draw a atom using bond lines only.
        """
        ## driver optimization
        glr_set_material_rgb = self.driver.glr_set_material_rgb
        glr_line             = self.driver.glr_line
        glr_cross            = self.driver.glr_cross
        ##
        
        self.driver.glr_lighting_disable()
        self.driver.glr_set_line_width(self.properties["line_width"])

        for atm1, pos1 in self.glal_iter_visible_atoms():
            glr_set_material_rgb(*self.glal_calc_color(atm1))

            if len(atm1.bond_list)>0:
                ## if there are bonds, then draw the lines 1/2 way to the
                ## bonded atoms
                for bond in atm1.iter_bonds():
                    atm2 = bond.get_partner(atm1)

                    try:
                        pos2 = self.glal_visible_atoms_dict[atm2]
                    except KeyError:
                        if self.glal_hidden_atoms_dict.has_key(atm2):
                            continue
                        else:
                            pos2 = self.glal_calc_position(atm2.position)
                    
                    end = pos1 + ((pos2 - pos1) / 2)
                    glr_line(pos1, end)

            ## draw a cross for non-bonded atoms
            else:
                glr_cross(
                    pos1,
                    self.glal_calc_color(atm1),
                    self.properties["line_width"])

    def glal_draw_ball_stick(self):
        """Draw atom with ball/stick model.
        """
        ## driver optimization
        glr_set_material_rgb = self.driver.glr_set_material_rgb
        glr_tube             = self.driver.glr_tube
        glr_sphere           = self.driver.glr_sphere
        ##

        ball_radius  = self.properties["ball_radius"]
        stick_radius = self.properties["stick_radius"]

        for atm1, pos1 in self.glal_iter_visible_atoms():
            glr_set_material_rgb(*self.glal_calc_color(atm1))

            ## if there are bonds, then draw the lines 1/2 way to the
            ## bonded atoms
            for bond in atm1.iter_bonds():
                atm2 = bond.get_partner(atm1)

                try:
                    pos2 = self.glal_visible_atoms_dict[atm2]
                except KeyError:
                    if self.glal_hidden_atoms_dict.has_key(atm2):
                        continue
                    else:
                        pos2 = self.glal_calc_position(atm2.position)

                end = pos1 + ((pos2 - pos1) / 2)
                glr_tube(pos1, end, stick_radius)

            ## draw ball
            glr_sphere(pos1, ball_radius, 10)

    def glal_draw_cross(self, atm, pos):
        """Draws atom with a cross of lines.
        """
        self.driver.glr_cross(pos, self.glal_calc_color(atm), self.properties["line_width"])

    def glal_draw_trace(self):
        """Draws trace over all polymer backbone atoms.
        """
        ## driver optimization
        glr_set_material_rgb = self.driver.glr_set_material_rgb
        glr_tube             = self.driver.glr_tube
        glr_sphere           = self.driver.glr_sphere
        ##
        
        trace_radius = self.properties["trace_radius"]
        r, g, b      = self.glal_calc_color_trace()
        
        glr_set_material_rgb(r, g, b)

        for chain in self.glal_iter_chains():

            last_atm = None

            for frag in chain.iter_fragments():

                if frag.is_amino_acid() is True:
                    backbone_atoms = ["CA"]
                    prev_atom_path = ["N", "C", "CA"]
                elif frag.is_nucleic_acid() is True:
                    backbone_atoms = ["P", "O5*", "C5*", "C4*", "C3*", "O3*"]
                    prev_atom_path = None
                else:
                    last_atm = None
                    prev_atom_path = None
                    continue

                for name in backbone_atoms:
                    atm = frag.get_atom(name)
                    if atm is None:
                        last_atm = None
                        continue

                    if prev_atom_path is not None:
                        prev_atm = atm.get_bonded_atom(prev_atom_path)
                        if prev_atm != last_atm:
                            last_atm = atm
                            continue

                    if last_atm is None:
                        last_atm = atm
                        continue

                    ## if there are alternate conformations, make sure to
                    ## trace them all in the backbone trace
                    
                    if last_atm.alt_loc=="" and atm.alt_loc=="":
                        lpos = self.glal_calc_position(last_atm.position)
                        pos = self.glal_calc_position(atm.position)
                        glr_sphere(lpos, trace_radius, 12)
                        glr_tube(lpos, pos, trace_radius)

                    elif last_atm.alt_loc=="" and atm.alt_loc!="":
                        lpos = self.glal_calc_position(last_atm.position)

                        for aa in atm.iter_alt_loc():
                            pos = self.glal_calc_position(aa.position)
                            glr_sphere(lpos, trace_radius, 12)
                            glr_tube(lpos, pos, trace_radius)

                    elif last_atm.alt_loc!="" and atm.alt_loc=="":
                        pos = self.glal_calc_position(atm.position)

                        for laa in last_atm.iter_alt_loc():
                            lpos = self.glal_calc_position(laa.position)
                            glr_sphere(lpos, trace_radius, 12)
                            glr_tube(lpos, pos, trace_radius)

                    elif last_atm.alt_loc!="" and atm.alt_loc!="":
                        for aa in atm.iter_alt_loc():
                            for laa in last_atm.iter_alt_loc():
                                if aa.alt_loc!=laa.alt_loc:
                                    continue
                                lpos = self.glal_calc_position(laa.position)
                                pos = self.glal_calc_position(aa.position)
                                glr_sphere(lpos, trace_radius, 12)
                                glr_tube(lpos, pos, trace_radius)

                    last_atm = atm

            if last_atm is not None:
                for laa in last_atm.iter_alt_loc():
                    lpos = self.glal_calc_position(laa.position)
                    glr_sphere(lpos, trace_radius, 10)


class GLChain(GLAtomList):
    """Visualization object for mmLib.Structure.Chain.
    """
    def __init__(self, **args):
        GLAtomList.__init__(self, **args)
        self.chain = args["chain"]
        self.glo_init_properties(**args)

    def glo_install_properties(self):
        GLAtomList.glo_install_properties(self)

    def glo_name(self):
        return "Chain %s" % (self.chain.chain_id)

    def glal_iter_atoms(self):
        return self.chain.iter_all_atoms()

    def glal_iter_fragments(self):
        """The GLAtomList implementation of this is slow.
        """
        return self.chain.iter_fragments()

    def glal_iter_chains(self):
        """The GLAtomList implementation of this is slow.
        """
        yield self.chain


class GLStructure(GLDrawList):
    """Visualization object for a mmLib.Structure.Structure.
    """
    def __init__(self, **args):
        GLDrawList.__init__(self, **args)
        self.struct = args["struct"]
        
        ## add GLObject children
        self.glo_set_properties_id("GLStructure_%s" % (self.struct.structure_id))

        ## structure axes
        self.gl_axes = GLAxes()
        self.gl_axes.glo_set_properties_id("GLAxes")
        self.glo_add_child(self.gl_axes)
        self.glo_link_child_property("axes_visible", "GLAxes", "visible")

        ## unit cell
        self.gl_unit_cell = GLUnitCell(unit_cell=self.struct.unit_cell)
        self.gl_unit_cell.glo_set_properties_id("GLUnitCell")
        self.glo_add_child(self.gl_unit_cell)
        self.glo_link_child_property("unit_cell_visible", "GLUnitCell", "visible")

        ## GLChains 
        for chain in self.struct.iter_chains():
            self.gls_add_chain(chain)

        ## init properties
        self.glo_init_properties(**args)

    def glo_install_properties(self):
        GLDrawList.glo_install_properties(self)

        self.glo_add_property(
            { "name":     "axes_visible",
              "desc":     "Show Cartesian Axes",
              "catagory": "Show/Hide",
              "type":     "boolean",
              "default":  False,
              "action":  "redraw" })
        self.glo_add_property(
            { "name":     "unit_cell_visible",
              "desc":     "Show Unit Cell",
              "catagory": "Show/Hide",
              "type":     "boolean",
              "default":  False,
              "action":   "redraw" })        
        self.glo_add_property(
            { "name":        "symmetry",
              "desc":        "Show Symmetry Equivelant",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":      "main_chain_visible",
              "desc":      "Show Main Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "oatm_visible",
              "desc":      "Show Main Chain Carbonyl Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "side_chain_visible",
              "desc":      "Show Side Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "hetatm_visible",
              "desc":      "Show Hetrogen Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "water_visible",
              "desc":      "Show Waters",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "hydrogen_visible",
              "desc":      "Show Hydrogens",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    ["recompile", "recalc_positions"] })
        
    def glo_name(self):
        return self.struct.structure_id

    def gls_add_chain(self, chain):
        """Adds a Chain object to the GLStructure.
        """
        gl_chain = GLChain(chain=chain)
        gl_chain.glo_set_properties_id("GLChain_%s" % (chain.chain_id))
        self.glo_add_child(gl_chain)

        chain_pid = gl_chain.glo_get_properties_id()

        self.glo_link_child_property(
            "symmetry", chain_pid, "symmetry")

        self.glo_link_child_property(
            "main_chain_visible", chain_pid, "main_chain_visible")
        self.glo_link_child_property(
            "oatm_visible", chain_pid, "oatm_visible")
        self.glo_link_child_property(
            "side_chain_visible", chain_pid, "side_chain_visible") 
        self.glo_link_child_property(
            "hetatm_visible", chain_pid, "hetatm_visible") 
        self.glo_link_child_property(
            "water_visible", chain_pid, "water_visible")        
        self.glo_link_child_property(
            "hydrogen_visible", chain_pid, "hydrogen_visible") 
            
    def iter_orth_symops(self):
        """Iterate orthogonal-space symmetry operations useful for
        displaying symmetry-equivelant molecules without having to
        calculate new draw lists.
        """
        if hasattr(self, "orth_symop_cache"):
            for symop in self.orth_symop_cache:
                yield symop
        else:
            self.orth_symop_cache = []
            uc = self.struct.unit_cell

            for symop in uc.iter_struct_orth_symops(self.struct):
                self.orth_symop_cache.append(symop)
                yield symop


class GLViewer(GLObject):
    """This class renders a list of GLDrawList (or subclasses of) onto
    the given glcontext and gldrawable objects.  The glcontext and gldrawable
    must be created by the underling GUI toolkit, or perhaps the GLUT
    libraries.  This class is completely platform and tookit independent
    once it is passed the glcontext and gldrawable.  The design of this
    class and the associated GLDrawList classes incorporates some basic
    OpenGL drawing optimizations.  The GLDrawList objects are drawn and
    compiled into OpenGL draw lists, and have their own
    transformation/rotation operators WRT the GLViewer origin, allowing
    each GLDrawList to be redrawn very quickly as long as it moves as a
    rigid body.
    """
    def __init__(self):
        GLObject.__init__(self)

        self.glo_set_properties_id("GLViewer")
        self.glo_set_name("GLViewer")
        self.glo_add_update_callback(self.glv_update_cb)
        self.glo_init_properties()

        self.glv_driver_list = []

    def glo_install_properties(self):
        GLObject.glo_install_properties(self)

        ## Background
        self.glo_add_property(
            { "name":      "bg_color",
              "desc":      "Background Color",
              "catagory":  "Background",
              "type":      "enum_string",
              "default":   "Black",
              "enum_list": Colors.COLOR_NAMES_CAPITALIZED[:],
              "action":    "redraw" })

        ## View
        self.glo_add_property(
            { "name":      "R",
              "desc":      "View Window Rotation Matrix",
              "catagory":  "View",
              "read_only": True,
              "type":      "array(3,3)",
              "default":   numpy.identity(3, float),
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "cor",
              "desc":      "Center of Rotation",
              "catagory":  "View",
              "read_only": True,
              "type":      "array(3)",
              "default":   numpy.zeros(3, float),
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "width",
              "desc":      "Window Width",
              "catagory":  "View",
              "read_only": True,
              "type":      "integer",
              "default":   1,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "height",
              "desc":      "Window Height",
              "catagory":  "View",
              "read_only": True,
              "type":      "integer",
              "default":   1,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "near",
              "desc":      "Near Clipping Plane",
              "catagory":  "View",
              "type":      "float",
              "default":   -20.0,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "far",
              "desc":      "Far Clipping Plane",
              "catagory":  "View",
              "type":      "float",
              "default":   1000.0,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "zoom",
              "desc":      "Zoom",
              "catagory":  "View",
              "type":      "float",
              "default":   20.0,
              "action":    "redraw" })
                
        ## OpenGL Lighting
        self.glo_add_property(
            { "name":      "GL_AMBIENT",
              "desc":      "Ambient Light",
              "catagory":  "Lighting",
              "type":      "float",
              "range":     "0.0-1.0,0.1",
              "default":   0.2,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "GL_SPECULAR",
              "desc":      "Specular Light",
              "catagory":  "Lighting",
              "type":      "float",
              "range":     "0.0-1.0,0.1",
              "default":   1.0,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "GL_DIFFUSE",
              "desc":      "Diffuse Light",
              "catagory":  "Lighting",
              "type":      "float",
              "range":     "0.0-1.0,0.1",
              "default":   1.0,
              "action":    "redraw" })

        ## High-Performance OpenGL Features
        self.glo_add_property(
            { "name":      "GL_LINE_SMOOTH",
              "desc":      "Smooth Lines",
              "catagory":  "OpenGL Performance",
              "type":      "boolean",
              "default":   False,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "GL_POINT_SMOOTH",
              "desc":      "Smooth Points",
              "catagory":  "OpenGL Performance",
              "type":      "boolean",
              "default":   False,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "GL_POLYGON_SMOOTH",
              "desc":      "Smooth Polygons",
              "catagory":  "OpenGL Performance",
              "type":      "boolean",
              "default":   False,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "GL_BLEND",
              "desc":      "Alpha-Blending (required for Fog)",
              "catagory":  "OpenGL Performance",
              "type":      "boolean",
              "default":   True,
              "action":    "redraw" })
        self.glo_add_property(
            { "name":      "GL_FOG",
              "desc":      "Enable Fog",
              "catagory":  "OpenGL Performance",
              "type":      "boolean",
              "default":   True,
              "action":    "redraw" })

    def glv_update_cb(self, updates, actions):
        ## prevent the near clipping plane from passing behind the far
        ## clipping plane
        slice = self.properties["near"] - self.properties["far"]
        if slice<1.0:
            if updates.has_key("near") and updates.has_key("far"):
                self.properties.update(far = self.properties["near"] - 1.0)
            elif updates.has_key("near") and not updates.has_key("far"):
                self.properties.update(near = self.properties["far"] + 1.0)
            elif updates.has_key("far") and not updates.has_key("near"):
                self.properties.update(far = self.properties["near"] - 1.0)

        ## redraw request
        if "redraw" in actions:
            self.glv_redraw()
            
    def glv_add_draw_list(self, draw_list):
        """Append a GLDrawList.
        """
        assert isinstance(draw_list, GLDrawList)
        self.glo_add_child(draw_list)
        self.glv_redraw()

    def glv_remove_draw_list(self, draw_list):
        """Remove a GLDrawList.
        """
        assert isinstance(draw_list, GLDrawList)
        draw_list.glo_remove()
        self.glv_redraw()

    def glv_calc_struct_orientation(self, struct):
        """Orient the structure based on a moment-of-intertia like tensor
        centered at the centroid of the structure.
        """
        slop = 2.0

        def aa_atom_iter(structx):
            if structx.count_standard_residues()>0:
                for frag in structx.iter_standard_residues():
                    for atm in frag.iter_atoms():
                        yield atm
            else:
                for atm in structx.iter_atoms():
                    yield atm
                    
        try:
            centroid = AtomMath.calc_atom_centroid(aa_atom_iter(struct))
        except OverflowError:
            return None

        R = AtomMath.calc_inertia_tensor(aa_atom_iter(struct), centroid)

        ori = {}

        ## now calculate a rectangular box
        first_atm = True

        min_x = 0.0
        max_x = 0.0
        min_y = 0.0
        max_y = 0.0
        min_z = 0.0
        max_z = 0.0

        for atm in aa_atom_iter(struct):
            x  = numpy.matrixmultiply(R, atm.position - centroid)

            if first_atm is True:
                first_atm = False

                min_x = max_x = x[0]
                min_y = max_y = x[1]
                min_z = max_z = x[2]
            else:
                min_x = min(min_x, x[0])
                max_x = max(max_x, x[0])
                min_y = min(min_y, x[1])
                max_y = max(max_y, x[1])
                min_z = min(min_z, x[2])
                max_z = max(max_z, x[2])

        ## add slop
        min_x -= slop
        max_x += slop
        min_y -= slop
        max_y += slop
        min_z -= slop
        max_z += slop

        ## calculate the zoom based on a target width
        target_pwidth = 640

        hwidth  = max(abs(min_x),abs(max_x))
        hheight = max(abs(min_y),abs(max_y))
        pheight = target_pwidth * (hheight / hwidth)
        hzoom   = 2.0 * hwidth

        ori["R"]        = R
        ori["centroid"] = centroid
        ori["pwidth"]   = target_pwidth
        ori["pheight"]  = pheight 
        ori["hzoom"]    = hzoom

        ## calculate near, far clipping blane
        ori["near"] = max_z
        ori["far"]  = min_z

        return ori

    def glv_add_struct(self, struct):
        """Adds the visualization for a mmLib.Structure.Structure object
        to the GLViewer.  It returns the GLStructure object created to
        visualize the Structure object.
        """
        assert isinstance(struct, Structure.Structure)

        ## add the structure
        gl_struct = GLStructure(struct=struct)
        self.glv_add_draw_list(gl_struct)

        ori = self.glv_calc_struct_orientation(struct)
        if ori is not None:
            self.properties.update(
                R         = ori["R"],
                cor       = ori["centroid"],
                zoom      = ori["hzoom"],
                near      = ori["near"],
                far       = ori["far"])

        return gl_struct

    def glv_redraw(self):
        """This method is called by GLViewer children to trigger a redraw
        in the toolkit embedding the GLViewer object.  It needs to be
        re-implemented when subclassed to call the tookit's widget redraw
        method.
        """
        pass
    
    def glv_init(self):
        """Called once to initalize the GL scene before drawing.
        """
        pass

    def glv_resize(self, width, height):
        """Called to set the size of the OpenGL window this class is
        drawing on.
        """
        self.properties.update(width=width, height=height)

    def glv_clip(self, near, far):
        """Adjust near/far clipping planes.
        """
        width  = self.properties["width"]
        zoom   = self.properties["zoom"]

        angstrom_per_pixel = zoom / float(width)

        nearA = angstrom_per_pixel * float(near)
        farA  = angstrom_per_pixel * float(far)

        n = self.properties["near"] + nearA
        f = self.properties["far"]  + farA
        self.properties.update(near=n, far=f)

    def glv_zoom(self, z):
        """Adjust zoom levels.
        """
        width  = self.properties["width"]
        zoom   = self.properties["zoom"]

        angstrom_per_pixel = zoom / float(width)
        
        zoom = self.properties["zoom"]
        zoom += angstrom_per_pixel * float(z)
        
        if zoom<1.0:
            zoom = 1.0
        
        self.properties.update(zoom=zoom)

    def glv_straif(self, x, y):
        """Translate in the XY plane.
        """
        ## figure out A/pixel, multipy straif by pixes to get the
        ## the translation

        width  = self.properties["width"]
        zoom   = self.properties["zoom"]

        angstrom_per_pixel = zoom / float(width)

        xA = angstrom_per_pixel * float(x)
        yA = angstrom_per_pixel * float(y)

        ## XY translational shift
        dt = numpy.array((xA, yA, 0.0), float)

        ## change the center of rotation
        R = self.properties["R"]

        ## shift in the XY plane by chainging the position of the
        ## center of rotation
        cor = self.properties["cor"] - numpy.matrixmultiply(numpy.transpose(R), dt)

        self.properties.update(cor=cor)

    def glv_trackball(self, x1, y1, x2, y2):
        """Implements a virtual trackball.
        """
        
        def project_to_sphere(r, x, y):
            d = math.sqrt(x*x + y*y)
            if d<(r*0.707):
                return math.sqrt(r*r - d*d)
            else:
                return (r/1.414)**2 / d

        width  = self.properties["width"]
        height = self.properties["height"]

        ## determine the circle where the trackball is vs. the edges
        ## which are z-rotation
        square = min(width, height)
        radius = int(square * 0.7)

        x1c = x1 - width/2
        y1c = y1 - width/2
        d = math.sqrt(x1c*x1c + y1c*y1c)

        ## Z rotation
        if d>=radius:
            x2c = x2 - width/2
            y2c = y2 - width/2

            p1 = AtomMath.normalize(numpy.array((x1c, y1c, 0.0), float))
            p2 = AtomMath.normalize(numpy.array((x2c, y2c, 0.0), float))

            c = numpy.cross(p2, p1)

            try:
                a = AtomMath.normalize(c)
            except OverflowError:
                return

            theta = AtomMath.length(c) * math.pi/2.0

        ## XY trackball rotation
        else:

            x1 = (2.0*x1 - width)  / width
            y1 = (height - 2.0*y1) / height
            x2 = (2.0*x2 - width)  / width
            y2 = (height - 2.0*y2) / height

            tb_size = 1.0

            ## check for zero rotation
            if x1==x2 and y1==y2:
                return

            p1 = numpy.array((x1, y1, project_to_sphere(tb_size, x1, y1)), float)
            p2 = numpy.array((x2, y2, project_to_sphere(tb_size, x2, y2)), float)

            a = numpy.cross(p1, p2)
            d = p1 - p2
            t = AtomMath.length(d) / (2.0 * tb_size)

            if t>1.0:
                t - 1.0
            if t<-1.0:
                t = -1.0

            theta = 2.0 * math.asin(t)

        ## convert rotation axis a and rotation theta to a quaternion
        Rcur = self.properties["R"]

        ## calculate a in the original coordinate frame
        a = numpy.matrixmultiply(numpy.transpose(Rcur), a)
        qup = AtomMath.rquaternionu(a, theta)

        ## convert the current rotation matrix to a quaternion so the
        ## new rotation quaternion can be added to it
        qcur = AtomMath.quaternionrmatrix(Rcur)
        qnew = AtomMath.addquaternion(qcur, qup)
        Rnew = AtomMath.rmatrixquaternion(qnew)

        self.properties.update(R=Rnew)

    def glv_background_color_rgbf(self):
        """Return the R,G,B triplit of the background color.
        """
        colorx = self.properties["bg_color"].lower()
        if Colors.COLOR_RGBF.has_key(colorx):
            return Colors.COLOR_RGBF[colorx]
        
        try:
            r, g, b = colorx.split(",")
        except ValueError:
            pass
        else:
            try:
                return (float(r), float(g), float(b))
            except ValueError:
                pass

        return (0.0, 0.0, 0.0)

    def glv_render(self):
        """Render scene using all drivers.
        """
        for driver in self.glv_driver_list:
            self.glv_render_one(driver)

    def glv_render_one(self, driver):
        """Render the scent once with the argument driver.
        """
        ## setup the scene for rendering
        driver.glr_render_begin(
            width              = self.properties["width"],
            height             = self.properties["height"],
            zoom               = self.properties["zoom"],
            near               = self.properties["near"],
            far                = self.properties["far"],
            bg_color_rgbf      = self.glv_background_color_rgbf(),
            ambient_light      = self.properties["GL_AMBIENT"],
            diffuse_light      = self.properties["GL_DIFFUSE"],
            specular_light     = self.properties["GL_SPECULAR"],
            gl_line_smooth     = self.properties["GL_LINE_SMOOTH"],
            gl_point_smooth    = self.properties["GL_LINE_SMOOTH"],
            gl_polygon_smooth  = self.properties["GL_POLYGON_SMOOTH"],
            gl_blend           = self.properties["GL_BLEND"],
            gl_fog             = self.properties["GL_FOG"])

        R = self.properties["R"]
        assert numpy.allclose(linalg.determinant(R), 1.0)

        driver.glr_mult_matrix_R(R)
        driver.glr_translate(-self.properties["cor"])

        ## render solid objects
        for draw_list in self.glo_iter_children():
            draw_list.gldl_render(driver)

        ## render transparent objects
        for draw_list in self.glo_iter_children():
            draw_list.gldl_render(driver, True) 

        driver.glr_render_end()
        
