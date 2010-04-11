clearVariables
logFile ff03ua.log
#
#	leap .cmd script for building the residue
#	libraries for the 2003 Yang et al. united-atom protein force field.
#
################################################
################################################
################################################
################################################
######
######    AMBER 2003ua prep.in files
######
################################################
################################################
################################################
################################################
#---------------------------------------------------
#
#
#       UNITED ATOM FORCE FIELD
#
#
#
# Extract the amino acids from uni_amino03.in
#
clearVariables

loadAmberPrep uni_amino03.in 

a = { 
      ALA GLY SER THR LEU ILE VAL ASN GLN ARG 
      HID HIE HIP TRP PHE TYR GLU ASP LYS PRO
      CYS MET
    }

set a       restype     protein
saveOff a   ./uni_amino03.lib 

set NME     restype     protein
set NME     tail        null
set NME     head        NME.1.N
set NME.1   connect0    NME.1.N
saveOff NME ./uni_amino03.lib 

set ACE     restype     protein
set ACE     head        null
set ACE     tail        ACE.1.C
set ACE.1   connect1    ACE.1.C
saveOff ACE ./uni_amino03.lib 

#
# Extract the N terminus residues
#
clearVariables

loadAmberPrep uni_aminont03.in

a = { 
      NALA NGLY NSER NTHR NLEU NILE NVAL NASN NGLN NARG 
      NHID NHIE NHIP NTRP NPHE NTYR NGLU NASP NLYS NPRO 
      NCYS NMET
    }

set a        head      null
set NALA.1   nend      null
set NGLY.1   nend      null
set NSER.1   nend      null
set NTHR.1   nend      null
set NLEU.1   nend      null
set NILE.1   nend      null
set NVAL.1   nend      null
set NASN.1   nend      null
set NGLN.1   nend      null
set NARG.1   nend      null
set NHID.1   nend      null
set NHIE.1   nend      null
set NHIP.1   nend      null
set NTRP.1   nend      null
set NPHE.1   nend      null
set NTYR.1   nend      null
set NGLU.1   nend      null
set NASP.1   nend      null
set NLYS.1   nend      null
set NPRO.1   nend      null
set NCYS.1   nend      null
set NMET.1   nend      null

set a        restype   protein
saveOff a ./uni_aminont03.lib 

#
# Extract the C terminus residues
#
clearVariables

loadAmberPrep uni_aminoct03.in

a = { 
      CALA CGLY CSER CTHR CLEU CILE CVAL CASN CGLN CARG 
      CHID CHIE CHIP CTRP CPHE CTYR CGLU CASP CLYS CPRO 
      CCYS CMET 
    }

set a        tail      null
set CALA.1   cend      null
set CGLY.1   cend      null
set CSER.1   cend      null
set CTHR.1   cend      null
set CLEU.1   cend      null
set CILE.1   cend      null
set CVAL.1   cend      null
set CASN.1   cend      null
set CGLN.1   cend      null
set CARG.1   cend      null
set CHID.1   cend      null
set CHIE.1   cend      null
set CHIP.1   cend      null
set CTRP.1   cend      null
set CPHE.1   cend      null
set CTYR.1   cend      null
set CGLU.1   cend      null
set CASP.1   cend      null
set CLYS.1   cend      null
set CPRO.1   cend      null
set CCYS.1   cend      null
set CMET.1   cend      null

set a        restype   protein
saveOff a ./uni_aminoct03.lib 

#
# DONE ff03ua
#
quit
