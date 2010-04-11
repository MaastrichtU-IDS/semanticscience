#ifndef Chimera_VRMLModel_h
# define Chimera_VRMLModel_h

# include <otf/WrapPy2.h>
# include <_chimera/_chimera_config.h>
# include <_chimera/Model.h>
# include <_chimera/LensViewer.h>	/* for DrawPass */
# include "common.h"

#ifdef WrapPy
//
// WrapPy does not follow include files.  We have to explicitly declare
// Model for WrapPy to use a wrapped version of that class.
//
namespace chimera
{
class Selectable: public otf::WrapPyObj
{
	// ABSTRACT
};
class Model: public Selectable
{
	// ABSTRACT
};
class Lens: public otf::WrapPyObj
{
};
class LensViewer: public otf::WrapPyObj
{
	// ABSTRACT
public:
	enum DrawPass;
};
class BBox {
};
}
#endif		// WrapPy

namespace VRML {

class Scene;
class Node;
class Field;

class VRML_IMEX VRMLModel: public chimera::Model
{
public:
	VRMLModel(const char *filename, int debug = 0);
	VRMLModel(std::istream &is, const char *name, int debug = 0);
	~VRMLModel();
	bool		valid() const;
	std::string	error() const;
	virtual bool	computeBounds(/*OUT*/ chimera::Sphere *s, /*OUT*/ chimera::BBox *box) const;
	typedef chimera::LensViewer::DrawPass DrawPass;
	DrawPass	drawPass() const;
	void		setDrawPass(DrawPass dp);
# ifndef WrapPy
	virtual Selectable::Selectables
			oslChildren() const;
	virtual Selectable::Selectables
			oslParents() const;
	VRML::Scene	*scene() const;
	virtual void	trackReason(const chimera::NotifierReason &reason) const;
	static Model::Reason	DRAW_PASS_CHANGED;
	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
# endif
private:
	virtual chimera::LensModel *
			newLensModel(chimera::Lens *l);
	VRML::Scene	*scene_;	// pointer to be isolated from VRML code
	class ColorNotifier: public chimera::Notifier {
	public:
		void update(const void *tag, void *, const chimera::NotifierReason &) const {
			VRMLModel *v = static_cast<VRMLModel *>
						(const_cast<void *>(tag));
			// No matter what kind of color change it was,
			// it still only causes a redisplay.
			v->setMinorChange();
		}
	};
	ColorNotifier	colorNotifier;
	// TODO: used hashed set
	static void	registerColors(VRML::Node *n, const char *name,
						VRML::Field *f, void *closure);
	static chimera::TrackChanges::Changes *const
			changes;
	DrawPass	drawPass_;
};

# ifndef WrapPy

inline VRML::Scene *
VRMLModel::scene() const
{
	return scene_;
}

inline VRMLModel::DrawPass
VRMLModel::drawPass() const
{
	return drawPass_;
}

# endif /* WrapPy */

} // namespace VRML

#endif
