#ifndef chimera_NoGuiViewer_object_h
# define chimera_NoGuiViewer_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "NoGuiViewer.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject NoGuiViewer_objectType;

struct NoGuiViewer_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	NoGuiViewer* _inst() { return static_cast<NoGuiViewer*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern NoGuiViewer* getInst(NoGuiViewer_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::NoGuiViewer>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::NoGuiViewer_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::NoGuiViewer* _o);
template <> inline PyObject* pyObject(chimera::NoGuiViewer const* _o) { return pyObject(const_cast<chimera::NoGuiViewer*>(_o)); }

} // namespace otf

#endif
