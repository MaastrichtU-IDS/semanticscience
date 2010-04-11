# awk script to
# convert Charmm topology file into Xplor format.
# Simple version; works for Amber force field (no Urey-Bradleys, etc).
# Fairly general, but some manual post-editing needed.
# Main problems:
# 1) Multiple dihedrals have to be declared in Xplor topology;
# first identify these in parameter file, then add manually.
# 2) Charmm patches don't know if atom is modified or added:
# appropriate MODIFY ATOMs have to be changed manually to ADD ATOMs.
# This mainly concerns terminal HT's and OT's.
# 3) Xplor patches don't have autogenerate angles, dihedrals.
# Therefore Amber/Charmm patches need to be supplemented by 
# patches in patches.pro: NTER, CTER, PROP, etc.
# 4) Nucleic acids not really tested so far.
#
#  Tom Simonson, July 2000.
#
BEGIN {pres = 0; prev = 0}    # will be toggled by RESI or PRES lines
#
{
#
done = 0
#
#
# process header (first six lines)
if (NR <= 6) { print "REMARKS ", $0 ; done = 1}
#
#
# process AUTOGENERATE line
if ($1 ~ /AUTOG/) {print "AUTOGENERATE  ANGLES=TRUE  DIHEDRALS=TRUE  END"
 done = 1 }
#
#
# leave out DEFAULT, DECL lines
if ($1 ~ /DEFAULT/ || $1 ~ /DECL/) {done = 1}
#
#
# process MASS lines
if ($1 ~ /MASS/)  {
printf("MASS  %-4s  %6.2f ! %s\n", $3, $4, substr($0,22))
    done = 1            }
#
#
# process RESIdue lines
if ($1 ~ /RESI/) {
pres = 0
# first add END line corresponding to previous residue (this is a hack)
# only do this if there is a previous residue
if (prev >= 1) {
print "END"
print "!-------------------------------------------------------------"
print ""
}
prev = 1
printf("%-s  %-s  ! %s\n", $1, $2, substr($0,10))
done = 1     }
#
#
# process PRESidue lines
if ($1 ~ /PRES/) {
pres = 1
# first add END line coorresponding to previous residue (this is a hack)
# only do this if there is a previous residue
if (prev >= 1) {
print "END"
print "!-------------------------------------------------------------"
print ""
}
prev = 1
printf("%-s  %-s  ! %s\n", $1, $2, substr($0,10))
done = 1     }
#
#
# process ATOM lines         # have to distinguish RESI from PRESI
if ($1 ~ /ATOM/)  {
if (pres == 1) {
printf("MODIFY ATOM  %-4s  TYPE= %-4s  CHARge= %7.4f   END  ! %s\n", $2, $3, $4, substr($0,25)) }
else {
printf("ATOM  %-4s  TYPE= %-4s  CHARge= %7.4f   END   ! %s\n", $2, $3, $4, substr($0,25)) }
done = 1          }
#
# process DELETE ATOM lines        
if ($2 ~ /ATOM/ && $1 ~ /DELE/)  {
printf("DELETE ATOM  %-4s  END ! %s\n", $3, substr($0,25))
done = 1          }
#
#
# process BOND lines         # have to distinguish RESI from PRESI
if ($1 ~ /BOND/) {
nbonds = (NF -1)/2
i = 1; ii=2; split($0,bonds)
while (i <= nbonds) {
     if (pres == 1) { printf("ADD BOND  %-4s  %-4s \n", bonds[ii], bonds[ii+1]) }
     else if (bonds[ii] !~ /-/ && bonds[ii] !~ /+/ && bonds[ii+1] !~ /-/ && bonds[ii+1] !~ /+/) {
          printf("BOND  %-4s  %-4s \n", bonds[ii], bonds[ii+1]) }
      ii = ii + 2 ; i++ 
                    }
     done = 1       }
#
#
# process IMPRoper lines       # have to distinguish RESI from PRES
if ($1 ~ /IMPR/) {
     if (pres == 1) {print "ADD ", $0}
     else if ($0 !~ /-/ && $0 !~ /+/) {print $0}
      done = 1   }
#
#
# process THET/ANGL lines         # have to distinguish RESI from PRESI
if ($1 ~ /THET/) {
nbonds = (NF -1)/3
i = 1; ii=2; split($0,bonds)
while (i <= nbonds) {
     if (pres == 1) { printf("ADD ANGL  %-4s  %-4s %-4s \n", bonds[ii], bonds[ii+1], bonds[ii+2]) }
     else if ($0 !~ /-/ && $0 !~ /+/) {
          printf("ANGL  %-4s  %-4s %-4s \n", bonds[ii], bonds[ii+1], bonds[ii+2]) }
      ii = ii + 3 ; i++ 
                    }
     done = 1       }
#
#
# process DIHE lines         # have to distinguish RESI from PRESI
if ($1 ~ /THET/) {
nbonds = (NF -1)/4
i = 1; ii=2; split($0,bonds)
while (i <= nbonds) {
     if (pres == 1) { printf("ADD DIHE  %-4s  %-4s %-4s %-4s\n", bonds[ii], bonds[ii+1], bonds[ii+2], bonds[ii+3]) }
     else if ($0 !~ /-/ && $0 !~ /+/) {
          printf("DIHE  %-4s  %-4s %-4s %-4s\n", bonds[ii], bonds[ii+1], bonds[ii+2], bonds[ii+3]) }
      ii = ii + 4 ; i++ 
                    }
     done = 1       }
#
#
# process DONOR, ACCEPTOR, IC lines         # have to distinguish RESI from PRESI
if ($1 ~ /DONO/ || $1 ~ /ACCE/ || $1 ~ /IC/)  {
if (pres == 1) {
print "ADD ", $0 }
else {
print $0 }
done = 1          }
#     
#
# process PATCH lines
if ($1 ~ /PATCH/) {
print "!!!", $0  
 done = 1  }
#
#
# process all other lines
if (done <= 0) {print $0}
}



