#ifndef Chimera_Model_h
# define Chimera_Model_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Geom3d.h>
# include <set>
# include "_chimera_config.h"
# include "Notifier.h"
# include "TrackChanges.h"
# include "Selectable.h"
# include "OpenModels.h"
# include "Plane.h"

namespace chimera {

using otf::Geom3d::Point;
using otf::Geom3d::Xform;
using otf::Geom3d::BBox;

class Lens;
class LensModel;
class X3DScene;

class CHIMERA_IMEX Model: public NotifierList, public Selectable
{
	// ABSTRACT
	friend class OpenModels;
public:
	const std::string &name() const;
	void		setName(const std::string &n);
	// ATTRIBUTE: id
	int		id() const;
	// ATTRIBUTE: subid
	int		subid() const;
	bool		display() const;
	void		setDisplay(bool d);
	bool		useClipPlane() const;
	void		setUseClipPlane(bool b);
	const Plane	&clipPlane() const;
	void		setClipPlane(const Plane &p);
	bool		useClipThickness() const;
	void		setUseClipThickness(bool b);
	double		clipThickness() const;
	void		setClipThickness(double thickness);
	// everything has a default color if only for GUIs
	const Color	*color() const;
	virtual void	setColor(/*NULL_OK*/ const Color *c);
	// ATTRIBUTE: openState
	OpenState	*openState() const;
	bool		bsphere(/*OUT*/ Sphere *s) const;
	bool		bbox(/*OUT*/ BBox *bbox) const;
	virtual bool	frontPoint(const Point &p1, const Point &p2, /*OUT*/ float *frac) const;
	virtual bool	intersects(const Plane &p) const;
# ifndef WrapPy
	virtual void	x3dNeeds(/*INOUT*/ X3DScene *scene, Lens *lens = NULL) const;
	virtual void	x3dWrite(std::ostream &out, unsigned indent, /*INOUT*/ X3DScene *scene, Lens *lens = NULL) const;

	std::string	oslIdent(Selector start = SelDefault,
					Selector end = SelDefault) const;
	bool		oslTestAbbr(OSLAbbreviation *a) const;
	Selector	oslLevel() const;
# endif
	static const Selector	selLevel = SelGraph;

	virtual void	destroy();

# ifndef WrapPy
	LensModel	*addLensModel(Lens *l);
	LensModel	*lensModel(Lens *l);
	void		removeLensModel(Lens *l);
	void		setMinorChange();
	void		setMajorChange();

	virtual PyObject* wpyNew() const;

	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason	JUST_COFR;	// just cofr status changed
	static Reason	MINOR;		// no need to recompute display list
	static Reason	MAJOR;		// need to recompute display list
	// attribute reasons
	static Reason	NAME_CHANGED;
	static Reason	DISPLAY_CHANGED;
	static Reason	USE_CLIP_PLANE_CHANGED;
	static Reason	CLIP_PLANE_CHANGED;
	static Reason	USE_CLIP_THICKNESS_CHANGED;
	static Reason	CLIP_THICKNESS_CHANGED;
	static Reason	COLOR_CHANGED;
	static Reason	ID_CHANGED;
	static Reason	SUBID_CHANGED;
	virtual void	updateCheck(const NotifierReason &);
# endif

	typedef std::vector<Model *> Models;
	const Models	&associatedModels() const;
	void		addAssociatedModel(Model *model);
	void		removeAssociatedModel(Model *model);
protected:
	Model();
	virtual ~Model();
	void		setId(int i);
	void		setSubid(int i);
	int		id_;
	int		subid_;
	std::string	name_;
	bool		display_;
	bool		justCofrChange;
	bool		minorChange;
	bool		majorChange;
	static TrackChanges::Changes *const
			changes;
	virtual void	trackReason(const NotifierReason &reason) const;
	// computeBounds must be replaced in subclass
	// The computeBounds stub converts a bounding box to a bounding sphere
	virtual bool	computeBounds(/*OUT*/ Sphere *s, /*OUT*/ BBox *box) const = 0;

	class CHIMERA_IMEX CheckNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const;
	};
	CheckNotifier checkNotifier;

	Models		associated;
	void		updateModel(Model *inst, const NotifierReason &reason);
	struct CHIMERA_IMEX ModelNotifier: public Notifier {
	public:
		virtual void update(const void *tag, void *instance,
					const NotifierReason &reason) const;
	};
	friend class ModelNotifier;
	ModelNotifier	modelNotifier;
	typedef std::map<Lens *, LensModel *> LensModels;
	LensModels	lensModels;
	virtual LensModel *
			newLensModel(Lens *l) = 0;

	bool		useClipPlane_;
	Plane		clipPlane_;
	bool		useClipThickness_;
	double		clipThickness_;
	const Color	*color_;

	// bounds cache
	mutable bool	validBound;
	mutable Sphere	bsphere_;
	mutable BBox	bbox_;
	mutable bool	dirtyBound;
};

# ifndef WrapPy

// "private" routine for OpenModels
inline void
Model::setId(int i)
{
	id_ = i;
	trackReason(ID_CHANGED);
}

// "private" routine for OpenModels
inline void
Model::setSubid(int i)
{
	subid_ = i;
	trackReason(SUBID_CHANGED);
}

inline const std::string &
Model::name() const
{
	return name_;
}

inline int
Model::id() const
{
	return id_;
}

inline int
Model::subid() const
{
	return subid_;
}

inline OpenState *
Model::openState() const
{
	return OpenModels::get()->openState(id_, subid_);
}

inline bool
Model::display() const
{
	return display_;
}

inline bool
Model::useClipPlane() const
{
	return useClipPlane_;
}

inline const Plane &
Model::clipPlane() const
{
	return clipPlane_;
}

inline bool
Model::useClipThickness() const
{
	return useClipThickness_;
}

inline double
Model::clipThickness() const
{
	return clipThickness_;
}

inline const Color *
Model::color() const
{
	return color_;
}

inline Selector
Model::oslLevel() const
{
	return selLevel;
}

inline void
Model::setMinorChange()
{
	minorChange = true;
}

inline void
Model::setMajorChange()
{
	majorChange = true;
	dirtyBound = true;
}

# endif /* WrapPy */

} // namespace chimera

#endif
