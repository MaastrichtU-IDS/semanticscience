c
c logical parameters used in qdiff, mainly from parameter file
c
	logical iautocon,iper(6),iconc,ibios,isite,iatout,diff,isph
	logical ipdbwrt,ifrcwrt,ifrcrd,ipoten,igraph,imem,ihome,icheb
	logical phiwrt,logs,logc,loga,logg,ipdbrd,logas,epswrt,iacent
	logical isen,isch,iacs,irea,ibufz,inrgwrt,iexun,iwgcrg,iuspec
	logical idbwrt,ixphiwt,iyphiwt,izphiwt,ixphird,iyphird,izphird
	logical isita,isitq,isitp,isitf,isitr,isitc,isitx,isiti,iself
	logical isitrf,isitcf,isitt,isolv,isrf,ibem
c b+++++++++++++++++++++++++++++++++++w Oct 2000
	logical lognl,logions,icreapdb,imanual,isitap,isitmd,isittf
c e++++++++++++++++++++++++++++++++++++++++++++

	character*80 epsnam,phinam,frcnam,mpdbnam,updbnam,ufrcnam
	character*80 srfnam
	character*80 centnam,siznam,crgnam,pdbnam,frcinam,phiinam
	character*80 prmnam,usernam,uhomenam,scrgnam,nrgnam,gcrgnam
	character*80 dbnam,xphonam,yphonam,zphonam,xphinam,yphinam,zphinam
	character*60 toplbl
c
	real scale,prbrad(2),exrad,perfil,repsout,repsin,gten,uspec
c b++++++++++++++++++++++++
        real rionst,conc(2),chi1,chi2,chi3,chi4,chi5,radpolext,relpar
        real res1,res2,res5,tol,ergestout,vdropx,vdropy,vdropz
        real atompotdist, temperature
        integer ival(2),ival2(2)
c e++++++++++++++++++++++++
	real offset(3),epsout,epsin,radprb(2),acent(3),epkt,fpi,deblen
	integer igrid,nlit,nnit,ibctyp,icon1,icon2,bufz(2,3)
	integer epslen,philen,srflen,frclen,mpdblen,updblen,ufrclen
	integer phifrm,epsfrm,frcfrm,mpdbfrm,updbfrm,ufrcfrm
	integer centlen,sizlen,crglen,pdblen,frcilen,phiilen
	integer centfrm,sizfrm,crgfrm,pdbfrm,frcifrm,phiifrm
	integer prmfrm,scrgfrm,scrglen,prmlen,userlen,uhomelen
	integer nrgfrm,nrglen,gcrglen,gcrgfrm,dblen,xphilen,yphilen
	integer zphilen,xphipos,yphipos,zphipos,xphopos,yphopos,zphopos
	integer xpholen,ypholen,zpholen,ngp,nhgp,nbgp
c
	common
     &  /log1/iautocon,iper,iconc,ibios,isite,iatout,diff,isph,
     &  ipdbwrt,ifrcwrt,ifrcrd,ipoten,igraph,imem,ihome,icheb,
     &  phiwrt,logs,logc,loga,logg,ipdbrd,logas,epswrt,iacent,
     &  isen,isch,iacs,irea,ibufz,inrgwrt,iexun,iwgcrg,iuspec,
     &  idbwrt,ixphiwt,iyphiwt,izphiwt,ixphird,iyphird,izphird,
     &  isita,isitq,isitp,isitf,isitr,isitc,isitx,isiti,iself,
     &  isitrf,isitcf,isitt,isolv,isrf,ibem,
     &  lognl,logions,icreapdb,imanual,isitap,isittf,isitmd
c
	common
     &  /val1/scale,prbrad,exrad,perfil,rionst,repsout,repsin,
     &  gten,offset,epsout,epsin,radprb,acent,epkt,fpi,deblen,uspec,
     &  conc,chi1,chi2,chi3,chi4,chi5,radpolext,relpar,res1,res2,tol,
     &  ergestout,res5,vdropx,vdropy,vdropz,atompotdist,temperature
c
	common
     &  /ival1/igrid,nnit,nlit,ibctyp,epslen,philen,srflen,frclen,
     &  mpdblen,updblen,ufrclen,centlen,sizlen,crglen,pdblen,
     &  frcilen,phiilen,sizfrm,crgfrm,pdbfrm,frcifrm,phiifrm,
     &  phifrm,epsfrm,frcfrm,mpdbfrm,updbfrm,ufrcfrm,prmfrm,
     &  prmlen,icon1,icon2,userlen,uhomelen,scrglen,scrgfrm,bufz,
     &  nrgfrm,nrglen,gcrglen,gcrgfrm,dblen,xphilen,yphilen,zphilen,
     &  xphipos,yphipos,zphipos,xphopos,yphopos,zphopos,
     &  xpholen,ypholen,zpholen,ngp,nhgp,nbgp,ival,ival2
c
     &  /icar1/epsnam,phinam,frcnam,mpdbnam,updbnam,ufrcnam,centnam,
     &  uhomenam,usernam,scrgnam,nrgnam,gcrgnam,dbnam,srfnam,
     &  xphonam,yphonam,zphonam,xphinam,yphinam,zphinam,
     &  prmnam,pdbnam,siznam,crgnam,phiinam,frcinam,toplbl
c
