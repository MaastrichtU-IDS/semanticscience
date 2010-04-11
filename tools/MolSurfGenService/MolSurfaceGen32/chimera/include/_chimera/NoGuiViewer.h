#ifndef Chimera_NoGuiViewer_h
# define Chimera_NoGuiViewer_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include "_chimera_config.h"
# include "Viewer.h"

extern "C" {
struct Togl;
}

namespace chimera {

class CHIMERA_IMEX NoGuiViewer: public Viewer
{
public:
	NoGuiViewer();
	~NoGuiViewer();
# ifndef WrapPy
	virtual void	postRedisplay() const;
	virtual void	windowSize(int *width, int *height) const;
	virtual void	setWindowSize(int width, int height);
	virtual void	windowOrigin(int *x, int *y) const;
	virtual bool	hasGraphicsContext() const;
	virtual void	setCursor(const char *);
	virtual void	draw() const;
	virtual void	makeGraphicsContextCurrent() const;

	virtual PyObject* wpyNew() const;
# endif
private:
	int	width_;
	int	height_;
};

# ifndef WrapPy

inline bool
NoGuiViewer::hasGraphicsContext() const
{
	return false;
}

# endif /* WrapPy */

} // namespace chimera

#endif
