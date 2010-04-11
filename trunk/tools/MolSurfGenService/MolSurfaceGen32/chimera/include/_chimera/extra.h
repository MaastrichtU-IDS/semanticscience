#ifndef Chimera_extra_h
# define Chimera_extra_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <vector>
# include <set>
# include <otf/Symbol.h>
# include "_chimera_config.h"

extern "C" {
typedef struct _object PyObject;
}

namespace chimera {

class Atom;
class Bond;
class Residue;
class TmplResidue;
class Molecule;
class CoordSet;

extern void initializeColors(bool nogui);
CHIMERA_IMEX extern std::vector<Bond *> bondsBetween(Residue *r0, Residue *r1, bool onlyOne = false);
CHIMERA_IMEX extern PyObject *numpyArrayFromAtoms(std::vector<const Atom *> atoms, CoordSet *crdSet=NULL);
CHIMERA_IMEX extern PyObject *RMSD_fillMatrix(PyObject *M, PyObject *Si, PyObject *Sj);
CHIMERA_IMEX extern PyObject *RMSD_matrix(double l, double m, double n, double s);
CHIMERA_IMEX extern PyObject *eigenMatrix(double q0, double q1, double q2, double q3);
CHIMERA_IMEX extern std::set<Residue *> atomsBonds2Residues(std::vector<const Atom *> atoms, std::vector<const Bond *> bonds);
CHIMERA_IMEX extern PyObject *memoryMap(void *start, int len, int type);
CHIMERA_IMEX extern TmplResidue *restmplFindResidue(otf::Symbol name, bool start, bool end);
CHIMERA_IMEX extern void connectMolecule(Molecule *m);
CHIMERA_IMEX extern std::string opengl_platform();
CHIMERA_IMEX extern double opengl_getFloat(const std::string& parameter);
CHIMERA_IMEX extern void tweak_graphics(const std::string& parameter, bool value);
CHIMERA_IMEX extern std::string xml_quote(std::string s);
CHIMERA_IMEX extern bool reverseStereo();
CHIMERA_IMEX extern void setReverseStereo(bool reverse);

} // namespace chimera

#endif
