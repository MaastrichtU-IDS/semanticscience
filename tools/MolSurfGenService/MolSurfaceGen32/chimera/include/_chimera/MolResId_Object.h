#ifndef chimera_MolResId_object_h
# define chimera_MolResId_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include <otf/molkit/MolResId.h>
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject MolResId_objectType;

struct MolResId_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (otf::MolResId) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	otf::MolResId* _inst() { return reinterpret_cast<otf::MolResId*>(_inst_data); }
};

CHIMERA_IMEX extern otf::MolResId* getInst(MolResId_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<otf::MolResId>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::MolResId_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(otf::MolResId* _o);
template <> inline PyObject* pyObject(otf::MolResId _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(otf::MolResId const* _o) { return pyObject(const_cast<otf::MolResId*>(_o)); }

} // namespace otf

#endif
