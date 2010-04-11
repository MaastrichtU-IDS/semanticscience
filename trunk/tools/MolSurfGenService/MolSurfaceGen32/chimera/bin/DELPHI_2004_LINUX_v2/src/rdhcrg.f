	subroutine rdhcrg(*)
c
	include "qdiffpar4.h"
c	include "qdiffpar1.h"
	include "qlog.h"
c
c	character*1 chn
c	character*3 res
c	character*4 rnum
c	character*6 atm
c
	character*80 filnam
	character*60 comment
c
	do i=1,nclist
	icnumb(i)=0
	iclink(i)=0
	end do
c
c read charge parameter file and store in hash table
c
	open(12,file=crgnam(:crglen),status='old',err=902)
	write(6,*)' '
	write(6,*)'atomic charges read from file'
	write(6,*)crgnam(:crglen)
	write(6,*)' '
c
c skip/print comments (start with !) and one column header line 
c
106	read(12,201,end=902)comment
	if(comment(1:1).eq.'!') then
	  write(6,*)comment
	  goto 106
	end if
	nchrec = 0
101   continue
	  nchrec = nchrec + 1
	  if(nchrec.gt.ncmax) then
	    write(6,*)' maximum # of charge records exceeded'
	    write(6,*)' - increase ncmax'
	    stop 
	  end if
	  read(12,202,err=905,end=301)atm,res,rnum,chn,chrgv
	  call up(atm,6)
	  call elb(atm,6)
	  call up(res,3)
	  call elb(res,3)
	  call up(rnum,4)
	  call elb(rnum,4)
	  call up(chn,1)
	  call elb(chn,1)
	  catnam(nchrec) = atm
	  crnam(nchrec)  = res
	  crnum(nchrec)  = rnum
	  cchn(nchrec)   = chn
	  chrgvt(nchrec) = chrgv
	  call cent(atm,res,rnum,chn,nchrec)
c	  write(6,*) atm,res,rnum,chn,nchrec
	goto 101
301   continue
	close(12)
201	format(a)
202     format(A6,A3,A4,A1,F8.3)
	nchrec = nchrec - 1 
	write(6,*)'# of charge parameter records:',nchrec
c
	return
902	write(6,*) "nonexistence or unexpected end of chargefile"
        write(6,*)"This is correct in case there are ONLY objects,"
        write(6,*)"or in case some specific delphi pdb format is used!"
	return  
905	write(6,*) "error in reading the charge file, fort.12"
	return 1
	end
