c-------------------------------------------------------
      subroutine gtoc(g,c)
c
c converts grid to real coordinates
c
	include 'qdiffpar4.h'
	include 'qlog.h'
c---------------------------------------------------

c
      dimension g(3),c(3)
	goff = (igrid + 1.)/2.
      do 9000 i = 1,3
         c(i) = (g(i) - goff)/scale + oldmid(i)
c      end do
9000	continue
      return
      end

c-------------------------------------------------------
c-------------------------------------------------------
      subroutine ctog(c,g)
c
c converts real to grid coordinates
c
	include 'qdiffpar4.h'
	include 'qlog.h'
c---------------------------------------------------
c
      dimension g(3),c(3)

	goff = (igrid + 1.)/2.
      do 9000 i = 1,3
         g(i) = (c(i) - oldmid(i))*scale + goff
c      end do
9000	continue
      return
      end
