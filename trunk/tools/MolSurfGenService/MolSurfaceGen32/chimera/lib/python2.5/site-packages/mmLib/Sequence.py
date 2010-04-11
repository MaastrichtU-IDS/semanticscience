## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.

import Library

class Sequence(object):
    """Sequence information for a biopolymer chain.
    """
    def __init__(self):
        self.sequence_list = list()

    def __len__(self):
        return len(self.sequence_list)

    def __getitem__(self, index):
        return self.sequence_list[index]
    
    def set_from_three_letter(self, sequence_list):
        self.sequence_list = list(sequence_list)

    def set_from_fragments(self, fragments):
        self.sequence_list = [frag.res_name for frag in fragments]

    def __iter__(self):
        return iter(self.sequence_list)

    def iter_three_letter(self):
        return iter(self)
    
    def one_letter_code(self):
        """Return the one letter code representation of the sequence as a string.
        """
        seqlist = list()
        for threeletter in self.sequence_list:
            mdesc = Library.library_get_monomer_desc(threeletter)
            if mdesc is not None and mdesc.one_letter_code:
                seqlist.append(mdesc.one_letter_code)
            else:
                seqlist.append("X")
        return "".join(seqlist)
