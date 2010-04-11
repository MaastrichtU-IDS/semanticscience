#ifndef Chimera_TrackChanges_h
# define Chimera_TrackChanges_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <set>
# include <map>
# include <vector>
# include <stdexcept>
# include <string.h>
# include "_chimera_config.h"
# include "Notifier.h"

extern "C" {
typedef struct _object PyObject;
}

#ifndef WrapPy

namespace otf {

template <> PyObject* pyObject(const chimera::NotifierReason* nr);
template <> inline PyObject*
pyObject(const chimera::NotifierReason& nr) { return pyObject(&nr); }

} // namespace otf

#endif

namespace chimera {

// TrackChanges provides a singleton instance (from get()) that is used
// to keep track of those Python Objects that have been modified since
// the last time it was "clear"ed.  A C++ class "enroll"s itself, and
// instances of that class update the Changes set directly.  A list of
// the "enrolled" classes is available.  You can "check" which classes
// have instances that changed and fetch those "changes".  Instances
// may use the NotifierList mechanism to be notified when a "check" is
// done.

class CHIMERA_IMEX TrackChanges: public NotifierList, public otf::WrapPyObj
{
	TrackChanges(const TrackChanges&);		// disable
	TrackChanges& operator=(const TrackChanges&);	// disable
public:
	static TrackChanges *get();
#ifndef WrapPy
	class CHIMERA_IMEX What {
		typedef std::set<PyObject *> Data;
		Data data;
		What &operator=(const What &);      // too lazy to implement
	public:
		What() {}
		What(const What& w);
		~What();
		typedef Data::iterator iterator;
		typedef Data::const_iterator const_iterator;
		typedef Data::size_type size_type;
		void insert(PyObject *obj);
		void clear();
		bool empty() const { return data.empty(); }
		bool has(PyObject *obj) { return data.find(obj) != data.end(); }
		iterator begin() { return data.begin(); }
		iterator end() { return data.end(); }
		const_iterator begin() const { return data.begin(); }
		const_iterator end() const { return data.end(); }
		size_type erase(PyObject *const &key);
		void erase(iterator i);
	};
	class CHIMERA_IMEX Reasons {
		typedef std::set<const NotifierReason *> Data;
		Data data;
	public:
		typedef Data::iterator iterator;
		typedef Data::const_iterator const_iterator;
		typedef Data::size_type size_type;
		void insert(const NotifierReason &nr) { data.insert(&nr); }
		void clear() { data.clear(); }
		bool empty() const { return data.empty(); }
		bool has(const NotifierReason& nr)
					{ return data.find(&nr) != data.end(); }
		iterator begin() { return data.begin(); }
		iterator end() { return data.end(); }
		const_iterator begin() const { return data.begin(); }
		const_iterator end() const { return data.end(); }
	};
#else
	// simplify what wrappy needs to generate interface
	typedef std::set<PyObject *> What;
	typedef std::set<PyObject *> Reasons;
#endif
	struct CHIMERA_IMEX Changes {
		// IMPLICIT COPY CONSTRUCTOR
		What	created;
		What	deleted;
		What	modified;
		Reasons	reasons;	// modified reasons
#ifndef WrapPy
		void	addCreated(PyObject *obj) { created.insert(obj); }
		void	addDeleted(PyObject *obj);
		void	addModified(PyObject *obj, const NotifierReason &nr)
				{ modified.insert(obj); reasons.insert(nr); }
#else
		// READONLY: created
		// READONLY: deleted
		// READONLY: modified
		// READONLY: reasons
#endif
	};
#ifndef WrapPy
	Changes		&enroll(const char *name);
#endif
	Changes		&enroll(PyObject *name);
	typedef std::vector<const char *> Names;
	Names		enrolled() const;
	Names		check();
	void		sync();
	const Changes	&changes(const char *name);
	void		clear();
	void		addModified(PyObject* obj, const char* reason);
#ifndef WrapPy
	virtual PyObject* wpyNew() const;

	// notification reasons
	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	static Reason CHECK;
#endif
private:
	TrackChanges(): NotifierList(this) {}

	struct ltstr {
		bool operator()(const char *s1, const char *s2) const {
			return ::strcmp(s1, s2) < 0;
		}
	};
	typedef std::map<const char *, Changes, ltstr> ChangeMap;
	ChangeMap	allChanges;

	// Add TrackChanges to the classes that TrackChanges knows about
	// so when new classes are enrolled, something can trigger off of it.
	static TrackChanges::Changes *const
			myChanges;
	static Reason	ENROLL;

	typedef std::map<const char *, NotifierReason, ltstr> ExtraNotifierReasons;
	ExtraNotifierReasons
			extraNotifierReasons;
	void		checkType(PyTypeObject* to, PyObject* obj,
						const NotifierReason& reason);
};

// Simple form of trackReason that works with a single public
// TrackChanges::Changes object named changes.  Classes with
// subclasses that have TrackChanges objects may their own
// version.  It is recommended that a virtual trackReason
// function be used in base classes.
template <class CLASS>
void trackReason(const CLASS *obj, const NotifierReason &reason)
{
	PyObject *pyObj = obj->wpyGetObject(otf::PWC_DONT_CREATE);
	if (pyObj != NULL) {
		CLASS::changes->addModified(pyObj, reason);
		Py_DECREF(pyObj);
	}
}

} // namespace chimera

#endif
