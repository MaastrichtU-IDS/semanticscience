	subroutine extrm(natom,igrid,cmin,cmax,nobject)
c
        include 'pointer.h'
	real atpos(3,natom),rad3(natom),cmax(3),cmin(3)
c b++++++++++++++++++++++++++++++++++++++++
        integer nobject,ii
        character*80 dataobject(nobject,2)
        character*80 strtmp
        real limobject(nobject,3,2)
c e++++++++++++++++++++++++++++++++++++++++
         
c
c find extrema and calculate scale according to them and
c to the percent box fill
c 
	cmin(1)=6000
	cmin(2)=6000
	cmin(3)=6000
	cmax(1)=-6000
	cmax(2)=-6000
	cmax(3)=-6000
	do 2103 ix=1,natom
	cmin(1)=min(cmin(1),atpos(1,ix)-rad3(ix))
	cmin(2)=min(cmin(2),atpos(2,ix)-rad3(ix))
	cmin(3)=min(cmin(3),atpos(3,ix)-rad3(ix))
	cmax(1)=max(cmax(1),atpos(1,ix)+rad3(ix))
	cmax(2)=max(cmax(2),atpos(2,ix)+rad3(ix))
	cmax(3)=max(cmax(3),atpos(3,ix)+rad3(ix))
2103	continue 
c
c b++++++++++++++++++++
c find global extrema, both, molecule and objects, are considered
        do ii=1,nobject
          strtmp=dataobject(ii,1)
          if ((strtmp(1:4).ne.'is a')) then
            cmin(1)=min(cmin(1),limobject(ii,1,1))
            cmin(2)=min(cmin(2),limobject(ii,2,1))
            cmin(3)=min(cmin(3),limobject(ii,3,1))
            cmax(1)=max(cmax(1),limobject(ii,1,2))
            cmax(2)=max(cmax(2),limobject(ii,2,2))
            cmax(3)=max(cmax(3),limobject(ii,3,2))
          end if
        end do
c e+++++++++++++++++++        
999	continue
	return
	end
