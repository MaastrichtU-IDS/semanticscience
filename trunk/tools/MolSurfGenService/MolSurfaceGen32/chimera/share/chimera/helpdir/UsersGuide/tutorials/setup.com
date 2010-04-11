open receptor.pdb
open GCP.pdb
preset apply interactive 1
color aquamarine #1
disp #1 & #0 z<5 
color orange,a #1@o=
color medium blue,a #1@n=
color magenta #2
repr bs #2
