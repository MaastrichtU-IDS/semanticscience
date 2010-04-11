#ifndef Chimera_LensViewer_h
# define Chimera_LensViewer_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Geom3d.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include <vector>
# include <map>
# include "_chimera_config.h"
# include "Viewer.h"
# include <GfxInfo.h>

extern "C" {
struct Togl;
}

namespace chimera {

using otf::Geom3d::Real;
using otf::Geom3d::Point;
using otf::Geom3d::Vector;
using otf::Geom3d::Xform;

class ScreenBox;
class GfxState;
class Lens;
class Selectable;
class Tile;
class Model;
class Light;

typedef std::vector<ScreenBox> ScreenBoxes;

class CHIMERA_IMEX LensViewer: public Viewer
{
	LensViewer(const LensViewer&);			// disable
	LensViewer& operator=(const LensViewer&);	// disable
public:
	LensViewer();
	~LensViewer();

	enum DrawPass {
		OpaqueSurfaces,	// draw opaque surfaces
		Labels,		// draw 3D positioned text labels
		LitLines,	// draw lit lines and points
		UnlitLines,	// draw unlit lines, points, and 2d labels
		Translucent1,	// draw back of translucent surface
		Translucent2,	// draw front of translucent surface, volumes
		Overlay2d,	// draw 2d overlay graphics
		LowRes,		// draw low-resolution version for sideview
		Selection,	// draw selectable geometry
		NumDrawPass
	};

	// selection highlighting methods
	enum Highlight { Outline, Fill };
	Highlight	highlight() const;
	void		setHighlight(Highlight h);
	Color		*highlightColor() const;
	void		setHighlightColor(/*NULL_OK*/ Color *color);
	bool		localViewer() const;
	void		setLocalViewer(bool lv);
	bool		showSilhouette() const;
	void		setShowSilhouette(bool s);
	Color		*silhouetteColor() const;
	void		setSilhouetteColor(/*NULL_OK*/ Color *color);
	float		silhouetteWidth() const;
	void		setSilhouetteWidth(float w);
	bool		showShadows() const;
	void		setShowShadows(bool s);

	// associated lenses
	// ATTRIBUTE: backgroundLens
	Lens		*backgroundLens() const;
#if 0
	bool		lensBorder() const;
	void		setLensBorder(bool lb);
	Color		*lensBorderColor() const;
	void		setLensBorderColor(/*NULL_OK*/ Color *color);
	float		lensBorderWidth() const;
	void		setLensBorderWidth(float w);
#endif

	// depth-cueing
	bool		depthCue() const;
	void		setDepthCue(bool dc);
	Color		*depthCueColor() const;
	void		setDepthCueColor(/*NULL_OK*/ Color *color);
	void		depthCueRange(/*OUT*/ float *start, /*OUT*/ float *end);
	void		setDepthCueRange(float start, float end);

	// lighting
	Light		*fillLight() const;
	void		setFillLight(/*NULL_OK*/ Light *l);
	Light		*keyLight() const;
	void		setKeyLight(/*NULL_OK*/ Light *l);

	// opengl shaders
	bool		haveShaderSupport() const;
	void		setShader(/*NULL_OK*/ const char *vshader,
				  /*NULL_OK*/ const char *fshader);
	bool		haveShader() const;
	void		enableShader(bool enable) const;
	void		deleteShader();

	// debugging
	bool		showBound() const;
	void		setShowBound(bool show);
	bool		showCofR() const;
	void		setShowCofR(bool show);

	// image support
	//	pilImages() is an internal interface -- do not use it!
	//	Use chimera.printer.saveImage() instead.
	PyObject	*pilImages(int width = 0, int height = 0,
				const char *printMode = NULL,
				int supersample = 0,
				bool opacity = false) const;
	// images need to use special rasterPos3 to work when tiling
#ifndef WrapPy
	void		rasterPos3(float x, float y, float z);
#endif
	void		rasterPos3(double x, double y, double z);

	// export support
	void		x3dWrite(const std::string &filename,
						const std::string& title = "");
	void		x3dWrite(std::ostream &out, unsigned indent = 0,
						const std::string& title = "");

	// gui support -- we assume that all Model's that can be affected
	//	by the gui are accessible through the background lens.
	void		recordPosition(int time, int x, int y, /*NULL_OK*/ const char *cursor);
	Xform		vsphere(int time, int x, int y, bool throttle = false);
	bool		startAutoSpin(int time, int x, int y);
	void		translateXY(int x, int y, bool throttle = false);
	void		translateZ(int x, int y, bool throttle = false);
	void		zoom(int x, int y, bool throttle = false);
	void		dragPick(int x, int y);
	void		pick(int x, int y,
				/*OUT*/ std::vector<Selectable *> *objs);
	void		pickLabel(int x, int y, /*OUT*/ Selectable **objs);
	void		moveLabel(int x, int y, bool adjustZ, /*INOUT*/ Point *coord);
#if 0
	void		selectLens(int x, int y);
	void		moveLens(int x, int y);
#endif
	void		delta(/*OUT*/ Real *dx, /*OUT*/ Real *dy, int x, int y, bool throttle = false);
	void		trackingXY(const char *mode, /*OUT*/ int *x, /*OUT*/ int *y);

	// per-model plane gui
	// WEAKREF: showPlaneModel
	bool		showPlaneModel() const;
	void		setShowPlaneModel(/*NULL_OK*/ Model *m, float opacity);

	// togl support
	void		createCB(PyObject *widget);
	void		destroyCB(PyObject *widget);
	void		reshapeCB(PyObject *widget);
	void		displayCB(PyObject *widget);
	void		updateCB(PyObject *widget);

	// for graphics benchmarking:
	//	0 -- use swapbuffers, 1 -- use glFlush, 2 -- use glFinish
	int		benchmarking() const;
	void		setBenchmarking(int i);

	// environment map support
	bool		envMap() const;
	void		setEnvMap(bool onoff);
	// ATTRIBUTE: envMapImage
	void		setEnvMapImages(PyObject *px, PyObject *nx,
					PyObject *py, PyObject *ny,
					PyObject *pz, PyObject *nz);

# ifndef WrapPy
	virtual void	draw() const;
	virtual void	postRedisplay() const;
	virtual void	invalidateSelectionCache() const;
	virtual void	invalidateCache() const;
	virtual void	addModel(Model *m);
	virtual void	removeModel(Model *m);
	virtual void	windowSize(/*OUT*/ int *width, /*OUT*/ int *height) const;
	virtual void	setWindowSize(int width, int height);
	virtual void	windowOrigin(/*OUT*/ int *x, /*OUT*/ int *y) const;
	virtual bool	hasGraphicsContext() const;
	virtual void	makeGraphicsContextCurrent() const;
	virtual void	setCursor(/*NULL_OK*/ const char *cursor);
	virtual void	notify(const NotifierReason &reason) const;

	void		drawBackground() const;
	Tile		*tile() const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
# endif
	// use z-buffer support
	bool		saveZbuffer() const;
	void		setSaveZbuffer(bool s);
	void		parallax(/*OUT*/ float *negative, /*OUT*/ float *positive);
private:
	friend class GuardFBO;
	mutable Togl	*togl;
	GfxState	*state_;

	Lens		*backgroundLens_;
	Highlight	highlight_;
	Color		*highlightColor_;
	bool		localViewer_;
	bool		showSilhouette_;
	Color		*silhouetteColor_;
	float		silhouetteWidth_;
	bool		showShadows_;
#if 0
	bool		border;
	Color		*borderColor_;
	float		borderWidth_;
#endif

	bool		depthCue_;
	Color		*fog;
	float		startDepth_;
	float		endDepth_;
	static void	drawFog(const otf::Array<double, 4> &rgba);
	virtual void	setBackground(/*NULL_OK*/ Color *c);

	virtual void	updateCamera(const NotifierReason &);

	void		updateLens(Lens *lens, const NotifierReason &);
	class CHIMERA_IMEX LensNotifier: public Notifier {
	public:
		void update(const void *tag, void *lens,
					const NotifierReason &reason) const {
			LensViewer *lv = static_cast<LensViewer *>
						(const_cast<void *>(tag));
			Lens *l = static_cast<Lens *>(lens);
			lv->updateLens(l, reason);
}
	};
	friend class LensNotifier;
	LensNotifier	lensNotifier;

	// opengl shader
	GLuint shaderProgram, vertexShader, fragmentShader;
	GLuint compileAndAttachShader(const char *code, GLenum t, GLuint p);

	// gui temporaries
	Real		vsphereCenter[2];
	Real		vsphereRadius;	// TODO: [2] for cheap stereo
	ScreenBoxes	*selectedLenses;
	enum Anchor { N, NE, E, SE, S, SW, W, NW, Center };
	Anchor		lensAnchor;
	Vector		spinAxis;
	Real		spinAngle;
	int		lastTime, lastX, lastY;
	bool		pickAreaVisible;
	int		pickX, pickY;
	void		drawPickArea() const;

	void		updateLOD(const NotifierReason &r);
	class CHIMERA_IMEX LODNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const {
			LensViewer *lv = static_cast<LensViewer *>
						(const_cast<void *>(tag));
			lv->updateLOD(reason);
		}
	};
	friend class LODNotifier;
	LODNotifier	lodNotifier;

	Model		*planeModel;
	float		planeModelOpacity;
	void		updatePlaneModel(const NotifierReason &r);
	class CHIMERA_IMEX PlaneModelNofifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const {
			LensViewer *lv = static_cast<LensViewer *>
						(const_cast<void *>(tag));
			lv->updatePlaneModel(reason);
		}
	};
	friend class PlaneModelNofifier;
	PlaneModelNofifier
			planeModelNotifier;

	bool		showBound_;
	bool		showCofR_;
	void		drawScreenBoxes(const otf::Array<int, 4> &vBox,
				ScreenBoxes::iterator first,
				ScreenBoxes::iterator last) const;
	void		drawSilhouette(const otf::Array<int, 4> &vBox,
				DrawPass dp,
				ScreenBoxes::iterator first,
				ScreenBoxes::iterator last) const;
	mutable Tile	*tile_;
	mutable	bool	skipLODNotification;

	Light		*fill;
	Light		*key;
	void		updateLight(Light *light, const NotifierReason &);
	class CHIMERA_IMEX LightNofifier: public Notifier {
	public:
		void update(const void *tag, void *light,
					const NotifierReason &reason) const {
			LensViewer *lv = static_cast<LensViewer *>
						(const_cast<void *>(tag));
			Light *l = static_cast<Light *>(light);
			lv->updateLight(l, reason);
		}
	};
	friend class LightNofifier;
	LightNofifier	lightNotifier;

	int		benchmarking_;

	// The following are for the OSMesa windowing system, but are always
	// included so instances of this class are the same size regardless of
	// windowing system.
	int		myWidth;
	int		myHeight;
	unsigned char	*framebuffer;
	mutable bool	updatePending;

	// use z-buffer support
	bool		saveZbuffer_;
	float		*zbuffer;

	// environment map support
	bool		envMap_;
	GLuint		envMapImages;

	// shadow support
	mutable GLuint	shadowMap;		// texture id
	mutable GLsizei	shadowMapSide;		// square shadow maps (for now)
	void		setupLightView(/*OUT*/ otf::Array<int, 4> *vp,
				/*OUT*/ otf::Array<double, 16> *proj,
				/*OUT*/ otf::Array<double, 16> *modelview) const;
	void		computeLightFrustum(const Xform &lightFrame,
				/*OUT*/ otf::Array<double, 16> *proj) const;
	void		finishLightView() const;
};

# ifndef WrapPy

inline Lens *
LensViewer::backgroundLens() const
{
	return backgroundLens_;
}

#if 0
inline bool
LensViewer::lensBorder() const
{
	return border;
}

inline Color *
LensViewer::lensBorderColor() const
{
	return borderColor_;
}

inline float
LensViewer::lensBorderWidth() const
{
	return borderWidth_;
}
#endif

inline LensViewer::Highlight
LensViewer::highlight() const
{
	return highlight_;
}

inline Color *
LensViewer::highlightColor() const
{
	return highlightColor_;
}

inline bool
LensViewer::localViewer() const
{
	return localViewer_;
}

inline bool
LensViewer::showSilhouette() const
{
	return showSilhouette_;
}

inline Color *
LensViewer::silhouetteColor() const
{
	return silhouetteColor_;
}

inline float
LensViewer::silhouetteWidth() const
{
	return silhouetteWidth_;
}

inline bool
LensViewer::showShadows() const
{
	return showShadows_;
}

inline bool
LensViewer::showBound() const
{
	return showBound_;
}

inline bool
LensViewer::showCofR() const
{
	return showCofR_;
}

inline Tile *
LensViewer::tile() const
{
	return tile_;
}

inline bool
LensViewer::depthCue() const
{
	return depthCue_;
}

inline Color *
LensViewer::depthCueColor() const
{
	return fog;
}

inline Light *
LensViewer::fillLight() const
{
	return fill;
}

inline Light *
LensViewer::keyLight() const
{
	return key;
}

inline int
LensViewer::benchmarking() const
{
	return benchmarking_;
}

inline bool
LensViewer::saveZbuffer() const
{
	return saveZbuffer_;
}

inline bool
LensViewer::envMap() const
{
	return envMap_;
}

# endif /* WrapPy */

} // namespace chimera

#endif
