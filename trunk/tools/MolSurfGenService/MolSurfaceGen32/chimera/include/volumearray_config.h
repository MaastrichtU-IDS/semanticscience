#ifndef VOLUMEARRAY_CONFIG_HEADER_INCLUDED
#define VOLUMEARRAY_CONFIG_HEADER_INCLUDED

# ifndef VOLUMEARRAY_DLL
#  define VOLUMEARRAY_IMEX
# elif defined(VOLUMEARRAY_EXPORT)
#  define VOLUMEARRAY_IMEX __declspec(dllexport)
# else
#  define VOLUMEARRAY_IMEX __declspec(dllimport)
# endif

#endif
