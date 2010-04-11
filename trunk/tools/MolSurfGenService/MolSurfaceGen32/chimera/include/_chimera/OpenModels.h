#ifndef Chimera_OpenModels_h
# define Chimera_OpenModels_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <map>
# include <vector>
# include <otf/Geom3d.h>
# include "_chimera_config.h"
# include "Notifier.h"
# include "TrackChanges.h"
# include "sphere.h"
# include "Viewer.h"

namespace chimera {

class Model;
using otf::Geom3d::Point;
using otf::Geom3d::Xform;
using otf::Geom3d::BBox;

typedef std::vector<Model *> ModelList;
typedef std::pair<int, int> ModelId;
typedef std::vector<ModelId> ModelIdList;

class Viewer;

class CHIMERA_IMEX OpenState: public NotifierList, public otf::WrapPyObj
{
	// DON'T CACHE
public:
	ModelList	models;
	ModelList	hidden;
#ifdef WrapPy
	// READONLY: models
	// READONLY: hidden
#endif
	bool		active() const;
	void		setActive(bool active);
	const Xform	&xform() const;
	void		setXform(const Xform &xform);
	bool		bsphere(/*OUT*/ Sphere *s) const;
	bool		bbox(/*OUT*/ BBox *box) const;
	bool		overrideCofr() const;
	void		setOverrideCofr(bool b);
	Point		cofr() const;
	void		setCofr(const Point &pt);
	void		localXform(const Xform &xf);
	void		globalXform(const Xform &xf);
#ifndef WrapPy
	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;

	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason	ACTIVE_CHANGE;
	static Reason	XFORM_CHANGE;
	virtual void	notify(const NotifierReason &reason) const;
#endif
private:
	friend class OpenModels;
	static TrackChanges::Changes *const changes;
	OpenState();
	~OpenState();
	Xform xform_;
	bool		overrideCofr_;
	Point		cofr_;
	bool		active_;
	typedef std::vector<Sphere> Spheres;
	void		computeBounds(/*OUT*/ Spheres *bspheres,
						/*OUT*/ BBox *box) const;
};

class CHIMERA_IMEX OpenModels: public NotifierList, public otf::WrapPyObj
{
	OpenModels();
	~OpenModels();
	OpenModels(const OpenModels &o);		// disable
	OpenModels &operator=(const OpenModels &o);	// disable
public:
	static OpenModels *get();
	static const int Default = -99;
	void		add(const ModelList &models, int baseId = Default,
				int subid = Default,
				const Model *sameAs = NULL,
				bool shareXform = true, bool hidden = false);
	void		remove(/*INOUT*/ ModelList *models);
	void		listIds(/*OUT*/ ModelIdList *mids, bool hidden = false,
							bool all = false) const;
	void		list(/*OUT*/ ModelList *models, int id = Default,
				int subid = Default, bool hidden = false,
				bool all = false) const;
	// count of non-empty models
	int		count(bool inclEmpty = true, bool hidden = false, bool all = false) const;

	OpenState	*openState(int id, int subid) const;
	void		setActive(int id, bool active);
	bool		hasActiveModels() const;

	void		setXform(int id, const Xform &xform);
	void		setXform(const Xform &xform);
	void		localXform(int id, const Xform &xf);
	void		globalXform(int id, const Xform &xf);

	// center of rotation support
	bool		bsphere(/*OUT*/ Sphere *s) const;
	bool		bbox(/*OUT*/ BBox *box) const;
	bool		computeBounds(/*OUT*/ Sphere *s, /*OUT*/ BBox *box,
				      bool includeInactive = true) const;
	const Point	&cofr() const;
	void		setCofr(const Point &pt);
	enum CofrMethod	{ Fixed, CenterOfModels, Independent, CenterOfView,
	                  FrontCenter };
	CofrMethod	cofrMethod() const;
	void		setCofrMethod(CofrMethod cm);
	void		applyXform(const Xform &xf);

	Viewer		*viewer() const;      // Used by CenterOfView rotation.
	void		setViewer(Viewer *v);

#ifndef WrapPy
	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;

	struct CHIMERA_IMEX Reason: public NotifierReason {
		const ModelList	*added;		// for MODEL_CHANGE
		Reason(const char *r): NotifierReason(r), added(NULL) {}
	private:
		Reason(const Reason&);
		Reason& operator=(const Reason&);
	};
	// notifier reasons
	static Reason	ATTR_CHANGE;
	static Reason	MODEL_CHANGE;

	virtual void	notify(const NotifierReason &reason) const;
#endif
private:
	bool	ref(Model *m, int id, int subid, bool hidden);
	bool	unref(Model *m, bool deleted = false);

	typedef std::map<Model *, ModelId> ModelIds;
	ModelIds modelIds;

	typedef std::map<int, OpenState *> OpenState1d;
	typedef std::map<int, OpenState1d> OpenState2d;
	OpenState2d	allOpenState;

	static TrackChanges::Changes *const changes;

	void		updateCheck(const NotifierReason &reason);
	class CheckNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const {
			OpenModels *m = static_cast<OpenModels *>(const_cast<void *>(tag));
			m->updateCheck(reason);
		}
	};
	friend class CheckNotifier;
	CheckNotifier	checkNotifier;

	void		updateModel(Model *m, const NotifierReason &reason);
	class ModelNotifier: public Notifier {
	public:
		void update(const void *tag, void *modelInst,
					const NotifierReason &reason) const {
			OpenModels *om = static_cast<OpenModels *>(const_cast<void *>(tag));
			Model *m = static_cast<Model *>(modelInst);
			om->updateModel(m, reason);
		}
	};
	friend class ModelNotifier;
	ModelNotifier	modelNotifier;

	void		updateOpenState(OpenState *os, const NotifierReason &reaason);
	class OpenStateNotifier: public Notifier {
	public:
		void update(const void *tag, void *osInst,
					const NotifierReason &reason) const {
			OpenModels *om = static_cast<OpenModels *>(const_cast<void *>(tag));
			OpenState *os = static_cast<OpenState *>(osInst);
			om->updateOpenState(os, reason);
		}
	};
	friend class OpenStateNotifier;
	OpenStateNotifier
			openStateNotifier;

	class CHIMERA_IMEX ViewerNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
			    const NotifierReason &reason) const;
	};
	friend class ViewerNotifier;
	ViewerNotifier	viewerNotifier;

	bool		xformChanged;
	CofrMethod	cofrMethod_;
	mutable Point	cofr_;
	mutable bool	cofrDirty;
	void		computeCofr() const;
	Point		computeCenterOfModels() const;
	Point		computeFrontCenter() const;
	Viewer		*viewer_;        // Used by CenterOfView rotation.

	bool		zoomedOut() const;
};

#ifndef WrapPy

inline bool
OpenState::overrideCofr() const
{
	return overrideCofr_;
}

inline bool
OpenState::active() const
{
	return active_;
}

inline const Xform &
OpenState::xform() const
{
	return xform_;
}

inline OpenModels::CofrMethod
OpenModels::cofrMethod() const
{
	return cofrMethod_;
}

#endif /* WrapPy */

} // namespace chimera

#endif
