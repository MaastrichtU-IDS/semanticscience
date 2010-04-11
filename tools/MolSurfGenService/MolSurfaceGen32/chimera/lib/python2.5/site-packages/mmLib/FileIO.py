## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Load and save mmLib.Structure objects from/to mmLib supported formats.
The mmCIF and PDB file formats are currently supported.
"""
import os
import types
import popen2

from mmCIF        import mmCIFFile
from mmCIFBuilder import mmCIFStructureBuilder, mmCIFFileBuilder
from PDB          import PDBFile
from PDBBuilder   import PDBStructureBuilder, PDBFileBuilder
from CIFBuilder   import CIFStructureBuilder


class FileIOUnsupportedFormat(Exception):
    pass


class ZCat(object):
    def __init__(self, path):
        self.path = path
    def __iter__(self):
        zcat = popen2.Popen3("/bin/zcat %s" % (self.path))
        for ln in iter(zcat.fromchild):
            yield ln
        zcat.wait()
    def readlines(self):
        return iter(self)


def OpenFile(path, mode):
    """Right now this only supports opening GZip'ed files, in the future
    it might be extended for URLs.
    """
    ## if path is not a string, assume it is a file object and
    ## return it
    
    if isinstance(path, str):
        base, ext = os.path.splitext(path)
        if ext == ".gz":
            import gzip
            return gzip.open(path, mode)
        elif ext == ".Z" and mode == "r":
            return ZCat(path)
        return open(path, mode)

    return path


def get_file_extension(path, default_extension = "PDB"):
    """Returns the 3-letter extension of the filename.
    """
    if not isinstance(path, str):
        return default_extension
    
    ## check/remove compressed file extention
    base, ext = os.path.splitext(path)
    if ext.lower() in ('.z', '.gz', '.bz2'):
        path = base

    base, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext == ".cif":
        return "CIF"
    elif ext == ".pdb":
        return "PDB"

    return default_extension

def get_file_arg(args):
    try:
        fil = args["fil"]
    except KeyError:
        try:
            fil = args["file"]
        except KeyError:
            raise TypeError,"LoadStructure(file=) argument required"

    return fil


def open_fileobj(fil, file_mode):
    if isinstance(fil, str):
        fileobj = OpenFile(fil, file_mode)
    else:
        fileobj = fil
    return fileobj


def LoadStructure(**args):
    """Loads a mmCIF file(.cif) or PDB file(.pdb) into a 
    Structure class and returns it.  The function takes 5 named arguments,
    one is required:

    file = <file object or path; required>
    format = <'PDB'|'CIF'; defaults to 'PDB'>
    structure = <mmLib.Structure object to build on; defaults to createing new>
    sequence_from_structure = [True|False] <infer sequence from structure file, default False>
    library_bonds = [True|False] <build bonds from monomer library, default False>
    distance_bonds = [True|False] <build bonds from covalent distance calculations, default False>
    """
    fil = get_file_arg(args)
    
    if not args.has_key("format"):
        args["format"] = get_file_extension(fil)
    else:
        args["format"] = args["format"].upper()
    
    args["fil"] = open_fileobj(fil, "r")

    if args["format"] == "PDB":
        return PDBStructureBuilder(**args).struct
    elif args["format"] == "CIF":
        from mmCIF import mmCIFSyntaxError
        try:
            return mmCIFStructureBuilder(**args).struct
        except mmCIFSyntaxError:
            args["fil"].seek(0)
            return CIFStructureBuilder(**args).struct

    raise FileIOUnsupportedFormat("Unsupported file format %s" % (str(fil)))


def SaveStructure(**args):
    """Saves a Structure object into a supported file type.
    file = <file object or path; required>
    structure = <mmLib.Structure object to save; required>
    format = <'PDB' or 'CIF'; defaults to 'PDB'>
    """
    fil = get_file_arg(args)
    
    if not args.has_key("format"):
        args["format"] = get_file_extension(fil)
    else:
        args["format"] = args["format"].upper()
    
    fileobj = open_fileobj(fil, "w")
    
    try:
        struct = args["struct"]
    except KeyError:
        try:
            struct = args["structure"]
        except KeyError:
            raise TypeError,"LoadStructure(structure=) argument required"

    if args["format"] == "PDB":
        pdb_file = PDBFile()
        PDBFileBuilder(struct, pdb_file)
        pdb_file.save_file(fileobj)
        return

    elif args["format"] == "CIF":
        cif_file = mmCIFFile()
        mmCIFFileBuilder(struct, cif_file)
        cif_file.save_file(fileobj)
        return

    raise FileIOUnsupportedFormat("Unsupported file format %s" % (str(fil)))


### <TESTING>
def test_module():
    import sys
    struct = LoadStructure(fil = sys.argv[1])
    SaveStructure(fil=sys.stdout, struct=struct)

if __name__ == "__main__":
    test_module()
### </TESTING>
