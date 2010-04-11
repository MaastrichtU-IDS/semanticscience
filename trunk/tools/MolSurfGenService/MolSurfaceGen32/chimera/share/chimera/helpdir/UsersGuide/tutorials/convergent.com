#
#  commands for Chimera image tutorial: Similar Binding Sites
#   (additional stuff must still be done interactively)
#   commands are for Chimera version 1.4 or newer
#
windowsize 831 544
open 1exp
open 1cel
delete :.b
preset apply int 1
~disp 
color gold #0
color cyan #1
set bg_color white
alias site1 #0:84,126,233,171,205
alias site2 #1:367,141,217,145,228
alias both site1 | site2
disp both
match iterate 2.0 site2 site1
focus both
color byhet
set subdivision 10
colordef tgold 1 .843 0 .2
colordef tcyan 0 1 1 .15
color tgold,r #0
color tcyan,r #1
#  the following requires a previously created ribbon style named slim
ribscale slim
