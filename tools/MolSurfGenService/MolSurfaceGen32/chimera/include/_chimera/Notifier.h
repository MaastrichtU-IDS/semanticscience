#ifndef Chimera_Notifier_h
# define Chimera_Notifier_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include <map>
# include <vector>
# include "_chimera_config.h"

namespace chimera {

// "Map has the important property that inserting a new element into a map
// does not invalidate iterators that point to existing elements. Erasing
// an element from a set also does not invalidate any iterators, except,
// of course, for iterators that actually point to the element that is
// being erased." -- SGI online STL documentation

class CHIMERA_IMEX NotifierReason {
	const char *explanation;
public:
	NotifierReason(): explanation("generic") {}
	NotifierReason(const char *why): explanation(why) {}
	NotifierReason(const NotifierReason& n): explanation(n.explanation) {}
	NotifierReason& operator=(const NotifierReason& n) {
		explanation = n.explanation;
		return *this;
	}
	virtual const char *reason() const { return explanation; }
	virtual ~NotifierReason() {}
	static NotifierReason DELETED;	// going away
};

class CHIMERA_IMEX Notifier {
protected:
	Notifier() {}
	virtual ~Notifier() {}
public:
	// the notifier tag is the instance that wants to be notified.
	// changed is the instance of the object that changed.
	// reason is the reason for the change.
	// If the reason is NotifierReason::DELETED, then the notifier
	// should be removed.
	virtual void update(const void *tag, void *changed,
					const NotifierReason &reason) const = 0;
};

class CHIMERA_IMEX NotifierList {
	typedef std::map<const void *, const Notifier *> NMap;
	mutable NMap	notifiers;
	mutable NMap	addList;		// used only if inNotify
	mutable bool	inNotify;
	void		*me;
	NotifierList(const NotifierList&);
	NotifierList& operator=(const NotifierList&);
public:
	NotifierList(void *tag): inNotify(false), me(tag) {}
	virtual ~NotifierList();
	// addNotification() and removeNotification() are const so they
	// do not change the const-ness of the class they are mixed into.
	void		addNotification(const void *tag, const Notifier *n,
					bool duplicateOkay = false) const;
	void		removeNotification(const void *tag) const;
	virtual void	notify(const NotifierReason &reason) const;
};

} // namespace chimera

# endif /* WrapPy */

#endif
