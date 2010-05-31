c----------------------------------------------------------------
      function ichash(atxt,rtxt,ntxt,ctxt)
c	
c produce hash number from atom and residue name,rsidue number and chain
c name for charge assignment
c	
	include 'qdiffpar4.h'
c	include 'qdiffpar1.h'

      character*6 atxt
      character*3 rtxt
      character*4 ntxt
      character*1 ctxt
c
c	character*1 chn
c	character*3 res
c	character*4 rnum
c	character*6 atm
c
      character*38 string
	integer n,irhash,j
      data string /'* 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'/
      n = 1
      do 9000 i = 1,3
        j = index(string,rtxt(i:i))
        n = 5*n + j
c      end do
9000	continue
      do 9001 i = 1,6
        j = index(string,atxt(i:i))
        n = 5*n + j
c      end do
9001	continue
      do 9002 i = 1,4
        j = index(string,ntxt(i:i))
        n = 5*n + j
c      end do
9002	continue
      do 9003 i = 1,1
        j = index(string,ctxt(i:i))
        n = 5*n + j
c      end do
9003	continue
	n = iabs(n)
      ichash = mod(n,nclist) + 1
      return
      end

