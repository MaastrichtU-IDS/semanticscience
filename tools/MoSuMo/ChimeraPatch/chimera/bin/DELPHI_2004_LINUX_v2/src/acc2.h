	include 'pointer.h'
	parameter(idmax=50)
	real r0(1),r02(1),rs2(1)
	common/index1/lcb,mcb,ncb,xo,yo,zo,cbai
	common/index2/lcb1,mcb1,ncb1,mnx,mny,mnz,grdi
	integer ast(1),extot
	real expos(3,1),mnx,mny,mnz,tary(2)
	common/extrem/cmin,cmax,rdmx
	real cmin(3),cmax(3)
c b+++++++++++++++++++++++++++++++++
        real sideinter,sidemin
        common/objver/sideinter,sidemin
c e+++++++++++++++++++++++++++++++++++
