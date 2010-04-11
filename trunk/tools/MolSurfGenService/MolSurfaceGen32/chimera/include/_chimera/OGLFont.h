#ifndef Chimera_OGLFont_h
# define Chimera_OGLFont_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include <string>
# include "_chimera_config.h"
# include "Notifier.h"

class FTFont;

namespace chimera {

class CHIMERA_IMEX OGLFont: public otf::WrapPyObj
{
	OGLFont(const OGLFont &f);		// disable
	OGLFont &operator=(const OGLFont &f);	// disable
public:
	static OGLFont *defaultFont();
	static void setDefaultFont(/*NULL_OK*/ OGLFont *f);
	enum Style {
		normal = 0x0, bold = 0x1, roman = 0x2, italic = 0x4,
		underline = 0x8, overstrike = 0x10
	};
	OGLFont(const std::string &name, int size, int style = 0);
	~OGLFont();
	otf::Symbol	name() const;
	int		size() const;
	int		style() const;

# ifndef WrapPy
	void		draw(const char *s, int len = 0) const;
	void		setColor(float rbga[4]);
	void		updateLOD(const NotifierReason &);

	virtual PyObject* wpyNew() const;
# endif
	void		setup();
	void		cleanup();
	void		setColor(float r, float b, float g, float a = 1.0f);
	void		draw(const std::string &str, int len = 0) const;
	float		width(const std::string &str, int len = 0) const;
	std::pair<float, float>
			height(const std::string &str, int len = 0) const;
	bool		valid() const;
	std::string	x3dFamily() const;
	std::string	x3dStyle() const;
	const std::string &filename() const;	
private:
	FTFont	*fi;
	otf::Symbol	name_;
	int		size_;
	int		style_;
	std::string	x3dFamily_;
	std::string	filename_;

	class LODNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const {
			OGLFont *f = static_cast<OGLFont *>
						(const_cast<void *>(tag));
			f->updateLOD(reason);
		}
	};
	LODNotifier	lodNotifier;
};

# ifndef WrapPy

inline bool
OGLFont::valid() const
{
	return fi != 0;
}

inline void
OGLFont::draw(const std::string &str, int len) const
{
	draw(str.c_str(), len ? len : str.length());
}

inline const std::string &
OGLFont::filename() const
{
	return filename_;
}

# endif /* WrapPy */

} // namespace chimera

#endif
