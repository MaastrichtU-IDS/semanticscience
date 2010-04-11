#ifndef Chimera_PyMol2ioHelper_h
# define Chimera_PyMol2ioHelper_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include "Mol.h"
# include "Mol2ioHelper.h"
# include <map>

namespace chimera {

class CHIMERA_IMEX PyMol2ioHelper : public Mol2ioHelper, public otf::WrapPyObj
{
	PyMol2ioHelper(const PyMol2ioHelper&);			// disable
	PyMol2ioHelper& operator=(const PyMol2ioHelper&);	// disable
protected:
	struct CHIMERA_IMEX SectionParser {
	public:
		PyObject	*init;
		PyObject	*data;
		PyObject	*finish;
				SectionParser();
				SectionParser(PyObject *i, PyObject *d,
						PyObject *f);
				SectionParser(const SectionParser& sp);
				void operator=(const SectionParser& sp);
				~SectionParser();
	};
	std::map<std::string, SectionParser>	sectionMap_;
	PyObject				*commentParser_;
	SectionParser				*curSP_;
public:
			PyMol2ioHelper();
	virtual		~PyMol2ioHelper();
	bool		addParser(const std::string &section,
						/*NONE_OK*/ PyObject *init,
						/*NONE_OK*/ PyObject *data,
						/*NONE_OK*/ PyObject *finish);
	bool		removeParser(const std::string &section);
	bool		setCommentParser(PyObject *p);
public:
	virtual void	start(Mol2io *io, /*OUT*/std::vector<Molecule *> *mols);
	virtual void	finish();
	virtual void	parseRTI(const std::string &rti);
	virtual void	parseDataRecord(const std::string &record);
	virtual void	parseComment(const std::string &comment);
# ifndef WrapPy
	virtual PyObject* wpyNew() const;
# endif
# ifdef WrapPy
	// from Mol2ioHelper
	virtual void	setCurrentMolecule(Molecule *m);
	virtual void	setCurrentResidue(Residue *r);
	virtual void	setCurrentAtom(Atom *a);
	virtual void	setCurrentBond(Bond *b);
	void		parserIgnore(const std::string &record);
	void		parserMolecule(const std::string &record);
	void		parserAtom(const std::string &record);
	void		parserBond(const std::string &record);
	void		parserSubst(const std::string &record);
# endif
};

} // namespace chimera

#endif
