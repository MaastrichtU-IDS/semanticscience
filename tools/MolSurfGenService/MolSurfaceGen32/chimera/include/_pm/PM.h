#ifndef PM_INCLUDE
#define	PM_INCLUDE

#include <Python.h>
#include <otf/WrapPy2.h>
#include <_chimera/_chimera_config.h>
#include <_chimera/LensViewer_Object.h>
#include <_chimera/LensViewer.h>
#include <_chimera/Model_Object.h>
#include <_chimera/Lens_Object.h>
#include <_chimera/Point_Object.h>
#include <_chimera/BBox_Object.h>
#include <_chimera/Xform_Object.h>
#include <_chimera/Color.h>
#include <_chimera/LensModel.h>

#ifdef WrapPy

// Let wrappy know what's already been wrapped
// Need the full "Model" definition for wrappy to expose it
// in "_PythonModel"

namespace chimera {

typedef double	Real;
class Xform;
class BBox { };
class Point { };
class Vector { };

class Selectable : public otf::WrapPyObj
{
	// ABSTRACT
};

class Model : public Selectable
{
	// ABSTRACT
#if 0
public:
	const std::string &name() const;
	void		setName(const std::string &n);
	// ATTRIBUTE: id
	int		id() const;
	// ATTRIBUTE: subid
	int		subid() const;
	// ATTRIBUTE: active
	bool		active() const;
	bool		display() const;
	void		setDisplay(bool b);
	// ATTRIBUTE: xform
	const Xform	&xform() const;
	virtual bool	computeBounds(/*OUT*/ Sphere *s, /*OUT*/ BBox *bbox) const = 0;

	bool		overrideCofr() const;
	void		setOverrideCofr(bool b);
	Point		cofr() const;
	void		setCofr(const Point &pt);

	virtual void	destroy();
#endif
protected:
	Model();
	virtual ~Model();
};

class Viewer: public otf::WrapPyObj { };
class LensViewer: public Viewer, public otf::WrapPyObj { };
class Lens : otf::WrapPyObj { };

} // namespace chimera

#endif

namespace _PythonModel {

class _PythonModel : public chimera::Model {
	// BASE CLASS
public:
				_PythonModel();
	virtual			~_PythonModel();
	// destroy is not virtual because it doesn't have the same
	// parameters as the base class destroy and thus hides it regardless.
	void			destroy(bool fromPython = 0);
#ifdef WrapPy
	// expose Model class APIs that Python normally doesn't see
	void			setMinorChange();
	void			setMajorChange();
#endif
#ifndef WrapPy
	virtual bool		computeBounds(/*OUT*/ chimera::Sphere *s, /*OUT*/ chimera::BBox *box) const;
	virtual chimera::Selectable::Selectables
				oslChildren() const;
	virtual chimera::Selectable::Selectables
				oslParents() const;
	virtual void		notify(const chimera::NotifierReason &reason) const;
	virtual void		wpyAssociate(PyObject *o) const;
	virtual PyObject	*wpyNew() const;
private:
	virtual chimera::LensModel *
				newLensModel(chimera::Lens *lens);
	bool			closing;
	static chimera::TrackChanges::Changes *const
				changes;
#endif
};

#ifndef WrapPy
class PythonLensModel : public chimera::LensModel {
public:
	typedef chimera::LensViewer::DrawPass DrawPass;
				PythonLensModel(chimera::Lens *lens,
						_PythonModel *model);
	virtual			~PythonLensModel();
	virtual void		invalidateCache();
	virtual void		invalidateSelection();
	virtual chimera::Point	cofm() const;
	virtual chimera::Real	mass() const;
	virtual chimera::Model	*model() const;
	virtual bool		validXform() const;
	virtual void		draw(const chimera::LensViewer *viewer,
					chimera::LensViewer::DrawPass pass) const;
	virtual void		drawPick(const chimera::LensViewer *viewer) const;
	virtual void		x3dNeeds(/*INOUT*/ chimera::X3DScene *) const;
	virtual void		x3dWrite(std::ostream &out, unsigned indent,
					/*INOUT*/ chimera::X3DScene *) const;
	void			updateModel(const chimera::NotifierReason
						&reason);
private:
	class ModelNotifier: public chimera::Notifier {
	public:
		void	update(const void *tag, void *,
				const chimera::NotifierReason &reason) const {
				PythonLensModel *plm =
					static_cast<PythonLensModel *>
					(const_cast<void *>(tag));
				plm->updateModel(reason);
			}
	};
	ModelNotifier		modelNotifier;
	_PythonModel		*pythonModel;
	PyObject		*pyModel() const;

	static PyObject		*displayAttr;
};
#endif

} // namespace _PythonModel

#endif
