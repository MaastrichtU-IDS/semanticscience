#                                                           ECMeng 11/20/2006
#  Chimera command script showing 
#  growth hormone/GHR interactions as probed by combinatorial scanning
#  Pal et al. J Biol Chem 281(31):22378-85.   
#
#  input files: 3hhr (fetched from PDB), 3hhr-scan.txt (attribute definitions)
#
#  Movie-recording commands commented out with ##
#  Recording a movie will slow replay of the script, but this will not
#  affect the replay rate of the resulting movie file.
#
windowsize 720 480; wait
2dlabels create title text 'hGH-Receptor Complex (3hhr)' color khaki size 28 xpos .2 ypos .94 visibility show; 2dlabels create credit text 'Combinatorial scanning: \nPal et al. J Biol Chem 281(31):22378 (2006).' color khaki size 18 xpos .01 ypos .05 visibility show; wait 
##movie record
# post-2006 I added scale 0.5776 below because the default scale is now larger
open 3hhr; ~disp; ribbon; ribrepr smooth; wait; rain chain; wait; turn x 90; wait; turn z 65; wait; move x -6; thickness -10; wait; scale 0.5776; wait
scale 1.01 50; wait; savepos pos1
defattr 3hhr-scan.txt raise false
colordef gray1 0.7 0.7 0.7; colordef gray2 0.2 0.2 0.2
# lower values, higher conservation for Ab binding (proxy for folding)
rangecol antibodyBinding,r min white mid gray1 max gray2; wait
2dlab create akey1 text 'conservation for \nfolding:' color gray size 22 xpos .69 ypos .37 visibility show; 2dlab create akey2 text 'low' color dim gray size 20 xpos .71 ypos .27 visibility show; 2dlab create akey3 text 'mid' color gray1 size 20 xpos .71 ypos .23 visibility show; 2dlab create akey4 text 'high' color white size 20 xpos .71 ypos .19 visibility show; wait
turn y -1 65; wait
wait 4
turn y 1 80; wait
wait 4
turn y -1 15; wait
wait 20
2d delete akey1; 2d delete akey2; 2d delete akey3; 2d delete akey4; wait
wait 10
alias bindca @ca & :/receptorBinding>0
rep sphere bindca; vdwdefine 0.8 @ca; ribbackbone
# higher scoreDiff, more important for binding receptor relative to folding
col blue,r :.a; disp bindca; rangecol scoreDiff,a 0 purple 4.5 red 9 yellow; wait
2dlab create rkey1 text 'conservation for \nbinding > folding:' color gray size 22 xpos .69 ypos .37 visibility show; 2dlab create rkey2 text 'low' color purple size 20 xpos .71 ypos .27 visibility show; 2dlab create rkey3 text 'mid' color red size 20 xpos .71 ypos .23 visibility show; 2dlab create rkey4 text 'high' color yellow size 20 xpos .71 ypos .19 visibility show; wait
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca
vdwdef +0.05 @ca; wait
wait 20
turn y -1 65; wait
wait 4
turn y 1 80; wait
wait 4
turn y -1 15; wait
wait 30
2d delete rkey1; 2d delete rkey2; 2d delete rkey3; 2d delete rkey4; wait
~ribbon :.b-c; turn x -0.8 90; turn y -0.8 90; turn z 0.2 90; scale 1.008 60; move y -0.33 60; move x -0.05 60; wait; savepos pos2
wait 20
alias intera :/scoreDiff>2
alias interb :/scoreDiff>2 zr<4 & :.b 
alias both intera | interb
~ribbackbone; ribbon :43-44.b,104-108.b,120-127.b,164-170.b; ~disp :/scoreDiff<2; rep stick both; color byhet,a both; disp both; ~disp :76-77.b,218.b; wait
sel intera; hb color white line 2 selRestrict cross; ~sel; wait
turn x -1 40; move y -0.15 40; sc 1.018 40; wait; savepos pos3
wait 120
~hb; wait
reset pos2 100; wait
surfcat gh :.a; surf gh; rangecol scoreDiff,s 0 purple 4.5 red 9 yellow; surftrans 40; wait
wait 80
~disp both; ribbon :.b-c; reset pos1 100; wait
wait 80
turn y -1 75; wait
wait 4
turn y 1 75; wait
wait 40
##movie stop
##movie encode mformat mov bitrate 5000 output /home/spin/meng/3hhr-scan.mov
