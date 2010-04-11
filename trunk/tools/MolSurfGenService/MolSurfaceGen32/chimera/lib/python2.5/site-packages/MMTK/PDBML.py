# Read PDBML files
#
# Written by Konrad Hinsen
# last revision: 2006-5-4
#

"""
Experimental PDBML reader. It doesn't treat water molecules correctly yet
(it creates a single molecule object with all atoms of all water molecules).
"""

#import elementtree.ElementTree as ET
import cElementTree as ET
from Scientific.Geometry import Vector
from Scientific.IO.PDB import Atom, AminoAcidResidue, NucleotideResidue, \
                              amino_acids, nucleic_acids
from Scientific.IO.TextFile import TextFile
import MMTK.PDB

class PDBConfiguration(MMTK.PDB.PDBConfiguration):

    def __init__(self, filename, model = 1, alternate_code = 'A'):
        self.filename = filename
        self.model = model
        self.alternate = alternate_code
        self.residues = []
        self.objects = []
        self.peptide_chains = []
        self.nucleotide_chains = []
        self.molecules = {}
        self.prefix = None
        self.chem_comp = None
        self.entity_names = None
        self.entities = None
        self.chain_entities = None
        self.chains = None
        self.nonchains = None
        self.atoms = {}
        self.parseFile(TextFile(filename))
        self._numberAtoms()

    def parseFile(self, file):
        current_comp_id = None
        current_seq_id = None
        current_asym_id = None
        current_chain = None
        current_residue = None
        for event, element in ET.iterparse(file):
            tag = element.tag
            if self.prefix is None:
                self.prefix = tag[:tag.find('}')+1]
            if tag == self.prefix+"atom_site":
                atom_spec = self.parseAtom(element)
                if (atom_spec['alt_id'] is None or
                    atom_spec['alt_id'] == self.alternate) \
                       and atom_spec['model'] == self.model:
                    atom = Atom(atom_spec['name'], atom_spec['position'],
                                element=atom_spec['element'],
                                occupancy=atom_spec['occupancy'],
                                temperature_factor=atom_spec['beta'])
                    self.atoms[atom_spec['atom_id']] = atom
                    if atom_spec['asym_id'] != current_asym_id:
                        # start new chain or molecule
                        entity = self.entities[atom_spec['entity_id']]
                        residue_name = atom_spec['comp_id']
                        if entity['type'] == 'polymer':
                            if residue_name in amino_acids:
                                current_chain = MMTK.PDB.PDBPeptideChain(chain_id = atom_spec['asym_id'], segment_id = '')
                                self.peptide_chains.append(current_chain)
                            elif residue_name in nucleic_acids:
                                current_chain = MMTK.PDB.PDBNucleotideChain(chain_id = atom_spec['asym_id'], segment_id = '')
                                self.nucleotide_chains.append(current_chain)
                            else:
                                raise ValueError('Unknown polymer type' +
                                                 'containing residue ' +
                                                 residue_name)
                            current_comp_id = None
                            current_residue = None
                        else:
                            current_chain = None
                            current_residue = MMTK.PDB.PDBMolecule(residue_name)
                            current_comp_id = residue_name
                            current_seq_id = atom_spec['seq_id']
                            mol_list = self.molecules.get(residue_name, [])
                            mol_list.append(current_residue)
                            self.molecules[residue_name] = mol_list
                            self.residues.append(current_residue)
                        current_asym_id = atom_spec['asym_id']
                    if atom_spec['comp_id'] != current_comp_id or \
                           atom_spec['seq_id'] != current_seq_id:
                        # start a new residue
                        current_comp_id = atom_spec['comp_id']
                        current_seq_id = atom_spec['seq_id']
                        if current_comp_id in amino_acids:
                            current_residue = AminoAcidResidue(current_comp_id,
                                                               [],
                                                               current_seq_id)
                        elif current_comp_id in nucleic_acids:
                            current_residue = NucleotideResidue(current_comp_id,
                                                                [],
                                                                current_seq_id)
                        else:
                            raise ValueError('Unknown residue ' +
                                             residue_name)
                        current_chain.addResidue(current_residue)
                        self.residues.append(current_residue)
                    if current_residue is not None:
                        # Ultimately, this should never be None, but for
                        # now we skip whatever we can't handle yet
                        current_residue.addAtom(atom)
                element.clear()
            elif tag == self.prefix+'chem_compCategory':
                self.chem_comp = element
            elif tag == self.prefix+'pdbx_entity_nameCategory':
                self.entity_names = element
            elif tag == self.prefix+'entityCategory':
                self.entities = {}
                for e in element:
                    entity_id = e.attrib['id']
                    entity_def = {}
                    for field in e:
                        entity_def[field.tag[len(self.prefix):]] = field.text
                    self.entities[entity_id] = entity_def
            elif tag == self.prefix+'entity_poly_seqCategory':
                self.chain_entities = None
            elif tag == self.prefix+'pdbx_poly_seq_schemeCategory':
                self.chains = element
            elif tag == self.prefix+'pdbx_nonpoly_schemeCategory':
                self.nonchains = element
            elif tag == self.prefix+'atom_siteCategory':
                # This event happens when all atoms have been treated
                element.clear()

    def parseAtom(self, element):
        atom_spec = {
            'atom_id': element.get('id', None),
            'element': element.find(self.prefix+'type_symbol').text,
            'name': element.find(self.prefix+'label_atom_id').text,
            'alt_id': element.find(self.prefix+'label_alt_id').text,
            'model': int(element.find(self.prefix+'pdbx_PDB_model_num').text),
            'comp_id': element.find(self.prefix+'label_comp_id').text,
            'asym_id': element.find(self.prefix+'label_asym_id').text,
            'entity_id': element.find(self.prefix+'label_entity_id').text,
            'position': Vector(float(element.find(self.prefix+'Cartn_x').text),
                               float(element.find(self.prefix+'Cartn_y').text),
                               float(element.find(self.prefix+'Cartn_z').text)),
            'occupancy': float(element.find(self.prefix+'occupancy').text),
            'beta': float(element.find(self.prefix+'B_iso_or_equiv').text),
            }
        seq_id = element.find(self.prefix+'label_seq_id').text
        if seq_id is None:
            atom_spec['seq_id'] = None
        else:
            atom_spec['seq_id'] = int(seq_id)
        return atom_spec



if __name__ == '__main__':
    
    #c = PDBConfiguration("/Users/hinsen/Desktop/1BTY.xml")
    #c_ref = MMTK.PDB.PDBConfiguration("/Users/hinsen/Desktop/1BTY.pdb")
    #c = PDBConfiguration("/Users/hinsen/Desktop/5CYT.xml")
    #c_ref = MMTK.PDB.PDBConfiguration("/Users/hinsen/Desktop/5CYT.pdb")
    c = PDBConfiguration("/Users/hinsen/Desktop/2BG9.xml")
