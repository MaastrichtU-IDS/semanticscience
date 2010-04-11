c------------------------------------------------------------------
      subroutine rent(atm,res,rnum,chn,nent)
c
c enter character strings res,atm into hash table for radii
c by assigning it a number nent
c
	include 'qdiffpar4.h'
c
c check to see if there is room
c
	if(irtot.eq.nrlist) then
	  write(6,*)' radii list full- increase nrlist'
	  stop 
	end if

	n = ichash(atm,res,rnum,chn)
	if(irnumb(n).ne.0) then
c
c slot filled
c run down linked list
c
9000	continue
	if(irlink(n).eq.0)goto 9001
            n = irlink(n)
	goto 9000
9001	continue
c
c  search for empty slot
c
         new = 1
9002	continue
	if(irnumb(new).eq.0)goto 9003
            new = new + 1
	goto 9002
9003	continue
c
c found one- add link
c
         irlink(n) = new
         n = new
      end if

c
c slot empty
c fill slot
c
      irnumb(n) = nent
      irlink(n) = 0
	irtot = irtot + 1
      return
      end
