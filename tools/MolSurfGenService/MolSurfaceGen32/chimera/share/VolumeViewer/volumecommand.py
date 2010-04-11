# -----------------------------------------------------------------------------
# Implementation of "volume" command.
#
from Midas import MidasError as syn

# -----------------------------------------------------------------------------
#
def volume_command(cmdname, args):

    fields = args.split()

    if len(fields) == 0:
        raise syn, 'Syntax: %s <volume-id> [options ...]' % cmdname

    if fields[0] == 'all':
        from volume import volume_list
        vlist = volume_list()
    else:
        vlist = volumes_from_specifier(fields[0])
        if len(vlist) == 0:
            raise syn, 'No volumes specified by "%s"' % fields[0]

    gsettings = {}
    dsettings = {}
    rsettings = {}
    opt = option_name_table((data_option_parse_table(), dsettings),
                            (rendering_option_parse_table(), rsettings),
                            (global_option_parse_table(), gsettings))
    fields = fields[1:]
    while fields:
        k = fields[0].lower()
        fields = fields[1:]
        if k in opt:
            fields = opt[k](fields)     # Parse option
        else:
            raise syn, 'Unknown option "%s"' % k

    from volume import default_settings
    default_settings.update(gsettings)
    if 'data_cache_size' in gsettings:
      from VolumeData import data_cache
      data_cache.resize(gsettings['data_cache_size'] * (2**20))

    for v in vlist:
        apply_volume_options(v, dsettings, rsettings)

    save(vlist, dsettings)
    
# -----------------------------------------------------------------------------
#
def apply_volume_options(v, doptions, roptions):

    if 'style' in doptions:
        v.set_representation(doptions['style'])

    kw = level_and_color_settings(v, doptions)
    kw.update(roptions)
    if kw:
        v.set_parameters(**kw)

    r = region(v, doptions)
    if not r is None:
        ijk_min, ijk_max, ijk_step = r
        v.new_region(ijk_min, ijk_max, ijk_step, show = False,
                     adjust_step = not 'step' in doptions)

    if 'name_region' in doptions:
        name = doptions['name_region']
        if r is None:
            r = v.region
        if r:
            v.region_list.add_named_region(name, r[0], r[1])

    if 'planes' in doptions:
        import volume
        volume.cycle_through_planes(v, *doptions['planes'])

    d = v.data
    if 'origin_index' in doptions:
        index_origin = doptions['origin_index']
        if len(index_origin) == 1: index_origin *= 3
        xyz_origin = map(lambda a,b: -a*b, index_origin, d.step)
        d.set_origin(xyz_origin)
    elif 'origin' in doptions:
        origin = doptions['origin']
        if len(origin) == 1: origin *= 3
        d.set_origin(origin)
    if 'voxel_size' in doptions:
        vsize = doptions['voxel_size']
        if len(vsize) == 1: vsize *= 3
        # Preserve index origin.
        origin = map(lambda a,b,c: (a/b)*c, d.origin, d.step, vsize)
        d.set_origin(origin)
        d.set_step(vsize)
    if 'symmetry' in doptions:
        d.symmetries = doptions['symmetry']

    if 'show' in doptions:
        v.initialize_thresholds()
        v.show()
    elif 'hide' in doptions:
        v.unshow()
    elif v.shown():
        v.show()

# TODO:
#  Allow quoted color names.
#  Could allow region name "full" or "back".
#  Could allow voxel_size or origin to be "original".

# -----------------------------------------------------------------------------
#
def save(vlist, doptions):

    if not 'save' in doptions:
        return
    
    path = doptions['save']
    format = doptions.get('save_format', None)
    options = {}
    if 'chunk_shapes' in doptions:
        options['chunk_shapes'] = doptions['chunk_shapes']
    if 'append' in doptions and doptions['append']:
        options['append'] = True
    if 'compress' in doptions and doptions['compress']:
        options['compress'] = True
    if path in ('browse', 'browser'):
        from VolumeData import select_save_path
        path, format = select_save_path()
    if path:
        subregion = doptions.get('save_region', None)
        step = doptions.get('save_step', (1,1,1))
        mask_zone = doptions.get('mask_zone', True)
        base_index = doptions.get('base_index', 1)
        grids = [v.grid_data(subregion, step, mask_zone) for v in vlist]
        from VolumeData import save_grid_data
        if is_multifile_save(path):
            for i,g in enumerate(grids):
                save_grid_data(g, path % (i + base_index), format, options)
        else:
            save_grid_data(grids, path, format, options)
   
# -----------------------------------------------------------------------------
# Check if file name contains %d type format specification.
#
def is_multifile_save(path):
    try:
        path % 0
    except:
        return False
    return True
   
# -----------------------------------------------------------------------------
#
def level_and_color_settings(v, options):

    kw = {}

    levels = options.get('level', [])
    colors = options.get('color', [])

    # Allow 0 or 1 colors and 0 or more levels, or number colors matching
    # number of levels.
    if len(colors) > 1 and len(colors) != len(levels):
        raise syn, ('Number of colors (%d) does not match number of levels (%d)'
                  % (len(colors), len(levels)))

    style = options.get('style', v.representation)
    if style in ('mesh', None):
        style = 'surface'

    if style == 'solid':
        if [l for l in levels if len(l) != 2]:
            raise syn, 'Solid level must be <data-value,brightness-level>'
    elif style == 'surface':
        if [l for l in levels if len(l) != 1]:
            raise syn, 'Surface level must be a single data value'
        levels = [lvl[0] for lvl in levels]

    if levels:
        kw[style+'_levels'] = levels

    if len(colors) == 1:
        if levels:
            clist = [colors[0]]*len(levels)
        else:
            clist = [colors[0]]*len(getattr(v, style + '_levels'))
        kw[style+'_colors'] = clist
    elif len(colors) > 1:
        kw[style+'_colors'] = colors

    if len(levels) == 0 and len(colors) == 1:
        kw['default_rgba'] = colors[0]

    if 'brightness' in options:
        kw[style+'_brightness_factor'] = options['brightness']

    if 'transparency' in options:
        if style == 'surface':
            kw['transparency_factor'] = options['transparency']
        else:
            kw['transparency_depth'] = options['transparency']

    return kw

# -----------------------------------------------------------------------------
#
def region(v, options):

    if 'region' in options or 'step' in options:
        r = v.subregion(options.get('step', None),
                        options.get('region', None))
    else:
        r = None
    return r

# -----------------------------------------------------------------------------
#
def data_option_parse_table():

    opt = {
        'style': lambda f,k: parse_string(f, k, ('surface', 'mesh', 'solid')),
        'brightness': lambda f,k: parse_values(f, k, float),
        'transparency': lambda f,k: parse_values(f, k, float),
        'step': parse_step,
        'region': parse_region,
        'name_region': parse_string,
        'origin': lambda f,k: parse_values(f, k, float, (1,3)),
        'origin_index': lambda f,k: parse_values(f, k, float, (1,3)),
        'voxel_size': lambda f,k: parse_values(f, k, float, (1,3)),
        'symmetry': parse_symmetry,
        'save': parse_string,
        'save_format': parse_string,
        'save_region': parse_region,
        'save_step': parse_step,
        'mask_zone': parse_boolean,
        'chunk_shapes': lambda f,k: parse_values(f, k, str, range(1,7)),
        'append': parse_boolean,
        'compress': parse_boolean,
        'base_index': lambda f,k: parse_values(f, k, int),
        }
    dopt = {}
    for k,v in opt.items():
        def p(f,opt,k=k,v=v):
            opt[k] = v(f,k)
            return f[1:]
        dopt[k] = p

    # Special case: 'show' and 'hide' take no second argument.
    for k in ('show', 'hide'):
        def p(f,opt,k=k):
            opt[k] = True
            return f
        dopt[k] = p

    # Special case: 'level' and 'color' accumulate values.
    for k,v in (('level', lambda f,k: parse_values(f, k, float, (1,2))),
                ('color', parse_color)):
        def p(f,opt,k=k,v=v):
            if k in opt:   opt[k].append(v(f,k))
            else:          opt[k] = [v(f,k)]
            return f[1:]
        dopt[k] = p

    # Arguments are axis,pstart,pend,pstep,pdepth.
    def p(f,opt,k='planes'):
        axis, param = (f[0].split(',',1) + [''])[:2]
        opt[k] = ([parse_string(axis,k,('x','y','z'))] +
                  parse_values([param], k, int, (1,2,3,4)))
        return f[1:]
    dopt['planes'] = p

    return dopt

# -----------------------------------------------------------------------------
#
def global_option_parse_table():

    keys = ('data_cache_size', 'show_on_open', 'voxel_limit_for_open',
            'show_plane', 'voxel_limit_for_plane')
    from volume import default_settings
    d = {}
    for k in keys:
        d[k] = default_settings[k]
    gopt = parse_table(d)
    return gopt

# -----------------------------------------------------------------------------
#
def rendering_option_parse_table():

    from volume import Rendering_Options
    ro = Rendering_Options()
    ropt = parse_table(ro.__dict__)
    def p(f,opt,k='outline_box_rgb'):
        opt[k] = parse_color(f,k)[:3]
        return f[1:]
    ropt['outline_box_rgb'] = p
    return ropt

# -----------------------------------------------------------------------------
#
def parse_table(dict):

    pt = {}
    for k,v in dict.items():
        if type(v) in (bool, int, float):
            def p(f,opts,k=k,t=type(v)):
                opts[k] = parse_values(f, k, t)
                return f[1:]
            pt[k] = p
        elif type(v) == str:
            if (k + 's') in dict:  allowed_values = dict[k+'s']
            else:                  allowed_values = None
            def p(f,opts,k=k,a=allowed_values):
                opts[k] = parse_string(f, k, a)
                return f[1:]
            pt[k] = p
            
    return pt

# -----------------------------------------------------------------------------
#
def option_name_table(*ptables):

    opt = {}
    for ptable, settings in ptables:
        for key, parse in ptable.items():
            k = key.lower().replace('_','')
            opt[k] = lambda f,p=parse,s=settings: p(f,s)

    # Add unique prefix abbreviations.
    kab = {}
    for k in opt.keys():
        for e in range(1, len(k)-1):
            ka = k[:e]
            if ka in kab or ka in opt:
                kab[ka] = None
            else:
                kab[ka] = k
    for ka,k in kab.items():
        if k:
            opt[ka] = opt[k]

    return opt

# -----------------------------------------------------------------------------
#
def parse_boolean(fields, name):

    if len(fields) == 0:
        raise syn, 'Missing %s value' % name

    b = boolean_value(fields[0])
    return b

# -----------------------------------------------------------------------------
#
def boolean_value(b):

    bl = b.lower()
    if bl in ('0', 'false', 'f', 'off', 'no', 'n'):
        return False
    elif bl in ('1', 'true', 't', 'on', 'yes', 'y'):
        return True
    else:
        raise syn, 'Invalid boolean value "%s"' % b

# -----------------------------------------------------------------------------
#
def parse_string(fields, name, allowed_values = None):

    if len(fields) == 0:
        raise syn, 'Missing %s value' % name

    if not allowed_values is None and not fields[0] in allowed_values:
        raise syn, ('Invalid %s "%s", should be one of %s'
                    % (name, fields[0], ', '.join(allowed_values)))

    return fields[0]

# -----------------------------------------------------------------------------
#
def parse_values(fields, name, vtype, nallowed = 1, string_ok = False):

    if len(fields) == 0:
        raise syn, 'Missing %s value' % name

    if vtype is bool:
        vtype = boolean_value

    invalid = False
    try:
        values = [vtype(f) for f in fields[0].split(',')]
    except:
        invalid = True

    if type(nallowed) is int:
        nallowed = (nallowed,)

    if invalid:
        msg = 'Invalid %s "%s"'
    elif not len(values) in nallowed:
        msg = 'Wrong number of %s values "%s"'
    else:
        msg = ''
    if msg:
        if string_ok:
            return fields[0]
        raise syn, msg % (name, fields[0])

    if nallowed == (1,):
        return values[0]

    return values

# -----------------------------------------------------------------------------
#
def parse_step(fields, name):

    values = parse_values(fields, name, int, (1,3))
    if len(values) == 1:
        v = values[0]
        values = (v,v,v)
    return values

# -----------------------------------------------------------------------------
# Accept 6 comma-separated numbers or "all" or the name of a subregion.
#
def parse_region(fields, name):

    v6 = parse_values(fields, name, int, (6,), string_ok = True)
    if isinstance(v6, basestring):
        values = v6
    else:
        values = (v6[:3], v6[3:])
    return values

# -----------------------------------------------------------------------------
#
def parse_color(fields, name):

    if len(fields) == 0:
        raise syn, 'Missing %s value' % name

    # Color from color dialog
    if fields[0] in ('colorpanel', 'fromeditor', 'editor'):
        from CGLtk.color import ColorWell
        if not ColorWell._colorPanel:
            from chimera import dialogs
            dialogs.display("color editor")
            raise syn, 'Choose color in panel first'
        return ColorWell.colorPanel().rgba

    # Chimera color defined with colordef
    from chimera import Color
    c = Color.lookup(fields[0])
    if c:
        return c.rgba()

    try:
        # Tk color name.
        from chimera.tkgui import app
        color = [c/65535.0 for c in app.winfo_rgb(fields[0])]
    except:
        # Comma separated list of rgb or rgba float values.
        color = parse_values(fields, 'color', float, (3,4))

    return color
    
# -----------------------------------------------------------------------------
#
def parse_symmetry(fields, name):

    if len(fields) == 0:
        raise syn, 'Missing %s value' % name

    spec = fields[0].split(',')
    if spec[0] != 'icos':
        raise syn, 'Invalid symmetry spec "%s", must start with "icos"' % fields[0]
    if len(spec) == 1:
        csname = '222'
    else:
        from Icosahedron import coordinate_system_names
        if spec[1] in coordinate_system_names:
            csname = spec[1]
        else:
            raise syn, 'Unknown icosahedral symmetry coordinate system "%s", use %s' % (spec[1], '|'.join(coordinate_system_names))

    from Icosahedron import icosahedral_symmetry_matrices
    smat = icosahedral_symmetry_matrices(csname)
    return smat

# -----------------------------------------------------------------------------
#
def volumes_from_specifier(spec):

    from chimera import specifier
    try:
        sel = specifier.evalSpec(spec)
    except:
        return []

    from volume import Volume, volume_list
    vlist = [m for m in sel.models() if isinstance(m, Volume)]

    # Translate solid volume models to volume models.
    from _volume import Volume_Model
    svlist = [m for m in sel.models() if isinstance(m, Volume_Model)]
    for s in svlist:
        for v in volume_list():
            if s in v.models():
                if not v in vlist:
                    vlist.append(v)
                break

    return vlist
