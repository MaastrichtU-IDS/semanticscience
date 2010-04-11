## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Library of colors matching PyMol color names.
"""

def rgbf2rgbi(rgbf):
    """Converts a RGB/float color into a RGB/integer.
    """
    return (int(rgbf[0]*255.0), int(rgbf[1]*255.0), int(rgbf[2]*255.0))


def rgbi2rgbf(rgbf):
    """Converts a RGB/integer color into a RGB/float.
    """
    return (int(rgbf[0]*255.0), int(rgbf[1]*255.0), int(rgbf[2]*255.0))

COLORS = [
    ('white', (1.0, 1.0, 1.0)),
    ('black', (0.0, 0.0, 0.0)),
    ('blue', (0.0, 0.0, 1.0)),
    ('green', (0.0, 1.0, 0.0)),
    ('magenta', (1.0, 0.0, 1.0)),
    ('red', (1.0, 0.0, 0.0)),
    ('cyan', (0.0, 1.0, 1.0)),
    ('yellow', (1.0, 1.0, 0.0)),
    ('violet', (1.0, 0.5, 1.0)),
    ('purpleblue', (0.5, 0.0, 1.0)),
    ('salmon', (1.0, 0.6, 0.5)),
    ('lime', (0.5, 1.0, 0.5)),
    ('slate', (0.5, 0.5, 1.0)),
    ('bluegreen', (0.0, 1.0, 0.5)),
    ('hotpink', (1.0, 0.0, 0.5)),
    ('orange', (1.0, 0.5, 0.0)),
    ('yellowgreen', (0.5, 1.0, 0.0)),
    ('blueviolet', (0.5, 0.0, 1.0)),
    ('marine', (0.0, 0.5, 1.0)),
    ('olive', (0.75, 0.75, 0.0)),
    ('purple', (0.75, 0.0, 0.75)),
    ('teal', (0.0, 0.75, 0.75)),
    ('ruby', (0.5, 0.1, 0.1)),
    ('forest', (0.1, 0.5, 0.1)),
    ('deep', (0.1, 0.1, 0.5)),
    ('gray', (0.5, 0.5, 0.5)),
    ('carbon', (0.2, 1.0, 0.2)),
    ('nitrogen', (0.2, 0.2, 1.0)),
    ('oxygen', (1.0, 0.3, 0.3)),
    ('hydrogen', (0.9, 0.9, 0.9)),
    ('brightorange', (1.0, 0.7, 0.2)),
    ('sulfur', (1.0, 0.5, 0.0)),
    ('tv_red', (1.0, 0.2, 0.2)),
    ('tv_green', (0.2, 1.0, 0.2)),
    ('tv_blue', (0.3, 0.3, 1.0)),
    ('tv_yellow', (1.0, 1.0, 0.2)),
    ('tv_orange', (1.0, 0.55, 0.15)),
    ('br0', (0.1, 0.1, 1.0)),
    ('br1', (0.2, 0.1, 0.9)),
    ('br2', (0.3, 0.1, 0.8)),
    ('br3', (0.4, 0.1, 0.7)),
    ('br4', (0.5, 0.1, 0.6)),
    ('br5', (0.6, 0.1, 0.5)),
    ('br6', (0.7, 0.1, 0.4)),
    ('br7', (0.8, 0.1, 0.3)),
    ('br8', (0.9, 0.1, 0.2)),
    ('br9', (1.0, 0.1, 0.1)),
    ('pink', (1.0, 0.65, 0.85)),
    ('firebrick', (0.697, 0.13, 0.13)),
    ('chocolate', (0.555, 0.222, 0.111)),
    ('brown', (0.555, 0.274, 0.15)),
    ('wheat', (0.99, 0.82, 0.65))
    ]

COLOR_NAMES             = []
COLOR_NAMES_CAPITALIZED = []
COLOR_RGBF              = {}
COLOR_RGBI              = {}

for name, rgb in COLORS:
    COLOR_NAMES.append(name)
    COLOR_NAMES_CAPITALIZED.append(name.capitalize())
    COLOR_RGBF[name] = rgb
    COLOR_RGBI[name] = rgbf2rgbi(rgb)
