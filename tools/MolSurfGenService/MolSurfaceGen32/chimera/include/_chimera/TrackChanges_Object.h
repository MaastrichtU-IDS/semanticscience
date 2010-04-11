#ifndef chimera_TrackChanges_object_h
# define chimera_TrackChanges_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "TrackChanges.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject TrackChanges_objectType;

struct TrackChanges_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	TrackChanges* _inst() { return static_cast<TrackChanges*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern TrackChanges* getInst(TrackChanges_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::TrackChanges>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::TrackChanges_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::TrackChanges* _o);
template <> inline PyObject* pyObject(chimera::TrackChanges const* _o) { return pyObject(const_cast<chimera::TrackChanges*>(_o)); }

} // namespace otf

#endif
