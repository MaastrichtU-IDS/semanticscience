#ifndef Chimera_SharedState_h
# define Chimera_SharedState_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <string>
# include <set>
# include "TrackChanges.h"

namespace chimera {

// SharedState is a base class for use by collaboratory-aware
// extensions.  The intention is that all variables that need to
// be synchronized are placed within a "state" variable of the
// extension.  The "state" variable derives from SharedState
// and automatically fires a notifier when a Python attribute is
// changed.  This causes the collaboratory code to try to propagate
// changes to remote collaborators.

class CHIMERA_IMEX SharedState: public NotifierList, public otf::WrapPyObj
{
public:
	typedef std::set<std::string>	Updates;
private:
	SharedState(const SharedState&);		// disable
	SharedState& operator=(const SharedState&);	// disable
	PyObject	*extension_;
	Updates		updates_;
public:
	SharedState(PyObject *ext);
	virtual ~SharedState();

	// ATTRIBUTE: _extension
	PyObject	*_extension() const { Py_INCREF(extension_);
						return extension_; }
	const Updates	&getUpdates() const { return updates_; }
	void		clearUpdates() { updates_.clear(); }
	void		touch(const std::string &a) { updates_.insert(a); }
	int		set(PyObject *key, PyObject *value,
						bool silent = false);
	int		update(PyObject *d, bool silent = false);

#ifndef WrapPy
	virtual PyObject* wpyNew() const;

	virtual void	notify(const NotifierReason &reason) const;
	virtual void	wpyAssociate(PyObject* o) const;
	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason CHANGE;
#endif
protected:
	static TrackChanges::Changes *const changes;
};

#ifndef WrapPy
extern "C" {
int SharedState_setAttrO(PyObject *obj, PyObject *name, PyObject *value);
}
#endif

} // namespace chimera

#endif
