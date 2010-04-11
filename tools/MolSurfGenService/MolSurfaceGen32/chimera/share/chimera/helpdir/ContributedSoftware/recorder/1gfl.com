#
#  Chimera command script showing green fluorescent protein (PDB 1gfl)
#
#  input file: 1gfl (fetched from PDB)
#
#  Movie-making commands commented out with ##
#  Recording a movie will slow replay of the script, but this will not
#  affect the replay rate of the resulting movie file.
#
2dlabels create lab1 text 'Green Fluorescent Protein' color light sea green size 26 xpos .03  ypos .92 visibility show
open noprefs 1gfl; del ~ :.a; window; linewidth 3; rainbow; wait
##movie record
wait 50
chain @n,ca,c,o; wait 1
wait 50
~disp; ribbon
2dlabels change lab1 visibility hide frames 90; wait
2dlabels delete lab1
roll y 1 180; wait
ribrepr edged
roll y 1 180; wait
ribrepr smooth
roll y 1 80; wait
ribbackbone; repr sphere :1.a,230.a@ca; color white,a :1.a,230.a@ca; disp :1.a,230.a@ca
roll y 1 90; wait
scale 1.015 20; wait
disp :65-67.a; color byatom :65-67.a; repr cpk :65-67.a; wait 1
clip hither -1 20; wait
wait 100
clip hither 1 20; wait 
scale 0.98 10; wait
disp :99.a,153.a,163.a,167.a,202.a,203.a,222.a;repr bs :99.a,153.a,163.a,167.a,202.a,203.a,222.a; ribrepr flat
wait 25
roll y 1 180; wait
##movie stop
##movie encode mformat mov output /MyPath/mymovie.mov
