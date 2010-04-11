## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Structural database based on mmCIF.
"""
from __future__ import generators
import copy

import mmCIF


class mmCIFDB(mmCIF.mmCIFData):
    """Database class for the storage and access of structural data.  This
    database is organized according to mmCIF data tags.  Methods to lookup
    common structure items are included.
    """
    def __str__(self):
        col_len = 12
        dump = ""

        for table in self:
            table.autoset_columns()
            dump += "Table: %s\n" % (table.name)
            for col_name in table.columns:
                dump += col_name[:col_len-1].ljust(col_len)
            dump += "\n"
            dump += "-"*col_len*len(table.columns) + "\n"
            for row in table:
                for col_name in table.columns:
                    try:
                        dump += str(row[col_name])[:col_len-1].ljust(col_len)
                    except KeyError:
                        dump += " "*col_len
                dump += "\n"
            dump += "\n"

        return dump

    def add_table(self, table):
        self.append(copy.deepcopy(table))
    
    def add_tables(self, tables):
        for table in tables:
            self.append(copy.deepcopy(table))

    def confirm_table(self, table_name):
        """Return table table_name, create the table if necessary.
        """
        if not self.has_key(table_name):
            table = mmCIF.mmCIFTable(table_name)
            self.append(table)
        else:
            table = self[table_name]
        return table

    def get_single(self, table_name, col_name):
        """Utility function for getting a table where there should only
        be a single row of data.
        """
        try:
            return self[table_name][col_name]
        except KeyError:
            return None

    def set_single(self, table_name, col_name, val):
        """Utility function for setting a table where there should only be
        a single row of data.
        """
        if val == None:
            return
        
        table = self.confirm_table(table_name)
        if len(table):
            table[0][col_name] = val
        else:
            row = mmCIF.mmCIFRow()
            table.append(row)
            row[col_name] = val

    def get_entry_id(self):
        """Methods to get/set the structure ID.
        """
        return self.get_single("entry", "id")

    def set_entry_id(self, idcode):
        self.set_single("entry", "id", idcode)
            
    def get_deposition_date(self):
        """Return the origional depositoin date as stored in
        _database_pdb_ref.date_original.
        """
        return self.get_single("database_pdb_rev", "date_original")

    def set_deposition_date(self, date):
        self.set_single("database_pdb_rev", "date_original")

    def get_struct_keywords(self):
        """Return structure keywords as stored in
        _struct_keywords.text
        """
        return self.get_single("struct_keywords", "text")
    def set_struct_keywords(self, text):
        self.set_single("struct_keywords", "text", text)
        
    def get_struct_keywords(self):
        """Return structure keywords as stored in
        _struct_keywords.text
        """
        return self.get_single("struct_keywords", "text")
    def set_struct_keywords(self, text):
        self.set_single("struct_keywords", "text", text)

    

##     ## generic data
##     set_ims("database_pdb_rev", "date_original", info_map, "date")
##         set_ims("struct_keywords", "text", info_map, "keywords")
##         set_ims("struct_keywords", "pdbx_keywords", info_map, "pdbx_keywords")
##         set_ims("struct", "title", info_map, "title")
        
##         ## X-ray experimental data
##         set_imf("refine", "ls_R_factor_R_work", info_map, "R_fact")
##         set_imf("refine", "ls_R_factor_R_free", info_map, "free_R_fact")
##         set_imf("refine", "ls_d_res_high", info_map, "res_high")
##         set_imf("refine", "ls_d_res_low", info_map, "res_low")
