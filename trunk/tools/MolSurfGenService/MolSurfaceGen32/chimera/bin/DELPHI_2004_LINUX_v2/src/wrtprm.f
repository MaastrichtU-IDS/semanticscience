	subroutine wrtprm(nmedia,cmin,cmax,cran)
c
c b+++++++++++++++++++++++
        include "qdiffpar4.h"
c e+++++++++++++++++++++++
	include "qlog.h"
c
c	character*80 line,filnam,asci,enc
	character*6 head
	character*9 bclab(4)
	character*8 testchar
c b+++++++++++++++++++++++
        real medeps(0:nmedia),cmin(3),cmax(3),cran(3)
c e+++++++++++++++++++++++

c
	data bclab / 'zero     ','dipolar  ',
     &             'focussing','coulombic' /
c
201	format(a)
	write(6,*)'  '
c	write(6,*)'parameters read from file'
c	write(6,*)filnam

	write(6,*)'grid size                  :',igrid
	write(6,*)'percent of box to be filled:',perfil
	write(6,*)'scale,in grids/A :',scale
        write(6,*)'xmin,xmax     (A):',cmin(1),cmax(1)
        write(6,*)'ymin,ymax     (A):',cmin(2),cmax(2)
        write(6,*)'zmin,zmax     (A):',cmin(3),cmax(3)
        write(6,*)'x,y,z range   (A): ',cran(1),cran(2),cran(3)

        write(6,*)'system geometric center in (A):',pmid
        write(6,*)' grid  box is centered in (A) :',oldmid
	write(6,*)'object centred at (gu)     :',offset
	if(isolv)then
	write(6,*)'outer dielectric           :',repsout
c b+++++++++++++++
        do i = 1,nmedia
        write(6,*)'dielectric in medium number',i,' :',medeps(i)*epkt
        end do
        write(6,*)'first kind salt concentration (M)   :',conc(1)
        write(6,*)'valences salt 1 are        ',ival(1),' and',ival(2)
        write(6,*)'second kind salt concentration (M)  :',conc(2)
        write(6,*)'valences salt 2 are        ',ival2(1),' and',ival2(2)
c e+++++++++++++++
	write(6,*)'ionic strength (M)         :',rionst
	write(6,*)'debye length (A)           :',deblen
      write(6,*)'absolute temperature (K)   :',temperature
	write(6,*)'ion exclusion radius (A)   :',exrad
	write(6,*)'probe radius facing water(A:',radprb(1)
        write(6,*)'probe radius, internal (A) :',radprb(2)
	write(6,*)'boundary conditions        : ',bclab(ibctyp)
	write(6,*)'x,y,z periodic bc. and volt. drop flags:',iper
        if(iper(4).or.iper(5).or.iper(6)) then
          write(6,*)"Voltage drops along x,y,z :",vdropx,vdropy,vdropz
        end if
	if(iautocon) then
	  if(gten.gt.0.)then
	    write(6,*)'convergence by grid energy :',gten,' kt'
	  else
	    write(6,*)'# of linear iterations     : automatic'
	  endif
	else
	  write(6,*)'# of linear iterations     :',nlit
	end if
c b+++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if (res1.gt.0..or.res2.gt.0..or.res5.gt.0.) then
          write(6,*)'convergence by rms  change :',res1,' kt'
          write(6,*)'convergence by max  change :',res2,' kt'
          write(6,*)'convergence by norm change :',res5,' kt'
        end if
        if (rionst.lt.1.e-6.and.nnit.gt.0) then
          write(6,*)'ionic strength=0 ==> only linear iterations'
        else
	  write(6,*)'# of non-linear iterations :',nnit
          write(6,*)'non-linear energy calculat.:',lognl
          write(6,*)'manual relaxation parameter :',imanual
        end if
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++
        write(6,*)'ionic direct energy contribution:',logions
	write(6,*)'concentration map output   :',iconc
	write(6,*)'spherical charge distbn.   :',isph
	write(6,*)'INSIGHT format output      :',ibios
	write(6,*)'site potential output      :',isite
	endif
	write(6,*)'modified atom file output  :',iatout
	write(6,*)'map file label             :'
	write(6,201)toplbl
c
	if(ipdbrd.or.ipdbwrt) then
	  if(ipdbrd) write(6,*) 'set to  read unformatted pdb file'
	if(ipdbrd.and.ipdbwrt) then
	write(6,*) ' '
	write(6,*) ' WARNING: can not write an unformatted pdb'
	write(6,*) ' file, while reading in an unformatted pdb file'
	write(6,*) ' Therefore the write option is disabled'
	else
	if(ipdbwrt) write(6,*) ' set to write unformatted pdb file'
	end if
	end if
c
	if(ifrcrd.or.ifrcwrt) then
	if(ifrcrd.and.isite) write(6,*) 'set to read unformatted frc.pdb
     &   file'
	if(ifrcrd.and.ifrcwrt) then
	write(6,*) ' '
	write(6,*) ' WARNING: can not write an unformatted frc'
	write(6,*) ' file, while reading in an unformatted frc file'
	write(6,*) ' Therefore the write option is disabled'
	else
	if(ifrcwrt) write(6,*) ' set to write unformatted frc.pdb file'
	end if
	end if
c
	if(.not.igraph) write(6,*) ' convergence graph turned off'
	if(.not.ipoten) write(6,*) ' potential listings turned off'
	if((icon1.ne.10).or.(icon2.ne.1)) then
	write(6,*) 'convergence test interval is every',icon1,'loops'
	write(6,*) 'testing',100/icon2,'%'
	end if
	write(6,*)' '
c
	return
	end
