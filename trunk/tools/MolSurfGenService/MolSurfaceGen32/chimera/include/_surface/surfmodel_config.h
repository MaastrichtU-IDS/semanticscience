#ifndef SURFMODEL_CONFIG_HEADER_INCLUDED
#define SURFMODEL_CONFIG_HEADER_INCLUDED

# ifndef SURFMODEL_DLL
#  define SURFMODEL_IMEX
# elif defined(SURFMODEL_EXPORT)
#  define SURFMODEL_IMEX __declspec(dllexport)
# else
#  define SURFMODEL_IMEX __declspec(dllimport)
# endif

#endif
