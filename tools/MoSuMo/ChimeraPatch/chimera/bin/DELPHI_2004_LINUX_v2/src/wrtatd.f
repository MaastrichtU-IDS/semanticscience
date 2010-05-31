	subroutine wrtadt(perfil,cmin,cmax,cran,oldmid,scale,natom
     &	,nqass,qnet,qplus,cqplus,qmin,cqmin,isolv)
c
	logical isolv
	dimension cmin(3),cmax(3),cran(3),oldmid(3),cqplus(3),cqmin(3)
c
c
	write(6,*)'  '
cwrite(6,*)'box fill      (%):',perfil
cwrite(6,*)'xmin,xmax     (A):',cmin(1),cmax(1)
cwrite(6,*)'ymin,ymax     (A):',cmin(2),cmax(2)
cwrite(6,*)'zmin,zmax     (A):',cmin(3),cmax(3)
cwrite(6,*)'x,y,z range   (A): ',cran(1),cran(2),cran(3)
cwrite(6,*)'scale   (grids/A): ',scale
c       write(6,*)'Lattice box is centered in (A):',oldmid
        write(6,*)'number of atom coordinates read  : ',natom
	if(isolv)then
	write(6,*)'total number of assigned charges    : ',nqass
     	write(6,*)'net assigned charge              : ',qnet
	write(6,*)'assigned positive charge         : ',qplus
	write(6,*)'centred at (gu) :',cqplus
	write(6,*)'assigned negative charge         : ',qmin
	write(6,*)'centred at (gu) :',cqmin
	endif
	write(6,*)'   '
c
	return
	end
