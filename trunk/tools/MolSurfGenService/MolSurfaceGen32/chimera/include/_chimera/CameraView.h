#ifndef Chimera_CameraView_h
# define Chimera_CameraView_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

namespace chimera {

// Don't need export CameraView because it has no methods
struct CameraView {
	double	eye[3];			// Eye position
	double	lookat[3];		// Lookat coordinate
	double	l, r, b, t, h, y, f;	// ortho/frustrum bounds
					// left, right, bottom, top, hither,
					// yon, focal
	int	llx, lly, urx, ury;	// Viewport bounds
};

} // namespace chimera

# endif /* WrapPy */

#endif
