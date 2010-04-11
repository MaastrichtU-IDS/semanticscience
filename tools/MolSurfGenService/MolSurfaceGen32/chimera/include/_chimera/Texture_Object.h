#ifndef chimera_Texture_object_h
# define chimera_Texture_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Texture.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Texture_objectType;

struct Texture_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Texture* _inst() { return static_cast<Texture*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Texture* getInst(Texture_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Texture>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Texture_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Texture* _o);
template <> inline PyObject* pyObject(chimera::Texture const* _o) { return pyObject(const_cast<chimera::Texture*>(_o)); }
template <> inline PyObject* pyObject(chimera::Name<chimera::Texture>* o) { return pyObject(static_cast<chimera::Texture*>(o)); }

} // namespace otf

#endif
