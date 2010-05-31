SRC1=qdiff4v.F objvertices.F distobj.F
#
SRC2=elb.f up.f cent4.f rent4.f \
 phintp4.f scaler4.f setbc4.f conplt.f itit4j.f \
 wrteps4b.f relfac4b.f react2.f clb.f setcrg.f setfcrg.f nitit.f \
 anagrd4.f cputime.f setrc4d.f  rdiv.f chkcrg.f expand4.f \
 anasurf.f rdlog4.f wrt4.f wrtprm.f  off4.f extrm.f wrtatd.f \
 distrTOpoint.f wrtvisual.f extrmobjects.f\
 nlener.f timef.f \
 grdatm.f crgarr.f dbsfd.f  mkdbsf.f phicon.f wrtphi.f wrtsit4.f \
 encalc4.f wrtgcrg.f  namlen3.f watput.f qinttot.f cfind4.f rfind4.f \
 rdhrad.f  radass4.f crgass4.f ichash4.f irhash4.f rdhcrg.f \
 form2.f  getatm2.f watpte.f omalt.f rforce.f  ts.f setout.f epsmak.f
#
SRC3=vwtms2.f scale.f indver.f sas.f  cube.f  msrf.f \
     mkvtl.f ex.f fxhl.f wrtsurf.f
#
SRC4=memalloc.c  creapdb.c
#----------------------------------------------------
OBJ1=$(SRC1:.F=.o)
OBJ2=$(SRC2:.f=.o)
OBJ3=$(SRC3:.f=.o)
OBJ4=$(SRC4:.c=.o)
#----------------------------------------------------
.F.o:
	$(FC) $(RECFLAGS) -c  $(VPATH)/$*.F
.f.o:
	$(FC) $(FLAGS) -c  $(VPATH)/$*.f
.c.o:
	$(CC) $(CFLAGS) -c  $(VPATH)/$*.c
#----------------------------------------------------
delphi:$(OBJ1) $(OBJ2) $(OBJ3) $(OBJ4) $(SRC1) $(SRC2) $(SRC3) $(SRC4)
	$(FC) $(LFLAGS) -o $@ $(OBJ1) $(OBJ2) $(OBJ3) $(OBJ4)
#----------------------------------------------------
$(OBJ1) : $(VPATH)/qdiffpar5.h $(VPATH)/qlog.h $(VPATH)/pointer.h
$(OBJ2) : $(VPATH)/qdiffpar5.h $(VPATH)/qlog.h $(VPATH)/pointer.h
$(OBJ3) : $(VPATH)/acc2.h $(VPATH)/pointer.h
#----------------------------------------------------
