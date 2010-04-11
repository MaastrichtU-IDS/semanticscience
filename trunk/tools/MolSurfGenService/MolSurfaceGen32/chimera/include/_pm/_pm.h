#ifndef _pm_h
# define _pm_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

// include Python.h first so standard defines are the same
# define PY_SSIZE_T_CLEAN 1
# include <Python.h>
# include <new>
# include <otf/WrapPy2.h>

#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif
# include "_PythonModel_Object.h"

namespace _PythonModel {

extern void _pmError();
extern int _pmDebug;

} // namespace _PythonModel

#endif
