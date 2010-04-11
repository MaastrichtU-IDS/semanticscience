      subroutine cfind(atm,res,rnum,chn,ifind,n)
c
c	find entry nres in hash table and check match with res
c
	include 'qdiffpar4.h'
c#	include "qdiffpar1.h"
c	character*1 chn
c	character*3 res
c	character*4 rnum
c	character*6 atm
c
      n = ichash(atm,res,rnum,chn)
c
c	write(6,*) chn,res,rnum,atm,n
c	check for match
      ifind = 0
100   continue
c	while no match and not at end of link list
      if(icnumb(n).eq.0) then !no match
        ifind = 0
        return
      end if

      if((res.eq.crnam(icnumb(n))).and.(atm.eq.catnam(icnumb(n)))
     &  .and.(rnum.eq.crnum(icnumb(n))).and.(chn.eq.cchn(icnumb(n)))) 
     &  then
        n = icnumb(n)
        ifind = 1
        return
      else
        if(iclink(n).ne.0) then
          n = iclink(n)
        else
          ifind = 0
          return
        end if
      end if
      go to 100
c
c
	end
