# XML I/O
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

import MMTK
from MMTK.MoleculeFactory import MoleculeFactory
from cElementTree import iterparse
from Scientific import N


class XMLMoleculeFactory(MoleculeFactory):

    """XML molecule factory.
    
    An XML molecule factory reads an XML specification of a molecular
    system and builds the molecule objects and universe described
    therein. The universe can be obtained through the attribute
    |universe|.
    
    Constructor: XMLMoleculeFactory(||xml_file|)
    
    Arguments:
        
    |xml_file| -- name of the XML file to be read
    """

    def __init__(self, file):
        MoleculeFactory.__init__(self)
        for event, element in iterparse(file):
            tag = element.tag
            ob_id = element.attrib.get('id', None)
            if tag == 'molecule' and ob_id is not None:
                self.makeGroup(element)
                element.clear()
            elif tag == 'templates':
                element.clear()
            elif tag == 'universe':
                self.makeUniverse(element)

    def makeGroup(self, element):
        group = element.attrib['id']
        self.createGroup(group)
        for molecule_element in element.findall('molecule'):
            self.addSubgroup(group, molecule_element.attrib.get('title', ''),
                             molecule_element.attrib['ref'])
        atom_array = element.find('atomArray')
        if atom_array is not None:
            for atom_element in atom_array:
                self.addAtom(group, atom_element.attrib['title'],
                             atom_element.attrib['elementType'])
        bond_array = element.find('bondArray')
        if bond_array is not None:
            for bond_element in bond_array:
                atom1, atom2 = bond_element.attrib['atomRefs2'].split()
                atom1 = '.'.join(atom1.split(':'))
                atom2 = '.'.join(atom2.split(':'))
                self.addBond(group, atom1, atom2)

    def makeUniverse(self, element):
        topology = element.attrib.get('topology', 'infinite')
        if topology == 'infinite':
            universe = MMTK.InfiniteUniverse()
        elif topology == 'periodic3d':
            cellshape = element.attrib['cellshape']
            if cellshape == 'orthorhombic':
                cellsize = element.attrib['cellsize'].split()
                units = element.attrib.get('units', 'units:nm')
                factor = getattr(MMTK.Units, units.split(':')[1])
                universe = MMTK.OrthorhombicPeriodicUniverse(tuple(
                                     [factor*float(size) for size in cellsize]))
            else:
                raise ValueError("cell shape %s not implemented" % cellshape)
        else:
            raise ValueError("topology %s not implemented" % topology)
        atom_index = 0
        for subelement in element:
            if subelement.tag == 'molecule':
                molecule = self.retrieveMolecule(subelement.attrib['ref'])
                for atom in molecule.atomList():
                    atom.index = atom_index
                    atom_index += 1
                universe.addObject(molecule)
            elif subelement.tag == 'atom':
                atom = MMTK.Atom(subelement.attrib['elementType'])
                atom.index = atom_index
                atom_index += 1
                universe.addObject(atom)
        configuration = element.find('configuration')
        if configuration is not None:
            array = configuration.find('atomArray')
            x = map(float, array.attrib['x3'].split())
            y = map(float, array.attrib['y3'].split())
            z = map(float, array.attrib['z3'].split())
            units = array.attrib.get('units', 'units:nm')
            factor = getattr(MMTK.Units, units.split(':')[1])
            array = universe.configuration().array
            array[:, 0] = x
            array[:, 1] = y
            array[:, 2] = z
            N.multiply(array, factor, array)
        self.universe = universe
