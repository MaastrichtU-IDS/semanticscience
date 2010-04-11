#ifndef Chimera_chimera_config_h
# define Chimera_chimera_config_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# ifndef CHIMERA_DLL
#  define CHIMERA_IMEX
# elif defined(CHIMERA_EXPORT)
#  define CHIMERA_IMEX __declspec(dllexport)
# else
#  define CHIMERA_IMEX __declspec(dllimport)
# endif

# ifdef CHIMERA_X11
#  ifndef GFXINFO_X11
#   define GFXINFO_X11
#  endif
# endif

# ifdef CHIMERA_WGL
#  ifndef GFXINFO_WGL
#   define GFXINFO_WGL
#  endif
# endif

# ifdef CHIMERA_AGL
#  ifndef GFXINFO_AGL
#   define GFXINFO_AGL
#  endif
# endif

# ifdef CHIMERA_OSMESA
#  ifndef GFXINFO_OSMESA
#   define GFXINFO_OSMESA
#  endif
# endif

// Assume 32 bit pointers unless CHIMERA_64BIT is defined.
// CHIMERA_64BITPTR is only used for passing pointers through
// OpenGL's name stack of 32 bit values.

# ifdef __alpha
#  define CHIMERA_64BITPTR
# endif

# if defined(__mips) && _MIPS_SZPTR == 64
#  define CHIMERA_64BITPTR
# endif

# if defined(__GNUC__) && defined(__LP64__)
#  define CHIMERA_64BITPTR
# endif

# endif /* WrapPy */

#endif
