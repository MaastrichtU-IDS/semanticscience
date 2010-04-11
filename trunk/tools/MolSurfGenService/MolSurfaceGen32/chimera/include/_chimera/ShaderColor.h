#ifndef Chimera_ShaderColor_h
# define Chimera_ShaderColor_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Array.h>
# include "_chimera_config.h"
# include "Shader.h"
# include "Color.h"
# include <GfxInfo.h>

namespace chimera {

class CHIMERA_IMEX ShaderColor: public Color
{
	ShaderColor(const ShaderColor&);		// disable
	ShaderColor& operator=(const ShaderColor&);	// disable
public:
	ShaderColor(Shader *shader = NULL);
	ShaderColor(const ShaderColor &s0, const ShaderColor &s1, double fraction);
	virtual	~ShaderColor();
# ifndef WrapPy
	virtual otf::Array<double, 4>	rgba() const;
	virtual bool	isTranslucent() const throw ();
# endif

# ifndef WrapPy
	// We sort colors to group colors that have the same shader
	// so we can use glColor instead of glShader to switch colors.
	virtual void	draw() const throw ();
	virtual ColorGroup *colorGroup() const;
	virtual void	notify(const NotifierReason &reason) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
# endif
	// ATTRIBUTE: shader
	Shader	*shader() const;

private:
	void		commonInit();
	Shader		*shader_;
	static TrackChanges::Changes *const
			changes;
};

# ifndef WrapPy

inline Shader *
ShaderColor::shader() const
{
	return shader_;
}

inline ColorGroup *
ShaderColor::colorGroup() const
{
	return shader_;
}

# endif /* WrapPy */

} // namespace chimera

#endif
