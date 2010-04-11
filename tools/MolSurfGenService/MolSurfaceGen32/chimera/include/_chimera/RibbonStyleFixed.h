#ifndef chimera_RibbonStyleFixed_h
#define	chimera_RibbonStyleFixed_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "RibbonStyle.h"
#include <functional>

namespace chimera {

class CHIMERA_IMEX RibbonStyleFixed: public RibbonStyle  {
public:
		~RibbonStyleFixed();
public:
	virtual float		width(float t) const;
	virtual float		thickness(float t) const;

	virtual PyObject* wpyNew() const;

	virtual void		setSize(const std::vector<float> &sz);
	virtual std::vector<float>
				size() const;
private:
	RibbonStyleFixed(const RibbonStyleFixed&);		// disable
	RibbonStyleFixed& operator=(const RibbonStyleFixed&);	// disable
private:
	float	width_;
	float	thickness_;
public:
	RibbonStyleFixed(const std::vector<float> &sz);
};

} // namespace chimera

#endif
