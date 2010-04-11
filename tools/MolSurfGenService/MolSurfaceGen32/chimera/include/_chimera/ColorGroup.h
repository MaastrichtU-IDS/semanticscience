#ifndef Chimera_ColorGroup_h
# define Chimera_ColorGroup_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <typeinfo>
# include <otf/WrapPy2.h>
# include "TrackChanges.h"

namespace chimera {

class Color;

// ColorGroups are the colors used to sort and build OpenGL display lists.
// Colors in this sense are materials and textures.
//
// Note:  this is very different than the Color (sub)class(es) presented
// in the user interface and as such should not be exposed to "user."

class CHIMERA_IMEX ColorGroup: public NotifierList, public otf::WrapPyObj
{
	// ABSTRACT
	// Notice that there are no public constructors because ColorGroup
	// pointers must point to an instance of a subclass.
protected:
	ColorGroup(): NotifierList(this) {}
public:
	// Assuming that having a virtual function is faster than RTTI.
	virtual bool	isTexture() const { return false; }

#ifndef WrapPy
	// Drawing support:  when building a display list, it is important
	// to know what the last drawn color was to minimize the OpenGL
	// state changes.
	//
	// undraw only needs to be called in 2 cases:
	//	1) in draw() when lastDrawn is of a different subtype,
	//	2) when building display lists, at the end to undo any
	//		side effects.  (We sometimes use ColorGroups outside
	//		of display lists.)
	virtual void	draw(bool lit) const throw ();
	virtual void	undraw() const throw ();
	static void	undoDrawEffects() throw ();
	virtual void	x3dWrite(std::ostream& out, unsigned indent, bool lit,
					const Color* single = NULL) const;
#endif

	virtual bool	isTranslucent() const throw () = 0;
#if 0
	// ColorGroup instances are sorted by subclass
	virtual bool	operator<(const ColorGroup &d) const {
				if (typeid(*this) != typeid(d))
					return typeid(*this).before(typeid(d));
				return this < &d;
			}
	virtual bool	operator==(const ColorGroup &d) const {
				if (typeid(*this) != typeid(d))
					return false;
				return this == &d;
			}
#endif

#ifndef WrapPy
	virtual PyObject* wpyNew() const;

	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason CHANGE;	// minor color change -- redisplay
#endif
protected:
	static TrackChanges::Changes *const
			changes;
	static const ColorGroup	*lastDrawn;
};

} // namespace chimera

#endif
