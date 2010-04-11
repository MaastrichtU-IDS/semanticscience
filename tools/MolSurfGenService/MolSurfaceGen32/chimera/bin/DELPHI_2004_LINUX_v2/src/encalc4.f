	subroutine encalc(icount1b,nqass,natom,ibnum,nmedia,nqgrd)
c
	include "qdiffpar4.h"
	include "qlog.h"
c
	real phimap(igrid,igrid,igrid)
	dimension gchrg(icount1b)
	dimension rad3(natom),xn2(3,natom),scspos(3,ibnum)
	integer gchrgp(3,icount1b),ibgrd(3,ibnum),nqgrd
	logical ido
c b++++++++++++++
        integer igridout
        real ergs,ergas,ergnl,ergc
c
	if(inrgwrt) open(42,file=nrgnam(:nrgfrm))

	if(loga)  then
c	  call anagrd(icount1b,epsin*epkt,erga,scale)
        erga=0.0
	  write(6,*) 'analytic grid energy is no more available'
	  stop
	  if(inrgwrt) write(42,*) 'analytic grid energy is',erga,' kt'
	end if

	if(logg) then
	  ergg=0.0
          limx1=2+bufz(1,1)
	  limx2=igrid-1-bufz(2,1)
	  limy1=2+bufz(1,2)
	  limy2=igrid-1-bufz(2,2)
	  limz1=2+bufz(1,3)
	  limz2=igrid-1-bufz(2,3)
	  do 587 i=1,icount1b
	    ix=gchrgp(1,i)
	    iy=gchrgp(2,i)
	    iz=gchrgp(3,i)
	    ido=.true.
	    if((ix.lt.limx1).or.(ix.gt.limx2)) ido=.false.
	    if((iy.lt.limy1).or.(iy.gt.limy2)) ido=.false.
	    if((iz.lt.limz1).or.(iz.gt.limz2)) ido=.false.
	    if(ido) ergg=ergg + phimap(ix,iy,iz)*gchrg(i)
587	  continue
	  ergg=ergg/2.0
	  write(6,*) ' '
	  write(6,*) 'total grid energy          :     ',ergg,' kt'
	  if(inrgwrt) write(42,*)'total grid energy: ',ergg,' kt'
	end if
c
	if(logg.and.loga) then
	  write(6,*) 'difference energy, in kt, is',(ergg-erga)
	  write(6,*) 'difference energy, in kcals, is',(ergg-erga)*0.6
	end if
c
c b+++++++++++++++++++++++++++++++++++++w Oct 2000
	if(irea.or.logs.or.lognl.or.logas.or.isen.or.isch) then
          ergs=0.0
          ergas=0.0
          ergnl=0.0
          ergest=0.0
c ergest=interaction energy of the solvent and the fixed charges
	  if(diff) ibc=0
	  call react(nqass,icount1b,ibnum,ergs,ergas,natom,nmedia)
	  write(6,*) ' '
	end if
c
	if(logc.and.(.not.logions.or..not.lognl)) then
          ergc=0.0
          if (logions) then
c           linear case
            ergest=0.0
            call clbtot(nqass,ergest,ergc)
            write(6,*)'solvent contribution to fixed charges'
            write(6,*)'respectively inside and outside the cube :',
     &ergest,'kt',ergestout,'kt'
            write(6,*)'total ionic direct contribution :',ergest+
     &ergestout,'kt'
          else
            if (nmedia.eq.1) then
 	      call clb(nqass,ergc)
              ergc=ergc/epsin
            else
              call clbmedia(nqass,ergc)
            end if
          end if
	  write(6,*) 'coulombic energy :              ',ergc,' kt'
	  if(inrgwrt) write(42,*) 'total coulombic energy:',ergc,' kt'
        end if

        if (lognl) then

          call nlener(ergnl,igridout)

          ergc=0.0
          ergest=0.0
          if (logions) then
            call clbnonl(nqass,ergc,ergest,igridout)
          write(6,*)'direct ionic contrib. inside the box:',ergest,' kt'
          write(6,*) 'coulombic energy:                     ',ergc,' kt'
          if(inrgwrt) write(42,*) 'total coulombic energy:',ergc,' kt'
          end if
        end if

        if (logs.and.logions) then
          write(6,*)'Energy arising from solvent and boundary pol.',
     &ergnl+ergs+ergest+ergestout,' kt'
        end if

        if (lognl.and.logg) then
           write(6,*)'Total non linear grid energy:',ergg+ergnl,' kt'
        end if

        ergtot=ergnl+ergc+ergs+ergest+ergestout
	if (logs.or.logc) then
        write(6,*)'All required energy terms but grid and self_react.:'
     &,ergtot,'kt'
        if(inrgwrt) write(42,*)'total required energy (everything
     & calculated but grid and self_reaction energies: ',ergtot,'kt'
	end if
c e+++++++++++++++++++++++++++++++++++++
c
	if(logas.and.loga.and.logg) then
	write(6,*) "excess grid energy= ",ergg-ergas-erga
	end if
c
	finish=cputime(start)
	write(6,*) 'energy calculations done at',finish
c
	if(inrgwrt) close(42)
c
	return
	end
