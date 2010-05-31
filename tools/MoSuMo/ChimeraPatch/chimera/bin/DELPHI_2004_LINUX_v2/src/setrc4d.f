	subroutine setrc(natom,*,nmedia,nobject,ndistr,ionlymol)
c
	include "qdiffpar4.h"
	include "qlog.h"
c
	character*80 line,filnam
	character*6 head
	character*5 atnum 
	character*24 crdstr
	character*13 radstr
	dimension atpos(3*1),rad3(1),chrgv4(1),xo(3)
	logical ifrm,iatinf,iatrad,iatcrg
	character*15 atinf(1)
c b++++++++++++++++++++
        integer nmedia,nobject,ndistr
	  logical ionlymol
c e++++++++++++++++++++
204	format(a80)
205	format(3f8.3)
206     format(F6.2,F7.3)
c
	write(6,*) "assigning charges and radii..."
	write(6,*) " "
	natom=0
c
c begin read
c b++++++++++++++++++++
	call getatm(pdbnam,pdblen,ifrm,idfrm,iatinf,iatrad,iatcrg,natom,
     &  nmedia,nobject,ndistr,ionlymol,repsin,epkt)
c e++++++++++++++++++++
c
	if(.not.iatrad) then
c
	do i=1,natom
c
	  atm = atinf(i)(1:5)
	  res = atinf(i)(7:9)
	  rnum = atinf(i)(12:15)
	  chn = atinf(i)(11:11)
c
	  call up(atm,6)
	  call elb(atm,6)
	  call up(res,3)
	  call elb(res,3)
	  call up(rnum,4)
	  call elb(rnum,4)
	  call up(chn,1)
	  call elb(chn,1)
c
c assign radius, searching for decreasingly specific specification
c ending with generic atom type
c note all atoms must have an assignment
c
	call radass(atm,res,rnum,chn,rad,norad)
c
	if(norad.eq.1) then
	rad=0.0
	if(atm(1:1).ne.'H')
     &	write(6,'(''!!! WARNING: no radius record for '',a15)')atinf(i)
c
c need stop here
c
	elseif(rad.lt.1.e-6.and.(atm(1:1).ne.'H'.and.atm(2:2).ne.'H'))
     &  then 
        write(6,'(''!!! WARNING: radius of heavy atom'',a15,''
     &	is set to zero'')')atinf(i)
	end if
c
c store rad,xn in rad3,  for later use
c
	rad3(i)=rad
c
c scale and assign charge to grid
c
	  call crgass(atm,res,rnum,chn,chrgv)
	  chrgv4(i)=chrgv
c
	end do
c
c write record to new coordinate file if required, with
c occupancy and temperature factor fields replaced by radius and charge
c
	end if
c
c check charge assignments (Sri April 2, 1996)
	call chkcrg(natom,atinf,chrgv4)
c unformatted write...
	  if(ipdbwrt) then
	open(20,file=updbnam(:updblen),form='unformatted')
	do i=1,natom
c	xo(1)=atpos(1,i)
c	xo(2)=atpos(2,i)
c	xo(3)=atpos(3,i)
	xo(1)=atpos(3*i-2)
	xo(2)=atpos(3*i-1)
	xo(3)=atpos(3*i)
	rad=rad3(i)
	chrgv=chrgv4(i)
	write(20) xo,rad,chrgv
	end do
	close(20)
	  end if
c 
	  if(iatout) then
c
          open(19,file=mpdbnam(:mpdblen))
c
          filnam = ' '
          inquire(19,name = filnam)
          write(6,*)
     &	  'atomic coordinates, charges and radii written to file'
          write(6,*)filnam
          write(6,*)'   '
	  write(19,*)'DELPHI PDB FILE'
	  write(19,*)'FORMAT = 1'
          write(19,*)'HEADER output from qdiff'
          write(19,*)'HEADER atom radii in columns 55-60'
          write(19,*)'HEADER atom charges in columns 61-67'
c
	line=' '
	line(1:11)="ATOM       "
	do i=1,natom
	rad=rad3(i)
	chrgv=chrgv4(i)
c	xo(1)=atpos(1,i)
c	xo(2)=atpos(2,i)
c	xo(3)=atpos(3,i)
	xo(1)=atpos(3*i-2)
	xo(2)=atpos(3*i-1)
	xo(3)=atpos(3*i)
	line(12:26)=atinf(i)
	write(radstr,206)rad,chrgv
	write(crdstr,205)xo
	line(55:67) = radstr
	line(31:54) = crdstr
	line(27:30)='    '
	write(19,204)line
	end do
	close(19)
	  end if
c
	if((natom.eq.0).and.(nobject.eq.0)) goto 903
	return
903	write(6,*) "exiting due to non-existence of atom file 
     &  nor object data"
	return 1
	end
