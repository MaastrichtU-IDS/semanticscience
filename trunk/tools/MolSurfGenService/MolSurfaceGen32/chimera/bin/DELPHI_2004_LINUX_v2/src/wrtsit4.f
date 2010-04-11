	subroutine wrtsit(nqass,icount2b,xn1,atcrg,rad3a,natm,ibnum,
     &  nmedia,nobject)
c
c write a file containing site potentials and/or fields and/or atom
c information. adapted april 92 to enable flexible output/input
c possible fields include atom information, coordinates, charge, potential
c salt concentration, reaction potentials, coulombic potential, and fields
c the default of which is coordinates, charges, potentials and fields.
c
c nqass = number of assigned charges, icount2b= number of boundary elements
c scspos= position in angstroms of induced surface charges
c xn1= positions of all atoms in angstroms, natm=number of atoms
c
	include "qdiffpar4.h"
	include "qlog.h"
c
c
	character*80 filnam
	character*65 datum
	character*80 line,vrow,oline
	character*15 otemp
	character*16 atdes
	character*6 head
	character*24 crdstr
	character*5 atnum
	character*15 atinf(natm)
	dimension xo(3),xn(3),scspos(3,icount2b),xn1(3,natm),atcrg(natm)
	dimension rfield(3,1),bedge(2,3),xu(3),trgelf(3)
	dimension xu2(3),xo2(3),scomp(30),sold(30)
	logical ifrm,ifrm2,iext,iqass,ofrm
	integer ibgrd(3,icount2b)
	integer crgatn(1)
c b+++++++++++++++++++++++
      integer nmedia,nobject,noradu
      real medeps(0:nmedia),atmeps(nqass),rad3a(natm),xt(3)
      real atmcrg(4,nqass),chgpos(3,nqass),aphi,radu,rads
	real atmforce(3,1)
      logical isitmp
c e+++++++++++++++++++++++
c
	i_rfield= memalloc(i_rfield,4*3*ibnum)
c initialize some parameters
	atdes=" "
	phirt=0
	phict=0
	sixth=1.0/6.0
	iqass=.true.
	ofrm=.true.
c
	bedge(1,1)=oldmid(1)-0.5*(igrid-1)/scale
	bedge(2,1)=oldmid(1)+0.5*(igrid-1)/scale
	bedge(1,2)=oldmid(2)-0.5*(igrid-1)/scale
	bedge(2,2)=oldmid(2)+0.5*(igrid-1)/scale
	bedge(1,3)=oldmid(3)-0.5*(igrid-1)/scale
	bedge(2,3)=oldmid(3)+0.5*(igrid-1)/scale
c
c ifrm is true if ANY of the flags for special output have been set
        ifrm=isita.or.isitq.or.isitp.or.isitf.or.isitr.or.isitt
	ifrm=ifrm.or.isitc.or.isitx.or.isiti.or.isitrf.or.isitcf
c b++++++++++++isitap=site atomic potential	
	ifrm=ifrm.or.isitap.or.isittf
c +++++++++++++isitmd=site reaction and coulombic fields for molecular dynamics
	if (isitmd) then
	  i_atmforce= memalloc(i_atmforce,4*3*natm)
	  frcfrm=-1
	  ofrm=.false.
	end if
c e++++++++++++++++++++++++++++++++++++++++
c
	if((.not.ifrm).and.((frcfrm.eq.0).or.(frcfrm.eq.3))) then
c set default to standard frc file
	  isitx=.true.
	  isitq=.true.
	  isitf=.true.
	  isitp=.true.
	end if
c
	if(frcfrm.eq.1) then
	  isitx=.true.
	  isitq=.true.
	  isitr=.true.
	  isitc=.true.
	end if
c
	if(frcfrm.eq.2) then
	  isitx=.true.
	  isitq=.true.
	  isitr=.true.
	end if
c
	if(frcfrm.eq.3) then
	  ofrm=.false.
	end if
c
	vrow=' '
	datum=' '
	j=1
	k=1
	if(isita) then
	  datum(k:k+4)="ATOM "
	  vrow(j:j+14)="ATOM DESCRIPTOR"
	  j=j+20
	  k=k+5
	end if
	if(isitx) then
	  vrow(j+4:j+27)="ATOM COORDINATES (X,Y,Z)"
	  datum(k:k+11)="COORDINATES "
	  k=k+12
	  j=j+30
	end if
	if(isitq) then
	  vrow(j+3:j+8)="CHARGE"
	  datum(k:k+6)="CHARGE "
	  k=k+7
	  j=j+10
	end if
	if(isitp) then
	  vrow(j+2:j+9)="GRID PT."
	  datum(k:k+10)="POTENTIALS "
	  k=k+11
	  j=j+10
	end if
	if(isiti) then
	  vrow(j+1:j+8)="SALT CON"
	  datum(k:k+4)="SALT "
	  j=j+10
	  k=k+5
	end if
	if(j.gt.80) then
	  isitr=.false.
	  isitc=.false.
c b+++++++++++++++++++++++++++++++++++++++
	  isitap=.false.
	  isittf=.false.
c e+++++++++++++++++++++++++++++++++++++++
	  isitf=.false.
	  isitrf=.false.
	  isitcf=.false.
	  isitt=.false.
	end if
	if(isitr) then
	  vrow(j:j+9)=" REAC. PT."
	  datum(k:k+8)="REACTION "
	  k=k+9
	  j=j+10
	end if
	if(j.gt.80) then
	  isitc=.false.
c b+++++++++++++++++++++++++++++++++++++++
	  isitap=.false.
	  isittf=.false.
c e+++++++++++++++++++++++++++++++++++++++
	  isitf=.false.
	  isitrf=.false.
	  isitcf=.false.
	  isitt=.false.
	end if
	if(isitc) then
	  vrow(j:j+9)=" COUL. POT"
	  datum(k:k+9)="COULOMBIC "
	  k=k+10
	  j=j+10
	end if

c b+++++++++++++++++++++++++++++++++++++++
	if(j.gt.80) then
	  isitap=.false.
	  isitf=.false.
	  isitrf=.false.
	  isitcf=.false.
	  isittf=.false.
	  isitt=.false.
	end if
	if(isitap) then
	  vrow(j+2:j+9)="ATOM PT."
	  datum(k:k+10)="ATOMIC PT. "
	  k=k+11
	  j=j+10
	end if
c e+++++++++++++++++++++++++++++++++++++++

	if(j.gt.60) then
	  isitf=.false.
	  isitrf=.false.
	  isitcf=.false.
c b+++++++++++++++++++++++++++++++++++++++
	  isittf=.false.
c e+++++++++++++++++++++++++++++++++++++++
	  isitt=.false.
	end if

	if(isitf) then
	  vrow(j+4:j+28)="GRID FIELDS: (Ex, Ey, Ez)"
	  datum(k:k+5)="FIELDS "
	  j=j+30
	end if
	if(j.gt.60) then
	  isitrf=.false.
	  isitcf=.false.
c b+++++++++++++++++++++++++++++++++++++++
	  isittf=.false.
c e+++++++++++++++++++++++++++++++++++++++
	  isitt=.false.
	end if

	if(isitrf) then
	  vrow(j+4:j+28)="REAC. FORCE: (Rx, Ry, Rz)"
	  datum(k:k+5)="RFORCE "
	  j=j+30
	end if
      if(j.gt.60) then
        isitcf=.false.
c b+++++++++++++++++++++++++++++++++++++++
	  isittf=.false.
c e+++++++++++++++++++++++++++++++++++++++
	  isitt=.false.
      end if

      if(isitcf) then
        vrow(j+4:j+28)="COUL. FORCE: (Cx, Cy, Cz)"
        datum(k:k+5)="CFORCE "
        j=j+30
      end if
      if(j.gt.60) then
c b+++++++++++++++++++++++++++++++++++++++
	  isittf=.false.
c e+++++++++++++++++++++++++++++++++++++++
	  isitt=.false.
      end if

      if(isittf) then
        vrow(j+4:j+28)="TOTAL FORCE: (Tx, Ty, Tz)"
        datum(k:k+5)="TFORCE "
        j=j+30
      end if
      if(j.gt.70) then
        isitt=.false.
      end if

	if(isitt) then
	  vrow(j+4:j+9)=" TOTAL"
	  datum(k:k+5)="TOTAL "
	  j=j+10
	end if
c
c if site potentials required and unformatted read/write, skip
c during formatted frc file read/write can write unformatted frc.pdb
c
        pot=0.0
        ex=0.0
        ey=0.0
        ez=0.0
        cx=0.0
	cy=0.0
	cz=0.0
c
c open files, write to log file..
        write(6,*)'  '
        write(6,*)'writing potentials at given sites...'
	write(6,*)'  '
c
	if(iself) then
	  write(6,*) "using the current pdb file"
	  ifrm2=.true.
	  iqass=.false.
	else
	  inquire(file=frcinam(:frcilen),exist=iext)
	  if(.not.iext) then
	    write(6,*) "the input frc file ",frcinam(:frcilen)," does 
     &not exist"
	    write(6,*) "exiting..."
	  else
            write(6,*)'coordinates, etc for potential output read from
     & file'
	    write(6,*)frcinam(:frcilen)
	    write(6,*)'  '
	  end if
	  call form(frcinam,frcilen,ifrm2)
	end if
c
c if unformatted may not contain all the info needed for all options, i.e
c atom info
	if((.not.ifrm2).and.(isita)) then
	  write(6,*) "atom info flag turned off cos this unformatted
     &file does"
	  write(6,*) "not contain atom info"
	  isita=.false.
	  iqass=.false.
	end if
c
	if(.not.ifrm2) iqass=.false.
c
	if(.not.iself) then
          if(ifrm2) open(15,file=frcinam(:frcilen),err=903)
          if(.not.ifrm2)open(15,file=frcinam(:frcilen),
     &form="unformatted",err=903)
	end if
c
        if(ofrm) open(16,file=frcnam(:frclen))
        if(.not.(ofrm.or.isitmd)) then
	    open(16,file=frcnam(:frclen),form="unformatted")
	  end if
	if (.not.isitmd) then 
	  write(6,*)'potentials written to file'
	  write(6,*)frcnam(:frclen)
	  write(6,*)'  '
	end if
c
c write header to file...(10 lines)
c
	if(ofrm) then
          write(16,*)'DELPHI SITE POTENTIAL FILE'
          write(16,*)'grid size,percent fill:',igrid,perfil
          write(16,*)'outer diel. and first one assigned :',repsout,
     &               medeps(1)*epkt
c b+++++++++++++++ mi piacerebbe ma non compatibile con vecchi scripts
c         do i = 1,nmedia
c           write(16,*)'dielectric in medium nr. ',i,':',medeps(i)*epkt
c         end do
c e+++++++++++++++
          write(16,*)'ionic strength (M):',rionst
          write(16,*)'ion excl., probe radii:',exrad,radprb(1),radprb(2)
          write(16,*)'linear, nolinear iterations:',nlit,nnit
          write(16,*)'boundary condition:',ibctyp
          write(16,*)'Data Output: ',datum
          write(16,*)'title: ',toplbl
          write(16,*)'    '
          write(16,*)'    '
	  write(16,204)vrow
	end if
c
	if((.not.ofrm).and.(.not.isitmd)) then
	  line=" "
	  line="DELPHI FRC FILE"
	  write(16) line
	  line=" "
	  line="FORMAT NUMBER=1"
	  write(16) line
	  line=" "
	  line(1:5)="DATA="
	  line(6:70)=datum
	  write(16) line
	  line=" "
	  write(line,'(i5,3f10.4)') igrid,perfil,repsout,rionst
	  write(16) line
c b+++++++++++++++
          do i = 1,nmedia
            write(6,*)'dielectric in medium nr. ',i,':',medeps(i)*epkt
          end do
c e+++++++++++++++
	  line=" "
	  write(line,'(3f10.4,3i5)') exrad,radprb,nlit,nnit,ibctyp
	  write(16) line
	end if
c
c write 2 formatting lines
c
c read atom coordinate file
c
	etot = 0.
	natom = 0
	chrgv=0.0
c
	if((.not.iself).and.(isitrf.or.isitmd.or.isittf)) then
	  write(6,*)"WARNING! Cannot calculate reaction forces without"
	  write(6,*) "WARNING! Using internal (self) coordinates"
	  isitrf=.false.
	  isittf=.false.
	  isitmd=.false.
	end if
c
	if(isitrf.or.isitmd.or.isittf) then
	  if (nmedia.eq.1.and.abs(medeps(1)-epkt).lt.1.e-6)then
c b+++++++++++++++++++++++++++++++++++++++
	    call rforceeps1(rfield,natm,scspos,schrg,atsurf,
     &    icount2b,atmcrg,xn1,chgpos,nqass,crgatn,nobject)
c b+++++++++++++++++++++++++++++++++++++++
	  else
	    call rforce(rfield,natm,scspos,schrg,atsurf,
     &    icount2b,atmcrg,xn1,chgpos,nqass,crgatn,nobject)
	  end if
	end if
104     continue

c beginning of the big loop on natom
	if(iself) then
	  if(natom.eq.natm) goto 304
	  natom=natom+1
  	  xo(1)=xn1(1,natom)
	  xo(2)=xn1(2,natom)
	  xo(3)=xn1(3,natom)
	  chrgv=atcrg(natom)
c b+++++++++++++++++++++++++++++++++++++++
        radu=rad3a(natom)*scale
c e+++++++++++++++++++++++++++++++++++++++
          atm = atinf(natom)(1:4)
          res = atinf(natom)(7:9)
          rnum = atinf(natom)(12:15)
          chn = atinf(natom)(11:11)
	else
	  if(ifrm2) then
            read(15,204,end=304)line
            head = line(1:6)
	    call up(head,6)
            if((head.ne.'ATOM  ').and.(head.ne.'HETATM')) goto 104
	    natom = natom + 1
	    crdstr = line(31:54)
	    atnum  = line(7:11)
c positions, atom number 
c non ho l'informazione concernente il raggio
	    read(crdstr,205)xo
	    read(atnum,209)inum
	  else
	    read(15,end=304) xo,radu,chrgv
	    natom=natom+1
	  end if
	end if
c end of atom read..
c
      isitmp=(isitq.and.iqass).or.isitap.or.isitp
	if((isita.or.isitmp).and..not.iself) then
	  atm = line(12:16)
	  res = line(18:20)
	  rnum = line(23:26)
	  chn = line(22:22)
	  call up(atm,6)
	  call elb(atm,6)
	  call up(res,3)
	  call elb(res,3)
	  call up(rnum,4)
	  call elb(rnum,4)
	  call up(chn,1)
	  call elb(chn,1)
	end if
c
c scale atoms to grid space
c
	call ctog(xo,xn)
	if(isita) then
	  atdes(1:4)=atm(1:4)
	  atdes(6:8)=res(1:3)
	  atdes(12:15)=rnum(1:4)
	  atdes(10:10)=chn(1:1)
	end if
c
c assignchargeto atom, searching for decreasingly specific specification
c note if no charge record found, is assumed to be 0.0
c
c b+++++++++++++++++++++++++++++++++++++++++++++++++
      if((.not.iself.and.ifrm2).and.isitmp)then
	  chrgv=0.0
	  call crgass(atm,res,rnum,chn,chrgv)
	  if(isitap) call radass(atm,res,rnum,chn,radu,noradu)
	  radu=radu*scale
	end if
c e+++++++++++++++++++++++++++++++++++++++++++++++++
c
        if(isitap.and.abs(chrgv).ge.1.e-6) then
          rads=amin1(radu,atompotdist*scale)
	    xt(1)=xn(1)+rads
	    xt(2)=xn(2)
	    xt(3)=xn(3)
	    call phintp(xt,vphi)
          aphi=vphi
c          write(6,*)'aphi 1=',aphi

	    xt(1)=xn(1)-rads
	    xt(2)=xn(2)
	    xt(3)=xn(3)
	    call phintp(xt,vphi)
          aphi=aphi+vphi
c          write(6,*)'aphi 2=',aphi

	    xt(1)=xn(1)
	    xt(2)=xn(2)+rads
	    xt(3)=xn(3)
	    call phintp(xt,vphi)
          aphi=aphi+vphi
c          write(6,*)'aphi 3=',aphi

	    xt(1)=xn(1)
	    xt(2)=xn(2)-rads
	    xt(3)=xn(3)
	    call phintp(xt,vphi)
          aphi=aphi+vphi
c          write(6,*)'aphi 4=',aphi

	    xt(1)=xn(1)
	    xt(2)=xn(2)
	    xt(3)=xn(3)+rads
	    call phintp(xt,vphi)
          aphi=aphi+vphi
c         write(6,*)'aphi 5=',aphi

	    xt(1)=xn(1)
	    xt(2)=xn(2)
	    xt(3)=xn(3)-rads
	    call phintp(xt,vphi)
c          write(6,*)'aphi 6=',aphi

          aphi=(aphi+vphi)/6.
c         write(6,*)'aphi M=',aphi
c          write(6,*)' '
	  end if

        if(isitp.or.isiti.or.(isitap.and.abs(chrgv).lt.1.e-6))then
	  call phintp(xn,vphi)
	  if(isitap.and.abs(chrgv).lt.1.e-6) aphi=vphi
	  if(isitp) then
          qphiv = chrgv*vphi
	    etot = etot + qphiv
	    phiv=vphi
	  end if
c
	  if(isiti) then
c NB we have changed the iconc action so that the phimap has NOT been
c converted to salt concentrations. therefore 
            write(6,*)'WRTSIT:these salt concentrations'
            write(6,*)'do NOT have the benefit of idebmap (as yet)'
	    if(nnit.ne.0) then
c b+++++++++++++++++++++
              temp = vphi*chi5 + chi4
              temp = vphi*temp + chi3
              temp = vphi*temp + chi2
              temp = chi1+temp*vphi
              phii = vphi*temp
	    else
	      phii= -rionst*2.0*vphi
c e++++++++++to check+++++++++++++
	    end if
	  end if
c end if isitp or isiti, salt and or potentials
	end if
c
	if(isitf) then
	  xn(1) = xn(1) + 1.
          call phintp(xn,fxu)
	  xn(1) = xn(1) - 2.
          call phintp(xn,fxl)
	  xn(1) = xn(1) + 1.
	  xn(2) = xn(2) + 1.
          call phintp(xn,fyu)
	  xn(2) = xn(2) - 2.
          call phintp(xn,fyl)
	  xn(2) = xn(2) + 1.
	  xn(3) = xn(3) + 1.
          call phintp(xn,fzu)
	  xn(3) = xn(3) - 2.
          call phintp(xn,fzl)
	  xn(3) = xn(3) + 1.
c b+++++++++++Walter OCt 2000
c the electric field is opposite the potential gradient
c so I change the sign
	  fx = (fxl-fxu)*scale/2.
	  fy = (fyl-fyu)*scale/2.
	  fz = (fzl-fzu)*scale/2.
c e+++++++++++++++++++++++++++
	end if
c
	if(isitt) then
c
c check if this point is within the box.
	  it=0
	  if((xo(1).lt.bedge(1,1)).or.(xo(1).gt.bedge(2,1))) it=1
	  if((xo(2).lt.bedge(1,2)).or.(xo(2).gt.bedge(2,2))) it=1	
	  if((xo(3).lt.bedge(1,3)).or.(xo(3).gt.bedge(2,3))) it=1	
c
	  if(it.eq.0) then
	    call ctog(xo,xo2)
c first find reaction field from surface elements inside of the box..
            phir=0.0
	    phias=0.0
	    ncrgs=0
	    tcrgs=0.0
	    do i=1,30
	      sold(i)=0.0
	    end do
c
            do i=1,icount2b
              dist=(xo(1)-scspos(1,i))**2 +(xo(2)-scspos(2,i))**2 +
     &    (xo(3)-scspos(3,i))**2
	      dist=sqrt(dist)
c
c find analytic potential from this induced charge..=phias
	      ncrgs=ncrgs+1
	      tcrgs=tcrgs+schrg(i)
	      phirtt=schrg(i)/dist
c medeps either epsin contain the 561.0 factor....
	      phirtt=phirtt*epkt 
              phir=phir + phirtt
              xu2(1)=ibgrd(1,i)
              xu2(2)=ibgrd(2,i)
              xu2(3)=ibgrd(3,i)
              crgs=schrg(i)
c ++++++++++1 took place of repsin because eps is no more included 
c       in schrg , surface charge
              call tops(xu2,xo2,crgs,1.,scale,phiat,trgelf,1)
	      phiat=phiat*2.0
	      phias=phias+phiat
	      idist=int(dist)+1
	      sold(idist)=sold(idist)+phiat-phirtt
c	write(6,*) phias
            end do
	    temp=0.0
	    write(6,*) "Writing sold(1:30) and temp "
	    do i=1,30
	      temp=temp+sold(i)
	      write(6,*) sold(i),temp
	    end do
	    write(6,*) " "
c
c next find the colombic potential for that site from charges within the box
            phic=0.0
            phiac=0.0
	    ncrg=0
            do i=1,nqass
	      it=0
	  if((chgpos(1,i).lt.bedge(1,1)).or.(chgpos(1,i).gt.bedge(2,1)))
     &  it=1	
	  if((chgpos(2,i).lt.bedge(1,2)).or.(chgpos(2,i).gt.bedge(2,2)))
     &  it=1	
	  if((chgpos(3,i).lt.bedge(1,3)).or.(chgpos(3,i).gt.bedge(2,3)))
     &  it=1	
	      if(it.eq.0) then
	        ncrg=ncrg+1
                dist1=(xo(1)-chgpos(1,i))
                dist2=(xo(2)-chgpos(2,i))
                dist3=(xo(3)-chgpos(3,i))
                dist=dist1**2+dist2**2+dist3**2
                dist=sqrt(dist)
c
	        if(dist.lt.5.0) then
                  if(dist.gt.1.e-6) then
                    temp=atmcrg(4,i)/dist
c b+++++++++++++++++++++++++++++++++++++
                    phic=phic + temp/atmeps(i)
c e+++++++++++++++++++++++++++++++++++++
                  end if
c find analytic potential from this real charge..=phiac
	          xu(1)=chgpos(1,i)
	          xu(2)=chgpos(2,i)
	          xu(3)=chgpos(3,i)
	          crgs=atmcrg(4,i)
	          call ctog(xu,xu2)
                  eps=atmeps(i)*epkt
	          call tops(xu2,xo2,crgs,eps,scale,phiact,trgelf,1)
	          phiac=phiac+phiact
	        end if
c	write(6,*) crgs,repsin,scale,phiac
c	write(6,*) xu(1),xu(2),xu(3),xo(1),xo(2),xo(3)
	      end if
            end do
c medeps, either epsin contain the 561.0 factor....
	    phiac=phiac*2.0
c
c find the grid potentials..
	    call phintp(xn,phiv)
	    open(7,file="extra.dat")
	    write(7,*) phic,phir,phiv,phias,phiac,ncrg,ncrgs,tcrgs
	    close(7)
	    phit=phic+phir+phiv-phias-phiac
	  else
	    phit=0.0
	  end if
c
c phit contains the total corrected potential
c
	end if
c
	if(isitr) then
	  do i=1,30
	    scomp(i)=0.0
	    sold(i)=0.0
	  end do
	  phir=0.
	  do i=1,icount2b
            dist=(xo(1)-scspos(1,i))**2 +(xo(2)-scspos(2,i))**2+
     &    (xo(3)-scspos(3,i))**2
	    dist=sqrt(dist)
	    idist=int(dist)+1
            if(idist.le.30)sold(idist)=sold(idist)+(561.0*schrg(i)/dist)
	    phir=phir + schrg(i)/dist
	  end do
c medeps either epsin contains the 561.0 factor....
	  phir=phir*epkt 
	  do i=1,30
	    if(i.eq.1) scomp(i)=sold(i)
	    if(i.ne.1) scomp(i)=scomp(i-1)+sold(i)
	    write(6,*)'sold(i),scomp(i)', sold(i),scomp(i)
	  end do
	  phirt=phirt+phir*chrgv
	end if
c
	if(isitrf.or.isitmd.or.isittf)then 
c b++++++++++++++++++++++++++++++++++++++++++++
c medeps either epsin contains the 561.0 factor....
	  rx=rfield(1,natom)*epkt 
	  ry=rfield(2,natom)*epkt 
	  rz=rfield(3,natom)*epkt 
c e+++++++++++++++++++++++++++++++++++++++++++++
	end if
c
      if(isitcf.or.isitmd.or.isittf) then
        cx=0.0
        cy=0.0
        cz=0.0
        if(abs(chrgv).gt.1.e-6) then
	    do i=1,nqass
            dist1=(xo(1)-chgpos(1,i))
            dist2=(xo(2)-chgpos(2,i))
            dist3=(xo(3)-chgpos(3,i))
            dist=dist1**2+dist2**2+dist3**2
            if(dist.gt.1.e-6) then
              sdist=sqrt(dist)*dist
c b+++++++++++++++++++++
              temp=atmcrg(4,i)/(atmeps(i)*sdist)
c e+++++++++++++++++++++
              cx=cx+dist1*temp
              cy=cy+dist2*temp
              cz=cz+dist3*temp
            end if
          end do
c atmeps and medeps and epsin contain the 561.0 factor....
	    cx=cx*chrgv
	    cy=cy*chrgv
	    cz=cz*chrgv
	  end if
	end if
c
	if(isitc) then
	  phic=0
	  do i=1,nqass
	    dist1=(xo(1)-chgpos(1,i))
	    dist2=(xo(2)-chgpos(2,i))
            dist3=(xo(3)-chgpos(3,i))
	    dist=dist1**2+dist2**2+dist3**2
	    if(dist.gt.1.e-6) then
	      sdist=sqrt(dist)
	      temp=atmcrg(4,i)/sdist
c b++++++++++++++++++++++++++++
	      phic=phic + temp/atmeps(i)
c e++++++++++++++++++++++++++++
	    end if
	  end do
c atmeps and medeps and epsin contain the 561.0 factor....
	  phict=phict+phic*chrgv
	end if
c
c write out calculated/assigned charges
	oline=' '
	j=1
	if(isita) then
	  oline(j:j+15)=atdes(1:16)
	  j=j+20
	end if
c
c NB need otemp cos can not write into a substring apparently
c NB otemp needs to be at least 15 long to avoid an error!!
200	format(f10.4)
	if(isitx) then
	  write(otemp,200) xo(1)
	  oline(j:j+9)=otemp
	  j=j+10
	  write(otemp,200) xo(2)
	  oline(j:j+9)=otemp
	  j=j+10
	  write(otemp,200) xo(3)
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c
	if(isitq) then
	  write(otemp,200) chrgv
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c
	if(isitp) then
	  write(otemp,200) phiv
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c
	if(isiti) then
	  write(otemp,200) phii
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c
	if(isitr) then
	  write(otemp,200) phir
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c
	if(isitc) then
	  write(otemp,200) phic
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c b+++++++++++++++++++++++++++++
	if(isitap) then
	  write(otemp,200) aphi
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c e+++++++++++++++++++++++++++++
	if(isitf) then
	  write(otemp,200) fx
	  oline(j:j+9)=otemp
	  j=j+10
	  write(otemp,200) fy
	  oline(j:j+9)=otemp
	  j=j+10
	  write(otemp,200) fz
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c
        if(isitrf) then
          write(otemp,200) rx
          oline(j:j+9)=otemp
          j=j+10
          write(otemp,200) ry
          oline(j:j+9)=otemp
          j=j+10
          write(otemp,200) rz
          oline(j:j+9)=otemp
          j=j+10
        end if
c
        if(isitcf) then
          write(otemp,200) cx
          oline(j:j+9)=otemp
          j=j+10
          write(otemp,200) cy
          oline(j:j+9)=otemp
          j=j+10
          write(otemp,200) cz
          oline(j:j+9)=otemp
          j=j+10
        end if

c b+++++++++++++++++++++++++++++
        if(isittf) then
          write(otemp,200) rx+cx
          oline(j:j+9)=otemp
          j=j+10
          write(otemp,200) ry+cy
          oline(j:j+9)=otemp
          j=j+10
          write(otemp,200) rz+cz
          oline(j:j+9)=otemp
          j=j+10
        end if
	  if(isitmd) then
c	    write(6,*)'atom:',natom,'x=',rx+cx
	    atmforce(1,natom)= rx+cx
c         write(6,*)'atom:',natom,'y=',ry+cy
		atmforce(2,natom)= ry+cy
c	    write(6,*)'atom:',natom,'z=',rz+cz
          atmforce(3,natom)= rz+cz
	  end if
c e+++++++++++++++++++++++++++++
c
	if(isitt) then
	  write(otemp,200) phit
	  oline(j:j+9)=otemp
	  j=j+10
	end if
c
	if(ofrm) write(16,204) oline
	if(.not.ofrm) then
	  if(isita) write(16) atdes
	  if(isitx) write(16) xo
	  if(isitq) write(16) chrgv
	  if(isitp) write(16) phiv
	  if(isiti) write(16) phii
	  if(isitr) write(16) phir
	  if(isitc) write(16) phic
c b++++++++++++++++++++++++++++++
	  if(isitap) write(16) aphi
c e++++++++++++++++++++++++++++++
	  if(isitf) write(16) fx,fy,fz
	  if(isitrf) write(16) rx,ry,rz
	  if(isitcf) write(16) cx,cy,cz
c b++++++++++++++++++++++++++++++
	  if(isittf) write(16) rx+cx,ry+cy,rz+cz
c e++++++++++++++++++++++++++++++
	end if
c
        go to 104
c	end of file
304     continue		
c
	if(.not.iself) close(15)
	write(6,*)'   '
	write(6,*)'number of atom coordinates read  : ',natom
	write(6,*)'   '
	etot = etot/2.
	if(ofrm) then
	  if(frcfrm.eq.0)  then
	    write(16,*)'total energy = ',etot,' kt'
	    if(isitap)write(16,*)'Atomic potential for charged atoms is
     & averaged over a spherical surface of less than',atompotdist,'A'
	  end if
	  if(frcfrm.eq.1) then
	    write(16,*) "total reaction field energy= ",phirt/2," kt"
	    write(16,*) "total coulombic energy     = ",phict/2," kt"
            if(isitap)write(16,*)'Atomic potential for charged atoms is
     & averaged over a spherical surface of less than',atompotdist,'A'
	  end if
	  if(frcfrm.eq.2) then
	    write(16,*) "total reaction field energy= ",phirt/2," kt"
            if(isitap)write(16,*)'Atomic potential for charged atoms is
     & averaged over a spherical surface of less than',atompotdist,'A'
	  end if
	end if
	close(16)
c
c end of formatted frc read/write and unformatted frc write
c END of unformatted frc.pdb read and frc write
c
	finish=cputime(start)
	write(6,*) 'frc stuff now done at',finish
c
	goto 904
903	continue
	write(6,*) "error reading the frc input file ",frcinam(:frcilen)
904	continue
c
209	format(I5)
204	format(a80)
205	format(3f8.3)
c206	format(f8.3)
c208	format(G10.3)
c
	i_rfield= memalloc(i_rfield,0)
c
	return
	end
