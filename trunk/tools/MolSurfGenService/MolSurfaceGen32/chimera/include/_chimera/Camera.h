#ifndef Chimera_Camera_h
# define Chimera_Camera_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

/*
 * Copyright (c) 1989,1997 Regents of the University of California.
 * All rights reserved.  This software provided pursuant to a
 * license agreement containing restrictions on its disclosure,
 * duplication and use.  This notice must be embedded in or
 * attached to all copies, including partial copies, of the
 * software or any revisions or derivations thereof.
 *
 * $Id: Camera.h 29605 2009-12-14 22:06:37Z gregc $
 */

# include <vector>
# include <otf/Array.h>
# include <otf/WrapPy2.h>
# include "_chimera_config.h"
# include "Notifier.h"
# include "TrackChanges.h"
# include <otf/Geom3d.h>

# ifdef _WIN32
#  undef near
#  undef far
# endif

// This module supports the rendering of multiple views of the same scene.
// Conceptually, it is a camera with one or more views.  A stereo camera
// would have two views, one for each eye.  It could be used to generate
// the three views needed for three side-by-side projectors as well.
// The camera also calculates the values needed for perspective or
// orthographic rendering.

# ifndef NULL
#  define NULL	0
# endif

namespace chimera {

using otf::Geom3d::Point;
using otf::Geom3d::Xform;

class CameraMode;
class Viewer;
class Model;

#ifndef WrapPy

struct CHIMERA_IMEX CameraModeParams
{
	// Common calculated values amoung camera modes
	double	E;	// Ratio of eye separation to window width
	double	R;	// Ratio of screen halfwidth to viewing distance
	double	a;	// Aspect ratio of viewport
	double	d;	// Dist from front of cube
			// that encloses view to focal plane
	double	s;	// X-dist from mono eye to stereo eye
	double	l;	// Z-dist from mono eye to stereo eye
	double	f;	// Dist of stereo eye to focal plane
	double	h;	// Dist of stereo eye to hither plane
	double	y;	// Dist of stereo eye to yon plane
};

// right-handed versions
inline double	zDist(double near, double far) { return near - far; }
inline double	zAdd(double z, double dist) { return z + dist; }

#endif /* ifndef WrapPy */

class CHIMERA_IMEX Camera: public NotifierList, public otf::WrapPyObj
{
	Camera(const Camera&);			// disable
	Camera& operator=(const Camera&);	// disable
public:
	typedef int	View;

	Camera(double windowWidth, double fov, double eyeSep, int llx, int lly, int urx, int ury);
	~Camera();

	// builtin modes are mono, crosseye, walleye, lefteye, righteye
	bool		setMode(const char *type, const Viewer *viewer = NULL);
	const char	*mode() const;
# ifndef WrapPy
	void		setTileMode(/*NULL_OK*/ CameraMode *mode);
	static void	addMode(CameraMode *mode);
	static CameraMode *
			findMode(const char *mode);
# endif
	static bool	hasMode(const char *mode);
	static std::vector<const char *>
			modes(bool printOnly = false, bool all = false);

	bool		ortho() const;
	void		setOrtho(bool o);

	bool		autoFocus() const;
	void		setAutoFocus(bool b);

	// near, focal, far are right-handed z-coordinate values from eye
	// focal corresponds to the view center
	double		focal() const;
	void		nearFar(/*OUT*/ double *near, /*OUT*/ double *far) const;
	const otf::Array<double, 3> &
			center() const;
	// Note: extent is maintained by viewer's scaleFactor and viewSize.
	double		extent() const;
	void		setFocal(double f);
	void		setNearFar(double h, double y);
# ifndef WrapPy
	void		setCenter(double [3]);
# endif
	void		setCenter(double x, double y, double z);
	void		setExtent(double e);
	double		eyeZ() const;

	// ATTRIBUTE: projectionExtent
	double		projectionExtent() const;
	// ATTRIBUTE: focalExtent
	double		focalExtent() const;
	// ATTRIBUTE: hitherExtent
	double		hitherExtent() const;

	double		walleyeScale() const;
	void		setWalleyeScale(double ws);

	// eye offset describes where the eye is relative
	// to the center line (line parallel to the
	// z-axis and going through the view center).
	// The values are fractions relative to the
	// displayed extent.
	void		setEyeOffset(double x, double y);
	void		eyeOffset(/*OUT*/ double *x, /*OUT*/ double *y) const;

	void		setViewport(int llx, int lly, int width, int height);
	int		llx() const;
	int		lly() const;
	int		urx() const;
	int		ury() const;

	int		numViews() const;
	View		lastView() const;
	bool		printOnly() const;
	void		printViews(/*OUT*/ std::vector<std::pair<View, int> > *views);
	void		viewport(View v, /*OUT*/ otf::Array<int, 4> *vp) const;
	void		eyePos(View v, /*OUT*/ otf::Array<double, 3> *eyepos) const;
	void		atPos(View v, /*OUT*/ otf::Array<double, 3> *atpos) const;
	void		window(View v, /*OUT*/ otf::Array<double, 7> *w) const;

			// viewXform returns the initial value of the OpenGL
			// modelview matrix and must be multiplied by the
			// model matrix to get value used for the modelview
			// matrix.
	void		viewXform(View v, /*OUT*/ Xform *xf) const;
	void		viewXform(View v, const Model *m, /*OUT*/ Xform *xf) const;
			// projMatrix returns the OpenGL projection matrix
	void		projMatrix(View v, /*OUT*/ otf::Array<double, 16> *proj) const;

			// convert world coordinates to opengl clip coordinates
	Point		clipCoordinates(View v, const Point &p) const;
	
	// the field of view is given in degrees.
	// the eye separation is in millimeters.
	// the screen distance is the distance to the screen in millimeters
	// and is computed from the window width and field of view.
	double		fieldOfView() const;
	void		setFieldOfView(double fov);
	double		windowWidth() const;
	void		setWindowWidth(double w);
	double		screenDistance() const;
	void		setScreenDistance(double d);
	double		eyeSeparation() const;
	void		setEyeSeparation(double es);

	bool		isStereoMode() const;
	static int	lenticularImageCount();
	static void	setLenticularImageCount(int ni);

# ifndef WrapPy
	bool		needBackgroundClear(View v) const;
	void		setupView(const Viewer *viewer, View v) const;
	void		setupPick(double x, double y, double xSize, double ySize) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;

	void		notify(const NotifierReason &reason) const;
	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notification reasons
	static Reason MODE_CHANGED;
	static Reason TILE_MODE_CHANGED;
	static Reason ORTHO_CHANGED;
	static Reason AUTO_FOCUS_CHANGED;
	static Reason FOCAL_CHANGED;
	static Reason NEAR_FAR_CHANGED;
	static Reason CENTER_CHANGED;
	static Reason EXTENT_CHANGED;
	static Reason WALLEYE_SCALE_CHANGED;
	static Reason EYE_OFFSET_CHANGED;
	static Reason VIEWPORT_CHANGED;
	static Reason FIELD_OF_VIEW_CHANGED;
	static Reason WINDOW_WIDTH_CHANGED;
	static Reason EYE_SEPARATION_CHANGED;

	// the next two are for CameraMode routines
	CameraModeParams	params;

	void		x3dWrite(std::ostream &out, unsigned indent, View v) const;
# endif /* ifndef WrapPy */

private:
	void		recomputeParams();
	void		recompute() const;
	CameraMode	*smode;
	double		near_, far_, focal_;	// z plane coordinates
	otf::Array<double, 3>
			center_;		// view center
	double		extent_;		// view extent
	double		eyeOffsetX_, eyeOffsetY_;
	int		llx_, lly_, urx_, ury_;	// actual viewport
	bool		ortho_;
	bool		autoFocus_;
	mutable bool	dirty;

	// see comments in public interface
	double		fieldOfView_;
	double		windowWidth_;
	double		eyeSeparation_;

	// computed (not settable) parameters
	double		tanFov_;		// tangent of half fov angle
	double		focalExtent_;		// extent at the focal plane
	double		hitherExtent_;		// extent at hither plane
						// above two only apply to
						// perspective view

	// vp_separation is number of scanlines in FullScreen stereo
	// between the top and bottom viewports
	double		vpSeparation;		// Viewport separation (0)

	double		walleyeScale_;		// 1.0
	static TrackChanges::Changes *const
			changes;
	CameraMode	*savedSMode;		// for printMode()
	double		savedExtent;		// for printMode()
	void		*smodeData;
	mutable View	lastView_;
};

# ifndef WrapPy

inline bool
Camera::ortho() const
{
	return ortho_;
}

inline bool
Camera::autoFocus() const
{
	return autoFocus_;
}

inline const otf::Array<double, 3> &
Camera::center() const
{
	return center_;
}

inline double
Camera::extent() const
{
	return extent_;
}

inline double
Camera::focalExtent() const
{
	return focalExtent_;
}

inline double
Camera::projectionExtent() const
{
	if (ortho_)
		return extent();
	else
		return hitherExtent();
}

inline double
Camera::hitherExtent() const
{
	return hitherExtent_;
}

inline int
Camera::llx() const
{
	return llx_;
}

inline int
Camera::lly() const
{
	return lly_;
}

inline int
Camera::urx() const
{
	return urx_;
}

inline int
Camera::ury() const
{
	return ury_;
}

inline Camera::View
Camera::lastView() const
{
	return lastView_;
}

inline double
Camera::walleyeScale() const
{
	return walleyeScale_;
}

inline double
Camera::fieldOfView() const
{
	return fieldOfView_;
}

inline double
Camera::windowWidth() const
{
	return windowWidth_;
}

inline double
Camera::eyeSeparation() const
{
	return eyeSeparation_;
}

# endif /* WrapPy */

} // namespace chimera

#endif
