#ifndef Chimera_Viewer_h
# define Chimera_Viewer_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Array.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include <otf/Geom3d.h>
# include "_chimera_config.h"
# include "Notifier.h"
# include "TrackChanges.h"

namespace chimera {

using otf::Geom3d::Xform;

class Camera;
class Color;
class OpenModels;
class Atom;
class Model;
class Molecule;

class CHIMERA_IMEX Viewer: public NotifierList, public otf::WrapPyObj
{
	// ABSTRACT
	Viewer(const Viewer&);			// disable
	Viewer& operator=(const Viewer&);	// disable
public:
	virtual void	windowSize(/*OUT*/ int *width, /*OUT*/ int *height) const = 0;
	virtual void	setWindowSize(int width, int height) = 0;
	// ATTRIBUTE: windowOrigin
	virtual void	windowOrigin(/*OUT*/ int *x, /*OUT*/ int *y) const = 0;
# ifndef WrapPy
	virtual void	draw() const = 0;
	virtual void	makeGraphicsContextCurrent() const = 0;
# endif
	virtual void	postRedisplay() const = 0;
	virtual bool	hasGraphicsContext() const = 0;
	virtual void	setCursor(/*NULL_OK*/ const char *cursor) = 0;

	Color		*background() const;
	virtual void	setBackground(/*NULL_OK*/ Color *color);
	// ATTRIBUTE: selectionSet
	PyObject	*selectionSet() const;
	virtual void	invalidateSelectionCache() const;
	virtual void	invalidateCache() const;
	virtual void	addModel(Model *m);
	virtual void	removeModel(Model *m);
	Camera		*camera() const;
	void		setCamera(Camera *camera);
	double		viewSize() const;
	void		setViewSize(double size);
	double		scaleFactor() const;
	void		setScaleFactor(double sf);

	// opengl shaders
	bool		haveShaderSupport() const { return false; }
	bool		haveShader() const { return false; }

	// near/far clip planes enabled
	bool		clipping() const;
	void		setClipping(bool c);

	void		checkInitialView();
	void		resetView();
	void		viewAll(bool resetCofrMethod = true);
	void		touch();

	virtual void	destroy();

# ifndef WrapPy
	virtual PyObject* wpyNew() const;

	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notification reasons
	static Reason	ATTR_CHANGE;
	static Reason	CLIPPING_CHANGE;
	static Reason	TOUCH;
	static Reason	NEW_SELECTION;

# endif
	void		pdbWrite(const std::vector<Molecule *> &mList,
					const Xform &xform,
					const std::string &filename,
					bool allFrames = false,
					bool displayedOnly = false,
					bool selectedOnly = false);
	void		pdbWrite(const std::vector<Molecule *> &mList,
					const Xform &xform,
					std::ostream &out,
					bool allFrames = false,
					bool displayedOnly = false,
					bool selectedOnly = false);
# ifndef WrapPy
	void		pdbrun(bool all, bool conect, bool nouser,
				bool surface, bool nowait, bool markedOnly,
				std::map<chimera::Atom *,
					std::vector<otf::Symbol> > &marks,
				std::vector<otf::Symbol> &activeMarks,
				const std::string &shellCommand) const;
# endif
	// temporary until wrappy handles maps/vectors...
	void		pdbrunNoMarks(bool all, bool conect, bool nouser,
					bool surface, bool nowait,
					const std::string &shellCommand) const {
				std::map<Atom *, std::vector<otf::Symbol> >
									empty1;
				std::vector<otf::Symbol> empty2;
				pdbrun(all, conect, nouser, surface, nowait,
					false, empty1, empty2, shellCommand);
			}

protected:
	Viewer();
	virtual ~Viewer();
	static TrackChanges::Changes *const
			changes;
	void		defaultCamera() const;
	mutable Camera	*cam;
	double		viewSize_;
	double		scaleFactor_;
	Color		*bg;
	PyObject	*selectionSet_;
	bool		clipping_;
	mutable bool	didInitialView_;

	virtual void	updateCamera(const NotifierReason &);
	class CHIMERA_IMEX CameraNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const;
	};
	friend class CameraNotifier;
	CameraNotifier	cameraNotifier;

	void		updateOpenModels(OpenModels *, const NotifierReason &);
	class CHIMERA_IMEX OpenModelsNotifier: public Notifier {
		void update(const void *tag, void *openModels,
					const NotifierReason &reason) const;
	};
	friend class OpenModelsNotifier;
	OpenModelsNotifier
			openModelsNotifier;
};

# ifndef WrapPy

template <class C> inline bool
selected(PyObject *attrs, C *inst)
{
	if (attrs == NULL)
		return false;
	PyObject *obj = inst->wpyGetObject(otf::PWC_DONT_CREATE);
	if (obj == NULL)
		return false;
	bool inSelection = PyDict_GetItem(attrs, obj) != NULL;
	Py_DECREF(obj);
	return inSelection;
}

inline PyObject *
Viewer::selectionSet() const
{
	if (selectionSet_ == NULL)
		Py_RETURN_NONE;
	Py_INCREF(selectionSet_);
	return selectionSet_;
}

inline double
Viewer::viewSize() const
{
	return viewSize_;
}

inline double
Viewer::scaleFactor() const
{
	return scaleFactor_;
}

inline Color *
Viewer::background() const
{
	return bg;
}

# endif /* WrapPy */

} // namespace chimera

#endif
