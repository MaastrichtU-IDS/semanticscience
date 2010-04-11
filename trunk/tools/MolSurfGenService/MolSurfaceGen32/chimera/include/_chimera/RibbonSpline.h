#ifndef RIBBONSPLINE_H
#define	RIBBONSPLINE_H

#include <map>
#include <string>
#include <otf/WrapPy2.h>
#include <otf/Symbol.h>
#include "_chimera_config.h"

namespace chimera {

extern void initRibbonResidueClasses();

class RibbonResidueClass;
typedef std::map<std::string, RibbonResidueClass *> RibbonResidueClasses;

class CHIMERA_IMEX RibbonResidueClass : public otf::WrapPyObj {
public:
	typedef std::map<otf::Symbol, float> Position;
private:
	otf::Symbol	guide_;
	otf::Symbol	plane_;
	bool		planeNormal_;		// false = binormal
	bool		isNucleic_;		// false ~ amino acid
	Position	position_;

	static RibbonResidueClasses classes_;
	friend void initRibbonResidueClasses();
public:
				RibbonResidueClass(const otf::Symbol &g,
							const otf::Symbol &p,
							bool pn,
							bool n);
				RibbonResidueClass(const char *g,
							const char *p,
							bool pn,
							bool n);
	const otf::Symbol	&guide() const;
	const otf::Symbol	&plane() const;
	bool			isNucleic() const;
	bool			planeNormal() const;
	bool			hasPosition(const otf::Symbol &name) const;
	std::pair<bool, float>	position(const otf::Symbol &name) const;
	void			addPosition(const otf::Symbol &name, float d);
	void			removePosition(const otf::Symbol &name);
	const Position		&positions() const;
	// some convenience functions so not everyone need to use Symbol
	std::pair<bool, float>	position(const char *name) const;
	void			addPosition(const char *name, float d);
	void			removePosition(const char *name);

	virtual PyObject *	wpyNew() const;

	static const RibbonResidueClasses &
				classes();
	static void		registerClass(const char *name,
						RibbonResidueClass *klass);
	static void		deregisterClass(const char *name);
};

inline const otf::Symbol &
RibbonResidueClass::guide() const
	{ return guide_; }

inline const otf::Symbol &
RibbonResidueClass::plane() const
	{ return plane_; }

inline bool
RibbonResidueClass::isNucleic() const
	{ return isNucleic_; }

inline bool
RibbonResidueClass::planeNormal() const
	{ return planeNormal_; }
	
inline const RibbonResidueClass::Position &
RibbonResidueClass::positions() const
	{ return position_; }
	
inline std::pair<bool, float>
RibbonResidueClass::position(const char *name) const
	{ return position(otf::Symbol(name)); }

inline void
RibbonResidueClass::addPosition(const char *name, float d)
	{ addPosition(otf::Symbol(name), d); }

inline void
RibbonResidueClass::removePosition(const char *name)
	{ removePosition(otf::Symbol(name)); }

inline const RibbonResidueClasses &
RibbonResidueClass::classes()
	{ return classes_; }

} // namespace chimera

#endif
