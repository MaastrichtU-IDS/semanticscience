#ifndef Chimera_TextureColor_h
# define Chimera_TextureColor_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include "_chimera_config.h"
# include "Color.h"
# include "Texture.h"

namespace chimera {

class CHIMERA_IMEX TextureColor: public Color
{
	TextureColor(const TextureColor&);		// disable
	TextureColor& operator=(const TextureColor&);	// disable
public:
	TextureColor(Texture *texture, double s);
	TextureColor(Texture *texture, double s, double t);
	TextureColor(Texture *texture, double s, double t, double r);
	TextureColor(Texture *texture, double s, double t, double r, double q);
	TextureColor(const TextureColor &t0, const TextureColor &t1, double fraction);
	~TextureColor();
	// ATTRIBUTE: texture
	Texture		*texture() const;
	// ATTRIBUTE: dimension
	int		dimension() const;
	void		coords(/*OUT*/ double *s, /*OUT*/ double *t = 0,
			/*OUT*/ double *r = 0, /*OUT*/ double *q = 0) const;
	void		setCoords(double s);
	void		setCoords(double s, double t);
	void		setCoords(double s, double t, double r);
	void		setCoords(double s, double t, double r, double q);
# ifndef WrapPy
	virtual otf::Array<double, 4>
			rgba() const;
	virtual bool	isTranslucent() const throw ();
# endif
# ifndef WrapPy
	virtual void	draw() const throw ();
	virtual ColorGroup *
			colorGroup() const;
	virtual void	x3dWrite(std::ostream& out, unsigned indent, unsigned count) const;
	virtual void	notify(const NotifierReason &reason) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
# endif
private:
	Texture		*tex;
	enum Size { ONE, TWO, THREE, FOUR };
	Size		dimension_;
	GLdouble	strq[4];
	static TrackChanges::Changes *const
			changes;
};

# ifndef WrapPy

inline Texture *
TextureColor::texture() const
{
	return tex;
}

inline ColorGroup *
TextureColor::colorGroup() const
{
	return tex;
}

inline int
TextureColor::dimension() const
{
	return int(dimension_) + 1;
}

# endif /* WrapPy */

} // namespace chimera

#endif
