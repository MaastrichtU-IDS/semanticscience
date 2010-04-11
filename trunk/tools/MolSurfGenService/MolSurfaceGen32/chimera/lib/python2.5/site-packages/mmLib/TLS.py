## Copyright 2002-2006 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Utility classes for loading, manipulating, and analyzing TLS parameters.
"""
import re
import fpformat
import math

try:
    import numpy
    try:
        from numpy.oldnumeric import linear_algebra as linalg
    except ImportError:
        from numpy.linalg import old as linalg
except ImportError:
    import NumericCompat as numpy
    from NumericCompat import linalg

import Constants
import ConsoleOutput
import AtomMath
import PDB
import Structure
import Viewer
import Gaussian
import Colors

###############################################################################
## EXCEPTION BASE CLASS
##

class TLSError(Exception):
    """Base exception class for TLS module exceptions.
    """
    pass

###############################################################################
## SUPPORTED TLS FILE FORMATS
##

class TLSFileFormatError(TLSError):
    """Raised when a file format error is encountered while loading a
    TLS group description file.
    """
    pass


class TLSGroupDesc(object):
    """Description of one TLS Group.
    """
    def __init__(self):
        self.name       = ""     # text name
        self.origin     = None   # array(3)
        self.range_list = []     # (chain1, res1, chain2, res2, selection)
        self.T          = None   # array(3,3)
        self.L          = None   # array(3,3)
        self.S          = None   # array(3,3)

    def set_name(self, name):
        """Sets the TLS group name.
        """
        self.name = name

    def set_origin(self, x, y, z):
        """Sets the TLS group origin of calculations.
        """
        self.origin = numpy.array((x, y, z), float)

    def add_range(self, chain_id1, frag_id1, chain_id2, frag_id2, selection):
        """Adds a segment of residues to the TLS group.  Not too sure how to
        handle segments which span chains, so assert on that condition.
        """
        assert chain_id1 == chain_id2
        self.range_list.append((chain_id1, frag_id1, chain_id2, frag_id2, selection))

    def set_T(self, t11, t22, t33, t12, t13, t23):
        """Sets the T tensor from the component arguments.  Units are in
        square Angstroms.
        """
        self.T = numpy.array( [[t11, t12, t13],
                               [t12, t22, t23],
                               [t13, t23, t33]], float)

    def set_L(self,  l11, l22, l33, l12, l13, l23):
        """Sets the L tensor from the component arguments.  Units are in
        square Radians.
        """
        self.L = numpy.array( [[l11, l12, l13],
                               [l12, l22, l23],
                               [l13, l23, l33]], float)

    def set_L_deg2(self,  l11, l22, l33, l12, l13, l23):
        """Sets the L tensor from the component arguments.  Units are in
        square Degrees.
        """
        self.set_L(l11*Constants.DEG2RAD2, l22*Constants.DEG2RAD2, l33*Constants.DEG2RAD2,
                   l12*Constants.DEG2RAD2, l13*Constants.DEG2RAD2, l23*Constants.DEG2RAD2)

    def set_S(self, s2211, s1133, s12, s13, s23, s21, s31, s32):
        """Sets the S tensor from the component arguments.  Units are in
        Radians*Angstroms.  The trace of S is set to 0.0.
        """
        s22 = 2.0*(s2211)/3.0 + s1133/3.0
        s11 = s22 - s2211
        s33 = s11 - s1133

        self.S = numpy.array([[s11, s12, s13],
                              [s21, s22, s23],
                              [s31, s32, s33]])
        
    def set_S_deg(self, s2211, s1133, s12, s13, s23, s21, s31, s32):
        """Sets the S tensor from the component arguments.  Units are in
        Degrees*Angstroms.  The trace of S is set to 0.0.
        """
        self.set_S(s2211*Constants.DEG2RAD, s1133*Constants.DEG2RAD, s12*Constants.DEG2RAD,
                   s13*Constants.DEG2RAD,   s23*Constants.DEG2RAD,   s21*Constants.DEG2RAD,
                   s31*Constants.DEG2RAD,   s32*Constants.DEG2RAD)

    def set_tls_group(self, tls_group):
        """Sets the TLSGroupDesc tensor values from the TLSGroup instance.
        """
        self.set_origin(
            tls_group.origin[0],
            tls_group.origin[1],
            tls_group.origin[2])

        self.set_T(
            tls_group.T[0,0],
            tls_group.T[1,1],
            tls_group.T[2,2],
            tls_group.T[0,1],
            tls_group.T[0,2],
            tls_group.T[1,2])
            
        self.set_L(
            tls_group.L[0,0],
            tls_group.L[1,1],
            tls_group.L[2,2],
            tls_group.L[0,1],
            tls_group.L[0,2],
            tls_group.L[1,2])

        self.set_S(
            tls_group.S[1,1] - tls_group.S[0,0],
            tls_group.S[0,0] - tls_group.S[2,2],
            tls_group.S[0,1],
            tls_group.S[0,2],
            tls_group.S[1,2],
            tls_group.S[1,0],
            tls_group.S[2,0],
            tls_group.S[2,1])

    def is_null(self):
        """Returns True if the T,L,S tensors are not set, or are set
        with values of zero.
        """
        if self.T is None or self.L is None or self.S is None:
            return True
        return False

    def calc_tls_name(self):
        """Creates a name for the TLS group using the selected
        residue ranges.
        """
        listx = []
        for (chain_id1, frag_id1, chain_id2, frag_id2, sel) in self.range_list:
            listx.append("%s%s-%s%s %s" % (chain_id1, frag_id1, chain_id2, frag_id2, sel))
        return ";".join(listx)

    def iter_atoms(self, struct):
        """Uses the TLS definition and the given Structure object to iterate
        over all atoms which should be included in the TLS group according
        to the range_list definitions.
        """
        for (chain_id1, frag_id1, chain_id2, frag_id2, sel) in self.range_list:
            assert chain_id1 == chain_id2

            chain1 = struct.get_chain(chain_id1)
            if chain1 is None:
                ConsoleOutput.warning("iter_tls_atoms(): no chain id=%s" % (chain_id1))
                continue

            try:
                seg = chain1[frag_id1:frag_id2]
            except KeyError:
                ConsoleOutput.warning(
                    "iter_tls_atoms():unable to find segment={%s..%s}" % (frag_id1, frag_id2))

            for atm in seg.iter_all_atoms():
                yield atm

    def construct_tls_group(self):
        """Creates a TLSGroup() object with the origin, T, L, and S tensors
        set according to the TLS description.
        """
        tls_group = TLSGroup()

        if self.name == "":
            tls_group.name = self.calc_tls_name()
        else:
            tls_group.name = self.name

        if self.origin is not None:
            tls_group.set_origin(self.origin[0], self.origin[1], self.origin[2])

        if self.T is not None:
            tls_group.set_T(self.T[0,0], self.T[1,1], self.T[2,2], self.T[0,1], self.T[0,2], self.T[1,2])

        if self.L is not None:
            tls_group.set_L(self.L[0,0], self.L[1,1], self.L[2,2], self.L[0,1], self.L[0,2], self.L[1,2])

        if self.S is not None:
            ## s2211, s1133, s12, s13, s23, s21, s31, s32)
            tls_group.set_S(
                self.S[1,1] - self.S[0,0],
                self.S[0,0] - self.S[2,2],
                self.S[0,1],
                self.S[0,2],
                self.S[1,2],
                self.S[1,0],
                self.S[2,0],
                self.S[2,1])
        
        return tls_group

    def construct_tls_group_with_atoms(self, struct):
        """Creates a TLSGroup() object with the origin, T, L, and S tensors
        set according to the TLS description, the add the Atoms to the TLSGroup
        from the given argument Structure.
        """
        tls_group = self.construct_tls_group()
        
        for atm in self.iter_atoms(struct):
            tls_group.append(atm)

        return tls_group


class TLSFile(object):
    """Read/Write a TLS files containing one or more TLSGroupDesc
    objects.
    """
    def __init__(self):
        self.path          = None
        self.tls_desc_list = []
        self.file_format   = None

    def set_file_format(self, file_format):
        """Set a instance of a TLSFileFormat subclass to use for reading and
        writing TLS description files.
        """
        self.file_format = file_format
    
    def load(self, fil, path=None):
        """Load TLS description file using the current TLSFileFormat instance.
        """
        assert self.file_format is not None
        self.path = path
        self.tls_desc_list = self.file_format.load(fil)
        
    def save(self, fil, path=None):
        """Save TLS description file using the curent TLSFileFormat instance.
        """
        assert self.file_format is not None
        self.path = path
        self.file_format.save(fil, self.tls_desc_list)

    def construct_tls_groups(self, struct):
        """Returns a list of TLSGroup instances constructed from the
        TLSGroupDesc instances contained in this class.
        """
        tls_group_list = []

        for tls_desc in self.tls_desc_list:
            tls_group = tls_desc.construct_tls_group(struct)
            if tls_group is not None:
                tls_group_list.append(tls_group)

        return tls_group_list

    def construct_tls_groups_with_atoms(self, struct):
        """Returns a list of TLSGroup instances constructed from the Structure
        instance argument and the TLSGroupDesc instances contained in this
        class.
        """
        tls_group_list = []

        for tls_desc in self.tls_desc_list:
            tls_group = tls_desc.construct_tls_group_with_atoms(struct)
            if tls_group is not None:
                tls_group_list.append(tls_group)

        return tls_group_list

    
class TLSFileFormat(object):
    """Base class for TLS file types.
    """
    def load_supported(self):
        """Returns True if file loading is supported, otherwise returns False.
        """
        return False

    def save_supported(self):
        """Return True if file saving is supported, otherwise returns False.
        """
        return False
    
    def load(self, fil):
        """Returns a list containing one TLSGroupDesc object for each TLS group
        description found in the file.
        """
        pass

    def save(self, fil, tls_desc_list):
        """Writes the list of TLSGroupDesc object to the given file.
        """
        pass


class TLSFileFormatPDB(TLSFileFormat, PDB.RecordProcessor):
    """Reads TLS descriptions from the REMARK records in PDB files.  These
    records are only written by REFMAC5.
    """
    pdb_regex_dict = {
        "group":       re.compile("\s*TLS GROUP :\s+(\d+)\s*$"),
        "range":       re.compile("\s*RESIDUE RANGE :\s+(\w)\s+(\w+)\s+(\w)\s+(\w+)\s*$"),
        "origin":      re.compile("\s*ORIGIN\s+FOR\s+THE\s+GROUP\s+[(]A[)]:([\s\-\.0-9]+)$"),
        "t11_t22":     re.compile("\s*T11:\s*(\S+)\s+T22:\s*(\S+)\s*$"),
        "t33_t12":     re.compile("\s*T33:\s*(\S+)\s+T12:\s*(\S+)\s*$"),
        "t13_t23":     re.compile("\s*T13:\s*(\S+)\s+T23:\s*(\S+)\s*$"),
        "l11_l22":     re.compile("\s*L11:\s*(\S+)\s+L22:\s*(\S+)\s*$"),
        "l33_l12":     re.compile("\s*L33:\s*(\S+)\s+L12:\s*(\S+)\s*$"),
        "l13_l23":     re.compile("\s*L13:\s*(\S+)\s+L23:\s*(\S+)\s*$"),
        "s11_s12_s13": re.compile("\s*S11:\s*(\S+)\s+S12:\s*(\S+)\s+S13:\s*(\S+)\s*$"),
        "s21_s22_s23": re.compile( "\s*S21:\s*(\S+)\s+S22:\s*(\S+)\s+S23:\s*(\S+)\s*$"),
        "s31_s32_s33": re.compile("\s*S31:\s*(\S+)\s+S32:\s*(\S+)\s+S33:\s*(\S+)\s*$")
        }

    def load_supported(self):
        return True

    def load(self, fil):
        if isinstance(fil, str):
            fileobj = open(fil, "r")
        else:
            fileobj = fil
        
        self.tls_desc = None
        self.tls_scrap = {}
        self.tls_desc_list = []

        filter_func = lambda pdb_record: isinstance(pdb_record, PDB.REMARK) 
        self.process_pdb_records(PDB.iter_pdb_records(iter(fileobj)), filter_func) 

        return self.tls_desc_list

    def complete_T(self):
        for key in ("t11","t22","t33","t12","t13","t23"):
            if not self.tls_scrap.has_key(key):
                return
        try:
            self.tls_desc.set_T(
                self.tls_scrap["t11"],
                self.tls_scrap["t22"],
                self.tls_scrap["t33"],
                self.tls_scrap["t12"],
                self.tls_scrap["t13"],
                self.tls_scrap["t23"])
        except AttributeError:
            raise TLSFileFormatError()

    def complete_L(self):
        for key in ("l11","l22","l33","l12","l13","l23"):
            if not self.tls_scrap.has_key(key):
                return
        try:
            self.tls_desc.set_L_deg2(
                self.tls_scrap["l11"],
                self.tls_scrap["l22"],
                self.tls_scrap["l33"],
                self.tls_scrap["l12"],
                self.tls_scrap["l13"],
                self.tls_scrap["l23"])
        except AttributeError:
            raise TLSFileFormatError()
        
    def complete_S(self):
        for key in ("s11","s22","s33","s12","s13","s23","s21","s31","s32"):
            if not self.tls_scrap.has_key(key):
                return
            
        ## s2211, s1133, s12, s13, s23, s21, s31, s32
        try:
            self.tls_desc.set_S_deg(
                self.tls_scrap["s22"] - self.tls_scrap["s11"],
                self.tls_scrap["s11"] - self.tls_scrap["s33"],
                self.tls_scrap["s12"],
                self.tls_scrap["s13"],
                self.tls_scrap["s23"],
                self.tls_scrap["s21"],
                self.tls_scrap["s31"],
                self.tls_scrap["s32"])
        except AttributeError:
            raise TLSFileFormatError()
            
    def process_REMARK(self, rec):
        """Callback for the PDBFile parser for REMARK records.  If the
        REMARK records contain TLS group information, then it is
        extracted and added to the TLSGroups list.
        """
        ## TLS REMARKs use remarkNum 3
        if rec.get("remarkNum", 0) != 3:
            return

        ## no text == no tls info
        if not rec.has_key("text"):
            return

        ## attempt to extract information from the text
        text = rec["text"]
        for (re_key, re_tls) in self.pdb_regex_dict.items():
            mx = re_tls.match(text)
            if mx is not None:
                break

        ## no match
        if mx is None:
            return

        if re_key == "group":
            self.tls_desc = TLSGroupDesc()
            self.tls_desc_list.append(self.tls_desc)
            self.tls_scrap = {}
        
        elif re_key == "origin":
            strx = mx.group(1)
            ## this is nasty -- I wish I could trust the numbers
            ## to stay in fixed columns, but I can't
            ox = [0.0, 0.0, 0.0]
            for i in (0,1,2):
                j = strx.find(".")
                if j==-1:
                    break
                x = strx[ max(0, j-4) : j+5]
                strx = strx[j+5:]
                ox[i] = float(x)
            
            try:
                self.tls_desc.set_origin(ox[0], ox[1], ox[2])
            except AttributeError:
                raise TLSFileFormatError()
            except ValueError:
                raise TLSFileFormatError()

        elif re_key == "range":
            (chain_id1, frag_id1, chain_id2, frag_id2) = mx.groups()
            try:
                self.tls_desc.add_range(
                    chain_id1, frag_id1, chain_id2, frag_id2, "")
            except AttributeError:
                raise TLSFileFormatError()

        elif re_key == "t11_t22":
            (t11, t22) = mx.groups()
            try:
                self.tls_scrap["t11"] = float(t11)
                self.tls_scrap["t22"] = float(t22)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_T()
            
        elif re_key == "t33_t12":
            (t33, t12) = mx.groups()
            try:
                self.tls_scrap["t33"] = float(t33)
                self.tls_scrap["t12"] = float(t12)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_T()
            
        elif re_key == "t13_t23":
            (t13, t23) = mx.groups()
            try:
                self.tls_scrap["t13"] = float(t13)
                self.tls_scrap["t23"] = float(t23)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_T()
            
        elif re_key == "l11_l22":
            (l11, l22) = mx.groups()
            try:
                self.tls_scrap["l11"] = float(l11)
                self.tls_scrap["l22"] = float(l22)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_L()

        elif re_key == "l33_l12":
            (l33, l12) = mx.groups()
            try:
                self.tls_scrap["l33"] = float(l33)
                self.tls_scrap["l12"] = float(l12)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_L()
            
        elif re_key == "l13_l23":
            (l13, l23) = mx.groups()
            try:
                self.tls_scrap["l13"] = float(l13)
                self.tls_scrap["l23"] = float(l23)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_L()

        elif re_key == "s11_s12_s13":
            (s11, s12, s13) = mx.groups()
            try:
                self.tls_scrap["s11"] = float(s11)
                self.tls_scrap["s12"] = float(s12)
                self.tls_scrap["s13"] = float(s13)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_S()

        elif re_key == "s21_s22_s23":
            (s21, s22, s23) = mx.groups()
            try:
                self.tls_scrap["s21"] = float(s21)
                self.tls_scrap["s22"] = float(s22)
                self.tls_scrap["s23"] = float(s23)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_S()

        elif re_key == "s31_s32_s33":
            (s31, s32, s33) = mx.groups()
            try:
                self.tls_scrap["s31"] = float(s31)
                self.tls_scrap["s32"] = float(s32)
                self.tls_scrap["s33"] = float(s33)
            except ValueError:
                raise TLSFileFormatError()
            self.complete_S()


class TLSFileFormatTLSOUT(TLSFileFormat):
    """Read/Write REFMAC5 TLSIN/TLSOUT files.
    """
    tlsout_regex_dict = {
        "group":  re.compile("(?:^\s*TLS\s*$)|(?:^\s*TLS\s+(.*)$)"),
        "range":  re.compile("^\s*RANGE\s+[']([A-Z])\s*([-0-9A-Z.]+)\s*[']\s+[']([A-Z])\s*([-0-9A-Z.]+)\s*[']\s*(\w*).*$"),
        "origin": re.compile("^\s*ORIGIN\s+(\S+)\s+(\S+)\s+(\S+).*$"),
        "T":      re.compile("^\s*T\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+).*$"),
        "L":      re.compile("^\s*L\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+).*$"),
        "S":      re.compile("^\s*S\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+).*$")
        }

    def convert_frag_id_load(self, frag_id):
        """Converts the residue sequence code to a mmLib fragment_id.
        """
        if len(frag_id) == 0:
            return ""
        if frag_id[-1] == ".":
            frag_id = frag_id[:-1]
        return frag_id

    def convert_frag_id_save(self, frag_id):
        """Converts a mmLib fragment_id to a TLSOUT fragment id.
        """
        if len(frag_id) == 0:
            return "."
        if frag_id[-1].isdigit():
            frag_id += "."
        return frag_id
        
    def load_supported(self):
        return True
    def save_supported(self):
        return True

    def load(self, fil):
        tls_desc_list = []
        tls_desc = None
        
        for ln in fil.xreadlines():
            ln = ln.rstrip()

            ## search all regular expressions for a match
            for (re_key, re_tls) in self.tlsout_regex_dict.items():
                mx = re_tls.match(ln)
                if mx is not None:
                    break

            ## no match was found for the line
            if mx is None:
                continue
            
            ## do not allow a match if tls_info is None, because then
            ## somehow we've missed the TLS group begin line
            if tls_desc is None and re_key!="group":
                raise TLSFileFormatError()

            if re_key == "group":
                tls_desc = TLSGroupDesc()
                tls_desc_list.append(tls_desc)

                if mx.group(1) is not None:
                    tls_desc.set_name(mx.group(1))

            elif re_key == "origin":
                (x, y, z) = mx.groups()
                try:
                    tls_desc.set_origin(float(x), float(y), float(z))
                except ValueError:
                    raise TLSFileFormatError()

            elif re_key == "range":
                (chain_id1, frag_id1, chain_id2, frag_id2, sel) = mx.groups()

                frag_id1 = self.convert_frag_id_load(frag_id1)
                frag_id2 = self.convert_frag_id_load(frag_id2)

                tls_desc.add_range(chain_id1, frag_id1, chain_id2, frag_id2, sel)

            elif re_key == "T":
                ## REFMAC ORDER: t11 t22 t33 t12 t13 t23
                (t11, t22, t33, t12, t13, t23) = mx.groups()

                try:
                    tls_desc.set_T(float(t11), float(t22), float(t33),
                                   float(t12), float(t13), float(t23))
                except ValueError:
                    raise TLSFileFormatError()

            elif re_key == "L":
                ## REFMAC ORDER: l11 l22 l33 l12 l13 l23
                (l11, l22, l33, l12, l13, l23) = mx.groups()

                try:
                    tls_desc.set_L_deg2(float(l11), float(l22), float(l33),
                                        float(l12), float(l13), float(l23))
                except ValueError:
                    raise TLSFileFormatError()
                    
            elif re_key == "S":
                ## REFMAC ORDER:
                ## <S22 - S11> <S11 - S33> <S12> <S13> <S23> <S21> <S31> <S32>
                (s2211, s1133, s12, s13, s23, s21, s31, s32) = mx.groups()

                try:
                    tls_desc.set_S_deg(float(s2211), float(s1133), float(s12),
                                       float(s13),   float(s23),   float(s21),
                                       float(s31),   float(s32))
                except ValueError:
                    raise TLSFileFormatError()

        return tls_desc_list

    def tlsout_tls_desc(self, tls_desc):
        """Converts TLSGroupDesc instance to a multi-line string format
        ready to write to a TLSOUT file.
        """        
        listx = []

        if tls_desc.name != "":
            listx.append("TLS %s" % (tls_desc.name))
        else:
            listx.append("TLS")

        for (chain_id1, frag_id1,
             chain_id2, frag_id2, sel) in tls_desc.range_list:

            frag_id1 = self.convert_frag_id_save(frag_id1)
            frag_id2 = self.convert_frag_id_save(frag_id2)

            listx.append("RANGE  '%s%s' '%s%s' %s" % (
                chain_id1, frag_id1.rjust(5),
                chain_id2, frag_id2.rjust(5), sel))

        if tls_desc.origin is not None:
            listx.append("ORIGIN   %8.4f %8.4f %8.4f" % (
                tls_desc.origin[0], tls_desc.origin[1], tls_desc.origin[2]))

        if tls_desc.T is not None:
            ## REFMAC ORDER: t11 t22 t33 t12 t13 t23
            listx.append("T   %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f" % (
                tls_desc.T[0,0], tls_desc.T[1,1], tls_desc.T[2,2],
                tls_desc.T[0,1], tls_desc.T[0,2], tls_desc.T[1,2]))

        if tls_desc.L is not None:
            ## REFMAC ORDER: l11 l22 l33 l12 l13 l23
            listx.append("L   %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f" % (
                tls_desc.L[0,0] * Constants.RAD2DEG2,
                tls_desc.L[1,1] * Constants.RAD2DEG2,
                tls_desc.L[2,2] * Constants.RAD2DEG2,
                tls_desc.L[0,1] * Constants.RAD2DEG2,
                tls_desc.L[0,2] * Constants.RAD2DEG2,
                tls_desc.L[1,2] * Constants.RAD2DEG2))

        if tls_desc.S is not None:
            ## REFMAC ORDER:
            ## <S22 - S11> <S11 - S33> <S12> <S13> <S23> <S21> <S31> <S32>
            listx.append(
                "S   %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f" % (
                (tls_desc.S[1,1] - tls_desc.S[0,0]) * Constants.RAD2DEG,
                (tls_desc.S[0,0] - tls_desc.S[2,2]) * Constants.RAD2DEG,
                tls_desc.S[0,1] * Constants.RAD2DEG,
                tls_desc.S[0,2] * Constants.RAD2DEG,
                tls_desc.S[1,2] * Constants.RAD2DEG,
                tls_desc.S[1,0] * Constants.RAD2DEG,
                tls_desc.S[2,0] * Constants.RAD2DEG,
                tls_desc.S[2,1] * Constants.RAD2DEG))

        return "\n".join(listx)

    def save(self, fil, tls_desc_list):
        ## with this line, the tensor components will be read by some
        ## programs in a different order, mangling the tensor values
        fil.write("REFMAC\n\n")
        
        for tls_desc in tls_desc_list:
            tls_desc_str = self.tlsout_tls_desc(tls_desc)
            fil.write(tls_desc_str + "\n")

###############################################################################
## SOLVE TLS LSQ-FIT BY SVD (Singular Value Decomposition)
##

def solve_TLS_Ab(A, b):
    """Sove a overdetermined TLS system by singular value decomposition.
    """
    ## solve by SVD
    U, W, Vt = linalg.singular_value_decomposition(A, full_matrices=0)

    V  = numpy.transpose(Vt)
    Ut = numpy.transpose(U)

    ## analize singular values and generate smallness cutoff
    cutoff = max(W) * 1E-10

    ## make W
    dim_W = len(W)
    Wi = numpy.zeros((dim_W, dim_W), float)

    for i in range(dim_W):
        if W[i]>cutoff:
            Wi[i,i] = 1.0 / W[i]
        else:
            #print "SVD: ill conditioned value %d=%f" % (i, W[i])
            Wi[i,i] = 0.0

    ## solve for x
    Utb  = numpy.matrixmultiply(Ut, b)
    WUtb = numpy.matrixmultiply(Wi, Utb)
    x    = numpy.matrixmultiply(V, WUtb)

    return x

def calc_rmsd(msd):
    """Calculate RMSD from a given MSD."""
    if msd < 0.0:
        return 0.0
    return math.sqrt(msd)

###############################################################################
## ISOTROPIC TLS MODEL
##

def set_TLSiso_b(b, i, Uiso, w):
    """Sets the six rows of vector b with the experimental/target anisotropic
    ADP values U starting at index b[i] and ending at b[i+6] with weight w.
    """
    b[i] = w * Uiso

def set_TLSiso_A(A, i, j, x, y, z, w):
    """Sets the one row of matrix A starting at A[i,j] with the istropic
    TLS model coefficents for a atom located at t position x, y, z with
    least-squares weight w.  Matrix A is filled to coumn j+12.
    """
    ## use label indexing to avoid confusion!
    T, L11, L22, L33, L12, L13, L23, S1, S2, S3 = (j,1+j,2+j,3+j,4+j,5+j,6+j,7+j,8+j,9+j)
    
    ## indecies of the components of U
    UISO = i
    
    ## C Matrix
    xx = x*x
    yy = y*y
    zz = z*z

    xy = x*y
    xz = x*z
    yz = y*z

    A[UISO, T]   = w * 1.0

    A[UISO, L11] = w * ((zz + yy) / 3.0)
    A[UISO, L22] = w * ((xx + zz) / 3.0)
    A[UISO, L33] = w * ((xx + yy) / 3.0)

    A[UISO, L12] = w * ((-2.0 * xy) / 3.0)
    A[UISO, L13] = w * ((-2.0 * xz) / 3.0)
    A[UISO, L23] = w * ((-2.0 * yz) / 3.0)

    A[UISO, S1]  = w * (( 2.0 * z) / 3.0)
    A[UISO, S2]  = w * (( 2.0 * y) / 3.0)
    A[UISO, S3]  = w * (( 2.0 * x) / 3.0)

def calc_itls_uiso(T, L, S, position):
    """Calculate the TLS predicted uiso from the isotropic TLS model for the atom at position.
    """
    x, y, z = position
    
    xx = x*x
    yy = y*y
    zz = z*z

    ## note: S1 == S21-S12; S2 == S13-S31; S3 == S32-S23 
    u_tls = T + (
        L[0,0]*(zz+yy) + L[1,1]*(xx+zz) + L[2,2]*(xx+yy)
        - 2.0*L[0,1]*x*y - 2.0*L[0,2]*x*z - 2.0*L[1,2]*y*z
        + 2.0*S[0]*z + 2.0*S[1]*y + 2.0*S[2]*x) / 3.0
    return u_tls

def iter_itls_uiso(atom_iter, T, L, S, O):
    """Iterates the pair (atom, u_iso)
    """
    for atm in atom_iter:
        yield atm, calc_itls_uiso(T, L, S, atm.position - O)

def calc_itls_center_of_reaction(iT, iL, iS, origin):
    """iT is a single float; iL[3,3]; iS[3]
    """
    ## construct TLS tensors from isotropic TLS description
    T0 = numpy.array([[iT,  0.0, 0.0],
                      [0.0,  iT, 0.0],
                      [0.0, 0.0,  iT]], float)
    
    L0 = iL.copy()
        
    S0 = numpy.array([ [  0.0,   0.0, iS[1]],
                       [iS[0],   0.0,  0.0],
                       [  0.0, iS[2],  0.0] ], float)


    ## LSMALL is the smallest magnitude of L before it is considered 0.0
    LSMALL = 0.5 * Constants.DEG2RAD2
    
    rdict = {}

    rdict["T'"] = T0.copy()
    rdict["L'"] = L0.copy()
    rdict["S'"] = S0.copy()

    rdict["rT'"] = T0.copy()

    rdict["L1_eigen_val"] = 0.0
    rdict["L2_eigen_val"] = 0.0
    rdict["L3_eigen_val"] = 0.0

    rdict["L1_rmsd"] = 0.0
    rdict["L2_rmsd"] = 0.0
    rdict["L3_rmsd"] = 0.0

    rdict["L1_eigen_vec"] = numpy.zeros(3, float)
    rdict["L2_eigen_vec"] = numpy.zeros(3, float)
    rdict["L3_eigen_vec"] = numpy.zeros(3, float)
    
    rdict["RHO"] = numpy.zeros(3, float)
    rdict["COR"] = origin

    rdict["L1_rho"] = numpy.zeros(3, float)
    rdict["L2_rho"] = numpy.zeros(3, float)
    rdict["L3_rho"] = numpy.zeros(3, float)
    
    rdict["L1_pitch"] = 0.0
    rdict["L2_pitch"] = 0.0
    rdict["L3_pitch"] = 0.0

    rdict["Tr1_eigen_val"] = 0.0
    rdict["Tr2_eigen_val"] = 0.0
    rdict["Tr3_eigen_val"] = 0.0
    
    rdict["Tr1_rmsd"] = 0.0
    rdict["Tr2_rmsd"] = 0.0
    rdict["Tr3_rmsd"] = 0.0

    ## set the L tensor eigenvalues and eigenvectors
    (L_evals, RL) = linalg.eigenvectors(L0)
    L1, L2, L3 = L_evals

    good_L_eigens = []

    if numpy.allclose(L1, 0.0) or isinstance(L1, complex):
        L1 = 0.0
    else:
        good_L_eigens.append(0)
        
    if numpy.allclose(L2, 0.0) or isinstance(L2, complex):
        L2 = 0.0
    else:
        good_L_eigens.append(1)

    if numpy.allclose(L3, 0.0) or isinstance(L3, complex):
        L3 = 0.0
    else:
        good_L_eigens.append(2)

    ## no good L eigen values
    if len(good_L_eigens)==0:
        Tr1, Tr2, Tr3 = linalg.eigenvalues(T0)

        if numpy.allclose(Tr1, 0.0) or isinstance(Tr1, complex):
            Tr1 = 0.0
        if numpy.allclose(Tr2, 0.0) or isinstance(Tr2, complex):
            Tr2 = 0.0
        if numpy.allclose(Tr3, 0.0) or isinstance(Tr3, complex):
            Tr3 = 0.0

        rdict["Tr1_eigen_val"] = Tr1
        rdict["Tr2_eigen_val"] = Tr2
        rdict["Tr3_eigen_val"] = Tr3

        rdict["Tr1_rmsd"] = calc_rmsd(Tr1)
        rdict["Tr2_rmsd"] = calc_rmsd(Tr2)
        rdict["Tr3_rmsd"] = calc_rmsd(Tr3)
        return rdict

    ## one good eigen value -- reconstruct RL about it
    elif len(good_L_eigens)==1:
        i = good_L_eigens[0]
        evec = RL[i]

        RZt = numpy.transpose(AtomMath.rmatrixz(evec))
        xevec = numpy.matrixmultiply(RZt, numpy.array([1.0, 0.0, 0.0], float))
        yevec = numpy.matrixmultiply(RZt, numpy.array([0.0, 1.0, 0.0], float))

        if i==0:
            RL[1] = xevec
            RL[2] = yevec
        elif i==1:
            RL[0] = xevec
            RL[2] = yevec
        elif i==2:
            RL[0] = xevec
            RL[1] = yevec

    ## two good eigen values -- reconstruct RL about them
    elif len(good_L_eigens)==2:
        i = good_L_eigens[0]
        j = good_L_eigens[1]

        xevec = AtomMath.normalize(numpy.cross(RL[i], RL[j]))
        for k in range(3):
            if k==i: continue
            if k==j: continue
            RL[k] = xevec
            break

    rdict["L1_eigen_val"] = L1
    rdict["L2_eigen_val"] = L2
    rdict["L3_eigen_val"] = L3

    rdict["L1_rmsd"] = calc_rmsd(L1)
    rdict["L2_rmsd"] = calc_rmsd(L2)
    rdict["L3_rmsd"] = calc_rmsd(L3)

    rdict["L1_eigen_vec"] = RL[0].copy()
    rdict["L2_eigen_vec"] = RL[1].copy()
    rdict["L3_eigen_vec"] = RL[2].copy()

    ## begin tensor transformations which depend upon
    ## the eigenvectors of L0 being well-determined
    ## make sure RLt is right-handed
    if numpy.allclose(linalg.determinant(RL), -1.0):
        I = numpy.identity(3, float)
        I[0,0] = -1.0
        RL = numpy.matrixmultiply(I, RL)

    if not numpy.allclose(linalg.determinant(RL), 1.0):
        return rdict
    
    RLt = numpy.transpose(RL)

    ## carrot-L tensor (tensor WRT principal axes of L)
    cL = numpy.matrixmultiply(numpy.matrixmultiply(RL, L0), RLt) 
    
    ## carrot-T tensor (T tensor WRT principal axes of L)
    cT = numpy.matrixmultiply(numpy.matrixmultiply(RL, T0), RLt)

    ## carrot-S tensor (S tensor WRT principal axes of L)
    cS = numpy.matrixmultiply(numpy.matrixmultiply(RL, S0), RLt)

    ## ^rho: the origin-shift vector in the coordinate system of L
    L23 = L2 + L3
    L13 = L1 + L3
    L12 = L1 + L2

    ## shift for L1
    if not numpy.allclose(L1, 0.0) and abs(L23)>LSMALL:
        crho1 = (cS[1,2] - cS[2,1]) / L23
    else:
        crho1 = 0.0

    if not numpy.allclose(L2, 0.0) and abs(L13)>LSMALL:
        crho2 = (cS[2,0] - cS[0,2]) / L13
    else:
        crho2 = 0.0

    if not numpy.allclose(L3, 0.0) and abs(L12)>LSMALL:
        crho3 = (cS[0,1] - cS[1,0]) / L12
    else:
        crho3 = 0.0

    crho = numpy.array([crho1, crho2, crho3], float)

    ## rho: the origin-shift vector in orthogonal coordinates
    rho = numpy.matrixmultiply(RLt, crho)
    rdict["RHO"] = rho
    rdict["COR"] = origin + rho

    ## set up the origin shift matrix PRHO WRT orthogonal axes
    PRHO = numpy.array([ [    0.0,  rho[2], -rho[1]],
                         [-rho[2],     0.0,  rho[0]],
                         [ rho[1], -rho[0],     0.0] ], float)

    ## set up the origin shift matrix cPRHO WRT libration axes
    cPRHO = numpy.array([ [    0.0,  crho[2], -crho[1]],
                          [-crho[2],     0.0,  crho[0]],
                          [ crho[1], -crho[0],     0.0] ], float)

    ## calculate tranpose of cPRHO, ans cS
    cSt = numpy.transpose(cS)
    cPRHOt = numpy.transpose(cPRHO)

    ## calculate S'^ = S^ + L^*pRHOt
    cSp = cS + numpy.matrixmultiply(cL, cPRHOt)

    ## calculate T'^ = cT + cPRHO*S^ + cSt*cPRHOt + cPRHO*cL*cPRHOt *
    cTp = cT + numpy.matrixmultiply(cPRHO, cS) + numpy.matrixmultiply(cSt, cPRHOt) + \
          numpy.matrixmultiply(numpy.matrixmultiply(cPRHO, cL), cPRHOt)

    ## transpose of PRHO and S
    PRHOt = numpy.transpose(PRHO)
    St = numpy.transpose(S0)

    ## calculate S' = S + L*PRHOt
    Sp = S0 + numpy.matrixmultiply(L0, PRHOt)
    rdict["S'"] = Sp

    ## calculate T' = T + PRHO*S + St*PRHOT + PRHO*L*PRHOt
    Tp = T0 + numpy.matrixmultiply(PRHO, S0) + numpy.matrixmultiply(St, PRHOt) + \
         numpy.matrixmultiply(numpy.matrixmultiply(PRHO, L0), PRHOt)
    rdict["T'"] = Tp

    ## now calculate the TLS motion description using 3 non
    ## intersecting screw axes, with one

    ## libration axis 1 shift in the L coordinate system
    ## you cannot determine axis shifts from the isotropic TLS parameters
    cL1rho = numpy.zeros(3, float)
    cL2rho = numpy.zeros(3, float)
    cL3rho = numpy.zeros(3, float)

    ## libration axes shifts in the origional orthogonal
    ## coordinate system
    rdict["L1_rho"] = numpy.matrixmultiply(RLt, cL1rho)
    rdict["L2_rho"] = numpy.matrixmultiply(RLt, cL2rho)
    rdict["L3_rho"] = numpy.matrixmultiply(RLt, cL3rho)

    ## calculate screw pitches (A*R / R*R) = (A/R)
    ## no screw pitches either
    rdict["L1_pitch"] = 0.0
    rdict["L2_pitch"] = 0.0
    rdict["L3_pitch"] = 0.0

    ## rotate the newly calculated reduced-T tensor from the carrot
    ## coordinate system (coordinate system of L) back to the structure
    ## coordinate system
    Tiso = numpy.trace(Tp) / 3.0
    rdict["rT'"] = Tiso * numpy.identity(3, float)

    rdict["Tr1_eigen_val"] = Tiso
    rdict["Tr2_eigen_val"] = Tiso
    rdict["Tr3_eigen_val"] = Tiso
    
    rdict["Tr1_rmsd"] = calc_rmsd(Tiso)
    rdict["Tr2_rmsd"] = calc_rmsd(Tiso)
    rdict["Tr3_rmsd"] = calc_rmsd(Tiso)
    
    return rdict

###############################################################################
## ANISOTROPIC TLS MODEL
##

def calc_s11_s22_s33(s2211, s1133):
    """Calculates s11, s22, s33 based on s22-s11 and s11-s33 using
    the constraint s11+s22+s33=0
    """
    s22 = 2.0*(s2211)/3.0 + s1133/3.0
    s11 = s22 - s2211
    s33 = s11 - s1133
    return s11, s22, s33

def calc_Utls(T, L, S, position):
    """Returns the calculated value for the anisotropic U tensor for
    the given position.
    """
    x, y, z = position

    xx = x*x
    yy = y*y
    zz = z*z

    xy = x*y
    yz = y*z
    xz = x*z

    u11 = T[0,0] + L[1,1]*zz + L[2,2]*yy - 2.0*L[1,2]*yz + 2.0*S[1,0]*z - 2.0*S[2,0]*y
    u22 = T[1,1] + L[0,0]*zz + L[2,2]*xx - 2.0*L[2,0]*xz - 2.0*S[0,1]*z + 2.0*S[2,1]*x
    u33 = T[2,2] + L[0,0]*yy + L[1,1]*xx - 2.0*L[0,1]*xy - 2.0*S[1,2]*x + 2.0*S[0,2]*y
    u12 = T[0,1] - L[2,2]*xy + L[1,2]*xz + L[2,0]*yz - L[0,1]*zz - S[0,0]*z + S[1,1]*z + S[2,0]*x - S[2,1]*y
    u13 = T[0,2] - L[1,1]*xz + L[1,2]*xy - L[2,0]*yy + L[0,1]*yz + S[0,0]*y - S[2,2]*y + S[1,2]*z - S[1,0]*x
    u23 = T[1,2] - L[0,0]*yz - L[1,2]*xx + L[2,0]*xy + L[0,1]*xz - S[1,1]*x + S[2,2]*x + S[0,1]*y - S[0,2]*z

    return numpy.array([[u11, u12, u13],
                        [u12, u22, u23],
                        [u13, u23, u33]], float)

def calc_LS_displacement(cor, Lval, Lvec, Lrho, Lpitch, position, prob):
    """Returns the amount of rotational displacement from L
    for a atom at the given position.
    """
    Lrot     = Gaussian.GAUSS3C[prob] * calc_rmsd(Lval)
    Lorigin  = cor + Lrho
    D        = AtomMath.dmatrixu(Lvec, Lrot)

    drot = numpy.matrixmultiply(D, position - Lorigin)
    dscw = (Lrot * Lpitch) * Lvec
    
    return drot + dscw

def set_TLS_A(A, i, j, x, y, z, w):
    """Sets the six rows of matrix A starting at A[i,j] with the TLS
    coefficents for a atom located at position x,y,z with least-squares
    weight w.  Matrix A is filled to row i+6 and column j+20.
    """
    ## use label indexing to avoid confusion!
    T11, T22, T33, T12, T13, T23, L11, L22, L33, L12, L13, L23, S1133, S2211, S12, S13, S23, S21, S31, S32 = (
        j,1+j,2+j,3+j,4+j,5+j,6+j,7+j,8+j,9+j,10+j,11+j,12+j,13+j,14+j,15+j,16+j,17+j,18+j,19+j)

    ## indecies of the components of U
    U11 =       i
    U22 = U11 + 1
    U33 = U11 + 2
    U12 = U11 + 3
    U13 = U11 + 4
    U23 = U11 + 5

    ## C Matrix
    xx = x*x
    yy = y*y
    zz = z*z

    xy = x*y
    xz = x*z
    yz = y*z

    A[U11, T11] = w * 1.0
    A[U11, L22] = w *        zz
    A[U11, L33] = w *        yy
    A[U11, L23] = w * -2.0 * yz
    A[U11, S31] = w * -2.0 *  y
    A[U11, S21] = w *  2.0 *  z

    A[U22, T22] = w * 1.0
    A[U22, L11] = w *        zz
    A[U22, L33] = w *        xx
    A[U22, L13] = w * -2.0 * xz
    A[U22, S12] = w * -2.0 *  z
    A[U22, S32] = w *  2.0 *  x

    A[U33, T33] = w * 1.0
    A[U33, L11] = w *        yy
    A[U33, L22] = w *        xx
    A[U33, L12] = w * -2.0 * xy
    A[U33, S23] = w * -2.0 *  x
    A[U33, S13] = w *  2.0 *  y

    A[U12, T12]   = w * 1.0
    A[U12, L33]   = w * -xy
    A[U12, L23]   = w *  xz
    A[U12, L13]   = w *  yz
    A[U12, L12]   = w * -zz
    A[U12, S2211] = w *   z
    A[U12, S31]   = w *   x
    A[U12, S32]   = w *  -y
    
    A[U13, T13]   = w * 1.0
    A[U13, L22]   = w * -xz
    A[U13, L23]   = w *  xy
    A[U13, L13]   = w * -yy
    A[U13, L12]   = w *  yz
    A[U13, S1133] = w *   y
    A[U13, S23]   = w *   z
    A[U13, S21]   = w *  -x
    
    A[U23, T23]   = w * 1.0
    A[U23, L11]   = w * -yz
    A[U23, L23]   = w * -xx
    A[U23, L13]   = w *  xy
    A[U23, L12]   = w *  xz
    A[U23, S2211] = w *  -x
    A[U23, S1133] = w *  -x
    A[U23, S12]   = w *   y
    A[U23, S13]   = w *  -z

def set_TLS_b(b, i, u11, u22, u33, u12, u13, u23, w):
    """Sets the six rows of vector b with the experimental/target anisotropic
    ADP values U starting at index b[i] and ending at b[i+6] with weight w.
    """
    b[i]   = w * u11
    b[i+1] = w * u22
    b[i+2] = w * u33
    b[i+3] = w * u12
    b[i+4] = w * u13
    b[i+5] = w * u23

def calc_TLS_least_squares_fit(atom_list, origin, weight_dict=None):
    """Perform a LSQ-TLS fit on the given AtomList.  The TLS tensors
    are calculated at the given origin, with weights of weight_dict[atm].
    Return values are T, L, S, lsq_residual. 
    """    
    ## calculate the number of parameters in the model
    num_atoms = len(atom_list)
    params = 20

    A = numpy.zeros((num_atoms * 6, params), float)
    B = numpy.zeros(num_atoms * 6,  float)

    i = -1
    for atm in atom_list:
        i += 1
        iU11 = i * 6
        
        ## is this fit weighted?
        if weight_dict is not None:
            w = math.sqrt(weight_dict[atm])
        else:
            w = 1.0

        ## set the b vector
        U = atm.get_U()
        set_TLS_b(B, iU11, U[0,0], U[1,1], U[2,2], U[0,1], U[0,2], U[1,2], w)

        ## set the A matrix
        x, y, z = atm.position - origin
        set_TLS_A(A, iU11, 0, x, y, z, w)

    ## solve by SVD
    X = solve_TLS_Ab(A, B)

    ## use label indexing to avoid confusion!
    T11, T22, T33, T12, T13, T23, L11, L22, L33, L12, L13, L23, S1133, S2211, S12, S13, S23, S21, S31, S32 = (
        0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19)

    T = numpy.array([ [ X[T11], X[T12], X[T13] ],
                      [ X[T12], X[T22], X[T23] ],
                      [ X[T13], X[T23], X[T33] ] ], float)

    L = numpy.array([ [ X[L11], X[L12], X[L13] ],
                      [ X[L12], X[L22], X[L23] ],
                      [ X[L13], X[L23], X[L33] ] ], float)

    s11, s22, s33 = calc_s11_s22_s33(X[S2211], X[S1133])

    S = numpy.array([ [    s11, X[S12], X[S13] ],
                      [ X[S21],    s22, X[S23] ],
                      [ X[S31], X[S32],    s33 ] ], float)

    ## calculate the lsq residual
    UTLS = numpy.matrixmultiply(A, X)
    D = UTLS - B
    lsq_residual = numpy.dot(D, D)

    return T, L, S, lsq_residual

def calc_TLS_center_of_reaction(T0, L0, S0, origin):
    """Calculate new tensors based on the center for reaction.
    This method returns a dictionary of the calculations:

    T^: T tensor in the coordinate system of L
    L^: L tensor in the coordinate system of L
    S^: S tensor in the coordinate system of L

    COR: Center of Reaction

    T',S',L': T,L,S tensors in origonal coordinate system
              with the origin shifted to the center of reaction.
    """
    ## LSMALL is the smallest magnitude of L before it is considered 0.0
    LSMALL = 0.5 * Constants.DEG2RAD2
    
    rdict = {}

    rdict["T'"] = T0.copy()
    rdict["L'"] = L0.copy()
    rdict["S'"] = S0.copy()

    rdict["rT'"] = T0.copy()

    rdict["L1_eigen_val"] = 0.0
    rdict["L2_eigen_val"] = 0.0
    rdict["L3_eigen_val"] = 0.0

    rdict["L1_rmsd"] = 0.0
    rdict["L2_rmsd"] = 0.0
    rdict["L3_rmsd"] = 0.0

    rdict["L1_eigen_vec"] = numpy.zeros(3, float)
    rdict["L2_eigen_vec"] = numpy.zeros(3, float)
    rdict["L3_eigen_vec"] = numpy.zeros(3, float)
    
    rdict["RHO"] = numpy.zeros(3, float)
    rdict["COR"] = origin

    rdict["L1_rho"] = numpy.zeros(3, float)
    rdict["L2_rho"] = numpy.zeros(3, float)
    rdict["L3_rho"] = numpy.zeros(3, float)
    
    rdict["L1_pitch"] = 0.0
    rdict["L2_pitch"] = 0.0
    rdict["L3_pitch"] = 0.0

    rdict["Tr1_eigen_val"] = 0.0
    rdict["Tr2_eigen_val"] = 0.0
    rdict["Tr3_eigen_val"] = 0.0
    
    rdict["Tr1_rmsd"] = 0.0
    rdict["Tr2_rmsd"] = 0.0
    rdict["Tr3_rmsd"] = 0.0

    ## set the L tensor eigenvalues and eigenvectors
    (L_evals, RL) = linalg.eigenvectors(L0)
    L1, L2, L3 = L_evals

    good_L_eigens = []

    if numpy.allclose(L1, 0.0) or isinstance(L1, complex):
        L1 = 0.0
    else:
        good_L_eigens.append(0)
        
    if numpy.allclose(L2, 0.0) or isinstance(L2, complex):
        L2 = 0.0
    else:
        good_L_eigens.append(1)

    if numpy.allclose(L3, 0.0) or isinstance(L3, complex):
        L3 = 0.0
    else:
        good_L_eigens.append(2)

    ## no good L eigen values
    if len(good_L_eigens)==0:
        return rdict

    ## one good eigen value -- reconstruct RL about it
    elif len(good_L_eigens)==1:
        i = good_L_eigens[0]
        evec = RL[i]

        RZt = numpy.transpose(AtomMath.rmatrixz(evec))
        xevec = numpy.matrixmultiply(RZt, numpy.array([1.0, 0.0, 0.0], float))
        yevec = numpy.matrixmultiply(RZt, numpy.array([0.0, 1.0, 0.0], float))

        if i==0:
            RL[1] = xevec
            RL[2] = yevec
        elif i==1:
            RL[0] = xevec
            RL[2] = yevec
        elif i==2:
            RL[0] = xevec
            RL[1] = yevec

    ## two good eigen values -- reconstruct RL about them
    elif len(good_L_eigens)==2:
        i = good_L_eigens[0]
        j = good_L_eigens[1]

        xevec = AtomMath.normalize(numpy.cross(RL[i], RL[j]))
        for k in range(3):
            if k==i: continue
            if k==j: continue
            RL[k] = xevec
            break

    rdict["L1_eigen_val"] = L1
    rdict["L2_eigen_val"] = L2
    rdict["L3_eigen_val"] = L3

    rdict["L1_rmsd"] = calc_rmsd(L1)
    rdict["L2_rmsd"] = calc_rmsd(L2)
    rdict["L3_rmsd"] = calc_rmsd(L3)

    rdict["L1_eigen_vec"] = RL[0].copy()
    rdict["L2_eigen_vec"] = RL[1].copy()
    rdict["L3_eigen_vec"] = RL[2].copy()

    ## begin tensor transformations which depend upon
    ## the eigenvectors of L0 being well-determined
    ## make sure RLt is right-handed
    if numpy.allclose(linalg.determinant(RL), -1.0):
        I = numpy.identity(3, float)
        I[0,0] = -1.0
        RL = numpy.matrixmultiply(I, RL)

    if not numpy.allclose(linalg.determinant(RL), 1.0):
        return rdict
    
    RLt = numpy.transpose(RL)

    ## carrot-L tensor (tensor WRT principal axes of L)
    cL = numpy.matrixmultiply(numpy.matrixmultiply(RL, L0), RLt) 
    rdict["L^"] = cL.copy()
    
    ## carrot-T tensor (T tensor WRT principal axes of L)
    cT = numpy.matrixmultiply(numpy.matrixmultiply(RL, T0), RLt)
    rdict["T^"] = cT.copy()

    ## carrot-S tensor (S tensor WRT principal axes of L)
    cS = numpy.matrixmultiply(numpy.matrixmultiply(RL, S0), RLt)
    rdict["S^"] = cS.copy()

    ## ^rho: the origin-shift vector in the coordinate system of L
    L23 = L2 + L3
    L13 = L1 + L3
    L12 = L1 + L2

    ## shift for L1
    if not numpy.allclose(L1, 0.0) and abs(L23)>LSMALL:
        crho1 = (cS[1,2] - cS[2,1]) / L23
    else:
        crho1 = 0.0

    if not numpy.allclose(L2, 0.0) and abs(L13)>LSMALL:
        crho2 = (cS[2,0] - cS[0,2]) / L13
    else:
        crho2 = 0.0

    if not numpy.allclose(L3, 0.0) and abs(L12)>LSMALL:
        crho3 = (cS[0,1] - cS[1,0]) / L12
    else:
        crho3 = 0.0

    crho = numpy.array([crho1, crho2, crho3], float)
    rdict["RHO^"] = crho.copy()
    
    ## rho: the origin-shift vector in orthogonal coordinates
    rho = numpy.matrixmultiply(RLt, crho)
    rdict["RHO"] = rho
    rdict["COR"] = origin + rho

    ## set up the origin shift matrix PRHO WRT orthogonal axes
    PRHO = numpy.array([ [    0.0,  rho[2], -rho[1]],
                         [-rho[2],     0.0,  rho[0]],
                         [ rho[1], -rho[0],     0.0] ], float)

    ## set up the origin shift matrix cPRHO WRT libration axes
    cPRHO = numpy.array([ [    0.0,  crho[2], -crho[1]],
                          [-crho[2],     0.0,  crho[0]],
                          [ crho[1], -crho[0],     0.0] ], float)

    ## calculate tranpose of cPRHO, ans cS
    cSt = numpy.transpose(cS)
    cPRHOt = numpy.transpose(cPRHO)

    rdict["L'^"] = cL.copy()

    ## calculate S'^ = S^ + L^*pRHOt
    cSp = cS + numpy.matrixmultiply(cL, cPRHOt)
    rdict["S'^"] = cSp.copy()

    ## calculate T'^ = cT + cPRHO*S^ + cSt*cPRHOt + cPRHO*cL*cPRHOt *
    cTp = cT + numpy.matrixmultiply(cPRHO, cS) + numpy.matrixmultiply(cSt, cPRHOt) +\
          numpy.matrixmultiply(numpy.matrixmultiply(cPRHO, cL), cPRHOt)
    rdict["T'^"] = cTp.copy()

    ## transpose of PRHO and S
    PRHOt = numpy.transpose(PRHO)
    St = numpy.transpose(S0)

    ## calculate S' = S + L*PRHOt
    Sp = S0 + numpy.matrixmultiply(L0, PRHOt)
    rdict["S'"] = Sp

    ## calculate T' = T + PRHO*S + St*PRHOT + PRHO*L*PRHOt
    Tp = T0 + numpy.matrixmultiply(PRHO, S0) + numpy.matrixmultiply(St, PRHOt) +\
         numpy.matrixmultiply(numpy.matrixmultiply(PRHO, L0), PRHOt)
    rdict["T'"] = Tp

    ## now calculate the TLS motion description using 3 non
    ## intersecting screw axes, with one

    ## libration axis 1 shift in the L coordinate system        
    if abs(L1)>LSMALL:
        cL1rho = numpy.array([0.0, -cSp[0,2]/L1, cSp[0,1]/L1], float)
    else:
        cL1rho = numpy.zeros(3, float)

    ## libration axis 2 shift in the L coordinate system
    if abs(L2)>LSMALL:
        cL2rho = numpy.array([cSp[1,2]/L2, 0.0, -cSp[1,0]/L2], float)
    else:
        cL2rho = numpy.zeros(3, float)

    ## libration axis 2 shift in the L coordinate system
    if abs(L3)>LSMALL:
        cL3rho = numpy.array([-cSp[2,1]/L3, cSp[2,0]/L3, 0.0], float)
    else:
        cL3rho = numpy.zeros(3, float)

    ## libration axes shifts in the origional orthogonal
    ## coordinate system
    rdict["L1_rho"] = numpy.matrixmultiply(RLt, cL1rho)
    rdict["L2_rho"] = numpy.matrixmultiply(RLt, cL2rho)
    rdict["L3_rho"] = numpy.matrixmultiply(RLt, cL3rho)

    ## calculate screw pitches (A*R / R*R) = (A/R)
    if abs(L1)>LSMALL:
        rdict["L1_pitch"] = cS[0,0]/L1
    else:
        rdict["L1_pitch"] = 0.0

    if L2>LSMALL:
        rdict["L2_pitch"] = cS[1,1]/L2
    else:
        rdict["L2_pitch"] = 0.0

    if L3>LSMALL:
        rdict["L3_pitch"] = cS[2,2]/L3
    else:
        rdict["L3_pitch"] = 0.0

    ## now calculate the reduction in T for the screw rotation axes
    cTred = cT.copy()

    for i in (0, 1, 2):
        for k in (0, 1, 2):
            if i==k:
                continue
            if abs(cL[k,k])>LSMALL:
                cTred[i,i] -= (cS[k,i]**2) / cL[k,k]

    for i in (0, 1, 2):
        for j in (0, 1, 2):
            for k in (0, 1, 2):
                if j==i:
                    continue
                if abs(cL[k,k])>LSMALL:
                    cTred[i,j] -= (cS[k,i]*cS[k,j]) / cL[k,k]

    ## rotate the newly calculated reduced-T tensor from the carrot
    ## coordinate system (coordinate system of L) back to the structure
    ## coordinate system
    Tr = numpy.matrixmultiply(numpy.matrixmultiply(RLt, cTred), RL)
    rdict["rT'"] = Tr

    Tr1, Tr2, Tr3 = linalg.eigenvalues(Tr)

    if numpy.allclose(Tr1, 0.0) or isinstance(Tr1, complex):
        Tr1 = 0.0
    if numpy.allclose(Tr2, 0.0) or isinstance(Tr2, complex):
        Tr2 = 0.0
    if numpy.allclose(Tr3, 0.0) or isinstance(Tr3, complex):
        Tr3 = 0.0

    rdict["Tr1_eigen_val"] = Tr1
    rdict["Tr2_eigen_val"] = Tr2
    rdict["Tr3_eigen_val"] = Tr3
    
    rdict["Tr1_rmsd"] = calc_rmsd(Tr1)
    rdict["Tr2_rmsd"] = calc_rmsd(Tr2)
    rdict["Tr3_rmsd"] = calc_rmsd(Tr3)
    
    return rdict

###############################################################################
## TLS + 1 Uiso per Atom
##

def calc_TLS_plus_b_least_squares_fit(atom_list, origin, weight_dict=None):
    """Perform a LSQ-TLS fit on the given Segment object using
    the TLS model with amino acid side chains which can pivot
    about the CA atom.  This model uses 20 TLS parameters and 6
    libration parameters per side chain.
    """
    ## calculate the number of parameters in the model
    num_atoms = len(atom_list)
    params = 20 + num_atoms

    A = numpy.zeros((num_atoms * 6, params), float)
    B = numpy.zeros(num_atoms * 6,  float)

    i = -1
    for atm in atom_list:
        i += 1
        iU11 = i * 6

        if weight_dict is None:
            w = 1.0
        else:
            w = math.sqrt(weight_dict[atm])
        
        ## set the b vector
        U = atm.get_U()
        assert numpy.trace(U)>0.0
        set_TLS_b(B, iU11, U[0,0], U[1,1], U[2,2], U[0,1], U[0,2], U[1,2], w)

        ## set the A matrix
        x, y, z = atm.position - origin
        set_TLS_A(A, iU11, 0, x, y, z, w)

        ## set A for additional Uiso / atom
        A[iU11,   20+i] = 1.0
        A[iU11+1, 20+i] = 1.0
        A[iU11+2, 20+i] = 1.0

    ## solve by SVD
    X = solve_TLS_Ab(A, B)

    ## use label indexing to avoid confusion!
    T11, T22, T33, T12, T13, T23, L11, L22, L33, L12, L13, L23, S1133, S2211, S12, S13, S23, S21, S31, S32 = (
        0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19)

    T = numpy.array([ [ X[T11], X[T12], X[T13] ],
                [ X[T12], X[T22], X[T23] ],
                [ X[T13], X[T23], X[T33] ] ], float)

    L = numpy.array([ [ X[L11], X[L12], X[L13] ],
                [ X[L12], X[L22], X[L23] ],
                [ X[L13], X[L23], X[L33] ] ], float)

    s11, s22, s33 = calc_s11_s22_s33(X[S2211], X[S1133])

    S = numpy.array([ [    s11, X[S12], X[S13] ],
                [ X[S21],    s22, X[S23] ],
                [ X[S31], X[S32],    s33 ] ], float)

    ## calculate the lsq residual
    UTLS = numpy.matrixmultiply(A, X)
    D = UTLS - B
    lsq_residual = numpy.dot(D, D)

    rdict = {}
    rdict["T"] = T
    rdict["L"] = L
    rdict["S"] = S
    rdict["lsq_residual"] = lsq_residual

    uiso_residual = {}
    i = 19
    for atm in atom_list:
        i += 1
        uiso_residual[atm] = X[i]
    rdict["uiso_residual"] = uiso_residual

    return rdict

###############################################################################
## NESTED VIBRATIONAL MODELS
##

CA_PIVOT_ATOMS = {
    "GLY": None,
    "ALA": None,
    "VAL": "CA",
    "LEU": "CA",
    "ILE": "CA",
    "PRO": None,
    "PHE": "CA",
    "TYR": "CA",
    "TRP": "CA",
    "MET": "CA",
    "CYS": "CA",
    "SER": "CA",
    "THR": "CA",
    "ASP": "CA",
    "GLU": "CA",
    "HIS": "CA",
    "LYS": "CA",
    "ARG": "CA",
    "ASN": "CA",
    "GLN": "CA" }
 
def set_L_A(A, i, j, x, y, z, w):
    """Sets coefficents of a L tensor in matrix A for a atom at position
    x,y,z and weight w.  This starts at A[i,j] and ends at A[i+6,j+6]
    Using weight w.
    """
    L11, L22, L33, L12, L13, L23 = (j, j+1, j+2, j+3, j+4, j+5)

    ## indecies of the components of U
    U11 =       i
    U22 = U11 + 1
    U33 = U11 + 2
    U12 = U11 + 3
    U13 = U11 + 4
    U23 = U11 + 5

    ## TLS coefficents
    xx = x * x
    yy = y * y
    zz = z * z

    xy = x * y
    xz = x * z
    yz = y * z

    A[U11, L22] = w * zz
    A[U11, L33] = w * yy
    A[U11, L23] = w * -2.0 * yz

    A[U22, L11] = w * zz
    A[U22, L33] = w * xx
    A[U22, L13] = w * -2.0 * xz

    A[U33, L11] = w * yy
    A[U33, L22] = w * xx
    A[U33, L12] = w * -2.0 * xy

    A[U12, L33] = w * -xy
    A[U12, L23] = w * xz
    A[U12, L13] = w * yz
    A[U12, L12] = w * -zz

    A[U13, L22] = w * -xz
    A[U13, L23] = w * xy
    A[U13, L13] = w * -yy
    A[U13, L12] = w * yz

    A[U23, L11] = w * -yz
    A[U23, L23] = w * -xx
    A[U23, L13] = w * xy
    A[U23, L12] = w * xz

def calc_TLSCA_least_squares_fit(segment, origin):
    """Perform a LSQ-TLS fit on the given Segment object using
    the TLS model with amino acid side chains which can pivot
    about the CA atom.  This model uses 20 TLS parameters and 6
    libration parameters per side chain.
    """
    ## calculate the number of parameters in the model
    num_atoms = segment.count_atoms()

    ## calculate the CB pivot L11 indexes for each fragment
    num_pivot_frags = 0
    i = 20
    iL11p = {}
    for frag in segment.iter_fragments():
        if CA_PIVOT_ATOMS.get(frag.res_name) is not None:
            num_pivot_frags += 1
            iL11p[frag] = i
            i += 6

    params = (6 * num_pivot_frags) + 20

    A = numpy.zeros((num_atoms * 6, params), float)
    B = numpy.zeros(num_atoms * 6,  float)

    i = -1
    for atm in segment.iter_atoms():
        i += 1
        iU11 = i * 6

        ## set the b vector
        U = atm.get_U()
        set_TLS_b(B, iU11,
                  U[0,0], U[1,1], U[2,2], U[0,1], U[0,2], U[1,2],
                  1.0)

        ## set the A matrix
        x, y, z = atm.position - origin
        set_TLS_A(A, iU11, 0, x, y, z, 1.0)

        ## independent side-chain Ls tensor
        frag = atm.get_fragment()

        assert frag.is_amino_acid()

        if frag.is_amino_acid():
            if atm.name in ["N", "CA", "C", "O"]:
                continue

            ## get the name of the pivot atom for this resiude
            patom_name = CA_PIVOT_ATOMS.get(frag.res_name)
            if patom_name is not None:
                patm = frag.get_atom(patom_name)
                assert patm is not None

                iL11 = iL11p[frag]
                xs, ys, zs = atm.position - patm.position
                set_L_A(A, iU11, iL11, xs, ys, zs, 1.0)

    ## solve by SVD
    X = solve_TLS_Ab(A, B)

    ## calculate the lsq residual
    UTLS = numpy.matrixmultiply(A, X)
    D = UTLS - B
    lsq_residual = numpy.dot(D, D)

    ## create the T,L,S tensors

    ## use label indexing to avoid confusion!
    T11, T22, T33, T12, T13, T23, L11, L22, L33, L12, L13, L23, \
    S1133, S2211, S12, S13, S23, S21, S31, S32 = (
        0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19)

    T = numpy.array([ [ X[T11], X[T12], X[T13] ],
                      [ X[T12], X[T22], X[T23] ],
                      [ X[T13], X[T23], X[T33] ] ], float)

    L = numpy.array([ [ X[L11], X[L12], X[L13] ],
                      [ X[L12], X[L22], X[L23] ],
                      [ X[L13], X[L23], X[L33] ] ], float)
    
    s11, s22, s33 = calc_s11_s22_s33(X[S2211], X[S1133])

    S = numpy.array([ [    s11, X[S12], X[S13] ],
                      [ X[S21],    s22, X[S23] ],
                      [ X[S31], X[S32],    s33 ] ], float)

    ## extract the CA-pivot L tensors
    frag_L_dict = {}
    for frag in segment.iter_fragments():
        if not iL11p.has_key(frag):
            print "NO PIVOT: %s" % (frag)
            continue

        iL11 = iL11p[frag]
        CA_L = numpy.array([ [ X[iL11],   X[iL11+3], X[iL11+4] ],
                             [ X[iL11+3], X[iL11+1], X[iL11+5] ],
                             [ X[iL11+4], X[iL11+5], X[iL11+2] ] ], float)
        
        frag_L_dict[frag] = CA_L
        eval = linalg.eigenvalues(CA_L) * Constants.RAD2DEG2

        print "%s %s: %6.2f %6.2f %6.2f" % (frag.fragment_id, frag.res_name, eval[0],eval[1],eval[2])

    ## calculate TLSCA-U
    udict = {}
    i = -1
    for atm in segment.iter_atoms():
        i += 1
        iU11 = i * 6

        U = numpy.array( ((UTLS[iU11],   UTLS[iU11+3], UTLS[iU11+4]),
                          (UTLS[iU11+3], UTLS[iU11+1], UTLS[iU11+5]),
                          (UTLS[iU11+4], UTLS[iU11+5], UTLS[iU11+2])), float)

        udict[atm] = U

    ## caclculate the center of reaction for the group and
    rdict = {}

    rdict["T"] = T
    rdict["L"] = L
    rdict["S"] = S

    rdict["lsq_residual"] = lsq_residual

    rdict["num_atoms"] = num_atoms
    rdict["params"] = params

    rdict["udict"] = udict

    return rdict


###############################################################################
## 

class TLSGroup(Structure.AtomList):
    """A subclass of AtomList implementing methods for performing TLS
    calculations on the contained Atom instances.
    """
    def __init__(self, *args):
        Structure.AtomList.__init__(self, *args)

        self.name           = "" 
        self.origin         = numpy.zeros(3, float)
        self.T              = numpy.array([[0.0, 0.0, 0.0],
                                           [0.0, 0.0, 0.0],
                                           [0.0, 0.0, 0.0]], float)
        self.L              = numpy.array([[0.0, 0.0, 0.0],
                                           [0.0, 0.0, 0.0],
                                           [0.0, 0.0, 0.0]], float)
        self.S              = numpy.array([[0.0, 0.0, 0.0],
                                           [0.0, 0.0, 0.0],
                                           [0.0, 0.0, 0.0]], float)

    def str_old(self):
        tstr  = "TLS %s\n" % (self.name)

        tstr += "ORIGIN  %f %f %f\n" % (
            self.origin[0], self.origin[1], self.origin[2])

        tstr += "T %f %f %f %f %f %f\n" % (
            self.T[0,0], self.T[1,1], self.T[2,2], self.T[0,1], self.T[0,2],
            self.T[1,2])

        tstr += "L %f %f %f %f %f %f\n" % (
            self.L[0,0], self.L[1,1], self.L[2,2], self.L[0,1], self.L[0,2],
            self.L[1,2])

        tstr += "S %f %f %f %f %f %f %f %f\n" % (
            self.S[1,1]-self.S[0,0], self.S[0,0]-self.S[2,2], self.S[0,1],
            self.S[0,2], self.S[1,2], self.S[1,0], self.S[2,0], self.S[2,1])

        return tstr
    
    def set_origin(self, x, y, z):
        """Sets the x, y, z components of the TLS origin vector.
        """
        self.origin = numpy.array([x, y, z])

    def set_T(self, t11, t22, t33, t12, t13, t23):
        """Sets the components of the symmetric T tensor.  Units in square
        Angstroms.
        """
        self.T = numpy.array([[t11, t12, t13],
                              [t12, t22, t23],
                              [t13, t23, t33]], float)

    def set_L(self, l11, l22, l33, l12, l13, l23):
        """Sets the components of the symmetric L tensor from arguments.
        Units should be in square radians.
        """
        self.L = numpy.array([[l11, l12, l13],
                              [l12, l22, l23],
                              [l13, l23, l33]], float)

    def set_S(self, s2211, s1133, s12, s13, s23, s21, s31, s32):
        """Sets the componets of the asymmetric S tenssor.  The trace
        of the S tensor is set with the standard convention of
        the Trace(S) = 0.  Units in Radians*Angstroms.
        """
        s11, s22, s33 = self.calc_s11_s22_s33(s2211, s1133)
        self.S = numpy.array([[s11, s12, s13],
                              [s21, s22, s23],
                              [s31, s32, s33]], float)

    def calc_s11_s22_s33(self, s2211, s1133):
        """Calculates s11, s22, s33 based on s22-s11 and s11-s33 using
        the constraint s11+s22+s33=0
        """
        s22 = 2.0*(s2211)/3.0 + s1133/3.0
        s11 = s22 - s2211
        s33 = s11 - s1133
        return s11, s22, s33

    def is_null(self):
        """Returns True if the T,L,S tensors are not set, or are set
        with values of zero.
        """
        if numpy.allclose(numpy.trace(self.T), 0.0) or numpy.allclose(numpy.trace(self.L), 0.0):
            return True
        return False

    def calc_TLS_least_squares_fit(self, weight_dict=None):
        """Perform a least-squares fit of the atoms contained in self
        to the three TLS tensors: self.T, self.L, and self.S using the
        origin given by self.origin.
        """
        T, L, S, lsq_residual = calc_TLS_least_squares_fit(self, self.origin, weight_dict)

        self.T = T
        self.L = L
        self.S = S

        return lsq_residual

    def iter_atm_Utls(self):
        """Iterates all the atoms in the TLS object, returning the 2-tuple
        (atm, U) where U is the calcuated U value from the current values
        of the TLS object's T,L,S, tensors and origin.
        """
        T = self.T
        L = self.L
        S = self.S
        o = self.origin
        
        for atm in self:
            Utls = calc_Utls(T, L, S, atm.position - o)
            yield atm, Utls

    def calc_COR(self):
        """Returns the calc_COR() return information for this TLS Group.
        """
        return calc_TLS_center_of_reaction(self.T, self.L, self.S, self.origin)

    def shift_COR(self):
        """Shift the TLS group to the center of reaction.
        """
        cor_desc    = self.calc_COR()
        self.T      = cor_desc["T'"].copy()
        self.L      = cor_desc["L'"].copy()
        self.S      = cor_desc["S'"].copy()
        self.origin = cor_desc["COR"].copy()

        return cor_desc
        
    def calc_tls_info(self):
        """Calculates a number of statistics about the TLS group tensors,
        goodness of fit, various parameter averages, center of reaction
        tensors, etc...
        """
        tls_info = self.calc_COR()

        ## EXPERIMENTAL DATA

        ## number of atoms
        tls_info["num_atoms"] = len(self)

        ## mean temp_factor/anisotropy from experimental data (PDB file)
        tls_info["exp_mean_temp_factor"] = self.calc_adv_temp_factor()
        tls_info["exp_mean_anisotropy"]  = self.calc_adv_anisotropy()

        ## model temp factors
        n = 0
        mean_max_tf = 0.0
        mean_tf     = 0.0
        mean_aniso  = 0.0

        for atm, Utls in self.iter_atm_Utls():
            n += 1

            evals  = linalg.eigenvalues(Utls)
            max_ev = max(evals)
            min_ev = min(evals)

            mean_max_tf += Constants.U2B * max_ev
            mean_tf     += Constants.U2B * numpy.trace(Utls) / 3.0
            mean_aniso  += AtomMath.calc_anisotropy(Utls)

        tls_info["tls_mean_max_temp_factor"] = mean_max_tf / n
        tls_info["tls_mean_temp_factor"]     = mean_tf     / n
        tls_info["tls_mean_anisotropy"]      = mean_aniso  / n  

        return tls_info


class TLSStructureAnalysis(object):
    """Algorithm object for rigid body searches on Structure objects.
    """
    def __init__(self, struct):
        self.struct = struct

    def iter_segments(self, chain, seg_len):
        """This iteratar yields a series of Segment objects of width
        seg_len.  The start at the beginning Fragment of the Chain,
        and the start point walks the chain one Fragment at a time
        until there are not enough Fragments left to cut Segments of
        seg_width.
        """
        chain_len = len(chain)

        for i in range(chain_len):
            start = i
            end   = i + seg_len

            if end>chain_len:
                break

            yield chain[start:end]

    def atom_filter(self, atm, **args):
        use_side_chains         = args.get("use_side_chains", True)
        include_hydrogens       = args.get("include_hydrogens", False)
        include_frac_occupancy  = args.get("include_frac_occupancy", False)
        include_single_bond     = args.get("include_single_bond", True)
        
        ## omit atoms which are not at full occupancy
        if not include_frac_occupancy and atm.occupancy<1.0:
            return False

        ## omit hydrogens
        if not include_hydrogens and atm.element=="H":
            return False

        ## omit side chain atoms
        if not use_side_chains and atm.name not in ("C", "N", "CA", "O"):
            return False

        ## omit atoms with a single bond 
        if not include_single_bond and len(atm.bond_list)<=1:
            return False
                        
        return True
        
    def iter_fit_TLS_segments(self, **args):
        """Run the algorithm to fit TLS parameters to segments of the
        structure.  This method has many options, which are outlined in
        the source code for the method.  This returns a list of dictionaries
        containing statistics on each of the fit TLS groups, the residues
        involved, and the TLS object itself.
        """
        import copy
        
        ## arguments
        chain_ids               = args.get("chain_ids", None)
        origin                  = args.get("origin_of_calc")
        residue_width           = args.get("residue_width", 6)
        use_side_chains         = args.get("use_side_chains", True)
        include_hydrogens       = args.get("include_hydrogens", False)
        include_frac_occupancy  = args.get("include_frac_occupancy", False)
        include_single_bond     = args.get("include_single_bond", True)
        calc_pivot_model        = args.get("calc_pivot_model", False)

        
        for chain in self.struct.iter_chains():

            ## skip some chains
            if chain_ids is not None and chain.chain_id not in chain_ids:
                continue

            ## don't bother with non-biopolymers and small chains
            if chain.count_amino_acids()<residue_width:
                continue
            
            for segment in self.iter_segments(chain, residue_width):
                frag_id1     = segment[0].fragment_id
                frag_id2     = segment[-1].fragment_id
                name         = "%s-%s" % (frag_id1, frag_id2)
                frag_id_cntr = segment[len(segment)/2].fragment_id
                
                ## create the TLSGroup
                pv_struct = Structure.Structure()
                pv_seg    = Structure.Chain(chain_id=segment.chain_id,
                                  model_id=segment.model_id)
                pv_struct.add_chain(pv_seg)
                
                tls_group = TLSGroup()

                ## add atoms into the TLSGroup
                ## filter the atoms going into the TLS group                
                for atm in segment.iter_atoms():
                    if self.atom_filter(atm, **args):
                        tls_group.append(atm)

                        atm_cp = copy.deepcopy(atm)
                        pv_seg.add_atom(atm_cp)

                ## check for enough atoms(parameters) after atom filtering
                if len(tls_group)<20:
                    tls_info = {
                        "name":         name,
                        "chain_id":     chain.chain_id,
                        "frag_id1":     frag_id1,
                        "frag_id2":     frag_id2,
                        "frag_id_cntr": frag_id_cntr,
                        "num_atoms":    len(tls_group),
                        "error":        "Not Enough Atoms"}
                    yield tls_info
                    continue
                
                tls_group.origin = tls_group.calc_centroid()
                lsq_residual     = tls_group.calc_TLS_least_squares_fit()
                tls_group.shift_COR()
                tls_info = tls_group.calc_tls_info()
                tls_info["lsq_residual"] = lsq_residual

                ## calculate using CA-pivot TLS model for side chains
                if calc_pivot_model==True:
                    rdict = calc_CB_pivot_TLS_least_squares_fit(pv_seg)
                    tls_info["ca_pivot"] = rdict

                ## add additional information
                tls_info["name"]      = name
                tls_info["chain_id"]  = chain.chain_id
                tls_info["frag_id1"]  = frag_id1
                tls_info["frag_id2"]  = frag_id2
                tls_info["frag_id_cntr"]  = frag_id_cntr
                tls_info["tls_group"] = tls_group
                tls_info["residues"]  = segment
                tls_info["segment"]   = segment
                    
                ## this TLS group passes all our tests -- yield it
                yield tls_info

    def fit_TLS_segments(self, **args):
        """Returns the list iterated by iter_fit_TLS_segments
        """
        tls_info_list = []
        for tls_info in self.iter_fit_TLS_segments(**args):
            tls_info_list.append(tls_info)
        return tls_info_list


###############################################################################
### GLViewer Rendering components for TLS Groups
###

def goodness_color(x):
    """x in range 0.0->1.0
    """
    if x<=0.0:
        return (0.0, 0.0, 0.0)

    r = math.sqrt(x)
    g = max(0.0, x**3)
    b = max(0.0, math.sin(2.0 * math.pi * x))

    return (r, g, b)

class GLTLSAtomList(Viewer.GLAtomList):
    """OpenGL visualizations of TLS group atoms.
    """
    def __init__(self, **args):
        self.tls_group = args["tls_group"] 
        Viewer.GLAtomList.__init__(self, **args)
        self.glo_set_properties_id("GLTLSAtomList")
        self.glo_init_properties(**args)

    def glo_install_properties(self):
        Viewer.GLAtomList.glo_install_properties(self)

        ## Show/Hide
        self.glo_add_property(
            { "name":        "fan_visible",
              "desc":        "Show COR-Backbone Fan",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile" })

        self.glo_add_property(
            { "name":        "L1_animation_visible",
              "desc":        "Show L<sub>1</sub> Screw Animation",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     True,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L2_animation_visible",
              "desc":        "Show L<sub>2</sub> Screw Animation",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     True,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L3_animation_visible",
              "desc":        "Show L<sub>3</sub> Screw Animation",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     True,
              "action":      "redraw" })

        ## TLS
        self.glo_add_property(
            { "name":        "tls_color",
              "desc":        "TLS Group Color",
              "catagory":    "TLS",
              "type":        "enum_string",
              "default":     "Green",
              "enum_list":   self.gldl_color_list,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "fan_opacity",
              "desc":        "COR-Backbone Fan Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "recompile_fan" })
        self.glo_add_property(
            { "name":        "L1_scale",
              "desc":        "Scale L<sub>1</sub> Rotation", 
              "catagory":    "TLS",
              "type":        "float",
              "default":     1.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L2_scale",
              "desc":        "Scale L<sub>2</sub> Rotation", 
              "catagory":    "TLS",
              "type":        "float",
              "default":     1.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L3_scale",
              "desc":        "Scale L<sub>3</sub> Rotation", 
              "catagory":    "TLS",
              "type":        "float",
              "default":     1.0,
              "action":      "redraw" })

        ## TLS Analysis
        self.glo_add_property(
            { "name":        "COR",
              "desc":        "TLS Center of Reaction", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "T",
              "desc":        "T<sup>COR</sup> Tensor (A<sup>2</sup>)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "rT",
              "desc":        "T<sup>r</sup> Tensor (A<sup>2</sup>)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L",
              "desc":        "L<sup>COR</sup> Tensor (DEG<sup>2</sup>)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "S",
              "desc":        "S<sup>COR</sup> Tensor (A*DEG)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_eigen_vec",
              "desc":        "L<sub>1</sub> Eigen Vector", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_eigen_vec",
              "desc":        "L<sub>2</sub> Eigen Vector", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_eigen_vec",
              "desc":        "L<sub>3</sub> Eigen Vector", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_eigen_val",
              "desc":        "L<sub>1</sub> Eigen Value", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_eigen_val",
              "desc":        "L<sub>2</sub> Eigen Value", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_eigen_val",
              "desc":        "L<sub>3</sub> Eigen Value", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_rho",
              "desc":        "L<sub>1</sub> Position from COR", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_rho",
              "desc":        "L<sub>2</sub> Position from COR", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_rho",
              "desc":        "L<sub>3</sub> Position from COR", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_pitch",
              "desc":        "L<sub>1</sub> Screw Pitch (A/DEG)", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_pitch",
              "desc":        "L<sub>2</sub> Screw Pitch (A/DEG)", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_pitch",
              "desc":        "L<sub>3</sub> Screw Pitch (A/DEG)", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })

        ## Simulation State
        self.glo_add_property(
            { "name":        "both_phases",
              "desc":        "Show Simultanius +/- Phases",
              "catagory":    "TLS",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_rot",
              "desc":        "L<sub>1</sub> Rotation", 
              "catagory":    "TLS",
              "type":        "float",
              "default":     0.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L2_rot",
              "desc":        "L<sub>2</sub> Rotation", 
              "catagory":    "TLS",
              "type":        "float",
              "default":     0.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L3_rot",
              "desc":        "L<sub>3</sub> Rotation", 
              "catagory":    "TLS",
              "type":        "float",
              "default":     0.0,
              "action":      "redraw" })

    def gldl_install_draw_methods(self):
        Viewer.GLAtomList.gldl_install_draw_methods(self)
        
        self.gldl_draw_method_install(
            { "name":                "fan",
              "func":                self.draw_fan,
              "visible_property":    "fan_visible",
              "opacity_property":    "fan_opacity",
              "recompile_action":    "recompile_fan" })

    def gldl_iter_multidraw_self(self):
        for draw_flag in Viewer.GLAtomList.gldl_iter_multidraw_self(self):
            for draw_flag2 in self.gldl_iter_multidraw_animate():
                yield True
            
    def gldl_iter_multidraw_animate(self):
        """
        """
        ## optimization: if a rotation of 0.0 degrees was already
        ## drawn, then there is no need to draw it again
        zero_rot = False

        if self.properties["both_phases"]==True:
            phase_tuple = (1.0, 0.66, 0.33, 0.0, -0.33, -0.66, -1.0)
        else:
            phase_tuple = (1.0,)
        
        for Lx_axis, Lx_rho, Lx_pitch, Lx_rot, Lx_scale in (
            ("L1_eigen_vec", "L1_rho", "L1_pitch", "L1_rot", "L1_scale"),
            ("L2_eigen_vec", "L2_rho", "L2_pitch", "L2_rot", "L2_scale"),
            ("L3_eigen_vec", "L3_rho", "L3_pitch", "L3_rot", "L3_scale") ):

            if Lx_axis=="L1_eigen_vec" and self.properties["L1_animation_visible"]==False:
                continue
            if Lx_axis=="L2_eigen_vec" and self.properties["L2_animation_visible"]==False:
                continue
            if Lx_axis=="L3_eigen_vec" and self.properties["L3_animation_visible"]==False:
                continue

            for sign in phase_tuple:
                axis  = self.properties[Lx_axis]
                rho   = self.properties[Lx_rho]
                pitch = self.properties[Lx_pitch]

                rot   = sign * self.properties[Lx_rot] *  self.properties[Lx_scale]
                screw = axis * (rot * pitch)
                
                if numpy.allclose(rot, 0.0):
                    if zero_rot:
                        continue
                    zero_rot = True
                    
                self.driver.glr_push_matrix()

                self.driver.glr_translate(rho)
                self.driver.glr_rotate_axis(rot, axis)
                self.driver.glr_translate(-rho + screw)
                yield True
            
                self.driver.glr_pop_matrix()

    def glal_iter_atoms(self):
        """
        """
        for atm in self.tls_group:
            yield atm

    def glal_calc_color(self, atom):
        """Overrides the GLAtomList coloring behavior and just
        colors using the tls_color.
        """
        return self.gldl_property_color_rgbf("tls_color")

    def glal_calc_color_U(self, atom):
        r, g, b = self.glal_calc_color(atom)
        dim     = 0.8
        return (r*dim, g*dim, b*dim)
    def glal_calc_color_Uellipse(self, atom):
        return self.glal_calc_color_U(atom)
    def glal_calc_color_Urms(self, atom):
        return self.glal_calc_color_U(atom)
    
    def glal_calc_color_trace(self):
        return self.gldl_property_color_rgbf("tls_color") 

    def glal_calc_U(self, atom):
        """Always return the reduced T tensor.
        """
        return self.properties["rT"]

    def draw_fan(self):
        """Draws a fan from the TLS group center of reaction to the
        TLS group backbone atoms.
        """
        COR     = self.properties["COR"]
        r, g, b = self.gldl_property_color_rgbf("tls_color")
        a       = self.properties["fan_opacity"]

        self.driver.glr_set_material_rgba(r, g, b, a)

        self.driver.glr_lighting_enable()
        self.driver.glr_normalize_enable()
        self.driver.glr_light_two_sides_enable()
        self.driver.glr_begin_triangle_fan()

        ## driver optimization
        driver = self.driver
        ##

        v1 = None
        v2 = None

        for atm in self.tls_group:
            if atm.name != "CA":
                continue

            if v1 is None:
                v1 = atm.position - COR
                continue
            elif v2 is None:
                v2 = atm.position - COR
                driver.glr_normal(numpy.cross(v1, v2))
                driver.glr_vertex3(0.0, 0.0, 0.0)
            else:
                v1 = v2
                v2 = atm.position - COR

            driver.glr_normal(numpy.cross(v1, v2))
            driver.glr_vertex(v1)
            driver.glr_vertex(v2)

        self.driver.glr_end()
        self.driver.glr_light_two_sides_disable()
        self.driver.glr_normalize_disable()
        self.driver.glr_lighting_disable()
        

class GLTLSGroup(Viewer.GLDrawList):
    """Top level visualization object for a TLS group.
    """
    def __init__(self, **args):
        self.tls_group = args["tls_group"]
        self.tls_info  = args["tls_info"]
        self.tls_name  = args["tls_name"]

        Viewer.GLDrawList.__init__(self)
        self.glo_set_properties_id("GLTLSGroup_%s" % (self.tls_name))
        self.glo_set_name(self.tls_name)

        ## add a child GLTLSAtomList for the animated atoms
        self.gl_atom_list = GLTLSAtomList(
            tls_group        = self.tls_group,
            trace            = True,
            lines            = False,
            fan_visible      = False)

        self.gl_atom_list.glo_set_name("TLS Atom Animation")
        self.gl_atom_list.glo_set_properties_id("gl_atom_list")
        self.glo_add_child(self.gl_atom_list)

        self.glo_link_child_property(
            "symmetry", "gl_atom_list", "symmetry")

        self.glo_link_child_property(
            "main_chain_visible", "gl_atom_list", "main_chain_visible")
        self.glo_link_child_property(
            "oatm_visible", "gl_atom_list", "oatm_visible")
        self.glo_link_child_property(
            "side_chain_visible", "gl_atom_list", "side_chain_visible") 
        self.glo_link_child_property(
            "hetatm_visible", "gl_atom_list", "hetatm_visible") 
        self.glo_link_child_property(
            "water_visible", "gl_atom_list", "water_visible")        
        self.glo_link_child_property(
            "hydrogen_visible", "gl_atom_list", "hydrogen_visible") 

        self.glo_link_child_property(
            "tls_color", "gl_atom_list", "tls_color")        

        self.glo_link_child_property(
            "fan_visible", "gl_atom_list", "fan_visible")
        self.glo_link_child_property(
            "fan_opacity", "gl_atom_list", "fan_opacity")
        self.glo_link_child_property(
            "axes_rT", "gl_atom_list", "U")
        self.glo_link_child_property(
            "ellipse_rT", "gl_atom_list", "ellipse")
        self.glo_link_child_property(
            "rms_rT", "gl_atom_list", "rms")

        self.glo_link_child_property(
            "adp_prob", "gl_atom_list", "adp_prob")

        self.glo_link_child_property(
            "COR", "gl_atom_list", "origin")
        self.glo_link_child_property(
            "COR", "gl_atom_list", "atom_origin")
        self.glo_link_child_property(
            "COR", "gl_atom_list", "COR")
        self.glo_link_child_property(
            "T", "gl_atom_list", "T")
        self.glo_link_child_property(
            "rT", "gl_atom_list", "rT")
        self.glo_link_child_property(
            "L", "gl_atom_list", "L")
        self.glo_link_child_property(
            "S", "gl_atom_list", "S")

        self.glo_link_child_property(
            "L1_eigen_vec", "gl_atom_list", "L1_eigen_vec")
        self.glo_link_child_property(
            "L2_eigen_vec", "gl_atom_list", "L2_eigen_vec")
        self.glo_link_child_property(
            "L3_eigen_vec", "gl_atom_list", "L3_eigen_vec")
        
        self.glo_link_child_property(
            "L1_eigen_val", "gl_atom_list", "L1_eigen_val")
        self.glo_link_child_property(
            "L2_eigen_val", "gl_atom_list", "L2_eigen_val")
        self.glo_link_child_property(
            "L3_eigen_val", "gl_atom_list", "L3_eigen_val")

        self.glo_link_child_property(
            "L1_rho", "gl_atom_list", "L1_rho")
        self.glo_link_child_property(
            "L2_rho", "gl_atom_list", "L2_rho")
        self.glo_link_child_property(
            "L3_rho", "gl_atom_list", "L3_rho")

        self.glo_link_child_property(
            "L1_pitch", "gl_atom_list", "L1_pitch")
        self.glo_link_child_property(
            "L2_pitch", "gl_atom_list", "L2_pitch")
        self.glo_link_child_property(
            "L3_pitch", "gl_atom_list", "L3_pitch")

        self.glo_link_child_property(
            "L1_rot", "gl_atom_list", "L1_rot")
        self.glo_link_child_property(
            "L2_rot", "gl_atom_list", "L2_rot")
        self.glo_link_child_property(
            "L3_rot", "gl_atom_list", "L3_rot")

        self.glo_link_child_property(
            "both_phases", "gl_atom_list", "both_phases")
         
        ## initalize properties
        self.glo_add_update_callback(self.tls_update_cb)

        if not self.tls_group.is_null():
            self.glo_init_properties(
                COR          = self.tls_info["COR"],

                T            = self.tls_info["T'"],
                rT           = self.tls_info["rT'"],
                L            = self.tls_info["L'"] * Constants.RAD2DEG2,
                S            = self.tls_info["S'"] * Constants.RAD2DEG,

                L1_eigen_vec = self.tls_info["L1_eigen_vec"],
                L2_eigen_vec = self.tls_info["L2_eigen_vec"],
                L3_eigen_vec = self.tls_info["L3_eigen_vec"],

                L1_eigen_val = self.tls_info["L1_eigen_val"] * Constants.RAD2DEG2,
                L2_eigen_val = self.tls_info["L2_eigen_val"] * Constants.RAD2DEG2,
                L3_eigen_val = self.tls_info["L3_eigen_val"] * Constants.RAD2DEG2,

                L1_rho       = self.tls_info["L1_rho"],
                L2_rho       = self.tls_info["L2_rho"],
                L3_rho       = self.tls_info["L3_rho"],

                L1_pitch     = self.tls_info["L1_pitch"] * (1.0/Constants.RAD2DEG),
                L2_pitch     = self.tls_info["L2_pitch"] * (1.0/Constants.RAD2DEG),
                L3_pitch     = self.tls_info["L3_pitch"] * (1.0/Constants.RAD2DEG),
                **args)
        else:
            self.glo_init_properties(**args)

    def set_tls_groupXXX(self, tls_group):
        """Set a new TLSGroup.
        """
        self.tls_group = tls_group

        if not self.tls_group.is_null():
            self.tls_info = self.tls_group.calc_tls_info()

            self.properties.update(
                COR          = self.tls_info["COR"],
                T            = self.tls_info["T'"],
                Tr           = self.tls_info["rT'"],
                L            = self.tls_info["L'"] * Constants.RAD2DEG2,
                S            = self.tls_info["S'"] * Constants.RAD2DEG,

                L1_eigen_vec = self.tls_info["L1_eigen_vec"],
                L2_eigen_vec = self.tls_info["L2_eigen_vec"],
                L3_eigen_vec = self.tls_info["L3_eigen_vec"],

                L1_eigen_val = self.tls_info["L1_eigen_val"] * Constants.RAD2DEG2,
                L2_eigen_val = self.tls_info["L2_eigen_val"] * Constants.RAD2DEG2,
                L3_eigen_val = self.tls_info["L3_eigen_val"] * Constants.RAD2DEG2,

                L1_rho       = self.tls_info["L1_rho"],
                L2_rho       = self.tls_info["L2_rho"],
                L3_rho       = self.tls_info["L3_rho"],

                L1_pitch     = self.tls_info["L1_pitch"] * (1.0/Constants.RAD2DEG),
                L2_pitch     = self.tls_info["L2_pitch"] * (1.0/Constants.RAD2DEG),
                L3_pitch     = self.tls_info["L3_pitch"] * (1.0/Constants.RAD2DEG) )

        else:
            self.tls_info = None

            self.properties.update(
                COR          = Viewer.GLObject.PropertyDefault,
                T            = Viewer.GLObject.PropertyDefault,
                Tr           = Viewer.GLObject.PropertyDefault,
                L            = Viewer.GLObject.PropertyDefault,
                S            = Viewer.GLObject.PropertyDefault,

                L1_eigen_vec = Viewer.GLObject.PropertyDefault,
                L2_eigen_vec = Viewer.GLObject.PropertyDefault,
                L3_eigen_vec = Viewer.GLObject.PropertyDefault,

                L1_eigen_val = Viewer.GLObject.PropertyDefault,
                L2_eigen_val = Viewer.GLObject.PropertyDefault,
                L3_eigen_val = Viewer.GLObject.PropertyDefault,

                L1_rho       = Viewer.GLObject.PropertyDefault,
                L2_rho       = Viewer.GLObject.PropertyDefault,
                L3_rho       = Viewer.GLObject.PropertyDefault,

                L1_pitch     = Viewer.GLObject.PropertyDefault,
                L2_pitch     = Viewer.GLObject.PropertyDefault,
                L3_pitch     = Viewer.GLObject.PropertyDefault )

    def glo_install_properties(self):
        Viewer.GLDrawList.glo_install_properties(self)

        ## TLS Analysis
        self.glo_add_property(
            { "name":        "COR",
              "desc":        "TLS Center of Reaction", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "COR_vector",
              "desc":        "TLS Center of Reaction", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "T",
              "desc":        "T<sup>COR</sup> Tensor (A<sup>2</sup>)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "rT",
              "desc":        "T<sup>r</sup> Tensor (A<sup>2</sup>)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L",
              "desc":        "L<sup>COR</sup> Tensor (DEG<sup>2</sup>)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "S",
              "desc":        "S<sup>COR</sup> Tensor (A*DEG)",
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3,3)",
              "default":     numpy.zeros((3,3), float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_eigen_vec",
              "desc":        "L<sub>1</sub> Eigen Vector", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_eigen_vec",
              "desc":        "L<sub>2</sub> Eigen Vector", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_eigen_vec",
              "desc":        "L<sub>3</sub> Eigen Vector", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_eigen_val",
              "desc":        "L<sub>1</sub> Eigen Value", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_eigen_val",
              "desc":        "L<sub>2</sub> Eigen Value", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_eigen_val",
              "desc":        "L<sub>3</sub> Eigen Value", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_rho",
              "desc":        "L<sub>1</sub> Position from COR", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_rho",
              "desc":        "L<sub>2</sub> Position from COR", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_rho",
              "desc":        "L<sub>3</sub> Position from COR", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "numpy.array(3)",
              "default":     numpy.zeros(3, float),
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L1_pitch",
              "desc":        "L<sub>1</sub> Screw Pitch (A/DEG)", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L2_pitch",
              "desc":        "L<sub>2</sub> Screw Pitch (A/DEG)", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "L3_pitch",
              "desc":        "L<sub>3</sub> Screw Pitch (A/DEG)", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "gof",
              "desc":        "Goodness of Fit", 
              "catagory":    "TLS Analysis",
              "read_only":   True,
              "type":        "float",
              "default":     0.0,
              "action":      "recompile" })
        
        ## Show/Hide
        self.glo_add_property(
            { "name":        "symmetry",
              "desc":        "Show Symmetry Equivelant",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":      "main_chain_visible",
              "desc":      "Show Main Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "oatm_visible",
              "desc":      "Show Main Chain Carbonyl Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "side_chain_visible",
              "desc":      "Show Side Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "hetatm_visible",
              "desc":      "Show Hetrogen Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "water_visible",
              "desc":      "Show Waters",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "hydrogen_visible",
              "desc":      "Show Hydrogens",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":        "fan_visible",
              "desc":        "Show COR-Backbone Fan",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "TLS_visible",
              "desc":        "Show TLS T<sup>r</sup> Ellipsoid/Screw Axes",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     True,
              "action":      "recompile_tensors" })
        self.glo_add_property(
            { "name":        "U",
              "desc":        "Show U<sup>TLS</sup> Thermal Axes",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile_Utls_axes" })
        self.glo_add_property(
            { "name":        "ellipse",
              "desc":        "Show U<sup>TLS</sup> Thermal Ellipsoids",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile_Utls_ellipse" })
        self.glo_add_property(
            { "name":        "rms",
              "desc":        "Show U<sup>TLS</sup> Thermal Peanuts",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile_Utls_rms" })

        self.glo_add_property(
            { "name":        "axes_rT",
              "desc":        "Show T<sup>r</sup> Thermal Axes", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "ellipse_rT",
              "desc":        "Show  T<sup>r</sup> Thermal Ellipsoids", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "rms_rT",
              "desc":        "Show  T<sup>r</sup> Thermal Peanuts",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile_Utls_rms" })
                
        self.glo_add_property(
            { "name":        "L1_visible",
              "desc":        "Show Screw L1 Displacement Surface", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile_surface" })
        self.glo_add_property(
            { "name":        "L2_visible",
              "desc":        "Show Screw L2 Displacement Surface", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile_surface" })
        self.glo_add_property(
            { "name":        "L3_visible",
              "desc":        "Show Screw L3 Displacement Surface",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile_surface" })
        
        ## TLS
        self.glo_add_property(
            { "name":        "add_biso",
              "desc":        "Add Atom B<sup>ISO</sup> to U<sup>TLS</sup>",
              "catagory":    "TLS",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "both_phases",
              "desc":        "Show Simultanius +/- Phases",
              "catagory":    "TLS",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "tls_color",
              "desc":        "TLS Group Visualization Color",
              "catagory":    "TLS",
              "type":        "enum_string",
              "default":     "Green",
              "enum_list":   self.gldl_color_list,
              "action":      ["redraw", "recompile"] })
        self.glo_add_property(
            { "name":       "adp_prob",
              "desc":       "Isoprobability Magnitude",
              "catagory":   "TLS",
              "type":       "integer",
              "range":      Viewer.PROP_PROBABILTY_RANGE,
              "default":    50,
              "action":     "recompile" })
        self.glo_add_property(
            { "name":       "L_axis_scale",
              "desc":       "Scale Screw Axis Length",
              "catagory":   "TLS",
              "type":       "float",
              "default":    5.00,
              "action":     "recompile_tensors" })        
        self.glo_add_property(
            { "name":       "L_axis_radius",
              "desc":       "Screw Axes Radius",
              "catagory":   "TLS",
              "type":       "float",
              "default":    0.4,
              "action":     "recompile_tensors" })
        self.glo_add_property(
            { "name":        "ellipse_opacity",
              "desc":        "U<sup>TLS</sup> Thermal Ellipsoid Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "recompile_Utls_ellipse" })
        self.glo_add_property(
            { "name":        "rms_opacity",
              "desc":        "U<sup>TLS</sup> Thermal Peanut Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "recompile_Utls_rms" })
        self.glo_add_property(
            { "name":        "surface_opacity",
              "desc":        "Screw Surface Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "recompile_surface" })
        self.glo_add_property(
            { "name":        "fan_opacity",
              "desc":        "COR-Backbone Fan Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "recompile_fan" })
        self.glo_add_property(
            { "name":        "time",
              "desc":        "Simulation Time",
              "catagory":    "TLS",
              "type":        "float",
              "default":     0.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "period",
              "desc":        "Simulation Period",
              "catagory":    "TLS",
              "type":        "float",
              "default":     1.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "amplitude",
              "desc":        "Simulation Amplitude",
              "catagory":    "TLS",
              "type":        "float",
              "default":     1.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L1_rot",
              "desc":        "L<sub>1</sub> Simulated Rotation (DEG)",
              "catagory":    "TLS",
              "type":        "float",
              "default":     0.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L2_rot",
              "desc":        "L<sub>2</sub> Simulated Rotation (DEG)", 
              "catagory":    "TLS",
              "type":        "float",
              "default":     0.0,
              "action":      "redraw" })
        self.glo_add_property(
            { "name":        "L3_rot",
              "desc":        "L<sub>3</sub> Simulated Rotation (DEG)",
              "catagory":    "TLS",
              "type":        "float",
              "default":     0.0,
              "action":      "redraw" })

    def gldl_install_draw_methods(self):
        self.gldl_draw_method_install(
            { "name":                "tls_tensors",
              "func":                self.draw_tensors,
              "transparent":         False,
              "visible_property":    "TLS_visible",
              "recompile_action":    "recompile_tensors" })
        self.gldl_draw_method_install(
            { "name":                "Utls_axes",
              "func":                self.draw_Utls_axes,
              "transparent":         False,
              "visible_property":    "U",
              "recompile_action":    "recompile_Utls_axes" })
        self.gldl_draw_method_install(
            { "name":                "Utls_ellipse",
              "func":                self.draw_Utls_ellipse,
              "visible_property":    "ellipse",
              "opacity_property":    "ellipse_opacity",
              "recompile_action":    "recompile_Utls_ellipse" })
        self.gldl_draw_method_install(
            { "name":                "Utls_rms",
              "func":                self.draw_Utls_rms,
              "visible_property":    "rms",
              "opacity_property":    "rms_opacity",
              "recompile_action":    "recompile_Utls_rms" })
        self.gldl_draw_method_install(
            { "name":                "L1_surface",
              "func":                self.draw_L1_surface,
              "visible_property":    "L1_visible",
              "opacity_property":    "surface_opacity",
              "recompile_action":    "recompile_surface" })
        self.gldl_draw_method_install(
            { "name":                "L2_surface",
              "func":                self.draw_L2_surface,
              "visible_property":    "L2_visible",
              "opacity_property":    "surface_opacity",
              "recompile_action":    "recompile_surface" })
        self.gldl_draw_method_install(
            { "name":                "L3_surface",
              "func":                self.draw_L3_surface,
              "visible_property":    "L3_visible",
              "opacity_property":    "surface_opacity",
              "recompile_action":    "recompile_surface" })
         
    def tls_update_cb(self, updates, actions):
        if "time" in updates or "adp_prob" in updates:
            self.update_time()

    def update_time(self):
        """Changes the time of the TLS group simulating harmonic motion.
        """
        if self.tls_group.is_null():
            return

        ## time should be in the range 0.0-0.1.0
        sin_tm = math.sin(2.0 * math.pi * self.properties["period"] * self.properties["time"])

        ## calculate L eignvalue displacements at the given
        ## probability levels
        C = Gaussian.GAUSS3C[self.properties["adp_prob"]]

        L1_rot  = self.properties["amplitude"] * C * calc_rmsd(self.properties["L1_eigen_val"]) * sin_tm
        L2_rot  = self.properties["amplitude"] * C * calc_rmsd(self.properties["L2_eigen_val"]) * sin_tm
        L3_rot  = self.properties["amplitude"] * C * calc_rmsd(self.properties["L3_eigen_val"]) * sin_tm

        self.glo_update_properties(L1_rot=L1_rot, L2_rot=L2_rot, L3_rot=L3_rot)

    def gldl_iter_multidraw_self(self):
        """Specialized draw list invokation to recycle the draw list for
        symmetry related copies.  Cartesian versions of the symmetry rotation
        and translation operators are generated by GLStructure/UnitCell
        classes.
        """
        if self.properties["symmetry"]==False:
            yield True
            
        else:

            gl_struct = self.glo_get_glstructure()
            if gl_struct is None:
                yield True

            else:
                for symop in gl_struct.iter_orth_symops():
                    self.driver.glr_push_matrix()
                    self.driver.glr_mult_matrix_Rt(symop.R, symop.t)
                    yield True
                    self.driver.glr_pop_matrix()

    def gltls_iter_atoms(self):
        """Special atom iterator for the TLS drawing functions yields:
        atm, Utls
        """
        T = self.tls_group.T
        L = self.tls_group.L
        S = self.tls_group.S
        o = self.tls_group.origin
        
        for atm, visible in self.gl_atom_list.glal_iter_atoms_filtered():
            if not visible:
                continue

            Utls = calc_Utls(T, L, S, atm.position - o)

            if self.properties["add_biso"] == True:
                if atm.temp_factor is not None:
                    Utls = Utls + (Constants.B2U * atm.temp_factor * numpy.identity(3, float))
            
            yield atm, Utls
    
    def draw_tensors(self):
        """Draw tensor axis.
        """
        if self.tls_group.is_null():
            return

        self.driver.glr_push_matrix()

        ## get the TLS color
        r, g, b = self.gldl_property_color_rgbf("tls_color")

        self.driver.glr_translate(self.properties["COR"])

        ## cor vector
        self.driver.glr_set_material_rgb(0.5, 0.5, 0.5)
        vec = self.properties["COR_vector"]
        if AtomMath.length(vec) > 1.0:
            vec2 = 2.0 * vec
            self.driver.glr_axis(-vec2 / 2.0, vec2, self.properties["L_axis_radius"])

        self.driver.glr_set_material_rgb(r, g, b)
        
        ## T: units (A^2)
        self.driver.glr_Uellipse((0.0,0.0,0.0), self.properties["rT"], self.properties["adp_prob"])

        ## L: units (DEG^2)
        L_scale = self.properties["L_axis_scale"]

        
        for Lx_eigen_val, Lx_eigen_vec, Lx_rho, Lx_pitch in [
            ("L1_eigen_val", "L1_eigen_vec", "L1_rho", "L1_pitch"),
            ("L2_eigen_val", "L2_eigen_vec", "L2_rho", "L2_pitch"),
            ("L3_eigen_val", "L3_eigen_vec", "L3_rho", "L3_pitch")]:

            L_eigen_vec = self.properties[Lx_eigen_vec]
            L_eigen_val = self.properties[Lx_eigen_val]
            L_rho       = self.properties[Lx_rho]
            L_pitch     = self.properties[Lx_pitch]

            C = Gaussian.GAUSS3C[self.properties["adp_prob"]]
            L_rot = C * (L_scale * calc_rmsd(L_eigen_val))

            if L_eigen_val <= 0.0:
                continue

            L_v = L_eigen_vec * L_rot

            ## line from COR to center of screw/rotation axis
            ## draw lines from COR to the axis
            self.driver.glr_lighting_disable()
            self.driver.glr_line((0.0, 0.0, 0.0), L_rho)

            ## draw axis
            self.driver.glr_axis(L_rho - (0.5*L_v), L_v, self.properties["L_axis_radius"])

            ## draw disks with translational displacement
            L_screw_dis = L_eigen_vec * L_rot * L_pitch

            self.driver.glr_axis(
                L_rho - (0.5 * L_screw_dis),
                L_screw_dis,
                1.5 * self.properties["L_axis_radius"])

        self.driver.glr_pop_matrix()

    def draw_Utls_axes(self):
        """Render the anisotropic thremal axes calculated from the TLS
        model.
        """
        if self.tls_group.is_null():
            return
        
        prob = self.properties["adp_prob"]
        rgbf = self.gldl_property_color_rgbf("tls_color")

        glr_Uaxes = self.driver.glr_Uaxes

        for atm, Utls in self.gltls_iter_atoms():
            glr_Uaxes(atm.position, Utls, prob, rgbf, 1.0)

    def draw_Utls_ellipse(self):
        """Render the anisotropic thremal ellipsoids at the given probability
        contour calculated from the TLS model.
        """
        if self.tls_group.is_null():
            return
        
        prob    = self.properties["adp_prob"]
        r, g, b = self.gldl_property_color_rgbf("tls_color")
        a       = self.properties["ellipse_opacity"]
        self.driver.glr_set_material_rgba(r, g, b, a)

        glr_Uellipse = self.driver.glr_Uellipse

        for atm, Utls in self.gltls_iter_atoms():
            glr_Uellipse(atm.position, Utls, prob)

    def draw_Utls_rms(self):
        """Render the anisotropic thremal peanuts calculated from the TLS
        model.
        """
        if self.tls_group.is_null():
            return
        
        r, g, b = self.gldl_property_color_rgbf("tls_color")
        a       = self.properties["rms_opacity"]
        self.driver.glr_set_material_rgb(r, g, b, a)

        for atm, Utls in self.gltls_iter_atoms():
            self.driver.glr_Urms(atm.position, Utls)

    def draw_L1_surface(self):
        if self.tls_group.is_null():
            return
        self.draw_tls_surface(
            self.properties["L1_eigen_vec"],
            self.properties["L1_eigen_val"],
            self.properties["L1_rho"],
            self.properties["L1_pitch"])

    def draw_L2_surface(self):
        if self.tls_group.is_null():
            return
        self.draw_tls_surface(
            self.properties["L2_eigen_vec"],
            self.properties["L2_eigen_val"],
            self.properties["L2_rho"],
            self.properties["L2_pitch"])

    def draw_L3_surface(self):
        if self.tls_group.is_null():
            return
        self.draw_tls_surface(
            self.properties["L3_eigen_vec"],
            self.properties["L3_eigen_val"],
            self.properties["L3_rho"],
            self.properties["L3_pitch"])

    def draw_tls_surface(self, Lx_eigen_vec, Lx_eigen_val, Lx_rho, Lx_pitch):
        """Draws the TLS probability surface for a single non-intersecting
        screw axis.  Lx_eigen_val is the vaiance (mean square deviation MSD)
        of the rotation about the Lx_eigen_vec axis.
        """
        ## create a unique list of bonds which will be used to
        ## render the TLS surface; this list may be passed in a argument
        ## to avoid multiple calculations for each screw-rotation axis
        bond_list = []
        in_dict   = {}

        for atm, Utls in self.gltls_iter_atoms():
            in_dict[atm] = True

        for atm, Utls in self.gltls_iter_atoms():
            for bond in atm.iter_bonds():
                if in_dict.has_key(bond.get_partner(atm)):
                    bond_list.append(bond)
        
        ## this just won't work...
        if numpy.allclose(Lx_eigen_val, 0.0):
            return

        C = Gaussian.GAUSS3C[self.properties["adp_prob"]]
        Lx_s = C * calc_rmsd(Lx_eigen_val * Constants.DEG2RAD2)
        if numpy.allclose(Lx_s, 0.0):
            return

        Lx_pitch      = Lx_pitch * (1.0 / Constants.DEG2RAD)
        COR           = self.properties["COR"]
        Lx_origin     = COR + Lx_rho
        steps         = 1
        rot_step      = Lx_s / float(steps)

        self.driver.glr_light_two_sides_enable()
        self.driver.glr_lighting_enable()
        self.driver.glr_normalize_enable()

        r, g, b = self.gldl_property_color_rgbf("tls_color")
        a       = self.properties["surface_opacity"]
        gam     = 0.50
        self.driver.glr_set_material_rgba(r*gam, g*gam, b*gam, a)


        self.driver.glr_begin_quads()

        ## driver optimization
        glr_normal = self.driver.glr_normal
        glr_vertex = self.driver.glr_vertex
        ##

        for step in range(steps):
            rot_start = rot_step * float(step)
            rot_end   = rot_step * float(step + 1)

            for sign in (-1.0, 1.0):
                rot1   = rot_start * sign
                rot2   = rot_end   * sign

                Rstep1 = AtomMath.rmatrixu(Lx_eigen_vec, rot1)
                Rstep2 = AtomMath.rmatrixu(Lx_eigen_vec, rot2)

                screw1 = Lx_eigen_vec * (rot1 * Lx_pitch)
                screw2 = Lx_eigen_vec * (rot2 * Lx_pitch)

                for bond in bond_list:

                    pos1 = bond.atom1.position - Lx_origin
                    pos2 = bond.atom2.position - Lx_origin

                    v1 = numpy.matrixmultiply(Rstep1, pos1) + screw1
                    v2 = numpy.matrixmultiply(Rstep2, pos1) + screw2
                    v3 = numpy.matrixmultiply(Rstep2, pos2) + screw2
                    v4 = numpy.matrixmultiply(Rstep1, pos2) + screw1
                    
                    ## one normal perpendicular to the quad
                    glr_normal(numpy.cross(v2-v1, v4-v1))

                    glr_vertex(v1 + Lx_origin)
                    glr_vertex(v2 + Lx_origin)
                    glr_vertex(v3 + Lx_origin)
                    glr_vertex(v4 + Lx_origin)

        self.driver.glr_end()
        self.driver.glr_light_two_sides_disable()
        self.driver.glr_normalize_disable()
        self.driver.glr_lighting_disable()

class GLTLSChain(Viewer.GLDrawList):
    """Collects a list of GLTLSGroup instances which are all in the
    same chain.
    """
    def __init__(self, **args):
        Viewer.GLDrawList.__init__(self)
        self.glo_set_properties_id("GLTLSChain_%s" % (args["chain_id"]))
        self.glo_set_name("TLS Chain %s" % (args["chain_id"]))
        self.glo_add_update_callback(self.update_cb)
        self.glo_init_properties(**args)

    def glo_install_properties(self):
        Viewer.GLDrawList.glo_install_properties(self)

        ## show/hide
        self.glo_add_property(
            { "name":        "symmetry",
              "desc":        "Show Symmetry Equivelant",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":      "main_chain_visible",
              "desc":      "Show Main Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    "" })
        self.glo_add_property(
            { "name":      "oatm_visible",
              "desc":      "Show Main Chain Carbonyl Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    ["recompile", "recalc_positions"] })
        self.glo_add_property(
            { "name":      "side_chain_visible",
              "desc":      "Show Side Chain Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    "" })
        self.glo_add_property(
            { "name":      "hetatm_visible",
              "desc":      "Show Hetrogen Atoms",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   True,
              "action":    "" })
        self.glo_add_property(
            { "name":      "water_visible",
              "desc":      "Show Waters",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    "" })
        self.glo_add_property(
            { "name":      "hydrogen_visible",
              "desc":      "Show Hydrogens",
              "catagory":  "Show/Hide",
              "type":      "boolean",
              "default":   False,
              "action":    "" })
        self.glo_add_property(
            { "name":        "fan_visible",
              "desc":        "Show COR-Backbone Fan",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":        "TLS_visible",
              "desc":        "Show TLS T<sup>r</sup> Ellipsoid/Screw Axes",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     True,
              "action":      "" })
        self.glo_add_property(
            { "name":        "U",
              "desc":        "Show U<sup>TLS</sup> Thermal Axes",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "ellipse",
              "desc":        "Show U<sup>TLS</sup> Thermal Ellipsoids",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "rms",
              "desc":        "Show U<sup>TLS</sup> Thermal Peanuts",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "axes_rT",
              "desc":        "Show T<sup>r</sup> Thermal Axes", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "ellipse_rT",
              "desc":        "Show T<sup>r</sup> Thermal Ellipsoids", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "rms_rT",
              "desc":        "Show T<sup>r</sup> Thermal Peanuts",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "L1_visible",
              "desc":        "Show L<sub>1</sub> Screw Displacement Surface", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "L2_visible",
              "desc":        "Show L<sub>2</sub> Screw Displacement Surface", 
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "L3_visible",
              "desc":        "Show L<sub>3</sub> Screw Displacement Surface",
              "catagory":    "Show/Hide",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        
        ## TLS
        self.glo_add_property(
            { "name":        "add_biso",
              "desc":        "Add Atom B<sup>ISO</sup> to U<sup>TLS</sup>",
              "catagory":    "TLS",
              "type":        "boolean",
              "default":     False,
              "action":      "" })
        self.glo_add_property(
            { "name":        "both_phases",
              "desc":        "Show Simultanius +/- Phases",
              "catagory":    "TLS",
              "type":        "boolean",
              "default":     False,
              "action":      "recompile" })
        self.glo_add_property(
            { "name":       "adp_prob",
              "desc":       "Isoprobability Magnitude",
              "catagory":   "TLS",
              "type":       "integer",
              "range":      Viewer.PROP_PROBABILTY_RANGE,
              "default":    50,
              "action":     "" })

        self.glo_add_property(
            { "name":       "L_axis_scale",
              "desc":       "Scale Screw Axis Length",
              "catagory":   "TLS",
              "type":       "float",
              "default":    5.00,
              "action":     "recompile_tensors" })
        self.glo_add_property(
            { "name":       "L_axis_radius",
              "desc":       "Screw Axes Radius",
              "catagory":   "TLS",
              "type":       "float",
              "default":    0.4,
              "action":     "" })
        self.glo_add_property(
            { "name":        "ellipse_opacity",
              "desc":        "U<sup>TLS</sup> Thermal Ellipsoid Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "" })
        self.glo_add_property(
            { "name":        "rms_opacity",
              "desc":        "U<sup>TLS</sup> Thermal Peanut Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "" })
        self.glo_add_property(
            { "name":        "surface_opacity",
              "desc":        "Screw Displacement Surface Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "" })
        self.glo_add_property(
            { "name":        "fan_opacity",
              "desc":        "COR-Backbone Fan Opacity",
              "catagory":    "TLS",
              "type":        "float",
              "range":       Viewer.PROP_OPACITY_RANGE,
              "default":     1.0,
              "action":      "recompile_fan" })

        ## color methods
        self.glo_add_property(
            { "name":        "color_method",
              "desc":        "TLS Group Coloring Scheme",
              "catagory":    "Macros",
              "type":        "enum_string",
              "default":     "Color by Group",
              "enum_list":   ["Color By Group", "Color By Goodness of Fit"],
              "action":      "recolor" })
        self.glo_add_property(
            { "name":       "show_frac",
              "desc":       "Show Fraction of Top Fitting Groups",
              "catagory":   "Macros",
              "type":       "integer",
              "range":      "0-100,1",
              "default":    100,
              "action":     "recolor" })
        self.glo_add_property(
            { "name":        "style1",
              "desc":        "Cool Visualization Style #1",
              "catagory":    "Macros",
              "type":        "boolean",
              "default":     False,
              "action":      "style1" })

    def update_cb(self, updates, actions):
        if "recolor" in actions:
            if self.properties["color_method"]=="Color By Goodness of Fit":
                show_frac = float(self.properties["show_frac"] / 100.0)
                self.color_by_gof(show_frac)
            elif self.properties["color_method"]=="Color By Group":
                self.color_by_group()

        if "style1" in actions and self.properties["style1"]==True:
            self.properties.update(style1=False)
            self.set_style1()
            
    def set_style1(self):
        self.properties.update(
            L1_visible         = True,
            L2_visible         = True,
            L3_visible         = True)
        
        for gl_tls_group in self.glo_iter_children():
            gl_tls_group.properties.update(
                time               = 0.25)
            
            gl_tls_group.gl_atom_list.properties.update(
                trace        = False,
                ball_stick   = True,
                ball_radius  = 0.075,
                stick_radius = 0.075)

    def color_by_group(self):
        """Color TLS Groups by 
        """
        colori = 2
        for gl_tls_group in self.glo_iter_children():
            try:
                tls_color = Colors.COLOR_NAMES_CAPITALIZED[colori]
            except IndexError:
                colori = 2
                tls_color = Colors.COLOR_NAMES_CAPITALIZED[colori]
                                                                
            gl_tls_group.properties.update(
                visible = True,
                tls_color=tls_color)

            colori += 1

    def color_by_gof(self, show_frac):
        """Color TLS Groups by goodness-of-fit.
        """
        gof_list = []
        
        for gl_tls_group in self.glo_iter_children():
            gof = gl_tls_group.properties["gof"]
            gof_list.append((gof, gl_tls_group))

        if len(gof_list)==0:
            return
        elif len(gof_list)==1:
            return

        ## sort from highest->lowest since the gof metric is a minimization
        ## residual
        gof_list.sort()
        gof_list.reverse()

        ## n is the number to show
        n = int(round(float(len(gof_list)) * show_frac))
        i = len(gof_list) - n

        ## hide the groups with the lowest gof values below the show_frac
        ## percentage
        for j in range(i):
            gof, gl_tls_group = gof_list[j]
            gl_tls_group.properties.update(
                visible   = False,
                tls_color = "gray")

        ## remove the hidden groups
        gof_list = gof_list[i:]

        min_gof = gof_list[0][0]
        max_gof = gof_list[-1][0]

        ## a reasonable range is needed to color by goodness of fit
        gof_range = max_gof - min_gof
        if numpy.allclose(gof_range, 0.0):
            for gof, gl_tls_group in gof_list:
                gl_tls_group.properties.update(
                    visible = True,
                    tls_color = "gray")
            return
        
        for gof, gl_tls_group in gof_list:
            goodness = 1.0 - (gof - min_gof) / gof_range
            tls_color = "%4.2f,%4.2f,%4.2f" % (goodness_color(goodness))
            
            ## set TLS color for group based on goodness of fit
            gl_tls_group.properties.update(
                visible   = True,
                tls_color = tls_color)

            ## set trace radius based on goodness of fit
            gl_tls_group.gl_atom_list.properties.update(
                trace_radius = 0.3 + (goodness * 0.01))

    def add_gl_tls_group(self, gl_tls_group):
        self.glo_add_child(gl_tls_group)
        
        child_id = gl_tls_group.glo_get_properties_id()

        self.glo_link_child_property(
            "symmetry", child_id, "symmetry")        

        self.glo_link_child_property(
            "main_chain_visible", child_id, "main_chain_visible")
        self.glo_link_child_property(
            "oatm_visible", child_id, "oatm_visible")
        self.glo_link_child_property(
            "side_chain_visible", child_id, "side_chain_visible") 
        self.glo_link_child_property(
            "hetatm_visible", child_id, "hetatm_visible") 
        self.glo_link_child_property(
            "water_visible", child_id, "water_visible")        
        self.glo_link_child_property(
            "hydrogen_visible", child_id, "hydrogen_visible") 

        self.glo_link_child_property(
            "fan_visible", child_id, "fan_visible")
        self.glo_link_child_property(
            "fan_opacity", child_id, "fan_opacity")
        self.glo_link_child_property(
            "TLS_visible", child_id, "TLS_visible")

        self.glo_link_child_property(
            "U", child_id, "U")
        self.glo_link_child_property(
            "ellipse", child_id, "ellipse")
        self.glo_link_child_property(
            "rms", child_id, "rms")

        self.glo_link_child_property(
            "axes_rT", child_id, "axes_rT")
        self.glo_link_child_property(
            "ellipse_rT", child_id, "ellipse_rT")
        self.glo_link_child_property(
            "rms_rT", child_id, "rms_rT")

        self.glo_link_child_property(
            "L1_visible", child_id, "L1_visible")
        self.glo_link_child_property(
            "L2_visible", child_id, "L2_visible")
        self.glo_link_child_property(
            "L3_visible", child_id, "L3_visible")
        self.glo_link_child_property(
            "add_biso", child_id, "add_biso")
        self.glo_link_child_property(
            "both_phases", child_id, "both_phases")
        self.glo_link_child_property(
            "adp_prob", child_id, "adp_prob")
        self.glo_link_child_property(
            "L_axis_scale", child_id, "L_axis_scale")
        self.glo_link_child_property(
            "L_axis_radius", child_id, "L_axis_radius")
        self.glo_link_child_property(
            "ellipse_opacity", child_id, "ellipse_opacity")
        self.glo_link_child_property(
            "rms_opacity", child_id, "rms_opacity")
        self.glo_link_child_property(
            "surface_opacity", child_id, "surface_opacity")

        ## update coloring
        if self.properties["color_method"]=="Color By Goodness of Fit":
            show_frac = float(self.properties["show_frac"] / 100.0)
            self.color_by_gof(show_frac)
        else:
            self.color_by_group()


## <testing>
def test_module():
    print "==============================================="
    print "TEST CASE 1: TLS Class"
    print

    tls = TLSGroup()
    tls.name = "All protein"
    tls.set_origin(18.885, 49.302, 13.315)
    tls.set_T(0.0263, 0.0561, 0.0048, -0.0128, 0.0065, -0.0157)
    tls.set_L(0.9730, 5.1496, 0.8488,  0.2151,-0.1296,  0.0815)
    tls.set_S(0.0007, 0.0281, 0.0336, -0.0446,-0.2288, -0.0551,
              0.0487, 0.0163)

    print tls

    print "eigenvalues(T)"
    print linalg.eigenvalues(tls.T)
    print "eigenvalues(L)"
    print linalg.eigenvalues(tls.L)

    print "==============================================="

    print 

##     print "==============================================="
##     print "TEST CASE 2: TLS/REFMAC file loading"

##     import sys

##     fil = open(sys.argv[1], "r")
##     tls_list = LoadTLSGroups(fil)
    
##     for tls in tls_list:
##         print "----- TLS Group #%d ---" % (tls_list.index(tls))
##         print tls

##         print "eigenvalues(T)"
##         print linalg.eigenvalues(tls.T)
##         print "eigenvalues(L)"
##         print linalg.eigenvalues(tls.L)

##         print "-----------------------"

##     print "==============================================="
    
if __name__ == "__main__":
    test_module()
    
## </testing>
