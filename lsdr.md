The Life Science Dataset Registry implements the [Semantic Entity Resolution Vocabulary  (SERV)](http://code.google.com/p/semanticscience/wiki/serv) to create a life-science oriented linked data network of namespaces, datasets, resolvers and their publishers. This registry is used by the [Semantic Entity Discovery Service (SEDS)](http://code.google.com/p/semanticscience/wiki/seds) to generate links to documents for a requested entity.

sources:

  * NAR
    * http://www.oxfordjournals.org/nar/database/summary/*  (`*` = database number)
    * NARID, Title, Email, Description, Category, Subcategory, Homepage

  * Pathguide
    * http://www.pathguide.org/fullrecord.php?DBID=*  (`*` = database number)
    * PGID, Abbrv, Title, URL, Description, DataSource Availability, PMID, datatype, tooltype

  * Uniprot
    * http://www.uniprot.org/docs/dbxref.txt
    * UID Abbr, Title, References, links, Server, docURL, note, category

  * GO
    * http://www.geneontology.org/doc/GO.xrf_abbs
    * Abbrv, Title, URL, URL syntax, Description, Object, ID example, URL example, Synonym

new relations:


namespace merging:


SPARQL endpoint: http://semanticscience.org/serv/sparql