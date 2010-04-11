#ifndef chimera_ReadGaussianFCF_h
#define	chimera_ReadGaussianFCF_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <vector>
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include <functional>

namespace chimera {

class CHIMERA_IMEX ReadGaussianFCF: public otf::WrapPyObj  {
public:
		~ReadGaussianFCF();
public:
	std::vector<Molecule *> readGaussianStream(std::istream &, const char *, int *);
	std::vector<Molecule *> readGaussianFile(const char *filename);
	inline bool		ok() const;
	inline std::string	error() const;
private:
	std::string	error_;
public:
	virtual PyObject* wpyNew() const;
public:
	ReadGaussianFCF();
};

} // namespace chimera

#endif
