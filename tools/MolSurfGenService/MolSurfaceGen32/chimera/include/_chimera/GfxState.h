#ifndef Chimera_GfxState_h
# define Chimera_GfxState_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include "_chimera_config.h"

typedef void	*GfxContext;		// GLXContext on X11 systems

namespace chimera {

// GfxState maintains information about graphics state
// and the helps maintain the Chimera graphics policies

class CHIMERA_IMEX GfxState {
public:
	static GfxState *fromCurrentContext();
	GfxState(GfxContext context);
	~GfxState();
	GfxContext	context() const;
	void		initialize(bool multisampling);
	bool		lights() const;
	void		setLights(bool onOff);
	bool		antiAlias() const;
	void		setAntiAlias(bool onOff);
	bool		multisampling() const;
	void		setMultisampling(bool onOff);
	void		restoreDefault();
	static void	setCurrent(GfxState *);
	static GfxState	*current();
	static float	version();
	enum Has { Not = 0x0, Extension = 0x01, Native = 0x02 };
	bool		blendByDefault() const;
	bool		useSeparateBlend() const;
	static void	setEnableSeparateBlend(bool on);
	static bool	separateBlendEnabled();
	static void	setFaceCulling(bool on);
	static bool	faceCullingEnabled();
	void		startBlending() const;
	void		stopBlending() const;
	static void	debugDump(std::ostream &os);
private:
	GfxState(const GfxState &gs);			// disable (for now)
	GfxState &operator=(const GfxState &gs);	// disable (for now)
	static GfxState	*current_;

	GfxContext	ctx;
	bool		lit;		// true if lights are on
	bool		antialias_;
	bool		defaultBlending;
	bool		separateBlend;
	bool		multisampling_;
	static bool	enableSeparateBlend;
	static bool	enableFaceCulling;
};

inline GfxContext
GfxState::context() const
{
	return ctx;
}

inline bool
GfxState::lights() const
{
	return lit;
}

inline bool
GfxState::antiAlias() const
{
	return antialias_;
}

inline bool
GfxState::blendByDefault() const
{
	return defaultBlending;
}

inline bool
GfxState::useSeparateBlend() const
{
	return separateBlend;
}

inline bool
GfxState::separateBlendEnabled()
{
	return enableSeparateBlend;
}

inline bool
GfxState::faceCullingEnabled()
{
	return GfxState::enableFaceCulling;
}

inline bool
GfxState::multisampling() const
{
	return multisampling_;
}

} // namespace chimera

# endif /* WrapPy */

#endif
