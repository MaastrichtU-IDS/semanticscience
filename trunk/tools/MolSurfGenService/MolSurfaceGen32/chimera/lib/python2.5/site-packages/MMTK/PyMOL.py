# PyMOL interface
#
# Note: this is still in a rather experimental state.
#
# Written by Konrad Hinsen
# last revision: 2005-9-26
#

import sys
in_pymol = sys.modules.has_key('pymol')
del sys
if in_pymol:
    try:
        from pymol import cmd
        from chempy import Atom, Bond, Molecule
        from chempy.models import Indexed
    except ImportError:
        in_pymol = False

import Units, Utility
from Scientific.Geometry import Vector
import traceback

#
# Create a PyMOL representation from an MMTK object
#
class Representation:

    def __init__(self, object, name = 'MMTK_model', configuration = None,
                 b_values = None):
        self.object = object
        self.universe = object.universe()
        self.name = name
        self.model = Indexed()
        self.index_map = {}
        self.atoms = []
        chain_id_number = 0
        in_chain = True
        for o in object.bondedUnits():
            if Utility.isSequenceObject(o):
                groups = [(g, g.name) for g in o]
                if not in_chain:
                    chain_id_number = (chain_id_number+1) % len(self.chain_ids)
                in_chain = True
            else:
                groups = [(o, o.name)]
                in_chain = False
            residue_number = 1
            for g, g_name in groups:
                for a in g.atomList():
                    atom = Atom()
                    atom.symbol = a.symbol
                    atom.name = a.name
                    atom.resi_number = residue_number
                    atom.chain = self.chain_ids[chain_id_number]
                    if b_values is not None:
                        atom.b = b_values[a]
                    atom.resn = g_name
                    self.model.atom.append(atom)
                    self.index_map[a] = len(self.atoms)
                    self.atoms.append(a)
                residue_number = residue_number + 1
            if in_chain:
                chain_id_number = (chain_id_number+1) % len(self.chain_ids)
            try:
                bonds = o.bonds
            except AttributeError:
                bonds = []
            for b in bonds:
                bond = Bond()
                bond.index = [self.index_map[b.a1], self.index_map[b.a2]]
                self.model.bond.append(bond)
        self._setCoordinates(configuration)

    chain_ids = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def _setCoordinates(self, configuration):
        if configuration is None:
            for i in range(len(self.atoms)):
                self.model.atom[i].coord = \
                                  list(self.atoms[i].position()/Units.Ang)
        else:
            for i in range(len(self.atoms)):
                self.model.atom[i].coord = \
                                  list(configuration[self.atoms[i]]/Units.Ang)

    def show(self):
        auto_zoom = cmd.get("auto_zoom")
        cmd.set("auto_zoom", 0)
        cmd.load_model(self.model, self.name)
        cmd.set("auto_zoom", auto_zoom)

    def remove(self):
        cmd.delete(self.name)

    def update(self, configuration=None):
        try:
            cmd.set("suspend_updates","1")
            self._setCoordinates(configuration)
            cmd.load_model(self.model, self.name, 1)
        except:
            cmd.set("suspend_updates","0")
            traceback.print_exc()
        cmd.set("suspend_updates","0")
        cmd.refresh()

    def movie(self, configurations):
        n = 1
        cmd.feedback("disable","executive","actions")
        auto_zoom = cmd.get("auto_zoom")
        cmd.set("auto_zoom", 0)
        for conf in configurations:
            self._setCoordinates(conf)
            cmd.load_model(self.model, self.name, n)
            n = n + 1
        cmd.set("auto_zoom", auto_zoom)
        cmd.feedback("enable","executive","actions")
        cmd.mplay()

#
# Create an MMTK object from a PyMOL model
#
# Note: PyMOL models are closer in structure to a PDB file than
# to an MMTK object. Some guessing is therefore required to make
# the conversion, and that can go wrong. At the moment, this works
# for standard proteins but it requires a lot of polishing or testing
# before it could be used for arbitrary systems. Still, it is useful
# as it is.
#
# This interface might change in future releases. Consider it experimental.
#
def scanModel(pymol_model):
    segment_dict = {}
    segment_list = []
    for atom in pymol_model.atom:
        seg_id = atom.segi + '_' + atom.chain
        if seg_id not in segment_list:
            segment_list.append(seg_id)
        res_num = atom.resi_number
        residue_dict = segment_dict.get(seg_id, {})
        segment_dict[seg_id] = residue_dict
        res_name, atom_list = residue_dict.get(res_num, (atom.resn, []))
        residue_dict[res_num] = res_name, atom_list
        atom_list.append((atom.name, Vector(atom.coord)*Units.Ang))
    segments = []
    for seg_id in segment_list:
        residue_dict = segment_dict[seg_id]
        residue_list = residue_dict.items()
        residue_list.sort(lambda a, b: cmp(a[0], b[0]))
        segments.append((seg_id, [r[1] for r in residue_list]))
    return segments

def buildCalphaModel(pymol_model):
    import Collections, Proteins
    data = scanModel(pymol_model)
    chains = []
    for seg_id, segment in data:
        amino_acids = []
        nucleic_acids = []
        for res_name, residue in segment:
            res_name = res_name.lower()
            if res_name in amino_acid_names_ca:
                amino_acids.append((res_name, residue))
        if amino_acids:
            chain = Proteins.PeptideChain([item[0] for item in amino_acids],
                                          model='calpha')
            for residue, res_data in zip(chain, amino_acids):
                pymol_atom_list = res_data[1]
                for atom_name, atom_pos in pymol_atom_list:
                    if atom_name.strip().lower() == 'ca':
                        residue.peptide.C_alpha.setPosition(atom_pos)
            chains.append(chain)
    return Proteins.Protein(chains)

def buildAllAtomModel(pymol_model):
    import ChemicalObjects, Collections, Proteins
    data = scanModel(pymol_model)
    all = Collections.Collection()
    peptide_chains = []
    for seg_id, segment in data:
        amino_acids = []
        nucleic_acids = []
        for res_name, residue in segment:
            res_name = res_name.lower().strip()
            if res_name in amino_acid_names:
                amino_acids.append((res_name, residue))
            elif res_name in nucleic_acid_names:
                nucleic_acids.append((res_name, residue))
            elif res_name == 'hoh':
                if len(residue) == 3:
                    m = ChemicalObjects.Molecule('water')
                    for atom_name, atom_pos in residue:
                        atom = getattr(m, atom_name)
                        atom.setPosition(atom_pos)
                elif len(residue) == 1 and residue[0][0] == 'O':
                    m = ChemicalObjects.Atom('O')
                    m.setPosition(residue[0][1])
                all.addObject(m)
            else:
                print "Skipping unknown residue", res_name
        if amino_acids:
            chain = Proteins.PeptideChain([item[0] for item in amino_acids])
            for residue, res_data in zip(chain, amino_acids):
                pdbmap = residue.pdbmap[0][1]
                try:
                    altmap = residue.pdb_alternative
                except AttributeError:
                    altmap = {}
                pymol_atom_list = res_data[1]
                atom_list = residue.atomList()
                for atom_name, atom_pos in pymol_atom_list:
                    try:
                        atom_name = altmap[atom_name]
                    except KeyError:
                        pass
                    try:
                        atom = atom_list[pdbmap[atom_name].number]
                    except KeyError:
                        print "No atom named " + atom_name
                    atom.setPosition(atom_pos)
                    print atom_name, atom.name
            chain.findHydrogenPositions()
            peptide_chains.append(chain)
    if peptide_chains:
        all.addObject(Proteins.Protein(peptide_chains))
    return all


amino_acid_names = ['ala', 'arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'gly',
                    'his', 'ile', 'leu', 'lys', 'met', 'phe', 'pro', 'ser',
                    'thr', 'trp', 'tyr', 'val', 'cyx', 'hsd', 'hse', 'hsp',
                    'hid', 'hie', 'hip', 'ace', 'nme', 'nhe']

amino_acid_names_ca = ['ala', 'arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'gly',
                       'his', 'ile', 'leu', 'lys', 'met', 'phe', 'pro', 'ser',
                       'thr', 'trp', 'tyr', 'val', 'cyx', 'hsd', 'hse', 'hsp',
                       'hid', 'hie', 'hip']

nucleic_acid_names = ['da', 'da5', 'da3', 'dan', 'dc', 'dc5', 'dc3', 'dcn',
                      'dg', 'dg5', 'dg3', 'dgn', 'dt', 'dt5', 'dt3', 'dtn',
                      'ra', 'ra5', 'ra3', 'ran', 'rc', 'rc5', 'rc3', 'rcn',
                      'rg', 'rg5', 'rg3', 'rgn', 'ru', 'ru5', 'ru3', 'run']
