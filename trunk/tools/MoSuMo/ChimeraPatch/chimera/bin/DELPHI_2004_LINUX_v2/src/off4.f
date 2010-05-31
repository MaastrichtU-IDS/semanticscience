	subroutine off(oldmid,pmid,*)
c
	include "qlog.h"
c
	real oldmid(3),pmid(3),summid(3),tempmid(3)
	character*80 line
	character*6 head
	character*24 crdstr
c
204	format(a80)
205	format(3f8.3)
c
	if(iacent) then
	oldmid(1)=acent(1)
	oldmid(2)=acent(2)
	oldmid(3)=acent(3)
	goto 900
	end if
c
	do 2108 i = 1,3
	  oldmid(i) = pmid(i) - offset(i)/scale
2108	continue
c
        if((offset(1).eq.999).or.(offset(1).eq.777)) then
	if(offset(1).eq.999) write(6,*)
     &       'modifying midpoints using frc input file'
	if(offset(1).eq.777) write(6,*)
     &       'modifying midpoints using fort.27'
	summid(1)=0.0
	summid(2)=0.0
	summid(3)=0.0
	frcnum=0.0
        if(offset(1).eq.999) open(15,file=centnam(:centlen),status='old'
     &  ,err=903)
        if(offset(1).eq.777) open(unit=27,status='old',err=903)
1124    continue
	if(offset(1).eq.999) read(15,204,end=828)line
	if(offset(1).eq.777) read(27,204,end=828)line
        head = line(1:6)
	  call up(head,6)
c
c skip header lines
c
          if((head.ne.'ATOM  ').and.(head.ne.'HETATM')) then
	    go to 1124
	  end if
	  frcnum=frcnum + 1.0
	  crdstr = line(31:54)
	read(crdstr,205)tempmid
	summid(1)=summid(1)+tempmid(1)
	summid(2)=summid(2)+tempmid(2)
	summid(3)=summid(3)+tempmid(3)
	if((offset(2).eq.999).or.(offset(2).eq.777)) goto 828
	goto 1124
828	continue
	if(frcnum.gt.0.0) then
	oldmid(1)=summid(1)/frcnum
	oldmid(2)=summid(2)/frcnum
	oldmid(3)=summid(3)/frcnum
	else
	if(offset(1).eq.999) write(6,*) 'frc file empty of atoms for'
	if(offset(1).eq.777) write(6,*) 'unit 27 empty of atoms for'
	write(6,*) 
     &	'midpoint determination therefore assuming zero offsets'
	oldmid(1)=oldmid(1) + offset(1)/scale
	oldmid(2)=oldmid(2) + offset(2)/scale
	oldmid(3)=oldmid(3) + offset(3)/scale
	end if
c
	if(offset(1).eq.999) close(15)
	if(offset(1).eq.777) close(27)
        end if
c
900	continue
	return
903 	write(6,*) 
     &	"nonexistence of atom file, for calculating midpoints"
	return 1
c
	end
