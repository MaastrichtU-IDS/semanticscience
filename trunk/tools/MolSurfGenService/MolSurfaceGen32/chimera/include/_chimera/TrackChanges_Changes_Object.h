#ifndef chimera_TrackChanges_Changes_object_h
# define chimera_TrackChanges_Changes_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "TrackChanges.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject TrackChanges_Changes_objectType;

struct TrackChanges_Changes_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (TrackChanges::Changes) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	TrackChanges::Changes* _inst() { return reinterpret_cast<TrackChanges::Changes*>(_inst_data); }
};

CHIMERA_IMEX extern TrackChanges::Changes* getInst(TrackChanges_Changes_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::TrackChanges::Changes>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::TrackChanges_Changes_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::TrackChanges::Changes* _o);
template <> inline PyObject* pyObject(chimera::TrackChanges::Changes _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(chimera::TrackChanges::Changes const* _o) { return pyObject(const_cast<chimera::TrackChanges::Changes*>(_o)); }

} // namespace otf

#endif
