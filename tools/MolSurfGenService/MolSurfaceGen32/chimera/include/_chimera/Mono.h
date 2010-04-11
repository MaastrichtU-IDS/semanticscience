#ifndef Chimera_Mono_h
# define Chimera_Mono_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include "Camera.h"
# include "CameraMode.h"

namespace chimera {

class CHIMERA_IMEX Mono: public CameraMode {
	CameraView	mono;
	void		setup(const Viewer *v, int view) const;
public:
	Mono(const char *n): CameraMode(n) {}
	int		numViews() const;
	const CameraView *
			view(int view) const;
	void		computeViews(const Camera &camera);
};

CHIMERA_IMEX extern Mono mono;

} // namespace chimera

# endif /* WrapPy */

#endif
