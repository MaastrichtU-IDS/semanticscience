#ifndef otf_mol2iohelper_include
#define otf_mol2iohelper_include

#include <string>
#include <vector>

namespace chimera {

class Mol2io;
class Molecule;
class Residue;
class Atom;
class Bond;

class Mol2ioHelper {
protected:
	typedef void	(Mol2ioHelper::*DataParser)(const std::string &);
	Mol2io		*io;
	Molecule	*curMol;
	Residue		*curRes;
	Atom		*curAtom;
	Bond		*curBond;
	DataParser	curParser;
	int		recordIndex;
	std::vector<Molecule *> *mols;
	std::string	dockKeys, dockValues;
	std::vector<std::string> comments, data;
public:
	virtual void	start(Mol2io *mol2io, std::vector<Molecule *> *);
	virtual void	resolveMissingSubstructures();
	virtual void	finish();
	virtual void	parseRTI(const std::string &rti);
	virtual void	parseDataRecord(const std::string &record);
	virtual void	parseComment(const std::string &comment);
	virtual void	setCurrentMolecule(Molecule *m);
	virtual void	setCurrentResidue(Residue *r);
	virtual void	setCurrentAtom(Atom *a);
	virtual void	setCurrentBond(Bond *b);
	virtual		~Mol2ioHelper() {}
public:
	void		parserIgnore(const std::string &);
	void		parserMolecule(const std::string &record);
	void		parserAtom(const std::string &record);
	void		parserBond(const std::string &record);
	void		parserSubst(const std::string &record);
	bool		parseIgnoreBlankLines() { return curParser != &Mol2ioHelper::parserMolecule; }
};

}

#endif
