import CIF
import Structure
import StructureBuilder
from ConsoleOutput import warning

def add_string(m, key, table, column, row):
    try:
        v = table.get_value(column, row)
        if v in ('', '?', '.'):
            return False
        m[key] = str(v)
        return True
    except (IndexError, KeyError):
        return False
    return False

def add_number(m, key, table, column, row):
    try:
        v = table.get_value(column, row)
        if v in ('', '?', '.'):
            return False
        m[key] = CIF.makeNumber(v)
        return True
    except (IndexError, KeyError, ValueError):
        return False

class CIFStructureBuilder(StructureBuilder.StructureBuilder):
    """Builds a new Structure object by loading a CIF file.
    """

    def read_start(self, filobj):
        ## parse the CIF file
        cif_file = CIF.CIFFile()
        cif_file.load_file(filobj)
        if len(cif_file.data_blocks) != 1:
            warning("read_start: only single-structure CIF files supported")
            self.halt = True
            return
        self.cif = cif_file.data_blocks[0]
        self.get_cell_parameters()
        self.atom_site_name_map = {}

    def get_cell_parameters(self):
        """Read unit information form various tags and compute
        the fractional-to-Cartesion conversion matrix.
        """
        a = CIF.makeNumber(self.cif.tags["cell_length_a"])
        b = CIF.makeNumber(self.cif.tags["cell_length_b"])
        c = CIF.makeNumber(self.cif.tags["cell_length_c"])
        alpha_degrees = CIF.makeNumber(self.cif.tags["cell_angle_alpha"])
        beta_degrees = CIF.makeNumber(self.cif.tags["cell_angle_beta"])
        gamma_degrees = CIF.makeNumber(self.cif.tags["cell_angle_gamma"])
        z = self.cif.tags["cell_formula_units_z"]
        space_group = self.cif.tags.get("symmetry_space_group_name_h-m", None)
        unit_cell = {
            "length_a": a,
            "length_b": b,
            "length_c": c,
            "angle_alpha": alpha_degrees,
            "angle_beta": beta_degrees,
            "angle_gamma": gamma_degrees,
            "z": z,
            "space_group": space_group
        }
        self.load_unit_cell(unit_cell)

        #
        # Transformation matrix from
        # http://www.ccl.net/cca/documents/molecular-modeling/node4.html
        #
        import math
        alpha = math.radians(alpha_degrees)
        cosa = math.cos(alpha)
        sina = math.sin(alpha)
        beta = math.radians(beta_degrees)
        cosb = math.cos(beta)
        sinb = math.sin(beta)
        gamma = math.radians(gamma_degrees)
        cosg = math.cos(gamma)
        sing = math.sin(gamma)
        V = a * b * c * math.sqrt(1 - cosa * cosa - cosb * cosb
                                    - cosg * cosg + 2 * cosa * cosb * cosg)
        self.xform = [
            [ a, b * cosg, c * cosb ],
            [ 0, b * sing, c * (cosa - cosb * cosg) / sing ],
            [ 0, 0,        V / (a * b * sing) ],
        ]

    def read_atoms(self):
        """Read atom information form the atom_site section.
        """
        for t in self.cif.tables:
            if "atom_site_label" in t.columns:
                table = t
                break
        else:
            warning("read_atoms: no atom_site section found")
            self.halt = True
            return

        for i in range(len(table.rows)):
            atm_map = {
                "res_name": self.cif.name,
                "fragment_id": "1",
                "chain_id": " ",
            }
            add_string(atm_map, "name", table, "atom_site_label", i)
            add_string(atm_map, "element", table, "atom_site_type_symbol", i)
            add_number(atm_map, "fractx", table, "atom_site_fract_x", i)
            add_number(atm_map, "fracty", table, "atom_site_fract_y", i)
            add_number(atm_map, "fractz", table, "atom_site_fract_z", i)
            add_number(atm_map, "temp_factor",
                                        table, "atom_site_U_iso_or_equiv", i)
            add_number(atm_map, "occupancy", table, "atom_site_occupancy", i)
            try:
                fx = atm_map["fractx"] 
                fy = atm_map["fracty"] 
                fz = atm_map["fractz"] 
            except KeyError:
                warning("read_atoms: missing coordinates")
            else:
                fc = [ fx, fy, fz ]
                xyz = [ 0.0, 0.0, 0.0 ]
                for i in range(3):
                    sum = 0.0
                    for j in range(3):
                        sum += self.xform[i][j] * fc[j]
                    xyz[i] = sum
                atm_map["x"] = xyz[0]
                atm_map["y"] = xyz[1]
                atm_map["z"] = xyz[2]
            atm = self.load_atom(atm_map)
            self.atom_site_name_map[atm_map["name"]] = atm
        #print "%d atoms" % len(self.atom_site_name_map)

        ## load the bonds
        bond_map = {}
        self.read_geom_bond(bond_map)
        self.read_geom_angle(bond_map)
        self.load_bonds(bond_map)
        #print "%d bonds" % len(bond_map)

    def read_geom_bond(self, bond_map):
        """Read bond information form the geom_bond section.
        """
        for t in self.cif.tables:
            if "geom_bond_atom_site_label_1" in t.columns:
                table = t
                break
        else:
            warning("read_atoms: no geom_bond section found")
            return

        for row in range(len(table.rows)):
            name1 = table.get_value("geom_bond_atom_site_label_1", row)
            try:
                atom1 = self.atom_site_name_map[name1]
            except KeyError:
                warning("read_atoms: bond references non-existent atom '%s'"
                        % name1)
                continue
            name2 = table.get_value("geom_bond_atom_site_label_2", row)
            try:
                atom2 = self.atom_site_name_map[name2]
            except KeyError:
                warning("read_atoms: bond references non-existent atom '%s'"
                        % name2)
                continue

            if id(atom1) < id(atom2):
                bnd = (atom1, atom2)
            else:
                bnd = (atom2, atom1)
            bond_map[bnd] = {}

    def read_geom_angle(self, bond_map):
        """Read bond information form the geom_angle section.
        """
        for t in self.cif.tables:
            if "geom_angle_atom_site_label_1" in t.columns:
                table = t
                break
        else:
            warning("read_atoms: no geom_angle section found")
            return

        for row in range(len(table.rows)):
            name1 = table.get_value("geom_angle_atom_site_label_1", row)
            atom1 = self.atom_site_name_map[name1]
            name2 = table.get_value("geom_angle_atom_site_label_2", row)
            atom2 = self.atom_site_name_map[name2]
            name3 = table.get_value("geom_angle_atom_site_label_3", row)
            atom3 = self.atom_site_name_map[name3]

            if id(atom1) < id(atom2):
                bnd = (atom1, atom2)
            else:
                bnd = (atom2, atom1)
            bond_map[bnd] = {}

            if id(atom2) < id(atom3):
                bnd = (atom2, atom3)
            else:
                bnd = (atom3, atom2)
            bond_map[bnd] = {}

    def read_metadata(self):
        self.read_structure_id()
        self.struct.cif_data = self.cif

    def read_structure_id(self):
        """Read the PDB ID.
        """
        name_tags = [
            "chemical_name_common",
            "database_code_depnum_ccdc_archive",
            "chemical_name_systematic",
        ]
        for tag in name_tags:
            try:
                entry_id = self.cif.tags[tag].strip()
            except KeyError:
                pass
            else:
                if entry_id != '.' and entry_id != '?':
                    self.load_structure_id(entry_id)
                    break

if __name__ == "__main__":
    def builder_test(test_file):
        csb = CIFStructureBuilder(fil=test_file)
        s = csb.struct
        print s
    builder_test("ccd.cif")
