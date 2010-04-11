	subroutine qqint(i,argnam,arglen)
c
	include "qlog.h"
c
	character*80 argnam
	integer arglen
c
	call defprm
c
	if(i.gt.0)then
	prmnam=argnam(:arglen)
	prmlen=arglen
	end if
c
	if(i.gt.1)then
	write(6,*) " "
	write(6,*) "WARNING!"
	write(6,*) " too many file names.."
	write(6,*) "only using the first as the parameter file"
	write(6,*) "file name= ",prmnam(:prmlen)
	write(6,*) " "
	end if

	call rdprm
c parameter assessment now because too complex to do elsewhere
        if (radprb(2).eq.-1.) radprb(2)=radprb(1)
	end
c
c *****************************************************************
	subroutine defprm
c
c logical parameters used in qdiff, mainly from parameter file
c
	include "qlog.h"
c
c     data conversion to kT/charge at 25 celsius
      data fpi /12.566/
c
	toplbl="qdiffxas: qdiffxs4 with an improved surfacing routine"
	isch=.false.
	isen=.false.
	iacs=.false.
	irea=.false.
	iautocon=.true.
	iper(1)=.false.
	iper(2)=.false.
	iper(3)=.false.
        iper(4)=.false.
        iper(5)=.false.
        iper(6)=.false.
	iconc=.false.
	ibios=.false.
	isite=.false.
	iatout=.false.
	diff=.false.
	isph=.false.
	phiwrt=.false.
	logs=.false.
	logc=.false.
	loga=.false.
	logg=.false.
c b++++++++++++++++++++++++++++++w Oct 2000
        logions=.false.
c flag for energy calculation of contribution from the solvent
        lognl=.false.
c flag for non linear energy calculation
        icreapdb=.false.
c flag for automatic insertion of objects
        imanual=.false.
c flag for manual assignment of relaxation parameterr
c e++++++++++++++++++++++++++++++++++++++++
	logas=.false.
	ipdbrd=.false.
	epswrt=.false.
	iacent=.false.
	ipdbwrt=.false.
	ifrcwrt=.false.
	ifrcrd=.false.
	ipoten=.false.
	igraph=.false.
	imem=.false.
	ihome=.false.
	ibufz=.false.
	inrgwrt=.false.
	iwgcrg=.false.
	iuspec=.false.
	icheb=.false.
	idbwrt=.false.
	ixphird=.false.
	iyphird=.false.
	izphird=.false.
	ixphiwt=.false.
	iyphiwt=.false.
	izphiwt=.false.
	isita=.false.
	isitq=.false.
	isitp=.false.
c b+++++++++++++++++++++++
        isitap=.false.
	  isitmd=.false.
	  isittf=.false.
c e+++++++++++++++++++++++
	isitf=.false.
	isitr=.false.
	isitc=.false.
	isitx=.false.
	isiti=.false.
	iself=.false.
	isitrf=.false.
	isitcf=.false.
	isitt=.false.
	isolv=.true.
	isrf=.false.
c
	icon1=10
	icon2=1
	epsnam="fort.17"
	phinam="fort.14"
	srfnam="grasp.srf"
	frcnam="fort.16"
	mpdbnam="fort.19"
	updbnam="fort.20"
	ufrcnam="fort.21"
	centnam="fort.15"
	pdbnam="fort.13"
	crgnam="fort.12"
	siznam="fort.11"
	phiinam="fort.18"
	frcinam="fort.15"
	prmnam="fort.10"
	scrgnam="scrg.dat"
	nrgnam="energy.dat"
	gcrgnam="crg.dat"
	dbnam="db.dat"
	xphinam="fort.31"
	yphinam="fort.32"
	zphinam="fort.33"
	xphonam="fort.34"
	yphonam="fort.35"
	zphonam="fort.36"
c
	epslen=7
	philen=7
	srflen=9
	frclen=7
	mpdblen=7
	updblen=7
	ufrclen=7
	centlen=7
	pdblen=7
	crglen=7
	sizlen=7
	phiilen=7
	frcilen=7
	scrglen=8
	nrglen=10
	prmlen=7
	gcrglen=7
	dblen=6
	xphilen=7
	yphilen=7
	zphilen=7
	xpholen=7
	ypholen=7
	zpholen=7
c
	phifrm=0
	epsfrm=0
	frcfrm=0
	mpdbfrm=0
	updbfrm=0
	ufrcfrm=0
	pdbfrm=0
	crgfrm=0
	sizfrm=0
	prmfrm=0
	phiifrm=0
	frcifrm=0
	scrgfrm=0
	nrgfrm=0
	gcrgfrm=0
        radprb(1)=1.4
	scale=10000.
	exrad=2.0
	perfil=10000.
c b++++++++++++++++++
        radpolext=1.0
        radprb(2)=-1.0
	conc(1)=0.0
        conc(2)=0.0
        rionst=0.0
        relpar=1.0 
c ival are the valencies of salts
        ival(1)=1
        ival(2)=1
        ival2(1)=0
        ival2(2)=0
        res1=0.0
        res2=0.0
        res5=0.0
        vdropx=0.0
        vdropy=0.0
        vdropz=0.0
        atompotdist=0.5
        temperature=297.3342119
c e++++++++++++++++++
	repsout=80
	epsout=80
	repsin=2
	epsin=2
	gten=0.0
	uspec=0.9975
	offset(1)=0.
	offset(2)=0.
	offset(3)=0.
	acent(1)=0.0
	acent(2)=0.0
	acent(3)=0.0
	do j=1,3
	bufz(1,j)=0
	bufz(2,j)=0
	end do
	igrid=0
	nlit=0
	nnit=0
	ibctyp=2
c
	return
	end
c ***********************************************************
	subroutine rdflnm(j1,j2,direc,fnam,flen)
c
	character*100 direc,calph
	integer un(10),unum,flen,six,five
	character*10 cnumb
	character*80 fnam
c
	cnumb="1234567890"
	calph=" "
	calph(1:40)="ABCDEFGHIJKLMNOPQRSTUVWXYZ.:_-+=!@#$^123"
	calph(41:80)="4567890abcdefghijklmnopqrstuvwxyz|\/?><;"
        fnam=" "
	flen=0
c
	if(j1.ne.0) then
	j=j1
	k=j+4
	n=1
150	k=k+1
	l=index(cnumb,direc(k:k))
	if(l.ne.0) then
	un(n)=l
	n=n+1
	goto 150
	end if
	unum=0
	fnam(1:5)="fort."
	do i=1,n-1
	fnam(5+i:5+i)=cnumb(un(i):un(i))
	end do
	flen=4+n
c	write(6,*) "(filename)unit number,length= ",fnam,flen
	end if
c
c j2=position of first letter in file descriptor, i.e. the letter
c f of "file"
	if(j2.ne.0) then
	j=j2
	k=j+5
	if(index(calph,direc(k:k)).ne.0) k=k-1
	n=1
	m=k+1
160	k=k+1
	l=index(calph,direc(k:k))
	if(l.ne.0) then
	n=n+1
	goto 160
	end if
	fnam(1:n-1)=direc(m:j+4+n)
	flen=n-1
c	write(6,*) "filename,length= ",fnam(1:n-1),flen
	end if
c
	return
	end
c *******************************************************
	 subroutine funcint(line,lineln)
c
	include "qlog.h"
c
	character*100 line,direc,calph,direc2
	integer lineln,flen,frmlen
	character*10 func(10),type,cnumb,frmnam
	character*26 calph1
	character*26 calph2
	logical ij3,ifrm,ipr,iflag,ij4
c
	cnumb="1234567890"
	calph=" "
	calph(1:40)="ABCDEFGHIJKLMNOPQRSTUVWXYZ.,:_-+=!@#$^123"
	calph(41:56)="4567890)(|\/?><;"
        calph2="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	calph1="abcdefghijklmnopqrstuvwxyz"
	ij3=.false.
	ifrm=.false.
c
	do i=1,lineln
	if(line(i:i).eq."(") goto 10
	end do
10	ieq1=i-1
	ieq2=lineln-ieq1
c
	type=" "
	type(1:ieq1)=line(1:ieq1)
c
c convert type to uppercase
c
	do i=1,ieq1
	j=index(calph1,type(i:i))
	if(j.ne.0) type(i:i)=calph2(j:j)
	end do
c
	direc=" "
	direc2=" "
	direc(1:ieq2)=line(ieq1+1:lineln)
	direc2(1:ieq2)=line(ieq1+1:lineln)
c
c conver direc to uppercase, not direc2
c
	do i=1,ieq2
	j=index(calph1,direc(i:i))
	if(j.ne.0) direc(i:i)=calph2(j:j)
	end do
c
	itype=0
	if(type(1:ieq1).eq."CENTER") itype=1
	if(type(1:ieq1).eq."CENT") itype=1
	if(type(1:ieq1).eq."ACENTER") itype=2
	if(type(1:ieq1).eq."ACENT") itype=2
	if(type(1:ieq1).eq."IN") itype=3
	if(type(1:ieq1).eq."READ") itype=3
	if(type(1:ieq1).eq."OUT") itype=4
	if(type(1:ieq1).eq."WRITE") itype=4
	if(type(1:ieq1).eq."ENERGY") itype=5
	if(type(1:ieq1).eq."BUFFZ") itype=7
	if(type(1:ieq1).eq."SITE") itype=6
	if(type(1:ieq1).eq."QPREF") itype=8
c b+++++++++++++++++++++++++++++++++++++++++
        if(type(1:ieq1).eq."INSOBJ") itype=9
c e+++++++++++++++++++++++++++++++++++++++++
c
	if(itype.eq.0) then
	write(6,*) "!!!!!!!!!!!!!!!!!"
	write(6,*) "The function specifier ",type(1:ieq1)," is"
	write(6,*) "not recognised. Therefore the function will not be p
     &  rocessed"
	write(6,*) "!!!!!!!!!!!!!!!!!"
	end if
c
c see if the function contains a format statement
c use direc2 to maintain case sensitivity
c
	k1=index(direc(1:ieq2),"FRM=")
	k2=index(direc(1:ieq2),"FORM=")
	k3=index(direc(1:ieq2),"FORMAT=")
	if((k1+k2+k3).ne.0) then
	if(k1.ne.0) k=k1+4
	if(k2.ne.0) k=k2+5
	if(k3.ne.0) k=k3+7
	k4=k+1
209	if((direc(k4:k4).eq.",").or.(direc(k4:k4).eq.")")) goto 210
	k4=k4+1
	goto 209
210	k4=k4-1
	if(index(calph,direc(k:k)).eq.0) then
	k=k+1
	k4=k4-1
	end if
	frmlen=k4+1-k
	frmnam=direc2(k:k4)
	call up(frmnam,k4-k+1)
	ifrm=.true.
	end if
c
c
	j1=index(direc,"UNIT=")
	j2=index(direc,"FILE=")
	if((j1+j2).ne.0) ij3=.true.
c
	if(itype.eq.1) then
	j0=0
	if((direc(1:ieq2).eq."()").or.(direc(1:ieq2).eq."(0,0,0)")) then
	offset(1)=0.0
	offset(2)=0.0
	offset(3)=0.0
	j0=1
	end if
c
	if(ij3) then
	call rdflnm(j1,j2,direc2,centnam,centlen)
	end if
c
	if((j1+j2).ne.0) then
	offset(1)=999.
	offset(2)=0.
	offset(3)=0.
	end if
c
	if(index(direc,"AN=1").ne.0) then
	offset(1)=999.
	offset(2)=999.
	offset(3)=0.
	end if
c
	if((j0+j1+j2).eq.0) then
	k1=2
302	continue
	k2=k1
	ipr=.false.
	do i=k2,ieq2
	if(direc(i:i).eq.".") ipr=.true.
	if((direc(i:i).eq.",").or.(direc(i:i).eq.")"))then
	if(.not.ipr) then
	do l=ieq2+1,i+1,-1
	direc(l:l)=direc(l-1:l-1)
	direc2(l:l)=direc2(l-1:l-1)
	end do
	direc(i:i)="."
	direc2(i:i)="."
	ieq2=ieq2+1
	k1=i+2
	if(k1.eq.ieq2) goto 303
	goto 302
	else
	ipr=.false.
	end if
	end if
	end do
303	continue
	read(direc(2:ieq2-1),103)offset
	end if
c
	end if
c
	if(itype.eq.2) then
c
	k1=2
300	continue
	k2=k1
	ipr=.false.
	do i=k2,ieq2
	if(direc(i:i).eq.".") ipr=.true.
	if((direc(i:i).eq.",").or.(direc(i:i).eq.")"))then
	if(.not.ipr) then
	do l=ieq2+1,i+1,-1
	direc(l:l)=direc(l-1:l-1)
	direc2(l:l)=direc2(l-1:l-1)
	end do
	direc(i:i)="."
	direc2(i:i)="."
	ieq2=ieq2+1
	k1=i+2
	if(k1.eq.ieq2) goto 301
	goto 300
	else
	ipr=.false.
	end if
	end if
	end do
301	continue
c
c
	read(direc(2:ieq2-1),103)acent
103	format(3f12.7)
	iacent=.true.
	end if
c
c READ
	if(itype.eq.3) then
c
	if(index(direc(1:ieq2),"(SIZ").ne.0) then
	sizfrm=0
	if(ij3) call rdflnm(j1,j2,direc2,siznam,sizlen)
	if(ifrm) then
	if(sizfrm.eq.0) then
	write(6,*) "unknown size file format",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(CRG").ne.0) then
	crgfrm=0
	if(ij3) call rdflnm(j1,j2,direc2,crgnam,crglen)
	if(ifrm) then
	if(crgfrm.eq.0) then
	write(6,*) "unknown charge file format",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(PDB").ne.0) then
	pbdfrm=0
	if(ij3) call rdflnm(j1,j2,direc2,pdbnam,pdblen)
	if(ifrm) then
	if(frmnam(:frmlen).eq."UN") pdbfrm=1
	if(frmnam(:frmlen).eq."MOD") pdbfrm=2
	if(pdbfrm.gt.0) ipdbrd=.true.
	if(pdbfrm.eq.0) then
	write(6,*) "unknown pdb file format",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(FRC").ne.0) then
	frcifrm=0
	if(ij3) call rdflnm(j1,j2,direc2,frcinam,frcilen)
	if(frcinam(:frclen).eq."self") iself=.true.
	if(frcinam(:frclen).eq."SELF") iself=.true.
	if(ifrm) then
	if(frcifrm.eq.0) then
	write(6,*) "unknown input frc file format for",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(PHI").ne.0) then
	phiifrm=0
	if(ij3) call rdflnm(j1,j2,direc2,phiinam,phiilen)
	if(ifrm) then
	if(phiifrm.eq.0) then
	write(6,*) "unknown input phimap format",frmnam(:frmlen)
	end if
	end if
	end if
c
	end if
c
c WRITE
	if(itype.eq.4) then
	iflag=.true.
	if(index(direc(1:ieq2),"OFF)").ne.0) iflag=.false.
	ij4=iflag.and.ij3
c
	if(index(direc(1:ieq2),"(PHI").ne.0) then
	phiwrt=iflag
	phifrm=0
	if(ij4) call rdflnm(j1,j2,direc2,phinam,philen)
	if(ifrm) then
	if(frmnam(:frmlen).eq."BIOSYM") phifrm=1
        if(frmnam(:frmlen).eq."GRASP") phifrm=2
	if(phifrm.eq.1) ibios=.true.
	if(phifrm.eq.0) then
	write(6,*) "unknown phimap format: ",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(SRF").ne.0) then
	isrf=.true.
	ibem=.false.
	if(ij4) call rdflnm(j1,j2,direc2,srfnam,srflen)
	if(ifrm) then
	if(frmnam(:frmlen).eq."BEM")ibem=.true.
	end if
	end if
c
	if(index(direc(1:ieq2),"(FRC").ne.0) then
	isite=iflag
	frcfrm=0
	if(ij4) call rdflnm(j1,j2,direc2,frcnam,frclen)
	if(ifrm) then
	if(frmnam(:frmlen).eq."RC") frcfrm=1
	if(frmnam(:frmlen).eq."R") frcfrm=2
	if(frmnam(:frmlen).eq."UN") frcfrm=3
	if((frcfrm.eq.1).or.(frcfrm.eq.2)) irea=.true.
	if((frcfrm.gt.3).or.(frcfrm.lt.1)) then
	write(6,*) "unknown frc format: ",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(EPS").ne.0) then
	epswrt=iflag
	epsfrm=0
	if(ij4) call rdflnm(j1,j2,direc2,epsnam,epslen)
	if(ifrm) then
	if(epsfrm.eq.0) then
	write(6,*) "unknown eps format: ",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(MODPDB").ne.0) then
	iatout=iflag
	mpdbfrm=0
	if(ij4) call rdflnm(j1,j2,direc2,mpdbnam,mpdblen)
	if(ifrm) then
	if(mpdbfrm.eq.0) then
	write(6,*) "unknown modified pdb format: ",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(UNPDB").ne.0) then
	ipdbwrt=iflag
	updbfrm=0
	if(ij4) call rdflnm(j1,j2,direc2,updbnam,updblen)
	if(ifrm) then
	if(updbfrm.eq.0) then
	write(6,*) "unknown unformatted pdb format: ",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(UNFRC").ne.0) then
	ifrcwrt=iflag
	ufrcfrm=0
	if(ij4) call rdflnm(j1,j2,direc2,ufrcnam,ufrclen)
	if(ifrm) then
	if(ufrcfrm.eq.0) then
	write(6,*) "unknown unformatted frc format: ",frmnam(:frmlen)
	end if
	end if
	end if
c
c
	if(index(direc(1:ieq2),"(ENERGY").ne.0) then
	inrgwrt=iflag
	nrgfrm=0
	if(ij4) call rdflnm(j1,j2,direc2,nrgnam,nrglen)
	if(ifrm) then
	if(nrgfrm.eq.0) then
	write(6,*) "unknown energy file format: ",frmnam(:frmlen)
	end if
	end if
	end if
c
	if(index(direc(1:ieq2),"(GCRG").ne.0) then
	iwgcrg=.true.
	end if
	if(index(direc(1:ieq2),"(HSURF").ne.0) then
	iacs=.true.
	end if
	if(index(direc(1:ieq2),"(DB").ne.0) then
	idbwrt=.true.
	end if
	if(index(direc(1:ieq2),"(SURFEN").ne.0) then
	isen=.true.
	end if
	if(index(direc(1:ieq2),"(SCRG").ne.0) then
	isch=iflag
	scrgfrm=0
	if(ij4) call rdflnm(j1,j2,direc2,scrgnam,scrglen)
	if(ifrm) then
	if(frmnam(:frmlen).eq."PDB") scrgfrm=1
	if(frmnam(:frmlen).eq."PDBA") scrgfrm=2
	if((scrgfrm.gt.2).or.(scrgfrm.lt.1)) then
	write(6,*) "unknown surface charge format: ",scrgnam(:scrglen)
	end if
	end if
	end if
	end if
c
	if(itype.eq.5) then
	  direc(ieq2:ieq2)=","
	  if(index(direc(1:ieq2),"GRID,").ne.0) logg=.true.
c
	  if(index(direc(1:ieq2),"S,").ne.0)then
	    ipos=index(direc(1:ieq2),"S,")
	    if(direc(ipos-1:ipos-1).ne."A")then
	      logs=.true.
	    else
	      logas=.true.
	    end if
	  end if
c
	  if(index(direc(1:ieq2),"G,").ne.0)then
	    ipos=index(direc(1:ieq2),"G,")
	    if(direc(ipos-1:ipos-1).ne."A")then
	      logg=.true.
	    else
	      loga=.true.
	    end if
	  end if
c
c b+++++++++++++++++++++++++++++++++++++w 2000
          if(index(direc(1:ieq2),"ION,").ne.0) logions=.true.
          if(index(direc(1:ieq2),"IONIC_C").ne.0) logions=.true.
c e+++++++++++++++++++++++++++++++++++++++++++
	  if(index(direc(1:ieq2),"SOLVATION").ne.0) logs=.true.
	  if(index(direc(1:ieq2),"SOL,").ne.0) logs=.true.
	  if(index(direc(1:ieq2),"C,").ne.0) logc=.true.
	  if(index(direc(1:ieq2),"COU,").ne.0) logc=.true.
	  if(index(direc(1:ieq2),"COULOMBIC").ne.0) logc=.true.
	  if(index(direc(1:ieq2),"AS,").ne.0) logas=.true.
	  if(index(direc(1:ieq2),"ANASURF,").ne.0) logas=.true.
	  if(index(direc(1:ieq2),"ANALYTICSURFACE").ne.0) logas=.true.
	  if(index(direc(1:ieq2),"AG,").ne.0) loga=.true.
	  if(index(direc(1:ieq2),"ANAGRID,").ne.0) loga=.true.
	  if(index(direc(1:ieq2),"ANALYTICGRID").ne.0) loga=.true.
c	  write(6,*) loga,logg,logs,logc,logas,logions
	end if
c
c	write(6,*) "wrtlog ",phiwrt,isite,epswrt,iatout,ipdbwrt,ifrcwrt
c
c SITE
	if(itype.eq.6) then
c
c empty bracket means reset all quantities to false
	if(ieq2.eq.2) then
	isita=.false.
	isitx=.false.
	isitq=.false.
	isitp=.false.
c b+++++++++++++++++++++++
        isitap=.false.
	  isitmd=.false.
	  isittf=.false.
c e+++++++++++++++++++++++
	isiti=.false.
	isitr=.false.
	isitc=.false.
	isitf=.false.
	isitt=.false.
	end if
c
	direc(ieq2:ieq2)=","
	if(index(direc(1:ieq2),"ATOM,").ne.0) isita=.true.
	if(index(direc(1:ieq2),"CHARGE,").ne.0) isitq=.true.
	if(index(direc(1:ieq2),"POTENTIAL,").ne.0) isitp=.true.
c b+++++++++++++++++++++++++++++
        if(index(direc(1:ieq2),"ATOMICPOT,").ne.0) isitap=.true.
c e+++++++++++++++++++++++++++++
	if(index(direc(1:ieq2),"FIELD,").ne.0) isitf=.true.
	if(index(direc(1:ieq2),"REACTION,").ne.0) isitr=.true.
	if(index(direc(1:ieq2),"COULOMB,").ne.0) isitc=.true.
	if(index(direc(1:ieq2),"COORDINATES,").ne.0) isitx=.true.
	if(index(direc(1:ieq2),"SALT,").ne.0) isiti=.true.
	if(index(direc(1:ieq2),"TOTAL,").ne.0) isitt=.true.
c
c NB can only do last letters like this if there is no cooincindence with
c those above
	if(index(direc(1:ieq2),"A,").ne.0) isita=.true.
	if(index(direc(1:ieq2),"Q,").ne.0) isitq=.true.
	if(index(direc(1:ieq2),"P,").ne.0) isitp=.true.
	if(index(direc(1:ieq2),"R,").ne.0) isitr=.true.
	if(index(direc(1:ieq2),"C,").ne.0) isitc=.true.
	if(index(direc(1:ieq2),"X,").ne.0) isitx=.true.
	if(index(direc(1:ieq2),"I,").ne.0) isiti=.true.
	if(index(direc(1:ieq2),"T,").ne.0) isitt=.true.
c
c b++++++++++++++++++
        if(index(direc(1:ieq2),"ATPO,").ne.0) isitap=.true.
c e++++++++++++++++++
c extra ones for fields
	if(index(direc(1:ieq2),"F,").ne.0) then
	  if(index(direc(1:ieq2),"RF,").ne.0) isitrf=.true.
	  if(index(direc(1:ieq2),"CF,").ne.0) isitcf=.true.
c b++++++++++++++++++
	  if(index(direc(1:ieq2),"MDF").ne.0) isitmd=.true.
	  if(index(direc(1:ieq2),"TF").ne.0) isittf=.true.
	  if(.not.(isitrf.or.isitcf.or.isitmd.or.isittf)) isitf=.true.
c	  if((.not.isitrf).and.(.not.isitcf).and.(.not.isitmd).and.(.not.isittf)) isitf=.true.
c e++++++++++++++++++
	end if
c
      if(isitr) irea=.true.
	if(isitrf) irea=.true.
c b++++++++++++++++++
	if(isitmd.or.isittf) irea=.true.
c e++++++++++++++++++
	if(isitt) irea=.true.
c
	end if
c
	if(itype.eq.7) then
	read(direc(2:ieq2-1),333)bufz
333	format(6i3)
	ibufz=.true.
	end if
c
	if(itype.eq.8) then
	end if
c b++++++++++++++++++++++++++++++++++++++++++++++++++++
        if(itype.eq.9) icreapdb=.true.
c e++++++++++++++++++++++++++++++++++++++++++++++++++
	return
	end
c ********************************************************
	subroutine pi(line,mlen)
c
	include "qlog.h"
c
	character*400 mline,line
	character*4 alph1,alph2
	character*1 chr
	integer comnum,comb(50),come(50)
	logical iuse,istat,icom(50)
c
	alph1="[{]}"
	alph2="(())"
c
c prepare line, removing blanks, changing brackets
c if we run into an explanation mark then turn off the character
c grabber until we reach another one. also ignore blanks
c
	if(mlen.eq.0) goto 99
	ml=0
	iuse=.true.
	do i=1,mlen
	  chr=line(i:i)
	  if(chr.eq."!") iuse=.not.iuse
	  if(chr.eq."!") goto 50
	  if(iuse) then
c remove blanks
	    if(chr.ne." ") then
	      ml=ml+1
c convert brackets of wrong type
	      j=index(alph1,chr)
	      if(j.ne.0) chr=alph2(j:j)
	      mline(ml:ml)=chr
	    end if
	  end if
50	  continue
	end do
c
c remove any termination with a comma
c
c b++++++++++++++++++++++++++++++there was a bug
	if (ml.gt.0) then
	  if(mline(ml:ml).eq.",") then
	    ml=ml-1
	  end if
	end if
c e++++++++++++++++++++++++++++++++
c
c try and interpret the line. look for statement (= signs), or
c functions ( a closed pair of brackets.)
c if there is trouble, e.g. an unpaired bracket, then print
c out the uninterpretable bit and continue
c
	branum=0
c
c branum = bracket number
c comb(i) = beginning of command i
c come(i) = end of command i
c
	j=1
	comb(1)=1
	do i=1,ml
	  chr=mline(i:i)
	  if(chr.eq."(") branum=branum+1
	  if(chr.eq.")") branum=branum-1
	  if(((chr.eq.",").or.(chr.eq.":").or.(chr.eq."|")).and.(branum
     &      .eq.0)) then
	    come(j)=i-1
	    j=j+1
	    comb(j)=i+1
	  end if
	end do
	come(j)=i-1
c
	comnum=j
c
c comnum = number of commands
c icom is a logical array, true if the corresponding command is
c a statement. once determined, pass to the statement or function
c interpreter
c
	do i=1,comnum
	  bnum1=0
	  bnum2=0
	  istat=.false.
	  icom(i)=.false.
	  do j=comb(i),come(i)
	    if(mline(j:j).eq."(") bnum1=bnum1+1
	    if(mline(j:j).eq.")") bnum2=bnum2+1
	    if(mline(j:j).eq."=") then
	      if(bnum1.eq.bnum2) istat=.true.
	    end if
	  end do
	  if(istat) icom(i)=.true.
	end do
c
	do i=1,comnum
	  if((come(i)-comb(i)).lt.1) goto 543
	  if(icom(i))then
	    call statint(mline(comb(i):come(i)),come(i)-comb(i)+1)
	  else
	    call funcint(mline(comb(i):come(i)),come(i)-comb(i)+1)
	  end if
543	  continue
	end do
c
99	continue
	return
	end
c *****************************************************************
	subroutine prm1(line,il)
c
	include "qlog.h"
c
	character*80 line
c
c	write(6,*) "in prm1 :",il,line
	if(line.eq." ") goto 1000
	goto(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)il
c
1	read(line,*)igrid
	goto 1000
c
2	j=index(line,"g")
	i=index(line,"G")
	k=max(i,j)
	if(k.eq.0) then
	read(line,*) perfil
c	scale=0.
	else
	read(line(:k-1),*) scale
c	perfil=0.
	end if
	goto 1000
c
3	read(line,*)offset
	goto 1000
c
4	read(line,*)repsin,repsout
	goto 1000
c
c b++++++++++++++++++not tested actually+++
5	read(line,*)conc(1),conc(2)
	goto 1000
c
6	read(line,*)exrad,radprb(1),radprb(2),radpolext,relpar,
     &              atompotdist
c da testare, manca imanual!!!
c e++++++++++++++++++
	goto 1000
c
7	read(line,*)ibctyp
	goto 1000
c
8	read(line,*)iper
	goto 1000
c
9	if((line(1:1).eq.'a').or.(line(1:1).eq.'A')) then
	iautocon=.true.
	gten=0.
	nlit=0
	else
	if(index(line,".").eq.0) then
	read(line,*)nlit
	iautocon=.false.
	gten=0.
	else
	read(line,*)gten
	iautocon=.true.
	nlit=0
	end if
	end if
	goto 1000
c
10	read(line,*)nnit
c b++++++++++++++++++++++++++++++++++++++++
        if (nnit.le.20) then
          write(6,*)'At least 30 nonlinear iterations'
          nnit=30
        end if
c e++++++++++++++++++++++++++++++++++++++++
	goto 1000
c
11	read(line,*)iconc,ibios
	goto 1000
c
12	read(line,*)isite
	goto 1000
c
13	read(line,*)iatout
	goto 1000
c
14	toplbl=line(:60)
	goto 1000
c
15	read(line,*)isph
	goto 1000
c
16	read(line,*)ipdbwrt
	goto 1000
c
17	read(line,*)ifrcwrt
	goto 1000
c
18	if((index(line,"g").ne.0).or.(index(line,"G").ne.0))logg=.true.
	if((index(line,"s").ne.0).or.(index(line,"S").ne.0))logs=.true.
	if((index(line,"c").ne.0).or.(index(line,"C").ne.0))logc=.true.
	if((index(line,"a").ne.0).or.(index(line,"A").ne.0))loga=.true.
c b++++++++++++++++++++++++w Oct 2000
        if((index(line,"ion").ne.0).or.(index(line,"ION").ne.0))
     &    logions=.true.
c e+++++++++++++++++++++++++++++++++++
	goto 1000
c
19	read(line,*)igraph,ipoten,icon1,icon2
	goto 1000
c
20	read(line,*)imem
	goto 1000
c
21	read(line,*)phiwrt
	goto 1000
c
22	read(line,*)iacs,isen,isch
	goto 1000
c
1000	continue
	return
	end
c *********************************************************************
	subroutine rdprm
c
	include "qlog.h"
c
	character*80 line,asci,enc,filnam
	character*10 cnumb
	character*400 mline
	dimension lin1(20),itype(20)
	logical iext
c b+++++++++++++++++++++++++++++++
        real cz1,cz2,z1p,z1m,z2p,z2m
c e++++++++++++++++++++++++++++++
c
c read in run parameters
c
204	format(a80)
	asci="1234567890 .-+#,$asdfghjklzxcvbnmqwertyuio
     &pASDFGHJKLZXCVBNMQWERTYUIOP)(}{][/"
c     &pASDFGHJKLZXCVBNMQWERTYUIOP)(}{][/\"
	cnumb="0123456789"
c
c
	inquire(file=prmnam(:prmlen),exist=iext)
	if(.not.iext) then
	write(6,*) "parameter file ",prmnam(:prmlen)," does not seem to 
     &  exist"
        write(6,*)'Therefore stopping'
        stop
	goto 1000
	end if
c
	write(6,*) "opening parameter file ",prmnam(:prmlen)
	open(10,file=prmnam(:prmlen))
c
c set current file length to prmlen
c set current file to prmnam
	ifn=10
	ifillen=prmlen
	filnam(:ifillen)=prmnam(:prmlen)
c
c goto here if a new file has just been opened
c and reset line number to 1 (only used by type 1 files)
c
10	itype(ifn)=0
	lin1(ifn)=1
c
c goto here to read a new line from an already opened file
c
20	line=" "
c	write(6,*) "reading line"
	read(ifn,204,err=500,end=100) line
c added 9/9/92 to fixed qincludes being not commented out!
	if(line(1:1).eq."!") line(2:80)=" "
c
c do below if the type of the prm file is undetermined
c normally the first line, unless that was a qinclude
c statement
c
c	write(6,*) "checking for type0"
	if(itype(ifn).eq.0) then
c check as to whether the first character of the file is a number
c	write(6,*) "checking for type"
	if(index(cnumb,line(1:1)).eq.0) then
	j1=index(line,"QINCLUDE")
	j2=j1+index(line,"qinclude")
	if(j2.ne.0) then
c	write(6,*) "there is an include file"
c there is a qinclude statement before the current file type is
c determined. is this a command passer or a file opener?
	j3=index(asci,line(j2+9:j2+9))
	if(j3.eq.0) then
c the qinclude statement does not open a file, but passes a
c command, therefore pass that command
	call namleb(line,j4)
	call pi(line(j2+10:j4-2),j4-2-j2-9)
	end if
	if(j3.ne.0) then
c	write(6,*) "it opens a file"
c the include statement opens a file, therefore increment ifn
c go back to 10 if it exists
	call namleb(line,j4)
	filnam=line(j2+9:j4-1)
	ifillen=j4-j2-9
	if(filnam.eq." ") then
        call system("echo $HOME > tmp101")
        open(7,file="tmp101")
        read(7,'(a)')uhomenam
        call namlen(uhomenam,uhomelen)
	filnam=uhomenam(:uhomelen)//"/qpref.prm"
	ifillen=uhomelen+10
	write(6,*) "opening default file qpref.prm"
        close (7)
        call system("/bin/rm tmp101")
	end if
	inquire(file=filnam(:ifillen),exist=iext)
	if(iext) then
	ifn=ifn+1
	write(6,*) "opening file: ",filnam(:ifillen)
	open(ifn,file=filnam(:ifillen))
	goto 10
	end if
	if(.not.iext) then
	write(6,*) "the file ",filnam(:ifillen)," specified in"
	write(6,*) "a qinclude statement does not exist. continuing"
	end if
	end if
	end if
c end of dealing with qinclude
c
	if(j2.eq.0) then
c no qinclude, therefore define this as a type 2 parameter file
c deal with possible multiply lines, deal with errors or
c errroneous end of files
	itype(ifn)=2
	iblen=1
30	call namleb(line,ilen)
c	write(6,*) "passing first line",line(:ilen)
	if(line(ilen:ilen).eq."&") then
	mline(iblen:iblen+ilen-2)=line(:ilen-1)
	iblen=iblen+ilen-1
	read(ifn,204,err=400,end=300) line
	goto 30
	else
	mline(iblen:iblen+ilen-1)=line(:ilen)
	end if	
	call pi(mline,ilen)
	goto 302
400	write(6,*) "error reading file :"
	write(6,*) filnam
	write(6,*) "continuing.."
	goto 100
300	write(6,*) "error, continuation slash on last line of"
	write(6,*) "file ",filnam
	write(6,*) "untoward things may happen"
	goto 100
302	continue
	end if
	end if
c
	if(index(cnumb,line(1:1)).ne.0) then
c the firstcharacter is a number , therefore define this is as a type 1
c without a qinclude on line 1
	itype(ifn)=1
	call prm1(line,lin1(ifn))
	lin1(ifn)=lin1(ifn)+1
	end if
c
c leave, having determined ttype unless a qinclude was encountered
c
	goto 450
	end if
c
c type is already determined
c
c ! need to check for qincludes! different for type 1 and type 2
c
	j1=index(line,"QINCLUDE")
	j2=j1+index(line,"qinclude")
	if(j2.ne.0) then
c	write(6,*) "include statement found"
c there is a qinclude statement
c determined. is this a command passer or a file opener?
	j3=index(asci,line(j2+9:j2+9))
	if(j3.eq.0) then
c the qinclude statement does not open a file, but passes a
c command, therefore pass that command
	call namleb(line,j4)
	call pi(line(j2+10:j4-2),j4-2-j2-9)
	end if
	if(j3.ne.0) then
c the include statement opens a file, therefore increment ifn
c go back to 10 if it exists
	call namleb(line,j4)
	filnam=line(j2+9:j4-1)
	ifillen=j4-j2-9
	if(filnam.eq." ") then
	call system("echo $HOME > tmp101")
	open(7,file="tmp101")
	read(7,'(a)')uhomenam
	call namlen(uhomenam,uhomelen)
	filnam=uhomenam(:uhomelen)//"/qpref.prm"
	ifillen=uhomelen+10
	write(6,*) "opening default file qpref.prm"
	close (7)
	call system("/bin/rm tmp101")
	end if
	inquire(file=filnam(:ifillen),exist=iext)
c
	if(iext) then
	ifn=ifn+1
	write(6,*) "opening file: ",filnam(:ifillen)
	open(ifn,file=filnam(:ifillen))
	goto 10
	end if
	if(.not.iext) then
	write(6,*) "the file ",filnam(:ifillen)," specified in"
	write(6,*) "a qinclude statement does not exist. continuing"
	end if
c
c end of opening fil "if",j3
	end if
	goto 450
	end if
c
c
c if no qincludes continue as below
	if(itype(ifn).eq.1) then
	call prm1(line,lin1(ifn))
	lin1(ifn)=lin1(ifn)+1
	end if
c
	if(itype(ifn).eq.2) then
	iblen=1
31	call namleb(line,ilen)
c
	if(line(ilen:ilen).eq."&") then
	mline(iblen:iblen+ilen-2)=line(:ilen-1)
	iblen=iblen+ilen-1
	read(ifn,204,err=401,end=301) line
	goto 31
	else
	mline(iblen:iblen+ilen-1)=line(:ilen)
	end if	
c
	call pi(mline,ilen)
	goto 303
c
401	write(6,*) "error reading file :"
	write(6,*) filnam
	write(6,*) "closing file and continuing.."
	goto 100
301	write(6,*) "error, continuation slash on last line of"
	write(6,*) "file ",filnam
	write(6,*) "which is now closed. untoward things may happen"
	goto 100
303	continue
	end if
c
c read next line
450	continue
	goto 20
c
c deal with end of file
500	write(6,*) "trouble at mill"
100	close(ifn)
c deal with end of file
	if(ifn.gt.10) then
	ifn=ifn-1
	goto 20
	end if
c
c
1000	continue
c
c
	if((repsin.lt.0.).or.(repsout.lt.0.)) then
	repsin=abs(repsin)
	repsout=abs(repsout)
	diff=.true.
	end if

c        dfact = 3.047*sqrt(repsout/80.)
      dfact=0.01990076478*sqrt(temperature*repsout)
c b++++++++++++++++++++++
c define a number that indicates whether or not there is some salt 
        z1p=ival(1)
        z1m=ival(2)
        z2p=ival2(1)
        z2m=ival2(2)
c now cz1 and cz2 are concentration of positive ion !!!
        cz1=conc(1)*z1m
        cz2=conc(2)*z2m
        rionst=(cz1*z1p*(z1p+z1m)+cz2*z2p*(z2p+z2m))/2.
c coefficients in Taylor series of the charge concentration
c  apart from n! (order >=1)
        chi1=-2.*rionst
        chi2=cz1*z1p*(z1p**2-z1m**2)+cz2*z2p*(z2p**2-z2m**2)
        chi2=chi2/2.
        chi3=cz1*z1p*(z1p**3+z1m**3)+cz2*z2p*(z2p**3+z2m**3)
        chi3=-chi3/6.
        chi4=cz1*z1p*(z1p**4-z1m**4)+cz2*z2p*(z2p**4-z2m**4)
        chi4=chi4/24.
        chi5=cz1*z1p*(z1p**5+z1m**5)+cz2*z2p*(z2p**5+z2m**5)
        chi5=-chi5/120.
c convert ionic strength to debye length
c
	if(rionst.gt.1.e-6) then
          deblen = dfact/sqrt(rionst) 
          if (nnit.gt.0) lognl=.true.
	else
          logions=.false.
	  deblen = 1.e6
	end if
        
c       write(6,*)'non linear energy:', lognl
c e++++++++++++++++++++++
c
c test for unformatted pdb and frc files
c
	if(.not.ipdbrd) then
 	open(13,file=pdbnam(:pdblen),form='formatted')
        read(13,204,iostat=n)line
	ias=0
	do 600 i=1,80
	if(index(asci,line(i:i)).eq.0) ias=ias+1
600	continue
	if(ias.gt.10) ipdbrd=.true.
 	close(13)
	end if
c
	if(ifrcwrt) then
 	open(15,form='formatted')
        read(13,204,iostat=n)line
	ias=0
	do 610 i=1,80
	if(index(asci,line(i:i)).eq.0) ias=ias+1
610	continue
	if(ias.gt.10) ifrcrd=.true.
 	close(15)
	end if
c
c epkt assignment as a function of temperature
	epkt=166804.4928/temperature
c set epsin and epsout (=epkt adjusted dielectrics such that
c all distances are in angstroms, charges in e)
c
	epsin = repsin/epkt
	epsout = repsout/epkt
c
c go back to main
c
	return
	end
c ******************************************************************
	subroutine statint(line,lineln)
c
	include "qlog.h"
c
	character*100 line
	character*30 type
	character*20 quant
	character*26 calph1,calph2
	character*2 stat2(100),typ2
	character*6 stat6(100),typ6
	character*1 chr
	integer lineln,typenum
	logical itf,icon
c
c have to decide whether to use decode or internal read
c the latter works better (and is easier!) for real quantities
c because if a period is absent from the number it assumes it
c is a very small number. this must be (?) an error. anyway
c read SEEMS to work so far.
c number of different statements
	calph1="abcdefghijklmnopqrstuvwxyz"
	calph2="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	do i=1,100
	stat2(i)=" "
	end do
c
c data list of two letter codes
c
c
	stat2(1)="GS"
	stat2(2)="SC"
	stat2(3)="PF"
	stat2(4)="ID"
	stat2(5)="ED"
	stat2(6)="PR"
	stat2(7)="IR"
	stat2(8)="IS"
	stat2(9)="BC"
	stat2(10)="LI"
	stat2(11)="NI"
	stat2(12)="MD"
	stat2(13)="FC"
	stat2(14)="LP"
	stat2(15)="LG"
	stat2(16)="CI"
	stat2(17)="CF"
	stat2(18)="PX"
	stat2(19)="PY"
	stat2(20)="PZ"
	stat2(21)="AC"
	stat2(22)="XU"
	stat2(23)="GC"
	stat2(24)="RF"
	stat2(25)="CI"
	stat2(26)="SP"
	stat2(27)="CS"
c b+++++++++++++++++++++++
        stat2(29)="RL"
        stat2(30)="RR"
        stat2(31)="S2"
        stat2(32)="R2"
        stat2(33)="+1"
        stat2(34)="-1"
        stat2(35)="+2"
        stat2(36)="-2"
        stat2(37)="MC"
        stat2(38)="XC"
        stat2(39)="NC"
        stat2(40)="VX"
        stat2(41)="VY"
        stat2(42)="VZ"
        stat2(43)="AD"
        stat2(44)="TE"
c e+++++++++++++++++++++++
c
	do i=1,100
	  if(stat2(i).ne." ") statnum=i
	end do
c data list of six letter codes
c
	stat6(1)="GSIZE"
	stat6(2)="SCALE"
	stat6(3)="PERFIL"
	stat6(4)="INDI"
	stat6(5)="EXDI"
	stat6(6)="PRBRAD"
	stat6(7)="IONRAD"
	stat6(8)="SALT"
	stat6(9)="BNDCON"
	stat6(10)="LINIT"
	stat6(11)="NONIT"
	stat6(12)="MEMDAT"
	stat6(13)="FCRG"
	stat6(14)="LOGPOT"
	stat6(15)="LOGGRP"
	stat6(16)="CONINT"
	stat6(17)="CONFRA"
	stat6(18)="PBX"
	stat6(19)="PBY"
	stat6(20)="PBZ"
	stat6(21)="AUTOC"
	stat6(22)="EXITUN"
	stat6(23)="GRDCON"
	stat6(24)="RELFAC"
	stat6(25)="CHEBIT"
	stat6(26)="SOLVPB"
	stat6(27)="CLCSRF"
        stat6(28)="PHICON"
c b+++++++++++++++++++++++
        stat6(29)="RADPOL"
        stat6(30)="RELPAR"
        stat6(31)="SALT2"
        stat6(32)="RADPR2"
        stat6(33)="VAL+1"
        stat6(34)="VAL-1"
        stat6(35)="VAL+2"
        stat6(36)="VAL-2"
        stat6(37)="RMSC"
        stat6(38)="MAXC"
        stat6(39)="NORMC"
        stat6(40)="VDROPX"
        stat6(41)="VDROPY"
        stat6(42)="VDROPZ"
        stat6(43)="ATPODS"
	  stat6(44)="TEMPER"
c e+++++++++++++++++++++++
c
c convert type to uppercase
c
	do i=1,lineln
	j=index(calph1,line(i:i))
	if(j.ne.0) line(i:i)=calph2(j:j)
	end do
c
	type(1:6)=" "
	quant(1:20)=" "
	ieq=index(line(1:lineln),"=")
	ieq1=ieq-1
c       ieq1 = lunghezza di cio' che e' prima dell'=
c
	ieq2=lineln-ieq
	type(1:ieq1)=line(1:ieq1)
	quant(1:ieq2)=line(ieq+1:lineln)
	typenum=0
c
c two and six letter codes are matched exactly
c otherwise the statement type is compared to a list of longer names
c where the first letter is compared, then the rest, tocut down on work
c
	if(ieq1.eq.2) then
	typ2=type(1:2)
	do i=1,statnum
	if(typ2.eq.stat2(i)) typenum=i
	end do
	end if
c
	if((ieq1.le.6).and.(ieq1.gt.2)) then
	typ6=type(1:6)
	do i=1,statnum
	if(typ6.eq.stat6(i)) typenum=i
	end do
	end if
c
	if(ieq1.gt.6) then
	chr=type(1:1)
	if(chr.eq."A") then
	if(type(1:ieq1).eq."AUTOMATICCONVERGENCE") typenum=21
	if(type(1:ieq1).eq."AUTOCONVERGENCE") typenum=21
	if(type(1:ieq1).eq."AUTOCON") typenum=21
        if(type(1:ieq1).eq."ATOMPOTDIST") typenum=43
	end if
	if(chr.eq."B") then
	if(type(1:ieq1).eq."BOXFILL") typenum=3
	if(type(1:ieq1).eq."BOUNDARYCONDITION") typenum=9
	if(type(1:ieq1).eq."BOUNDARYCONDITIONS") typenum=9
	end if
	if(chr.eq."C") then
	if(type(1:ieq1).eq."CONVERGENCEINTERVAL") typenum=16
	if(type(1:ieq1).eq."CONVERGENCEFRACTION") typenum=17
	end if
	if(chr.eq."D") then
	end if
	if(chr.eq."E") then
	if(type(1:ieq1).eq."EXTERIORDIELECTRIC") typenum=5
	if(type(1:ieq1).eq."EXTERNALDIELECTRIC") typenum=5
	if(type(1:ieq1).eq."EXITUNIFORMDIELECTRIC") typenum=22
	end if
	if(chr.eq."F") then
	if(type(1:ieq1).eq."FANCYCHARGE") typenum=13
	end if
	if(chr.eq."G") then
	if(type(1:ieq1).eq."GRIDSIZE") typenum=1
	if(type(1:ieq1).eq."GRIDCONVERGENCE") typenum=23
	end if
c       if(chr.eq."H") then
c       end if
	if(chr.eq."I") then
	if(type(1:ieq1).eq."IONRADIUS") typenum=7
	if(type(1:ieq1).eq."IONICSTRENGTH") write(6,*)'the option 
     & IONICSTRENGTH is no longer available, try SALT or SALT1'
c no longer available  typenum=8
	if(type(1:ieq1).eq."INTERIORDIELECTRIC") typenum=4
	if(type(1:ieq1).eq."ITERATIONS") typenum=10
	if(type(1:ieq1).eq."ITERATION") typenum=10
	end if
c       if(chr.eq."J") then
c       end if
c       if(chr.eq."K") then
c       end if
	if(chr.eq."L") then
	if(type(1:ieq1).eq."LINEARITERATION") typenum=10
	if(type(1:ieq1).eq."LINEARITERATIONS") typenum=10
	if(type(1:ieq1).eq."LOGFILEPOTENTIALS") typenum=14
	if(type(1:ieq1).eq."LOGFILECONVERGENCE") typenum=15
	end if
	if(chr.eq."M") then
	if(type(1:ieq1).eq."MEMBRANEDATA") typenum=12
	end if
	if(chr.eq."N") then
	if(type(1:ieq1).eq."NONLINEARITERATION") typenum=11
	if(type(1:ieq1).eq."NONLINEARITERATIONS") typenum=11
	end if
c       if(chr.eq."O") then
c       end if
	if(chr.eq."P") then
	if(type(1:ieq1).eq."PERIODICBOUNDARYX") typenum=18
	if(type(1:ieq1).eq."PERIODICBOUNDARYY") typenum=19
	if(type(1:ieq1).eq."PERIODICBOUNDARYZ") typenum=20
	if(type(1:ieq1).eq."PROBERADIUS") typenum=6
	if(type(1:ieq1).eq."PERCENTBOXFILL") typenum=3
	if(type(1:ieq1).eq."PERCENTFILL") typenum=3
	end if
c       if(chr.eq."Q") then
c       end if
	if(chr.eq."R") then
	  if(type(1:ieq1).eq."RELAXATIONFACTOR") typenum=24
c b+++++++++++++++++++++++
          if(type(1:ieq1).eq."RADPOLEXT") typenum=29
          if(type(1:ieq1).eq."RELPAR") typenum=30
          if(type(1:ieq1).eq."RMSCONVERGENCE") typenum=37
          if(type(1:ieq1).eq."MAXCONVERGENCE") typenum=38
          if(type(1:ieq1).eq."NORMCONVERGENCE") typenum=39
c e++++++++++++++++++++++
	end if
	if(chr.eq."S") then
	  if(type(1:ieq1).eq."SALTCONC") typenum=8
	  if(type(1:ieq1).eq."SALTCONCENTRATION") typenum=8
	  if(type(1:ieq1).eq."SPHERICALCHARGEDISTRIBUTION") typenum=13
	end if

     	if(chr.eq."T") then
	  if(type(1:ieq1).eq."TEMPERATURE") typenum=44
      end if
c      	if(chr.eq."U") then
c      	end if
c      	if(chr.eq."V") then
c      	end if
c      	if(chr.eq."W") then
c      	end if
c      	if(chr.eq."X") then
c      	end if
c      	if(chr.eq."Y") then
c      	end if
c      	if(chr.eq."Z") then
c      	end if
c
	end if
c
	if(typenum.eq.0) then
	write(6,*) "!!!!!!!!!!!!!"
	write(6,*) "the statement"
	write(6,*) line(1:lineln)
	write(6,*) "could not be interpreted"
	write(6,*) "!!!!!!!!!!!!!"
	end if
c
	if(typenum.eq.1) then
c	decode(ieq2,101,quant) igrid
	read(quant,*) igrid
c	write(6,*) "grid size. ok ",igrid
c101	format(i5)
	end if
c
	if(typenum.eq.2) then
c	decode(ieq2,102,quant) scale
	read(quant,*) scale
c	perfil=0.0
c102	format(f12.7)
c	write(6,*) "scale. ok",scale
	end if
c
	if(typenum.eq.3) then
c	decode(ieq2,102,quant) perfil
	read(quant,*) perfil
c	write(6,*) "perfil ok",perfil
	end if
c
	if(typenum.eq.4) then
c	decode(ieq2,102,quant) repsin
	read(quant,*) repsin
c	write(6,*) "epsin. ok",repsin
	end if
c
	if(typenum.eq.5) then
c	decode(ieq2,102,quant) repsout
	read(quant,*) repsout
c	write(6,*) "epsout ok",repsout
	end if
c
	if(typenum.eq.6) then
c	decode(ieq2,102,quant) radprb
c b++++++++++++++++++++++++++++++
        read(quant,*) radprb(1)
c	read(quant,'(2f4.2)') radprb(1)
c e++++++++++++++++++++++++++++++
	end if
c
	if(typenum.eq.7) then
c	decode(ieq2,102,quant) exrad
	read(quant,*) exrad
	end if
c
c b++++++++++++++++++++++++++++++
	if(typenum.eq.8) then
	read(quant,*) conc(1)
	end if
c e++++++++++++++++++++++++++++++
c
	if(typenum.eq.9) then
	read(quant,*) ibctyp
	end if
c
	if(typenum.eq.10) then
c	decode(ieq2,101,quant) nlit
	read(quant,*) nlit
	iautocon=.false.
c	write(6,*) "nlit ok",nlit
	end if
c
	if(typenum.eq.11) then
c	decode(ieq2,101,quant) nnit
	read(quant,*) nnit
c b++++++++++++++++++++++++++++++++++++++++
        if (nnit.le.20) then
          write(6,*)'At least 30 nonlinear iterations'
          nnit=30
        end if
c e++++++++++++++++++++++++++++++++++++++++
c	write(6,*) "nnit ok",nnit
	end if
c
	if(typenum.eq.12) then
	call yesno(type,ieq1,quant,ieq2,itf)
	imem=itf
c	write(6,*) "imem = ",imem
	end if
c
	if(typenum.eq.13) then
	call yesno(type,ieq1,quant,ieq2,itf)
	isph=itf
c	write(6,*) "isph = ",isph
	end if
c
	if(typenum.eq.14) then
	call yesno(type,ieq1,quant,ieq2,itf)
        ipoten=itf
	end if
c
	if(typenum.eq.15) then
	call yesno(type,ieq1,quant,ieq2,itf)
	igraph=itf
	end if
c
	if(typenum.eq.16) then
c	decode(ieq2,101,quant) icon1
	read(quant,*) icon1
c	write(6,*) "icon1=",icon1
	end if
c
	if(typenum.eq.17) then
c	decode(ieq2,101,quant) icon2
	read(quant,*) icon2
c	write(6,*) "icon2=",icon2
	end if
c
	if(typenum.eq.18) then
	call yesno(type,ieq1,quant,ieq2,itf)
	iper(1)=itf
c	write(6,*) "iper(1)=",iper(1)
	end if
c
	if(typenum.eq.19) then
	call yesno(type,ieq1,quant,ieq2,itf)
	iper(2)=itf
c	write(6,*) "iper(2)=",iper(2)
	end if
c
	if(typenum.eq.20) then
	call yesno(type,ieq1,quant,ieq2,itf)
	iper(3)=itf
c	write(6,*) "iper(3)=",iper(3)
	end if
c
	if(typenum.eq.21) then
	call yesno(type,ieq1,quant,ieq2,itf)
	iautocon=itf
c	write(6,*) "automatic convergence= ",itf
	end if
c
	if(typenum.eq.22) then
	call yesno(type,ieq1,quant,ieq2,itf)
	iexun=itf
	end if
c
	if(typenum.eq.23) then
	read(quant,*)gten
	iautocon=.true.
	end if
c
	if(typenum.eq.24) then
	read(quant,*)uspec
	iuspec=.true.
	end if
c
	if(typenum.eq.25) then
	call yesno(type,ieq1,quant,ieq2,itf)
	icheb=itf
	end if
c
	if(typenum.eq.26) then
	call yesno(type,ieq1,quant,ieq2,itf)
	isolv=itf
	end if
c
	if(typenum.eq.27) then
	call yesno(type,ieq1,quant,ieq2,itf)
	isrf=itf
	end if
c
        if(typenum.eq.28) then
        call yesno(type,ieq1,quant,ieq2,itf)
        iconc=itf
        end if
c
c b++++++++++++++++++++++++++++++
        if(typenum.eq.29) then
          read(quant,*) radpolext
          write(6,*)'radpolext= ',radpolext
        end if
        if(typenum.eq.30) then
          read(quant,*) relpar
          imanual=.true.
        end if
        if(typenum.eq.31) then
          read(quant,*) conc(2)
        end if
        if(typenum.eq.32) then
c now having different probes if the molecule faces the water or not
          read(quant,*) radprb(2)
        end if
        if(typenum.eq.33) then
          read(quant,*) ival(1)
        end if
        if(typenum.eq.34) then
          read(quant,*) ival(2)
        end if
        if(typenum.eq.35) then
          read(quant,*) ival2(1)
        end if
        if(typenum.eq.36) then
          read(quant,*) ival2(2)
        end if
        if(typenum.eq.37) then
          read(quant,*) res1
        end if
        if(typenum.eq.38) then
          read(quant,*) res2
        end if
        if(typenum.eq.39) then
          read(quant,*) res5
        end if
        if(typenum.eq.40) then
          iper(4)=.true.
          read(quant,*) vdropx
        end if
        if(typenum.eq.41) then
          iper(5)=.true.
          read(quant,*) vdropy
        end if
        if(typenum.eq.42) then
          iper(6)=.true.
          read(quant,*) vdropz
        end if
        if(typenum.eq.43) then
          read(quant,*) atompotdist
        end if
        if(typenum.eq.44) then
          read(quant,*) temperature
c		conversion from Celsius to absolute
	    temperature=temperature+273.15
        end if
c e+++++++++++++++++++++++++++++
	return
	end
c
c ***************************************************************
	subroutine yesno(type,ieq1,quant,ieq2,itf)
c
	character*20 quant
	character*30 type
	logical itf
	itf=.false.
c
c	write(6,*) type,ieq1
c	write(6,*) quant,ieq2
	j=index(quant,"TRUE")
	if(j.ne.0) then
	itf=.true.
	if(quant(1:ieq2).ne."TRUE") goto 80
	goto 90
	end if
	j=index(quant,"YES")
	if(j.ne.0) then
	itf=.true.
	if(quant(1:ieq2).ne."YES") goto 80
	goto 90
	end if
	j=index(quant,"ON")
	if(j.ne.0) then
	itf=.true.
	if(quant(1:ieq2).ne."ON") goto 80
	goto 90
	end if
	j=index(quant,"T")
	if(j.ne.0) then
	itf=.true.
	if(quant(1:ieq2).ne."T") goto 80
	goto 90
	end if
c
	k=index(quant,"FALSE")
	if(k.ne.0) then
	itf=.false.
	if(quant(1:ieq2).ne."FALSE") goto 80
	goto 90
	end if
	k=index(quant,"OFF")
	if(k.ne.0) then
	itf=.false.
	if(quant(1:ieq2).ne."OFF") goto 80
	goto 90
	end if
	k=index(quant,"NO")
	if(k.ne.0) then
	itf=.false.
	if(quant(1:ieq2).ne."NO") goto 80
	goto 90
	end if
	k=index(quant,"F")
	if(k.ne.0) then
	itf=.false.
	if(quant(1:ieq2).ne."F") goto 80
	goto 90
	end if
c
	write(6,*) "!!!!!!!!!!!!!!"
	write(6,*) "Could not assign a value to the field ",quant(1:ieq2
     &  )
	write(6,*) "for the statement type ",type(1:ieq1)
	write(6,*) "!!!!!!!!!!!!!!"
	goto 90
c
80	continue
	write(6,*) "!!!!!!!!!!!!!!"
	write(6,*) "Spurious characters found in the field ",quant(1:ieq
     &  2)
	write(6,*) "for the statement type ",type(1:ieq1)
	if(itf) write(6,*) "which was never the less set to be true"
	if(.not.itf) write(6,*) "which was never the less set to be fals
     &  e"
	write(6,*) "!!!!!!!!!!!!!!"
c
90	return
	end
c **************************************************************
	subroutine namleb(fname,nlen)
	character*80 fname
	integer nlen
	i=80
100	if(i.eq.0) then
	nlen=0
	goto 200
	end if
	if(fname(i:i).ne.' ') then
	nlen=i
	goto 200
	else
	i=i-1
	goto 100
	end if
200	continue
	return
	end
