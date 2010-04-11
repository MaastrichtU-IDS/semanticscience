# awk script to
# convert Charmm parameter file into Xplor format.
# Simple version; works for Amber force field (no Urey-Bradleys, etc).
# Fairly general, but some manual post-editing needed.
#
#  Tom Simonson, July 2000.
#
BEGIN {parse = ""}    # will be toggled by BOND , ANGL, etc lines
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
# process BONDS
if ($1 ~ /BOND/) {parse = "BOND"; done = 1}
if (parse == "BOND" && length($0) > 1 && $1 !~ /!/ && done == 0) {
print "BOND  ", $0 
done = 1 }
#
#
# process ANGLes
if ($1 ~ /THET/) {parse = "ANGL"; done = 1}
if (parse == "ANGL" && length($0) > 1 && $1 !~ /!/ && done == 0) {
print "ANGLE  ", $0 
done = 1 }
#
#
# process DIHEdrals
if ($1 ~ /PHI/) {parse = "DIHE"; done = 1}
if (parse == "DIHE" && length($0) > 1 && $1 !~ /!/ && done == 0) {
print "DIHEDRAL  ", $0 
done = 1 }
#
#
# process IMPRopers
if ($1 ~ /IMPHI/) {parse = "IMPR"; done = 1}
if (parse == "IMPR" && length($0) > 1 && $1 !~ /!/ && done == 0) {
print "IMPROPER  ", $0 
done = 1 }
#
#
# process nonbonded
if ($1 ~ /NONB/) {parse = "NONB"; done = 1}
if (parse == "NONB" && length($0) > 1 && $1 !~ /!/ && done == 0) {
printf("NONBonded  %-4s  %10.6f   %10.6f  %10.6f  %10.6f %-s\n", $1, -$3, $4*1.781797, -$6, $7*1.781797, substr($0,57))
done = 1 }
#
#
# process all other lines
if (done <= 0) {print $0}
}



