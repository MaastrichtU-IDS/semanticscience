#ifndef Chimera_PixelMap_h
# define Chimera_PixelMap_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include "Texture.h"

namespace chimera {

class CHIMERA_IMEX PixelMap: public NotifierList, public Name<PixelMap>,
							public otf::WrapPyObj
{
public:
	static int maxLength();
	PixelMap(otf::Symbol name, int format, int type, int length);
	virtual ~PixelMap();
	// ATTRIBUTE: type
	int	type() const;
	// ATTRIBUTE: format
	int	format() const;
	void	sizes(/*OUT*/ int* len, /*OUT*/ int* nc);
	bool	isTranslucent() const throw ();
	void	*startEditing();
	void	finishEditing();
#if 0
	otf::Array<double, 4>
		rgba(int index) const;
	void	setRgba(int index, otf::Array<double, 4> value);
#endif
#ifndef WrapPy
	void	draw();
	void	undraw();

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;

	void	notify(const NotifierReason &reason) const;
	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char* r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason CHANGE;	// change -- reload dependent texture
#endif
#if defined(WrapPy)
	// wrappy can't handle Name<PixelMap> yet
	// Note: C++ still sees NameMap as map<Symbol, Name<PixelMap> >.
	typedef std::map<otf::Symbol, PixelMap*> NameMap;
	typedef std::pair<NameMap::const_iterator, NameMap::const_iterator> NameMapRange;
	static PixelMap* lookup(otf::Symbol name);
	//static void remove(otf::Symbol name) throw ();
	static NameMapRange list() throw ();
	void save(otf::Symbol name) throw (std::logic_error);
	void remove() throw ();
	otf::Symbol name() const throw ();
private:
	typedef std::map<PixelMap*, otf::Symbol> BackMap;
	static NameMap	all;
	static BackMap	back;
# endif
private:
	PixelMap(const PixelMap &p);			// disable (for now)
	PixelMap &operator=(const PixelMap &p);		// disable (for now)
	static TrackChanges::Changes* const
			changes;
	int	dataFormat;
	int	dataType;
	int	dataLength;
	void	*data;
};

# ifndef WrapPy

inline int
PixelMap::type() const
{	
	return dataType;
}

inline int
PixelMap::format() const
{
	return dataFormat;
}

# endif /* WrapPy */

} // namespace chimera

#endif
