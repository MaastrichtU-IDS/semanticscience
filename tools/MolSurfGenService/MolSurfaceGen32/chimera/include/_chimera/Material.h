#ifndef Chimera_Material_h
# define Chimera_Material_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Array.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include "_chimera_config.h"
# include "ColorGroup.h"
# include "NameMap.h"
# include <GfxInfo.h>

namespace chimera {

class CHIMERA_IMEX Material: public ColorGroup, public Name<Material>
{
public:
	Material(otf::Symbol name);
	virtual	~Material();

# ifndef WrapPy
	// We use materials, so we can use glColor instead of glMaterial
	// to switch colors.
	virtual void	draw(bool lit) const throw ();
	virtual void	undraw() const throw ();
	void		baseDraw() const throw ();	// for Texture
	virtual void	x3dWrite(std::ostream& out, unsigned indent, bool lit,
					const Color* single = NULL) const;
# endif
# if 0
	virtual bool	operator<(const ColorGroup &o) const;
	virtual bool	operator==(const ColorGroup &o) const;
# endif
# ifndef WrapPy
	virtual bool	isTranslucent() const throw ();
# endif

	otf::Array<double, 3>	ambientDiffuse() const;
	otf::Array<double, 3>	specular() const;
	double		shininess() const;
	double		opacity() const;

# ifndef WrapPy
	void		setAmbientDiffuse(const otf::Array<double, 3> &ad);
# endif
	void		setAmbientDiffuse(double r, double g, double b);
# ifndef WrapPy
	void		setSpecular(const otf::Array<double, 3> &s);
# endif
	void		setSpecular(double r, double g, double b);
	void		setShininess(double s);
	void		setOpacity(double o);

# ifndef WrapPy
	virtual void	notify(const NotifierReason &reason) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
# endif
#if defined(WrapPy)
	// wrappy can't handle Name<Material> yet
	// Note: C++ still sees NameMap as map<Symbol, Name<Material> >.
	typedef std::map<otf::Symbol, Material*> NameMap;
	typedef std::pair<NameMap::const_iterator, NameMap::const_iterator> NameMapRange;
	static Material* lookup(otf::Symbol name);
	//static void remove(otf::Symbol name) throw ();
	static NameMapRange list() throw ();
	void save(otf::Symbol name) throw (std::logic_error);
	void remove() throw ();
	otf::Symbol name() const throw ();
# endif
private:
	GLdouble	ambDiff[4];	// default color
	GLdouble	spec[4];
	GLdouble	shine;
	GLuint		odl;		// OpenGL display list(s)
	void		recompileODL();
	static TrackChanges::Changes* const
			changes;
};

} // namespace chimera

#endif
