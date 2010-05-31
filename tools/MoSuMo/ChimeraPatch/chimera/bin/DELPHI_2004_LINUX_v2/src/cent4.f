c------------------------------------------------------------------
c------------------------------------------------------------------
      subroutine cent(atm,res,rnum,chn,nent)
c
c enter character strings res,atm,rnum,chn into hash table for charges
c by assigning it a number nent
c
	include 'qdiffpar4.h'
c
c	write(6,*) atm,res,rnum,chn,nent
c check to see if there is room
c
	if(ictot.eq.nclist) then
	  write(6,*)'charge list full- increase nclist'
	  stop
	end if

	n = ichash(atm,res,rnum,chn)
	if(icnumb(n).ne.0) then
c
c slot filled
c run down linked list
c
9000	   continue
	   if(iclink(n).eq.0)goto 9001
c         do while(iclink(n).ne.0)
            n = iclink(n)
c         end do            
	   goto 9000
9001	   continue
c
c  search for empty slot
c
         new = 1
9002	   continue
	   if(icnumb(new).eq.0)goto 9003
c         do while(icnumb(new).ne.0)
            new = new + 1
c         end do
    	   goto 9002
9003     continue

c
c found one- add link
c
         iclink(n) = new
         n = new
      end if

c
c slot empty
c fill slot
c
      icnumb(n) = nent
      iclink(n) = 0
	ictot = ictot + 1
      return
      end

