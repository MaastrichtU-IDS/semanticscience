For more information please visit http://semanticscience.org/projects/rkb/

# Introduction #

The RNA knowledge base (RKB) captures RNA structure-based knowledge using RDF/OWL Semantic Web technologies. RKB consists of an RNA ontology with basic terminology for nucleic acid composition along with context/model-specific representation of structural features such as sugar conformations, base pairings and base stackings. RKB is populated with both DNA and RNA structures form the [PDB](http://www.rcsb.org/pdb/) and [MC-Annotate](http://www-lbit.iro.umontreal.ca/mcannotate-simple/) structural annotation.


## Exploring the RKB ##

  1. To enable the viewing of the ontology we recommend the usage of Protege 4, which can be downloaded from [here](http://protege.stanford.edu/download/protege/4.0/installanywhere/). Choose the appropriate platform, download and install.
  1. Launch Protege 4 and load the RKB. On the welcome screen select "Open OWL ontology from URI" and copy into the URI text-box the following URI: http://semanticscience.googlecode.com/svn/tags/RKB-0.2/rna-with-individuals.owl which contains all models from [PDBID:1AM0](http://www.rcsb.org/pdb/explore/explore.do?structureId=1AM0). If you prefer to load the ontology with no individuals simply use the following URI: http://semanticscience.googlecode.com/svn/tags/RKB-0.2/rna.owl
  1. Once the ontology has loaded, you may want to change the way that class names are rendered. To do so in Protege simply go to File->Preferences and in the Renderer tab select "Render entities using annotation values", then click on the "Annotations..." button to specify which annotations to use for class names then select the "Add annotations" button and select the IAO\_0000111, click "Ok". Now the classnames should be displayed by the value contained in the IAO label.
  1. Turn on the reasoner by clicking on "Reasoner->FaCT++". Depending on your computer this may take some time, so be patient.
  1. Now you can test some of the following sample queries by simply typing them in the DL-Query tab:
    * 'nucleotide base pair'
    * nucleotide base pair' that 'has part' some (('hoogsteen edge' or 'part of' some 'hoogsteen edge') and externally\_connected\_to some ('nucleotide edge' or 'part of' some 'nucleotide edge')
    * 'nucleotide base pair' that 'has part' some (('hoogsteen edge' or 'part of' some 'hoogsteen edge') and 'part of' some 'GMP residue `[chebi:50324]`' and externally\_connected\_to some('nucleotide edge' or 'part of' some 'nucleotide edge'))
    * 'nucleotide base pair' that 'has part' some (('hoogsteen edge' or 'part of' some 'hoogsteen edge') and 'part of' some 'GMP residue `[chebi:50324]`' and externally\_connected\_to some('nucleotide edge' or 'part of' some 'nucleotide edge'))
    * 'nucleotide  base  pair'    that  'has  part'  some  (('hoogsteen  edge'  or  'part  of'  some  'hoogsteen edge') and externally\_connected\_to some ('nucleotide edge' or 'part of' some 'nucleotide edge')) and  inv('is  about') some ('structure model'  that  'is  represented  by'  some{'Molecular  Structure File PDB:1am0'})
    * 'structure model' that 'is represented by' some {'Molecular Structure File PDB:1am0'}




> Be sure to select the "Individuals" check box on the Query results pane in order to view the set of instances that satisfy these queries.