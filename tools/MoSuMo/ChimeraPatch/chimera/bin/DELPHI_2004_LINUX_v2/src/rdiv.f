	subroutine rdiv(igrid,icount2b,ibc,sppos,spdiv,cgbp,cgrid,
     &                 ergsrea)
c
        real cgbp(5,ibc)
	dimension cgrid(igrid,igrid,igrid)
	integer sppos(3,icount2b)
	dimension spdiv(icount2b)
        real ergsrea
c
	do i=1,icount2b
	  ix=sppos(1,i)
	  iy=sppos(2,i)
	  iz=sppos(3,i)
	  cgrid(ix,iy,iz)=spdiv(i)
	end do
c
	do i=1,ibc
	  ix=cgbp(1,i)
	  iy=cgbp(2,i)
	  iz=cgbp(3,i)
	  cgrid(ix,iy,iz)=cgrid(ix,iy,iz)-cgbp(4,i)
c b++++++++++++++++++++++++++++++++++++++++++++++
c NO LONGERthe self reaction energy close to surface is not counted twice
c         ergsrea=ergsrea-cgbp(6,i)
c e++++++++++++++++++++++++++++++++++++++++++++++
	end do
c
	do i=1,icount2b
	  ix=sppos(1,i)
	  iy=sppos(2,i)
	  iz=sppos(3,i)
	  spdiv(i)=cgrid(ix,iy,iz)
	end do
c
c
	return
	end
