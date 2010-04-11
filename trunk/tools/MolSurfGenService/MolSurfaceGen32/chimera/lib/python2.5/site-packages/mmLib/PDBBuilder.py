## Copyright 2002-2006 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Convert a Structure object to its PDBFile description.
"""
import ConsoleOutput
import Library
import PDB
import mmCIF
import Structure
import StructureBuilder


## class specification for alpha helicies mapping mmLib classification
## strings with PDB helix class integers, -1 where no PDB helix class
## would apply; here is the PDB helix class description
##
##     TYPE OF HELIX             CLASS NUMBER (COLUMNS 39 - 40)
##     --------------------------------------------------------------
##     Right-handed alpha (default)                1
##     Right-handed omega                          2
##     Right-handed pi                             3
##     Right-handed gamma                          4
##     Right-handed 310                            5
##     Left-handed alpha                           6
##     Left-handed omega                           7
##     Left-handed gamma                           8
##     27 ribbon/helix                             9
##     Polyproline                                10
##

HELIX_CLASS_LIST = [
    ## protein helix classes
    ("HELIX_P",      -1),
    ("HELX_OT_P",    -1),
    ("HELX_RH_P",    -1),
    ("HELX_RH_OT_P", -1),

    ("HELX_RH_AL_P",  1),
    ("HELX_RH_GA_P",  4),
    ("HELX_RH_OM_P",  2),
    ("HELX_RH_PI_P",  3),
    ("HELX_RH_27_P",  9),
    ("HELX_RH_3T_P",  5),
    ("HELX_RH_PP_P", 10),
    
    ("HELX_LH_P",    -1),
    ("HELX_LH_OT_P", -1),

    ("HELX_LH_AL_P",  6),
    ("HELX_LH_GA_P",  8),
    ("HELX_LH_OM_P",  7),
    ("HELX_LH_PI_P", -1),
    ("HELX_LH_27_P",  9),
    ("HELX_LH_3T_P", -1),
    ("HELX_LH_PP_P", 10),

    ## nucleic acid helix classes
    ("HELX_N",       -1),
    ("HELX_OT_N",    -1),
    ("HELX_RH_N",    -1),
    ("HELX_RH_OT_N", -1),
    ("HELX_RH_A_N",  -1),
    ("HELX_RH_B_N",  -1),
    ("HELX_RH_Z_N",  -1),
    ("HELX_LH_N",    -1),
    ("HELX_LH_OT_N", -1),
    ("HELX_LH_A_N",  -1),
    ("HELX_LH_B_N",  -1),
    ("HELX_LH_Z_N",  -1)
    ]


def setmap(smap, skey, dmap, dkey):
    """Sets the dmap/dkey with the value from smap/skey/
    """
    if smap.has_key(skey):
        dmap[dkey] = str(smap[skey])
        return True
    return False


def setmaps(smap, skey, dmap, dkey):
    """Sets the dmap/dkey with the string value from smap/skey/
    """
    if smap.has_key(skey):
        try:
            dmap[dkey] = str(smap[skey])
        except ValueError:
            print "setmaps(): ValueError"
            return False
        return True
    return False


def setmapi(smap, skey, dmap, dkey):
    """Sets the dmap/dkey with the integer value from smap/skey.
    """
    if smap.has_key(skey) and smap[skey]!="":
        try:
            dmap[dkey] = int(smap[skey])
        except ValueError:
            print "setmapi(): ValueError"
            return False
        return True
    return False


def setmapf(smap, skey, dmap, dkey):
    """Sets the dmap/dkey with the float value from smap/skey or
    default if not smap/skey value is found.
    """
    if smap.has_key(skey) and smap[skey]!="":
        try:
            dmap[dkey] = float(smap[skey])
        except ValueError:
            print "setmapf(): ValueError dmap[%s]=smap[%s]=%s" % (
                dkey, skey, smap[skey])
            return False
        return True
    return False


class PDBStructureBuilder(StructureBuilder.StructureBuilder,
                          PDB.RecordProcessor):
    """Builds a new Structure object by loading a PDB file.
    """
    def pdb_error(self, rec_name, text):
        ConsoleOutput.warning("PDB::%s %s" % (rec_name, text))

    def get_fragment_id(self, rec, res_seq = "resSeq", icode = "iCode"):
        fragment_id = None
        if rec.has_key(res_seq):
            fragment_id = str(rec[res_seq])
            if rec.has_key(icode):
                fragment_id += rec[icode]
        return fragment_id
    
    def read_start(self, fil, update_cb = None):
        self.pdb_file = PDB.PDBFile()
        self.pdb_file.load_file(fil)

    def load_atom(self, atm_map):
        """Override load_atom to maintain a serial_num->atm map.
        """
        atm = StructureBuilder.StructureBuilder.load_atom(self, atm_map)
        ## map PDB atom serial number -> Atom object
        try:
            self.atom_serial_map[atm_map["serial"]] = atm
        except KeyError:
            pass

    def read_atoms(self):
        ## map PDB atom serial numbers to the structure atom classes
        self.atom_serial_map = {}
        ## current atom map
        self.atm_map = {}
        ## current model number
        self.model_num = None

        def filter_func(rec):
            if isinstance(rec, PDB.ATOM) or \
               isinstance(rec, PDB.SIGATM) or \
               isinstance(rec, PDB.ANISOU) or \
               isinstance(rec, PDB.SIGUIJ) or \
               isinstance(rec, PDB.TER) or \
               isinstance(rec, PDB.MODEL) or \
               isinstance(rec, PDB.ENDMDL):
                return True
            return False

        ## process the coordinate records
        self.process_pdb_records(self.pdb_file, filter_func)

        ## load last atom read
        if self.atm_map:
            self.load_atom(self.atm_map)

        ## cleanup
        del self.model_num
        del self.atm_map
        
    def read_metadata(self):
        ## store extracted bond information
        self.bond_map = {}

        ## secondary structure annotation
        self.helix_list = []
        self.beta_sheet_list = []
        self.site_list = []

        def filter_func(rec):
            if isinstance(rec, PDB.ATOM) or \
               isinstance(rec, PDB.SIGATM) or \
               isinstance(rec, PDB.ANISOU) or \
               isinstance(rec, PDB.SIGUIJ) or \
               isinstance(rec, PDB.TER) or \
               isinstance(rec, PDB.MODEL) or \
               isinstance(rec, PDB.ENDMDL):
                return False
            return True

        ## process the non-coordinate records
        self.process_pdb_records(self.pdb_file, filter_func)

        ## load chemical bond informaton
        self.load_bonds(self.bond_map)
        del self.bond_map

        ## load secondary structure annotation
        self.load_alpha_helicies(self.helix_list)
        del self.helix_list

        self.load_beta_sheets(self.beta_sheet_list)
        del self.beta_sheet_list

        self.load_sites(self.site_list)
        del self.site_list

    def process_ATOM(self, rec):
        ## load current atom since this record indicates a new atom
        if self.atm_map:
            self.load_atom(self.atm_map)
            self.atm_map = {}

        ## optimization
        atm_map = self.atm_map

        ## always derive element from atom name for PDB files -- they are
        ## too messed up to use the element column
        try:
            name = rec["name"]
        except KeyError:
            atm_map["name"] = ""
            atm_map["element"] = ""
        else:
            atm_map["name"] = name.strip()
            
            res_name = rec.get("resName", "")
            gelement = Library.library_guess_element_from_name(name, res_name)
            if gelement != None:
                atm_map["element"] = gelement

        ## additional atom information
        if rec.has_key("serial"):
            atm_map["serial"] = rec["serial"]

        if rec.has_key("altLoc"):
            atm_map["alt_loc"] = rec["altLoc"]

        if rec.has_key("resName"):
            atm_map["res_name"] = rec["resName"]

        if rec.has_key("chainID"):
            atm_map["chain_id"] = rec["chainID"]

        ## construct fragment_id
        if rec.has_key("resSeq"):
            if rec.has_key("iCode"):
                atm_map["fragment_id"] = "%d%s" % (rec["resSeq"],rec["iCode"])
            else:
                atm_map["fragment_id"] = "%d" % (rec["resSeq"])
                
        ## add the model number for the atom
        if self.model_num != None:
            atm_map["model_id"] = self.model_num

        ## position
        if rec.has_key("x"):
            atm_map["x"] = rec["x"]
        if rec.has_key("y"):
            atm_map["y"] = rec["y"]
        if rec.has_key("z"):
            atm_map["z"] = rec["z"]

        if rec.has_key("occupancy"):
            atm_map["occupancy"] = rec["occupancy"]
        if rec.has_key("tempFactor"):
            atm_map["temp_factor"] = rec["tempFactor"]

    def process_HETATM(self, rec):
        self.process_ATOM(rec)

    def process_SIGATM(self, rec):
        setmapf(rec, "sigX", self.atm_map, "sig_x")
        setmapf(rec, "sigY", self.atm_map, "sig_y")
        setmapf(rec, "sigZ", self.atm_map, "sig_z")
        setmapf(rec, "sigOccupancy", self.atm_map, "sig_occupancy")
        setmapf(rec, "sigTempFactor", self.atm_map, "sig_temp_factor")

    def process_ANISOU(self, rec):
        self.atm_map["u11"] = rec.get("u[0][0]", 0.0) / 10000.0
        self.atm_map["u22"] = rec.get("u[1][1]", 0.0) / 10000.0
        self.atm_map["u33"] = rec.get("u[2][2]", 0.0) / 10000.0
        self.atm_map["u12"] = rec.get("u[0][1]", 0.0) / 10000.0
        self.atm_map["u13"] = rec.get("u[0][2]", 0.0) / 10000.0
        self.atm_map["u23"] = rec.get("u[1][2]", 0.0) / 10000.0

    def process_SIGUIJ(self, rec):
        self.atm_map["sig_u11"] = rec.get("sig[1][1]", 0.0) / 10000.0
        self.atm_map["sig_u22"] = rec.get("sig[2][2]", 0.0) / 10000.0
        self.atm_map["sig_u33"] = rec.get("sig[3][3]", 0.0) / 10000.0
        self.atm_map["sig_u12"] = rec.get("sig[1][2]", 0.0) / 10000.0
        self.atm_map["sig_u13"] = rec.get("sig[1][3]", 0.0) / 10000.0
        self.atm_map["sig_u23"] = rec.get("sig[2][3]", 0.0) / 10000.0

    def process_MODEL(self, rec):
        self.model_num = rec.get("serial")

    def process_ENDMDL(self, rec):
        self.model_num = None

    def process_HEADER(self, rec):
        self.struct.header = "%s:%s:%s" % (rec.get("idCode", ""),
                                           rec.get("classification", ""),
                                           rec.get("depDate", ""))
        
        if rec.get("idCode"):
            self.load_structure_id(rec["idCode"])
        
        self.struct.cifdb.set_single(
            "struct_keywords", "pdbx_keywords", rec.get("classification"))
        self.struct.cifdb.set_single(
            "database_pdb_rev", "date_original", rec.get("depDate"))
        self.struct.cifdb.set_single(
            "entry", "id", rec.get("idCode"))

    def preprocess_TITLE(self, title):
        self.struct.title = title
        self.struct.cifdb.set_single("struct", "title", title)

    def preprocess_COMPND(self, compnd_list):
        entity = self.struct.cifdb.confirm_table("entity")
        entity_keywords = self.struct.cifdb.confirm_table("entity_keywords")

        for compnd in compnd_list:
            erow = mmCIF.mmCIFRow()
            ekrow = mmCIF.mmCIFRow()

            setmaps(compnd, "MOLECULE", erow, "pdbx_description")
            if erow:
                entity.append(erow)

            setmaps(compnd, "FRAGMENT", ekrow, "pdbx_fragment")
            setmaps(compnd, "EC", ekrow, "pdbx_ec")
            setmaps(compnd, "MUTATION", ekrow, "pdbx_mutation")
            if ekrow:
                entity_keywords.append(ekrow)

    def preprocess_SOURCE(self, source_list):
        entity_src_nat = self.struct.cifdb.confirm_table("entity_src_nat")
        entity_src_gen = self.struct.cifdb.confirm_table("entity_src_gen")

        for source in source_list:
            nrow = mmCIF.mmCIFRow()
            grow = mmCIF.mmCIFRow()

            setmaps(source, "FRAGMENT",
                    grow, "pdbx_gene_src_fragment")
            setmaps(source, "ORGANISM_SCIENTIFIC",
                    grow, "pdbx_gene_src_scientific_name")
            setmaps(source, "ORGANISM_COMMON",
                    grow, "pdbx_gene_src_common_name")            
            setmaps(source, "GENUS",
                    grow, "pdbx_gene_src_genus")
            setmaps(source, "GENUS",
                    grow, "pdbx_gene_src_genus")
            setmaps(source, "SPECIES",
                    grow, "pdbx_gene_src_species")
            setmaps(source, "STRAIN",
                    grow, "pdbx_gene_src_strain")
            setmaps(source, "VARIANT",
                    grow, "pdbx_gene_src_variant")
            setmaps(source, "CELL_LINE",
                    grow, "pdbx_gene_src_cell_line")
            setmaps(source, "ATCC",
                    grow, "pdbx_gene_src_atcc")
            setmaps(source, "ORGAN",
                    grow, "pdbx_gene_src_organ")
            setmaps(source, "TISSUE",
                    grow, "pdbx_gene_src_tissue")
            setmaps(source, "CELL",
                    grow, "pdbx_gene_src_cell")
            setmaps(source, "ORGANELLE",
                    grow, "pdbx_gene_src_organelle")
            setmaps(source, "SECRETION",
                    nrow, "pdbx_secretion")
            setmaps(source, "CELLULAR_LOCATION",
                    grow, "pdbx_gene_src_cellular_location")
            setmaps(source, "PLASMID",
                    nrow, "pdbx_plasmid_name")
            setmaps(source, "GENE",
                    grow, "pdbx_gene_src_gene")
            setmaps(source, "EXPRESSION_SYSTEM",
                    grow, "pdbx_host_org_scientific_name")
            setmaps(source, "EXPRESSION_SYSTEM_COMMON",
                    grow, "pdbx_host_org_common_name")
            setmaps(source, "EXPRESSION_SYSTEM_GENUS",
                    grow, "pdbx_host_org_genus")
            setmaps(source, "EXPRESSION_SYSTEM_SPECIES",
                    grow, "pdbx_host_org_species")
            setmaps(source, "EXPRESSION_SYSTEM_STRAIN",
                    grow, "pdbx_host_org_strain")
            setmaps(source, "EXPRESSION_SYSTEM_VARIANT",
                    grow, "pdbx_host_org_variant")
            setmaps(source, "EXPRESSION_SYSTEM_CELL_LINE",
                    grow, "pdbx_host_org_cell_line")
            setmaps(source, "EXPRESSION_SYSTEM_ATCC_NUMBER",
                    grow, "pdbx_host_org_atcc")
            setmaps(source, "EXPRESSION_SYSTEM_ORGAN",
                    grow, "pdbx_host_org_organ")
            setmaps(source, "EXPRESSION_SYSTEM_TISSUE",
                    grow, "pdbx_host_org_tissue")
            setmaps(source, "EXPRESSION_SYSTEM_CELL",
                    grow, "pdbx_host_org_cell")
            setmaps(source, "EXPRESSION_SYSTEM_ORGANELLE",
                    grow, "pdbx_host_org_organelle")
            setmaps(source, "EXPRESSION_SYSTEM_CELLULAR_LOCATION",
                    grow, "pdbx_host_org_cellular_location")
            setmaps(source, "EXPRESSION_SYSTEM_VECTOR_TYPE",
                    grow, "pdbx_host_org_vector_type")
            setmaps(source, "EXPRESSION_SYSTEM_VECTOR",
                    grow, "pdbx_host_org_vector")
            setmaps(source, "EXPRESSION_SYSTEM_PLASMID",
                    grow, "plasmid")
            setmaps(source, "EXPRESSION_SYSTEM_GENE",
                    grow, "pdbx_host_org_gene")
            setmaps(source, "OTHER_DETAILS",
                    grow, "pdbx_description")

            if nrow:
                entity_src_nat.append(nrow)
            if grow:
                entity_src_gen.append(grow)

    def preprocess_KEYWDS(self, keywds_list):
        struct_keywords = self.struct.cifdb.confirm_table("struct_keywords")
        for keywds in keywds_list:
            struct_keywords.append(mmCIF.mmCIFRow({"text": keywds}))

    def preprocess_AUTHOR(self, author_list):
        audit_author = self.struct.cifdb.confirm_table("audit_author")
        for author in author_list:
            audit_author.append(mmCIF.mmCIFRow({"name": author}))

    def preprocess_EXPDTA(self, expdta_list):
        for technique, details in expdta_list:
            self.struct.experimental_method = technique
            break
        
        exptl = self.struct.cifdb.confirm_table("exptl")
        for (technique, details) in expdta_list:
            row = mmCIF.mmCIFRow({"method": technique})
            if details:
                row["details"] = details
            exptl.append(row)

    def preprocess_SEQRES(self, seqres):
        self.load_sequence(seqres)

    def process_CRYST1(self, rec):
        ucell_map = {}

        setmapf(rec, "a", ucell_map, "a")
        setmapf(rec, "b", ucell_map, "b")
        setmapf(rec, "c", ucell_map, "c")
        setmapf(rec, "alpha", ucell_map, "alpha")
        setmapf(rec, "beta", ucell_map, "beta")
        setmapf(rec, "gamma", ucell_map, "gamma")

        setmaps(rec, "sgroup", ucell_map, "space_group")
        setmapi(rec, "z", ucell_map, "z")

        self.load_unit_cell(ucell_map)

    def process_HELIX(self, rec):
        ## the helixID field is mandatory
        try:
            helix_id = rec["helixID"]
        except KeyError:
            return

        ## get the dictionary describing this helix or
        ## create it if it doesn't exist
        helix = None
        for helix_x in self.helix_list:
            if helix_x["helix_id"]==helix_id:
                helix = helix_x
                break

        ## new helix dictionary
        if helix is None:
            helix = {"helix_id": helix_id}
            self.helix_list.append(helix)

        setmaps(rec, "initResName", helix, "res_name1")
        setmaps(rec, "endResName",  helix, "res_name2")

        setmaps(rec, "initChainID", helix, "chain_id1")
        setmaps(rec, "endChainID",  helix, "chain_id2")
        
        frag_id1 = self.get_fragment_id(rec, "initSeqNum", "initICode")
        if frag_id1 is not None:
            helix["frag_id1"] = frag_id1

        frag_id2 = self.get_fragment_id(rec, "endSeqNum", "endICode")
        if frag_id2 is not None:
            helix["frag_id2"] = frag_id2

        setmaps(rec, "helixClass", helix, "helix_class")
        setmaps(rec, "comment", helix, "details")

    def process_SHEET(self, rec):
        ## the sheetID field is mandatory
        try:
            sheet_id = rec["sheetID"]
        except KeyError:
            return

        ## get the dictionary describing this sheet or
        ## create it if it doesn't exist
        sheet = None
        for sheet_x in self.beta_sheet_list:
            if sheet_x["sheet_id"]==sheet_id:
                sheet = sheet_x
                break

        ## new sheet dictionary
        if sheet is None:
            sheet = {"sheet_id": sheet_id}
            self.beta_sheet_list.append(sheet)
            setmapi(rec, "numStrands", sheet, "num_strands")

        ## create the dictionary for this strand
        strand = {}

        setmaps(rec, "initResName", strand, "res_name1")
        setmaps(rec, "initChainID", strand, "chain_id1")
        frag_id1 = self.get_fragment_id(rec, "initSeqNum", "initICode")
        if frag_id1 is not None:
            strand["frag_id1"] = frag_id1

        setmaps(rec, "endResName", strand, "res_name2")
        setmaps(rec, "endChainID", strand, "chain_id2")
        frag_id2 = self.get_fragment_id(rec, "endSeqNum", "endICode")
        if frag_id2 is not None:
            strand["frag_id2"] = frag_id2

        ## sense
        if rec.has_key("sense"):
            if rec["sense"]==1:
                strand["sense"] = "parallel"
            elif rec["sense"]==-1:
                strand["sense"] = "anti_parallel"

        ## registration with previous strand
        setmaps(rec, "curResName", strand, "reg_res_name")
        setmaps(rec, "curChainID", strand, "reg_chain_id")
        reg_frag_id = self.get_fragment_id(rec, "curResSeq", "curICode")
        if reg_frag_id is not None:
            strand["reg_frag_id"] = reg_frag_id
        setmaps(rec, "curAtom", strand, "reg_atom")

        setmaps(rec, "prevResName", strand, "reg_prev_res_name")
        setmaps(rec, "prevChainID", strand, "reg_prev_chain_id")
        reg_prev_frag_id = self.get_fragment_id(rec, "prevResSeq", "prevICode")
        if reg_prev_frag_id is not None:
            strand["reg_prev_frag_id"] = reg_prev_frag_id
        setmaps(rec, "prevAtom", strand, "reg_prev_atom")

        ## append to the strand list
        try:
            sheet["strand_list"].append(strand)
        except KeyError:
            sheet["strand_list"] = [strand]
            
    def process_SITE(self, rec):
        ## the siteID field is mandatory
        try:
            site_id = rec["siteID"]
        except KeyError:
            return

        ## get the dictionary describing this site or
        ## create it if it doesn't exist
        site = None
        for site_x in self.site_list:
            if site_x["site_id"] == site_id:
                site = site_x
                break

        ## new site dictionary
        if site == None:
            site = {"site_id": site_id}
            self.site_list.append(site)
            setmapi(rec, "numRes", site, "num_residues")

        ## add the residue descriptions
        for i in (1, 2, 3, 4):
            chain_key = "chainID%d" % (i)
            res_name  = "resName%d" % (i)
            seq_key   = "seq%d" % (i)
            icode_key = "icode%d" % (i)

            ## check for manditory fields
            try:
                rec[chain_key]
                rec[seq_key]
            except KeyError:
                break

            ## get resiude information and create dictionary
            residue = {}

            setmaps(rec, chain_key, residue, "chain_id")
            setmaps(rec, res_name,  residue, "res_name")
            residue["frag_id"] =  self.get_fragment_id(
                rec, seq_key, icode_key)

            ## add the fragment description to the site description
            ## fragment list
            try:
                site["fragment_list"].append(residue)
            except KeyError:
                site["fragment_list"] = [residue]

    def bond_processor(self, **args):
        """Complicated method.  Required arguments are:
        rec = PDB record
        atm1/2 = Atom object, if you want to override the lookup
        chain_id_field1/2: PDB field name for the chain ID
        res_seq1/2_field: PDB field for the residue sequence num
        icode1/2_field: PDB field for the residue insertion code
        name1/2_field: PDB field for the atom name
        atl_loc1/2: PDB filed name for the atom alt_loc
        symop1/2_field: PDB field name for the atom symmetry operation
        
        chain_id1/2: override the chain ID
        frag_id1/2: override the fragmetn ID
        name1/2: override the atom name
        alt_loc1/2: override the atom alt_loc
        """
        rec = args["rec"]

        def get_atom(chain_id, frag_id, name, alt_loc):
            try:
                atm = self.struct[chain_id][frag_id][name]
            except KeyError:
                return None
            except TypeError:
                return None
            
            if alt_loc:
                try:
                    atm = atm[alt_loc]
                except KeyError:
                    pass

            return atm

        ## get atm1
        try:
            atm1 = args["atm1"]
        except KeyError:
            chain_id1 = args.get("chain_id1") or rec.get(args["chain_id1_field"])
            frag_id1 = args.get("frag_id1") or self.get_fragment_id(rec, args["res_seq1_field"],args["icode1_field"])
            name1 = args.get("name1") or rec.get("name1_field")
            alt_loc1 = args.get("alt_loc1") or rec.get(args["alt_loc1_field"])
            atm1 = get_atom(chain_id1, frag_id1, name1, alt_loc1)

        ## get atm2
        try:
            atm2 = args["atm2"]
        except KeyError:
            chain_id2 = args.get("chain_id2") or rec.get(args["chain_id2_field"])
            frag_id2 = args.get("frag_id2") or  self.get_fragment_id(rec, args["res_seq2_field"],args["icode2_field"])
            name2 = args.get("name2") or  rec.get("name2_field")
            alt_loc2 = args.get("alt_loc2") or  rec.get(args["alt_loc2_field"])
            atm2 = get_atom(chain_id2, frag_id2, name2, alt_loc2)

        ## unable to retrieve the atoms?
        if not (atm1 and atm2):
            return None

        ## the bond map is keyed from the 2-tuple of the atoms involved in
        ## the bond; they are sorted by their object ID just to have
        ## a definate order
        if id(atm1) < id(atm2):
            bkey = (atm1, atm2)
        else:
            bkey = (atm2, atm1)

        try:
            bond = self.bond_map[bkey]
        except KeyError:
            bond = self.bond_map[bkey] = {}

        ## set bond type
        bond["bond_type"] = args["bond_type"]

        ## symmetry operations
        symop1 = args.get("symop1") or rec.get(args["symop1_field"])
        symop2 = args.get("symop2") or  rec.get(args["symop2_field"])

        if symop1:
            bond["symop1"] = symop1
        if symop2:
            bond["symop2"] = symop2

        return bkey

    def process_SSBOND(self, rec):
        x = self.bond_processor(
            rec = rec,
            
            bond_type = "disulf",
            
            chain_id1_field = "chainID1",
            res_seq1_field = "seqNum1",
            icode1_field = "iCode1",
            name1 = "SG",
            alt_loc1_field = None,
            symop1_field = "sym1",
            
            chain_id2_field = "chainID2",
            res_seq2_field = "seqNum2",
            icode2_field = "iCode2",
            name2 = "SG",
            alt_loc2_field = None,
            symop2_field = "sym2")

        if not x:
            self.pdb_error("SSBOND", "Atom not found")

    def process_LINK(self, rec):
        x = self.bond_processor(
            rec = rec,
            
            bond_type = "covale",
            
            chain_id1_field = "chainID1",
            res_seq1_field = "resSeq1",
            icode1_field = "iCode1",
            name1_field = "name1",
            alt_loc1_field = "altLoc1",
            symop1_field = "sym1",
            
            chain_id2_field = "chainID2",
            res_seq2_field = "resSeq2",
            icode2_field = "iCode2",
            name2_field = "name2",
            alt_loc2_field = "altLoc2",
            symop2_field = "sym2")

        if not x:
            self.pdb_error("LINK", "Atom not found")

    def process_HYDBND(self, rec):
        ## retrieve the hydrogen atom
        try:
            name = rec["nameH"]
            alt_loc = rec.get("altLocH", "")
            chain_id = rec["chainH"]
            frag_id = self.get_fragment_id(rec, "resSeqH", "iCodeH")
            atmh = self.struct[chain_id][frag_id][name][alt_loc]
        except KeyError:
            atmh = None
        
        x = self.bond_processor(
            rec = rec,
            
            bond_type = "hydrog",
            
            chain_id1_field = "chainID1",
            res_seq1_field = "resSeq1",
            icode1_field = "iCode1",
            name1_field = "name1",
            alt_loc1_field = "altLoc1",
            symop1_field = "sym1",
            
            chain_id2_field = "chainID2",
            res_seq2_field = "resSeq2",
            icode2_field = "iCode2",
            name2_field = "name2",
            alt_loc2_field = "altLoc2",
            symop2_field = "sym2")
        
        if not x:
            self.pdb_error("HYDBND", "Atom not found")

    def process_SLTBRG(self, rec):
        x = self.bond_processor(
            rec = rec,
            
            bond_type = "saltbr",
            
            chain_id1_field = "chainID1",
            res_seq1_field = "resSeq1",
            icode1_field = "iCode1",
            name1_field = "name1",
            alt_loc1_field = "altLoc1",
            symop1_field = "sym1",
            
            chain_id2_field = "chainID2",
            res_seq2_field = "resSeq2",
            icode2_field = "iCode2",
            name2_field = "name2",
            alt_loc2_field = "altLoc2",
            symop2_field = "sym2")

        if not x:
            self.pdb_error("SLTBRG", "Atom not found")
        
    def process_CONECT(self, rec):
        try:
            serial = rec["serial"]
        except KeyError:
            self.pdb_error("CONECT", "missing serial field")
            return

        try:
            atm1 = self.atom_serial_map[serial]
        except KeyError:
            self.pdb_error("CONECT", "incorrect serial number")
            return

        def helper_func(field_list, bond_type):
            for field in field_list:
                try:
                    serial2 = rec[field]
                except KeyError:
                    continue

                try:
                    atm2 = self.atom_serial_map[serial2]
                except KeyError:
                    self.pdb_error("CONECT", "incorrect serial number")
                    continue

                self.bond_processor(
                    rec = rec,
                    bond_type = bond_type,
                    atm1 = atm1,
                    atm2 = atm2,
                    symop1_field = None,
                    symop2_field = None)

        helper_func(
            ["serialBond1","serialBond2",
             "serialBond3","serialBond4"], "covale")
        helper_func(
            ["serialHydBond1","serialHydBond2",
             "serialHydBond3","serialHydBond4"], "hydrog")
        helper_func(
            ["serialSaltBond1","serialSaltBond2"], "saltbr")


class PDBFileBuilder(object):
    """Builds a PDBFile object from a Structure object.
    """
    def __init__(self, struct, pdb_file):
        self.struct = struct
        self.pdb_file = pdb_file

        self.atom_count = 0
        self.atom_serial_num = 0
        self.atom_serial_map = {}

        self.add_title_section()
        self.add_primary_structure_section()
        self.add_heterogen_section()
        self.add_secondary_structure_section()
        self.add_connectivity_annotation_section()
        self.add_miscellaneous_fatures_section()
        self.add_crystallographic_coordinate_transformation_section()
        self.add_coordinate_section()
        self.add_connectivity_section()
        self.bookkeeping_section()

    def next_serial_number(self):
        self.atom_serial_num += 1
        return self.atom_serial_num

    def new_atom_serial(self, atm):
        """Gets the next available atom serial number for the given atom
        instance, and stores a map from atm->atom_serial_num for use
        when creating PDB records which require serial number identification
        of the atoms.
        """
        assert isinstance(atm, Structure.Atom)
        
        try:
            return self.atom_serial_map[atm]
        except KeyError:
            pass
        atom_serial_num = self.next_serial_number()
        self.atom_serial_map[atm] = atom_serial_num
        return atom_serial_num

    def set_from_cifdb(self, rec, field, ctbl, ccol):
        try:
            rec[field] = self.struct.cifdb[ctbl][ccol]
        except KeyError:
            pass

    def add_title_section(self):
        """ HEADER, TITLE, EXPDTA, AUTHOR
        """
        ## add HEADER records
        header = PDB.HEADER()
        self.pdb_file.append(header)

        header["idCode"] = self.struct.structure_id
        self.set_from_cifdb(header, "depDate", "database_pdb_rev", "date_original")
        self.set_from_cifdb(header, "classification", "struct_keywords", "pdbx_keywords")

        ## add TITLE records
        try:
            struct_title = self.struct.cifdb["struct"]["title"]
        except KeyError:
            pass
        else:
            cont = 0
            while len(struct_title):
                stx = struct_title[:60]
                struct_title = struct_title[60:]
        
                title = PDB.TITLE()
                self.pdb_file.append(title)

                cont += 1
                if cont > 1:
                    title["continuation"] = cont

                title["title"] = stx

        ## add EXPDTA records
        try:
            exptl_method = self.struct.cifdb["exptl"]["method"]
        except KeyError:
            pass
        else:
            expdta = PDB.EXPDTA()
            self.pdb_file.append(expdta)
            expdta["technique"] = exptl_method

        ## add AUTHOR records
        ## XXX: need to write a function to fix author names to PDB format
        try:
            audit_author = self.struct.cifdb["audit_author"]
        except KeyError:
            pass
        else:
            name_list = []
            for cif_row in audit_author:
                try:
                    name_list.append(cif_row["name"])
                except KeyError:
                    pass

            author = PDB.AUTHOR()
            self.pdb_file.append(author)
            author["authorList"] = ",".join(name_list)

    def add_primary_structure_section(self):
        """DBREF,SEQADV,SEQRES,MODRES
        """
        for chain in self.struct.iter_chains():
            if len(chain.sequence) == 0:
                continue

            sernum = 0
            seq_len = len(chain.sequence)            
            seq_index = 0
            while seq_index < seq_len:
                seqres = PDB.SEQRES()
                self.pdb_file.append(seqres)

                sernum += 1
                seqres["serNum"]  = sernum
                seqres["chainID"] = chain.chain_id
                seqres["numRes"]  = seq_len
                
                for field in ["resName1","resName2","resName3","resName4",
                              "resName5","resName6","resName7","resName8",
                              "resName9","resName10","resName11","resName12",
                              "resName13"]:
                    try:
                        seqres[field] = chain.sequence[seq_index]
                    except IndexError:
                        break
                    seq_index += 1

    def add_heterogen_section(self):
        """HET,HETNAM,HETSYN,FORMUL
        """
        pass

    def add_secondary_structure_section(self):
        """HELIX,SHEET,TURN
        PDB files do not put separate secondary structure descriptions
        within MODEL definitions, so you have to hope the models
        do not differ in secondary structure.  mmLib allows separate
        MODELs to have different secondary structure, but one MODEL must
        be chosen for the PDF file, so the default Model of the Structure
        is used.
        """

        ## HELIX
        serial_num = 0
        for alpha_helix in self.struct.iter_alpha_helicies():
            serial_num += 1

            helix = PDB.HELIX()
            self.pdb_file.append(helix)

            helix["serNum"]      = serial_num
            helix["helixID"]     = alpha_helix.helix_id
            helix["helixClass"]  = alpha_helix.helix_class

            helix["initResName"] = alpha_helix.res_name1
            helix["initChainID"] = alpha_helix.chain_id1
            try:
                helix["initSeqNum"], helix["initICode"] = Structure.fragment_id_split( alpha_helix.fragment_id1)
            except ValueError:
                pass

            helix["endResName"]  = alpha_helix.res_name2
            helix["endChainID"]  = alpha_helix.chain_id2
            try:
                helix["endSeqNum"], helix["endICode"] = Structure.fragment_id_split(alpha_helix.fragment_id2)
            except ValueError:
                pass

            helix["comment"]     = alpha_helix.details
            helix["initChainID"] = alpha_helix.chain_id1
            helix["length"]      = alpha_helix.helix_length

        ## SHEET
        for beta_sheet in self.struct.iter_beta_sheets():
            num_strands = len(beta_sheet.strand_list)

            strand_num = 0
            for strand in beta_sheet.iter_strands():
                strand_num += 1

                sheet = PDB.SHEET()
                self.pdb_file.append(sheet)

                sheet["strand"]     = strand_num
                sheet["sheetID"]    = beta_sheet.sheet_id
                sheet["numStrands"] = num_strands
                
                sheet["initResName"] = strand.res_name1
                sheet["initChainID"] = strand.chain_id1
                try:
                    sheet["initSeqNum"], sheet["initICode"] = Structure.fragment_id_split(strand.fragment_id1)
                except ValueError:
                    pass
                
                sheet["endResName"] = strand.res_name2
                sheet["endChainID"] = strand.chain_id2
                try:
                    sheet["endSeqNum"], sheet["endICode"] = Structure.fragment_id_split(strand.fragment_id2)
                except ValueError:
                    pass
                
                sheet["curAtom"]    = strand.reg_atom
                sheet["curResName"] = strand.reg_res_name
                sheet["curChainID"] = strand.reg_chain_id

                try:
                    sheet["curSeqNum"], sheet["curICode"] = Structure.fragment_id_split(strand.reg_fragment_id)
                except ValueError:
                    pass

                sheet["prevAtom"]    = strand.reg_prev_atom
                sheet["prevResName"] = strand.reg_prev_res_name
                sheet["prevChainID"] = strand.reg_prev_chain_id
                try:
                    sheet["prevSeqNum"],sheet["prevICode"] = Structure.fragment_id_split(strand.reg_prev_fragment_id)
                except ValueError:
                    pass

    def add_connectivity_annotation_section(self):
        """SSBOND,LINK,SLTBRG,CISPEP
        """
        pass

    def add_miscellaneous_fatures_section(self):
        """SITE
        """
        serial_num = 0
        for site in self.struct.iter_sites():
            num_fragments = len(site.fragment_dict_list) 

            site_pdb  = None
            key_index = 0
            for frag_dict in site.fragment_dict_list:

                if site_pdb is None or key_index==4:
                    serial_num += 1

                    key_index = 0

                    site_pdb = PDB.SITE()
                    self.pdb_file.append(site_pdb)

                    site_pdb["serNum"] = serial_num
                    site_pdb["siteID"] = site.site_id
                    site_pdb["numRes"] = num_fragments

                chain_id  = "chainID%d" % (key_index)
                res_name  = "resName%d" % (key_index)
                res_seq   = "seq%d"     % (key_index)
                icode     = "icode%d"   % (key_index)

            site_pdb[chain_id] = frag_dict["chain_id"]
            site_pdb[res_name] = frag_dict["res_name"]
            try:
                site_pdb[res_seq], site_pdb[icode] = Structure.fragment_id_split(frag_dict["frag_id"])
            except KeyError:
                pass

    def add_crystallographic_coordinate_transformation_section(self):
        """CRYST1,ORIGXn,SCALEn,MTRIXn,TVECT
        """
        cryst1 = PDB.CRYST1()
        self.pdb_file.append(cryst1)

        unit_cell = self.struct.unit_cell

        cryst1["a"] = self.struct.unit_cell.a
        cryst1["b"] = self.struct.unit_cell.b
        cryst1["c"] = self.struct.unit_cell.c
        cryst1["alpha"] = self.struct.unit_cell.calc_alpha_deg()
        cryst1["beta"] = self.struct.unit_cell.calc_beta_deg()
        cryst1["gamma"] = self.struct.unit_cell.calc_gamma_deg()
        cryst1["sgroup"] = self.struct.unit_cell.space_group.pdb_name

    def add_coordinate_section(self):
        """ MODEL,ATOM,SIGATM,ANISOU,SIGUIJ,TER,HETATM,ENDMDL 
        """
        if len(self.struct.model_list) > 1:
            ## case 1: multiple models
            orig_model = self.struct.default_model
            
            for model in self.struct.iter_models():
                self.struct.default_model = model

                model_rec = PDB.MODEL()
                self.pdb_file.append(model_rec)
                model_rec["serial"] = model.model_id

                self.add_atom_records()

                endmdl = PDB.ENDMDL()
                self.pdb_file.append(endmdl)

            self.struct.default_model = orig_model

        else:
            ## case 2: single model
            self.add_atom_records()

    def add_connectivity_section(self):
        """CONECT
        """
        pass
    
    def bookkeeping_section(self):
        """MASTER,END
        """
        ## END
        end = PDB.END()
        self.pdb_file.append(end)

    def add_atom_records(self):
        """With a default model set, output all the ATOM and associated
        records for the model.
        """
        ## atom records for standard groups
        for chain in self.struct.iter_chains():
            res = None
            
            for res in chain.iter_standard_residues():
                for atm in res.iter_all_atoms():
                    self.add_ATOM("ATOM", atm)

            ## chain termination record
            if res:
                ter_rec = PDB.TER()
                self.pdb_file.append(ter_rec)
                res_seq, icode = Structure.fragment_id_split(res.fragment_id)
                ter_rec["serial"]  = self.next_serial_number()
                ter_rec["resName"] = res.res_name
                ter_rec["chainID"] = res.chain_id
                ter_rec["resSeq"]  = res_seq
                ter_rec["iCode"]   = icode

        ## hetatm records for non-standard groups
        for chain in self.struct.iter_chains():
            for frag in chain.iter_non_standard_residues():
                for atm in frag.iter_all_atoms():
                    self.add_ATOM("HETATM", atm)

    def add_ATOM(self, rec_type, atm):
        """Adds ATOM/SIGATM/ANISOU/SIGUIJ/TER/HETATM 
        """
        self.atom_count += 1

        if rec_type == "ATOM":
            atom_rec = PDB.ATOM()
        elif rec_type == "HETATM":
            atom_rec = PDB.HETATM()

        self.pdb_file.append(atom_rec)

        serial = self.new_atom_serial(atm)
        res_seq, icode = Structure.fragment_id_split(atm.fragment_id)

        atom_rec["serial"]      = serial
        atom_rec["chainID"]     = atm.chain_id
        atom_rec["resName"]     = atm.res_name
        atom_rec["resSeq"]      = res_seq
        atom_rec["iCode"]       = icode
        atom_rec["name"]        = atm.name
        atom_rec["element"]     = atm.element
        atom_rec["altLoc"]      = atm.alt_loc

        if atm.position is not None:
            if atm.position[0] is not None:
                atom_rec["x"] = atm.position[0]
            if atm.position[1] is not None:
                atom_rec["y"] = atm.position[1]
            if atm.position[2] is not None:
                atom_rec["z"] = atm.position[2]

        if atm.occupancy is not None:
            atom_rec["occupancy"] = atm.occupancy

        if atm.temp_factor is not None:
            atom_rec["tempFactor"] = atm.temp_factor

        if atm.charge is not None:
            atom_rec["charge"] = atm.charge

        def atom_common(arec1, arec2):
            if arec1.has_key("serial"):
                arec2["serial"] = arec1["serial"]
            if arec1.has_key("chainID"):
                arec2["chainID"] = arec1["chainID"]
            if arec1.has_key("resName"):
                arec2["resName"] = arec1["resName"]
            if arec1.has_key("resSeq"):
                arec2["resSeq"] = arec1["resSeq"]
            if arec1.has_key("iCode"):
                arec2["iCode"] = arec1["iCode"]
            if arec1.has_key("name"):
                arec2["name"] = arec1["name"]
            if arec1.has_key("altLoc"):
                arec2["altLoc"] = arec1["altLoc"]
            if arec1.has_key("element"):
                arec2["element"] = arec1["element"]
            if arec1.has_key("charge"):
                arec2["charge"] = arec1["charge"]

        if atm.sig_position is not None:
            sigatm_rec = PDB.SIGATM()
            self.pdb_file.append(sigatm_rec)
            atom_common(atom_rec, sigatm_rec)

            if atm.sig_position[0] is not None:
                sigatm_rec["sigX"] = atm.sig_position[0]
            if atm.sig_position[1] is not None:
                sigatm_rec["sigY"] = atm.sig_position[1]
            if atm.sig_position[2] is not None:
                sigatm_rec["sigZ"] = atm.sig_position[2]
            if atm.sig_temp_factor is not None:
                sigatm_rec["sigTempFactor"] = atm.sig_temp_factor
            if atm.sig_occupancy is not None:
                sigatm_rec["sigOccupancy"] = atm.sig_occupancy

        if atm.U is not None:
            anisou_rec = PDB.ANISOU()
            self.pdb_file.append(anisou_rec)
            atom_common(atom_rec, anisou_rec)

            if atm.U[0,0] is not None:
                anisou_rec["u[0][0]"] = int(round(atm.U[0,0] * 10000.0))
            if atm.U[1,1] is not None:
                anisou_rec["u[1][1]"] = int(round(atm.U[1,1] * 10000.0))
            if atm.U[2,2] is not None:
                anisou_rec["u[2][2]"] = int(round(atm.U[2,2] * 10000.0))
            if atm.U[0,1] is not None:
                anisou_rec["u[0][1]"] = int(round(atm.U[0,1] * 10000.0))
            if atm.U[0,2] is not None:
                anisou_rec["u[0][2]"] = int(round(atm.U[0,2] * 10000.0))
            if atm.U[1,2] is not None:
                anisou_rec["u[1][2]"] = int(round(atm.U[1,2] * 10000.0))

        if atm.sig_U is not None:
            siguij_rec = PDB.SIGUIJ()
            self.pdb_file.append(siguij_rec)
            atom_common(atom_rec, siguij_rec)

            if atm.sig_U[0,0] is not None:
                siguij_rec["u[0][0]"] = int(round(atm.sig_U[0,0] * 10000.0))
            if atm.sig_U[1,1] is not None:
                siguij_rec["u[1][1]"] = int(round(atm.sig_U[1,1] * 10000.0))
            if atm.sig_U[2,2] is not None:
                siguij_rec["u[2][2]"] = int(round(atm.sig_U[2,2] * 10000.0))
            if atm.sig_U[0,1] is not None:
                siguij_rec["u[0][1]"] = int(round(atm.sig_U[0,1] * 10000.0))
            if atm.sig_U[0,2] is not None:
                siguij_rec["u[0][2]"] = int(round(atm.sig_U[0,2] * 10000.0))
            if atm.sig_U[1,2] is not None:
                siguij_rec["u[1][2]"] = int(round(atm.sig_U[1,2] * 10000.0))

