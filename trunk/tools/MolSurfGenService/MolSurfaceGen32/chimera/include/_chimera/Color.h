#ifndef Chimera_Color_h
# define Chimera_Color_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Array.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include <typeinfo>
# include "_chimera_config.h"
# include "Notifier.h"
# include "TrackChanges.h"
# include "NameMap.h"

namespace chimera {

class ColorGroup;

class CHIMERA_IMEX Color: public NotifierList, public Name<Color>,
							public otf::WrapPyObj
{
	// ABSTRACT
	// Color's encapsulate the OpenGL color and texture properties
	// of vertices.
public:
	virtual otf::Array<double, 4>
			rgba() const = 0;
	virtual bool	isTranslucent() const throw () = 0;

#ifndef WrapPy
	virtual void	draw() const throw () = 0;
	virtual ColorGroup*
			colorGroup() const = 0;
	virtual void	x3dWrite(std::ostream& out, unsigned indent, unsigned count) const;

	// Color instances are sorted by colorgroup
	virtual bool	operator<(const Color &c) const {
				if (typeid(*this) != typeid(c))
					return typeid(*this).before(typeid(c));
				const ColorGroup* a = this->colorGroup();
				const ColorGroup* b = c.colorGroup();
				if (a == b)
					return this < &c;
				return a < b;
			}
	virtual bool	operator==(const Color &c) const {
				return this == &c;
			}

	virtual PyObject* wpyNew() const;

	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char* r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason CHANGE;	// color change (remake display list?)
#endif

#if defined(WrapPy)
	// wrappy can't handle Name<Color> yet
	// Note: C++ still sees NameMap as map<Symbol, Name<Color> >.
	typedef std::map<otf::Symbol, Color*> NameMap;
	typedef std::pair<NameMap::const_iterator, NameMap::const_iterator> NameMapRange;
	static Color* lookup(otf::Symbol name);
	//static void remove(otf::Symbol name) throw ();
	static NameMapRange list() throw ();
	void save(otf::Symbol name) throw (std::logic_error);
	void remove() throw ();
	otf::Symbol name() const throw ();
	virtual ~Color();
private:
	typedef std::map<Color*, otf::Symbol> BackMap;
	static NameMap	all;
	static BackMap	back;
#endif
protected:
	// Note: there are no public constructors because Color
	// pointers must point to an instance of a subclass.
	Color(): NotifierList(this) {}
	static TrackChanges::Changes* const
			changes;
};

} // namespace chimera

#endif
