c----------------------------------------------------------------
      function irhash(atxt,rtxt)
c	
c produce hash number from atom and residue name
c for radius assignment
c	
	include 'qdiffpar4.h'
c	include 'qdiffpar1.h'
c---------------------------------------------------

      character*6 atxt
      character*3 rtxt
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
	n = iabs(n)
      irhash = mod(n,nrlist) + 1
      return
      end

