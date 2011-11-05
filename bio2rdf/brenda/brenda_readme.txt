http://www.brenda-enzymes.info/brenda_download/readme.txt

GENERAL INFORMATION
Due to an infrastructure grant from the European Union (project
FELICS) the contents of BRENDA can now be made available for free
download. The information is in form of a text file the structure
of which is similar but not identical to the Swissprot/Trembl/Uniprot text file format so that parsers written
for that file could be easily modified. Information on the
structure of the file is given at the end of this README.

LICENSE
The full BRENDA contents are copyright-protected. For details see
the file LICENCE. The following simple rules apply:

-	Internal use of the BRENDA information is free provided that
	the copyright information is not removed. The BRENDA contents
	can be fully or partially included in internal information
systems.
-	Publications originating from the use of BRENDA material
	should include citations of the relevant publications (see
	below).
-	The use of a part of the BRENDA material for redistribution
	for example in special organism--specific or other databases
	requires a separate license agreement with the copyright
	owner (please contact Prof. Dr. Dietmar Schomburg).

PUBLICATIONS
Chang A., Scheer M., Grote A., Schomburg I., Schomburg D. (2009). 
BRENDA, AMENDA and FRENDA the enzyme information system: new content and tools in 2009.
Nucleic Acids Res, 37, D588-D592.

Barthelmes J., Ebeling C., Chang A., Schomburg I., Schomburg D. 
BRENDA, AMENDA and FRENDA: the enzyme information system in 2007.
Nucleic Acids Res, 35, D511-D514.

Schomburg, I., Chang, A., Ebeling, C., Gremse, M., Heldt, C., Huhn, G. & Schomburg, D. (2004). 
BRENDA, the enzyme database: updates and major new developments.
Nucleic Acids Res, 32, D431-D433.

Schomburg, I., Chang, A. & Schomburg, D. (2002). 
BRENDA, enzyme data and metabolic information. 
Nucleic Acids Res, 30, 47-49.

Schomburg, I., Chang, A., Hofmann, O., Ebeling, C., Ehrentreich, F. & Schomburg, D. (2002). 
BRENDA: a resource for enzyme data and metabolic information. Trends Biochem Sci, 27, 54-56.


INFORMATION ON CONTENTS
The file is organised in an EC-number specific format. The
information on each EC-number is given in a very short and compact
way in a part of the file. The contents of each line are described
by a two/three letter acronym at the beginning of the line and
start after a TAB. Empty spaces at the beginning of a line
indicate a continuation line.

The contents are organised in 40 information fields as given
below. Protein information is included in '#'...#', literature
citations are in '<...>', commentaries in '(...)' and field-
special information in '{...}'.

Protein information is given as the combination organism/Uniprot
accession number where available. When this information is not
given in the original paper only the organism is given.

///	indicates the end of an EC-number specific part. 
AC	activating compound
AP	application
CF	cofactor
CL	cloned
CR	crystallization
CR	CAS registry_number
EN	engineering
GS	general stability
ID	EC-class
IN	inhibitors
KI	ki-value	inhibitor in {...}
KM	KM-value	substrate in {...}
LO	Localization
ME	Metals/Ions
MW	molecular weight
NSP	natural substrates/products	reversibilty information in {...}
OS	oxygen stability
OSS	organic solvent stability
PHO	pH-optimum
PHR	pH-range
PHS	pH stability
PI	isoelectric point
PM	posttranslation modification
PR	protein
PU	purification
RE	reaction catalyzed
RF	references
RN	renatured
RN	accepted name (IUPAC) 
RT	reaction type
SA	specific activity
SN	synonyms
SP	substrates/products	reversibilty information in {...}
SS	storage stability
ST	source/tissue
SU	subunits
SY	systematic name 
TN	turnover number	substrate in {...}
TO	temperature optimum
TR	temperature range
TS	temperature stability

