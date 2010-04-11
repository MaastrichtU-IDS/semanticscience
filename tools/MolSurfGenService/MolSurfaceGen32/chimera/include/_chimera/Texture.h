#ifndef Chimera_Texture_h
# define Chimera_Texture_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Array.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include "_chimera_config.h"
# include <GfxInfo.h>
# include "ColorGroup.h"
# include "NameMap.h"

namespace chimera {

class Material;
class PixelMap;

// Note: so textures can work in non-graphics programs, all of the OpenGL
// calls are guarded by checking to see if the display list exists.  And
// the display list is only created if we have a graphics context.

// All textures are MODULATEd.
// baseMaterial is used for 1 and 2 component textures.
// baseMaterial is white for 3 and 4 component textures.

class CHIMERA_IMEX Texture: public ColorGroup, public Name<Texture>
{
	Texture(const Texture&);		// disable
	Texture& operator=(const Texture&);	// disable
public:
	enum Formats {
		ColorIndex = GL_COLOR_INDEX,
		Red = GL_RED,
		Green = GL_GREEN,
		Blue = GL_BLUE,
		Alpha = GL_ALPHA,
		RGB = GL_RGB,
		RGBA = GL_RGBA,
		Luminance = GL_LUMINANCE,
		LuminanceAlpha = GL_LUMINANCE_ALPHA
	};
	enum Types {
		UnsignedByte = GL_UNSIGNED_BYTE, Byte = GL_BYTE,
		UnsignedShort = GL_UNSIGNED_SHORT, Short = GL_SHORT,
		UnsignedInt = GL_UNSIGNED_INT, Int = GL_INT,
		Float = GL_FLOAT, Double = GL_DOUBLE
	};
	Texture(otf::Symbol name, int format, int type, int width,
						int height = 1, int depth = 1);
	Texture(otf::Symbol name, PixelMap* colormap, int type, int width,
						int height = 1, int depth = 1);
	virtual ~Texture();

# ifndef WrapPy
	virtual bool	isTexture() const { return true; }
	virtual void	draw(bool lit) const throw ();
	virtual void	undraw() const throw ();
	virtual void	x3dWrite(std::ostream& out, unsigned indent, bool lit,
					const Color* single = NULL) const;
	// can't do any extra color sorting for textures
	// virtual bool	operator<(const ColorGroup &o) const;
	// virtual bool	operator==(const ColorGroup &o) const;
# endif

# ifndef WrapPy
	bool		isTranslucent() const throw ();
# endif
	void		*startEditing();
	void		finishEditing() const;
	int		dimension() const { return dim; }
	int		format() const { return imageFormat; }
	int		type() const { return imageType; }
	void		sizes(/*OUT*/ int* w, /*OUT*/ int* h, /*OUT*/ int* d,
					/*OUT*/ int* nc, /*OUT*/ int* nb);
	otf::Array<double, 4>	rgba(int index) const;
# ifndef WrapPy
	void		setRgba(int index, otf::Array<double, 4> value);
# endif
	void		setImage(PyObject* image);
	PyObject	*getImage() const;
	PixelMap	*pixelMap() const;
	void		setPixelMap(PixelMap* pixelMap);

	static int	computeComponents(int format);
	static int	computeDimension(int w, int h = 1, int d = 1);
	static int	computeTarget(int dim);
	static int	computeImageTypeBytes(int type);
# ifndef WrapPy
	virtual void	notify(const NotifierReason &reason) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
# endif
#if defined(WrapPy)
	// wrappy can't handle Name<Texture> yet
	// Note: C++ still sees NameMap as map<Symbol, Name<Texture> >.
	typedef std::map<otf::Symbol, Texture*> NameMap;
	typedef std::pair<NameMap::const_iterator, NameMap::const_iterator> NameMapRange;
	static Texture* lookup(otf::Symbol name) throw ();
	//static void remove(otf::Symbol name) throw ();
	static NameMapRange list() throw ();
	void save(otf::Symbol name) throw (std::logic_error);
	void remove() throw ();
	otf::Symbol name() const throw ();
private:
	typedef std::map<Texture* , otf::Symbol> BackMap;
	static NameMap	all;
	static BackMap	back;
# endif
private:
	void		commonInit(otf::Symbol name);
	GLenum		computeInternalFormat(int attempt) const;
	void		pixelMapDraw(int pass) const;
	static TrackChanges::Changes* const
			changes;

	void		updatePixelMap(const NotifierReason &);
	class PixelMapNotifier: public Notifier {
	public:
		void update(const void* tag, void*,
					const NotifierReason &reason) const;
	};
	friend class PixelMapNotifier;
	PixelMapNotifier	pixelMapNotifier;

	void		updateBaseMaterial(const NotifierReason &);
	class ColorGroupNotifier: public Notifier {
	public:
		void update(const void* tag, void*,
					const NotifierReason &reason) const;
	};
	friend class ColorGroupNotifier;
	ColorGroupNotifier
			baseMaterialNotifier;

	Material	*baseMaterial;
	GLenum		imageFormat, imageType;		// see gluScaleImage(3)
	GLsizei		imageWidth, imageHeight, imageDepth;
	PixelMap	*pm;
	void		*image;
	GLuint		dl;		// texture object (display list)
	int		nc;		// # of color components
	int		nb;		// # of bytes in imageType
	int		dim;		// 1, 2, or 3
	GLenum		target;		// GL_TEXTURE_1D, ...
};

# ifndef WrapPy

inline void
Texture::sizes(int* w, int* h, int* d, int* c, int* b)
{
	if (w)
		*w = imageWidth;
	if (h)
		*h = imageHeight;
	if (d)
		*d = imageDepth;
	if (c)
		*c = nc;
	if (b)
		*b = nb;
}

inline PixelMap*
Texture::pixelMap() const
{
	return pm;
}

# endif /* WrapPy */

} // namespace chimera

#endif
