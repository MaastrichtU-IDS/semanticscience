	subroutine wrtsurf(fname,flen, mid, vert, vtot,
     &	vindx, itot, vnor)
	include 'qlog.h'
c
	character*80 line(5),fname,pname
	integer vtot,itot,flen,i,k
	real mid(3)
c
	real vert(3,vtot),vnor(3,vtot)
	integer vindx(3*itot)
c
c
c NB scale and igrid only used if no bscale, and for picking purposes
c
c	copy vindx4 (int*4) to vindx(int*2) since int*2/4 affects
c	unformatted output
c
c	do i = 1, 3*itot
c		vindx(i) = vindx4(i)
c	end do
c
c form header
c
	if(.not.ibem)then
	write(6,*) "writing GRASP file to ",fname(:flen)
	do i=1,5
	    line(i)=" "
	end do

	line(1)="format=2"
	line(2)="vertices,normals,triangles"
	line(3)=" "
	write(line(4),'(3i6,f12.6)') vtot,itot,igrid,scale
	write(line(5),'(3f12.6)') mid(1),mid(2),mid(3)
c
c NB, from 6/14/92 output surface coordinates in angstroms..
c
	open(20,file=fname(:flen),form="unformatted")
c
	do i=1,5
	    write(20)line(i)
	end do	
c
	write(6,*) "writing data for ",vtot, "vertices and ", 
     &	itot, " triangles"
c
	call wrtr4(vert,3*vtot,20)
	call wrtr4(vnor,3*vtot,20)
	call wrti2(vindx,3*itot,20)
c
	close(20)
80	format(a80)
c
	write(6,*) "finished writing ",fname(:flen)
c
	else
	open(7,file="bem.srf")
	write(7,*)vtot,itot
        do i=1,vtot
        write(7,*)(vert(k,i),k=1,3)
        end do
        do i=1,itot
        write(7,*)(vindx(3*i-3+k),k=1,3)
        end do
        do i=1,vtot
        write(7,*)(vnor(k,i),k=1,3)
        end do
	close (7)

	endif
	return
	end

	subroutine wrtr4(r4,i,if)
c
	dimension r4(i)
c
	write(if) r4
c
	return
	end
c
        subroutine wrti4(i4,i,if)
c
        integer*4 i4(i)
c
        write(if) i4
c
        return
        end
c
        subroutine wrti2(i2,i,if)
c
        integer i2(i)
c
        write(if) i2
c
        return
        end
