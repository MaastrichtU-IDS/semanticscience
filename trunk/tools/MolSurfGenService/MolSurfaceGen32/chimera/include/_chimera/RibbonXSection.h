#ifndef chimera_RibbonXSection_h
#define	chimera_RibbonXSection_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include <utility>
#include <vector>
#include <functional>

namespace chimera {

class CHIMERA_IMEX RibbonXSection: public NotifierList, public otf::WrapPyObj  {
public:
		virtual ~RibbonXSection();
public:
	inline const std::vector<std::pair<float, float> >
			&outline() const;
	inline void		setOutline(const std::vector<std::pair<float, float> >
					&o);
	inline void		addOutlineVertex(float x, float y);
	inline bool		smoothWidth() const;
	inline void		setSmoothWidth(bool sw);
	inline bool		smoothLength() const;
	inline void		setSmoothLength(bool sl);
	inline bool		closed() const;
	inline void		setClosed(bool c);

	virtual PyObject* wpyNew() const;

	virtual void	notify(const NotifierReason &reason) const;
	struct Reason: public NotifierReason {
                Reason(const char *r): NotifierReason(r) {}
        };
	static Reason		OUTLINE_CHANGED;
	static Reason		SMOOTH_WIDTH_CHANGED;
	static Reason		SMOOTH_LENGTH_CHANGED;
	static Reason		CLOSED_CHANGED;

	static RibbonXSection *line();
	static RibbonXSection *square();
	static RibbonXSection *circle();
private:
	std::vector<std::pair<float, float> >
			outline_;
	bool		smoothWidth_;
	bool		smoothLength_;
	bool		closed_;
protected:
	static TrackChanges::Changes *const changes;
public:
	RibbonXSection(bool sw, bool sl, bool c);
	RibbonXSection(int n, const float (*o)[2],
				bool sw, bool sl, bool c);
	RibbonXSection(const std::vector<std::pair<float, float> > &o,
				bool sw, bool sl, bool c);
};

} // namespace chimera

#endif
