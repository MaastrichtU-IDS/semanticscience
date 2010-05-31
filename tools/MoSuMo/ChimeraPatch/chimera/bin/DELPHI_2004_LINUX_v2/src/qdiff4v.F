	program qdiff
c b++++++++++++++++++++++++++++++++++++++++++++
#ifdef PC
cDEC$ IF DEFINED (PC)
        use dflib
        use dfport
cDEC$ END IF
#endif
c e++++++++++++++++++++++++++++++++++++++++++++
c------------------------------------------------------------------
	include 'qdiffpar4.h'
	include 'qlog.h'
c------------------------------------------------------------------
     	character*50 fnma(30)
	character*80 argnam
	real cmin(3),cmax(3),cran(3),xo(3),atpos(1)
	dimension xn(3),xn2(1),ibgrd(3,1),dbval(0:1,0:6,0:1)
	dimension rad3(1),chrgv2(1),idpos(1),db(6,1)
	dimension sf1(1),sf2(1),qval(ngcrg)
	dimension sfd(5,0:1),chrgv4(1),scspos(3,1)
	dimension cqplus(3),cqmin(3)
	integer ifnma(30),iqpos(ngcrg),arglen
        character*24 day,atinf(1)*15
c b+++++++++++++++++++
        integer crgatn(1),nqgrdtonqass(1),extracrg
        integer nmedia,nobject,ndistr,uniformdiel
	  logical ionlymol
        integer idirectalg,numbmol,icount1a,icount1b
        real medeps(0:nmediamax),atmeps(1),qfact
        character*80 dataobject(nobjectmax,2)
        character*80 datadistr(ndistrmax)
        character*80 strtmp
c
c pointer based arrays
        real limobject(1),cgbp(5,1),chgpos(3,1)
c e+++++++++++++++++++

	integer iepsmp(1)
        logical*1 idebmap(1)
        integer iatmmed(1)
        real phimap(1),atmforce(3,1)
        real phimap1(1),phimap2(1),phimap3(1)
	integer neps(1),keps(1)
c------------------------------------------------------------------
c
c b+++++++++++++++++++++++++++++++++++++++++
c tolerance in small numbers
        tol=1.e-7
c debug flag
        debug=.false.
c e+++++++++++++++++++++++++++++++++++++++++
        icount1a=0
        icount1b=0
	start = cputime(0.0)
        call wrt(1)
c
c	call rdlog(fnma,ifnma); find logical links..
c
        i=iargc()
	argnam=" "
	if(i.gt.0)then
	call getarg(1,argnam)
	call namlen(argnam,arglen)
	end if
c
	call qqint(i,argnam,arglen)
c b++++++++++++++++++++++++++++++++++++++
c create suitable pdb file, if necessary
        if (icreapdb) call creapdb(repsout,numbmol)
c e++++++++++++++++++++++++++++++++++++++
c
c set hash tables from size and charge files
c
	call rdhrad(*999)
	if(isolv)call rdhcrg(*999)
c read in pdbfile and, if necesssary, assign charges/radii
c
c  b++++++++++++++++++++++++++++++
        uniformdiel=1
        i_iatmmed=memalloc(i_iatmmed,4*natmax)
c  e+++++++++++++++++++++++++++++
	call setrc(natom,*999,nmedia,nobject,ndistr,ionlymol)
        idirectalg=1
        if (nmedia.gt.1) then
          write(6,*)'Attention, many dielectrics! not all the surface
     & charge is facing the solution!!'
          idirectalg=1
        end if
        write(6,*)'Direct mapping of epsilon: (0/1)(n/y)',idirectalg
c  b++++++++++++++++++++++++++++++
        i_iatmmed=memalloc(i_iatmmed,4*(natom+nobject))
c  epsin = repsin /epkt !!!!!
        epsin=medeps(1)
c  e+++++++++++++++++++++++++++++
c
	finish=cputime(start)
	write(6,*) 'time to read in and/or assign rad/chrg=',finish
c b+++++++++++++++++++++
        i_limobject=memalloc(i_limobject,4*nobject*3*2) 
c find box enclosing each object at this moment expressed in Angstrom
        call extrmobjects(nobject,scale,natom,numbmol)
c e+++++++++++++++++++++
c find extrema
c
	call extrm(natom,igrid,cmin,cmax,nobject)
c b++++++++++++++++++++
        pmid(1)=(cmax(1)+cmin(1))/2.
        pmid(2)=(cmax(2)+cmin(2))/2.
        pmid(3)=(cmax(3)+cmin(3))/2.
c
c calculate offsets
c
        call off(oldmid,pmid,*999)

        cran(1)=cmax(1)-cmin(1)
        cran(2)=cmax(2)-cmin(2)
        cran(3)=cmax(3)-cmin(3)
c       rmaxdim=max(cran(1),cran(2),cran(3))
c ++++modificato per convenienza di dimensionamento
        rmaxdim=2.*max(abs(cmax(1)-oldmid(1)),abs(cmin(1)-oldmid(1)),
     &          abs(cmax(2)-oldmid(2)),abs(cmin(2)-oldmid(2)),
     &          abs(cmax(3)-oldmid(3)),abs(cmin(3)-oldmid(3)))
c e+++++++++++++++++++
c
c atpos=atom positions, oldmid=current midpoints, rmaxdim=largest dimension
c rad3= radii in angstroms. calculate scale according to them and
c to the percent box fill
c
	if(igrid.eq.0)then

	  if(scale.eq.10000.)scale=1.2
	  if(perfil.eq.10000.)perfil=80.
	  igrid=scale*100./perfil*rmaxdim

	elseif(scale.eq.10000.)then

	      if(perfil.eq.10000.)then
	        scale=1.2
	        perfil=100.*rmaxdim*scale/float(igrid-1)
	      else
	        scale=float(igrid-1)*perfil/(100.*rmaxdim)
	      endif
	    else
	      perfil=100.*rmaxdim*scale/float(igrid-1)
	endif
c     calcolo quante deblen di soluzione sono contenute nel box
	if (deblen.lt.1000000.) then
        debnum=(100./perfil-1.)*rmaxdim/deblen
	write(6,*)'Debye Lengths contained in the finite diff. box',debnum
	end if
c       if(rionst.gt.0.0.and.exrad.lt.1.e-6)exrad=2.0
c
	irm=mod(igrid,2)
	if(irm.eq.0)igrid=igrid+1
c
	if(igrid.gt.ngrid)then
	  igrid=ngrid
	  write(6,*)'igrid = ',igrid,' exceeds ','ngrid = ',ngrid,'
     & so reset'
	  scale=float(igrid-1)*perfil/(100.*rmaxdim)
	endif
c b+++++++++++++ added dependence by nmedia                              
        medeps(0)=epsout
	call wrtprm(nmedia,cmin,cmax,cran)
c e+++++++++++++

	ngp=igrid*igrid*igrid+1
	nhgp=ngp/2
	nbgp=igrid*igrid+1
	i_iepsmp=memalloc(i_iepsmp,4*3*igrid*igrid*igrid)
	i_idebmap=memalloc(i_idebmap,-igrid*igrid*igrid)
c
c calculate offsets
c
ccall off(oldmid,*999) vecchio posto
c
        xl1=oldmid(1)-(1.0/scale)*float(igrid+1)*0.5
        xl2=oldmid(2)-(1.0/scale)*float(igrid+1)*0.5
        xl3=oldmid(3)-(1.0/scale)*float(igrid+1)*0.5
        xr1=oldmid(1)+(1.0/scale)*float(igrid+1)*0.5
        xr2=oldmid(2)+(1.0/scale)*float(igrid+1)*0.5
        xr3=oldmid(3)+(1.0/scale)*float(igrid+1)*0.5

	if(cmin(1).lt.xl1.or.cmin(2).lt.xl2.or.cmin(3).lt.xl3.or.
     &	cmax(1).gt.xr1.or.cmax(2).gt.xr2.or.cmax(3).gt.xr3)
     &	write(6,*)
     &	'!!! WARNING: part of system outside the box!'
c convert atom coordinates from angstroms to grid units
c
	i_xn2=memalloc(i_xn2,4*3*natom)
	call grdatm(natom,igrid,scale,oldmid)
c b++++++++write visual.txt to dialog with the GUI
c       call wrtvisual(natom,igrid,nobject,scale,oldmid,nmedia,epkt)
c verify if dielectric is uniform 

        do i = 0,nmedia-1
        if (medeps(i).ne.medeps(i+1)) uniformdiel=0 
        end do
c e+++++++++now pass uniformdiel to epsmak
c make the epsmap, and also a listing of boundary elements, and
c the second epsmap used for the molecular surface scaling
	call epsmak(ibnum,natom,oldmid,uniformdiel,
     &  ionlymol,nobject,nmedia,numbmol)

c ++++I have postponed crgarr to epsmak
c
c make some charge arrays for boundary conditions etc.
c
        if(isolv)then
c b++++++++++increased the starting dimension of crgatn and..+++++
        extracrg=0
        if (ndistr.gt.0)  extracrg=igrid**3
        i_crgatn=memalloc(i_crgatn,4*(natom+extracrg))
        i_chrgv2=memalloc(i_chrgv2,4*4*(natom+extracrg))
        i_nqgrdtonqass=memalloc(i_nqgrdtonqass,4*(natom+extracrg))
        i_atmeps=memalloc(i_atmeps,4*(natom+extracrg))
        i_chgpos=memalloc(i_chgpos,4*3*ncrgmx)
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
        call crgarr(ncrgmx,cqplus,cqmin,atpos,igrid,natom,nqass
     &  ,nqgrd,qmin,qnet,qplus,nmedia,ndistr,scale,oldmid,nobject,
     &  radpolext,extracrg)
c
c b+++++++++++++++++++++++++++++
        i_crgatn=memalloc(i_crgatn,4*nqass)
        i_nqgrdtonqass=memalloc(i_nqgrdtonqass,4*nqgrd)
        i_atmeps=memalloc(i_atmeps,4*nqass)
        i_chrgv2=memalloc(i_chrgv2,4*4*nqgrd)
        i_iatmmed=memalloc(i_iatmmed,0)
        i_chgpos=memalloc(i_chgpos,4*3*nqass)

        if(logs.or.lognl)then
c e++++++++++++++++++++++++++++
          ico=0
          do ic=1,nqass
            cx1=chgpos(1,ic)
            cx2=chgpos(2,ic)
            cx3=chgpos(3,ic)
            if(cx1.lt.xl1.or.cx1.gt.xr1.or.cx2.lt.xl2.or.
     &     cx2.gt.xr2.or.cx3.lt.xl3.or.cx3.gt.xr3)then
c
              if (crgatn(ic).lt.0) then
c b+++++++++++++++++
                write(6,
     &  '(''!WARNING: distribution'',I4,'' outside the box'')')
     &  (-crgatn(ic))
              else
                if (crgatn(ic).gt.natom) then
                  write(6,
     &  '(''!WARNING : crg in object'',I4,'' outside the box'')')
     &  (crgatn(ic)-natom)  
                else
c e+++++++++++++++++
                  write(6,
     &  '(''!!! WARNING : charge '',a15,'' outside the box'')')
     &  atinf(crgatn(ic))
                endif
              endif
c
              ico=1
            endif
          end do
          if(ico.gt.0.and.ibctyp.ne.3)then
            write(6,*)'CHARGES OUTSIDE THE BOX AND NOT DOING FOCUSSING,
     &THEREFORE STOP'
            stop
          end if
        endif
        endif
c write details

        call wrtadt(perfil,cmin,cmax,cran,oldmid,scale,natom
     &  ,nqass,qnet,qplus,cqplus,qmin,cqmin,isolv)

c ++++++++++++++++++++++++++++++++++++
	if(isolv) then
      	write(6,*) 'number of dielectric boundary points',ibnum
	if(iexun.and.(ibnum.eq.0)) then
	write(6,*) "exiting as no boundary elements and"
	write(6,*) "uniform dielectric exit flag has been set"
	goto 998
	end if
c###################
	call dbsfd(dbval,sfd)
c
        nsp=ibnum+1000
        i_db= memalloc(i_db,4*6*nsp)
        i_idpos= memalloc(i_idpos,4*nsp)
        i_sf1= memalloc(i_sf1,4*nhgp)
        i_sf2= memalloc(i_sf2,4*nhgp)

	call mkdbsf(ibnum,nsp,dbval,icount2a,icount2b,sfd,natom,
     &  nmedia,idirectalg,nobject)
c
c make qval and other linear charge arrays for the solver
c
	i_phimap=memalloc(i_phimap,4*igrid*igrid*igrid)
        if(isph) then
	call setfcrg(nqgrd,nqass,icount1a,icount1b,nmedia,natom,
     &idirectalg,nobject)
	else
	call setcrg(nqgrd,nqass,icount1a,icount1b,nmedia,natom,
     &idirectalg,nobject)
        endif
c b++++++++++++++++++++
        i_nqgrdtonqass=memalloc(i_nqgrdtonqass,0)
c e++++++++++++++++++++
	finish=cputime(start)
	write(6,*) 'iepsmp to db, and charging done at', finish
	write(6,*) 'number of grid points assigned charge', icount1b
c
c write dielectric map
c
	if(epswrt)then
          imaxwrd = igrid/16 + 1
          i_neps= memalloc (i_neps,4*3*imaxwrd*igrid*igrid)
	  i_keps= memalloc (i_keps,4*imaxwrd*igrid*igrid)
	  call wrteps(imaxwrd,natom+nobject+2)
	  i_neps= memalloc (i_neps,0)
	  i_keps= memalloc (i_keps,0)
	endif
c	call chkeps(natom,atpos,rad3,ibnum,ibgrd,igrid,scale,radprb)
c       I can't get rid of iepsmp if I have to calculate the nonlin energy
        i_iepsmp= memalloc(i_iepsmp,0)
c
c calculate boundary conditions
c
	call setbc(qplus,qmin,cqplus,cqmin,nqass,natom,ibnum)
c
        i_phimap1= memalloc(i_phimap1,4*nhgp)
        i_phimap2= memalloc(i_phimap2,4*nhgp)
        i_phimap3= memalloc(i_phimap3,4*ngp)

        i_bndx= memalloc(i_bndx,4*nbgp)
        i_bndy= memalloc(i_bndy,4*nbgp)
        i_bndz= memalloc(i_bndz,4*nbgp)

	if(iuspec) then
	  spec=uspec
	  write(6,*) "using entered value for relaxation of: ",spec
	else
	  call relfac(idpos,db,sf1,sf2,icount2a,icount2b,spec,nsp,
     &	phimap1,phimap2,phimap3,bndx,bndy,bndz,idirectalg)
	end if
c
	noit=int(7.8/log(1.0 + sqrt(1-spec)))
	write(6,*) 'estimated iterations to convergence',noit
	if(iautocon) nlit = noit
c
        i_bndx1= memalloc(i_bndx1,4*nbgp)
        i_bndx2= memalloc(i_bndx2,4*nbgp)
        i_bndx3= memalloc(i_bndx3,4*nbgp)
        i_bndx4= memalloc(i_bndx4,4*nbgp)
c
	finish=cputime(start)
	write(6,*)'  '
	write(6,*)'setup time was (sec) ',finish
	write(6,*)'  '
c
c iterate
c
c b++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if (float(ibc)/ibnum.gt..3.and.iautocon) then
           nlit=nlit*ibc/(.3*ibnum)
           write(6,*)'Re-estimated iterations now :',nlit
        end if
c e++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	if(nnit.eq.0.or.rionst.lt.1.e-6) then
        call itit(idpos,db,sf1,sf2,iqpos,qval,icount2a,icount2b,
     &	icount1a,icount1b,spec,nsp,phimap,phimap1,phimap2,phimap3,
     &	bndx,bndy,bndz,bndx1,bndx2,bndx3,bndx4,gval,idirectalg,cgbp)

	else

        i_qmap1=memalloc(i_qmap1,4*nhgp)
        i_qmap2=memalloc(i_qmap2,4*nhgp)
        i_debmap1=memalloc(i_debmap1,4*nhgp)
        i_debmap2=memalloc(i_debmap2,4*nhgp)
        if (noit.gt.50) then
           nlit=noit/2
           write(6,*)'Re-estimated iterations now :',nlit
        end if
        qfact=abs(qnet)*float(ibc)/ibnum
        call nitit(idpos,db,sf1,sf2,iqpos,qval,icount2a,icount2b,
     &	icount1a,icount1b,spec,nsp,phimap,phimap1,phimap2,phimap3,
     &  idebmap,bndx,bndy,bndz,bndx1,bndx2,bndx3,bndx4,
     &	qmap1,qmap2,debmap1,debmap2,idirectalg,qfact)
        i_qmap1=memalloc(i_qmap1,0)
        i_qmap2=memalloc(i_qmap2,0)
        i_debmap1=memalloc(i_debmap1,0)
        i_debmap2=memalloc(i_debmap2,0)

	end if
c
        i_bndx1= memalloc(i_bndx1,0)
        i_bndx2= memalloc(i_bndx2,0)
        i_bndx3= memalloc(i_bndx3,0)
        i_bndx4= memalloc(i_bndx4,0)

        i_bndx= memalloc(i_bndx,0)
        i_bndy= memalloc(i_bndy,0)
        i_bndz= memalloc(i_bndz,0)
c
        i_phimap1= memalloc(i_phimap1,0)
        i_phimap2= memalloc(i_phimap2,0)
        i_phimap3= memalloc(i_phimap3,0)
c
	i_db= memalloc(i_db,0)
	i_idpos= memalloc(i_idpos,0)
	i_sf1= memalloc(i_sf1,0)
	i_sf2= memalloc(i_sf2,0)
c b++++++++++++++++++++++++++++++++
c ++++++now encalc take nmedia++++
	call encalc(icount1b,nqass,natom,icount2b,nmedia,nqgrd)
        i_chrgv2=memalloc(i_chrgv2,0)
c e++++++++++++++++++++++++++++++++++++++++++++
c
	if(isite) call wrtsit(nqass,icount2b,atpos,chrgv4,rad3,natom,
     &  ibnum,nmedia,nobject)
c
	finish=cputime(start)
c b++++++++++++++++++write potential map for the GUI
        call wrtphiForGUI
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
c	if phiwrt set true then write potential map
c
	if(phiwrt) call wrtphi
	i_debmap= memalloc(i_idebmap,0)
	i_phimap= memalloc(i_phimap,0)
c
	endif
	goto 998
c
999	continue
	stop
c
998	continue
	finish = cputime(start)
c	finish = finish - start
	write(6,*)'  '
	write(6,*)'total cpu time was (sec) ',finish
	write(6,*)'  '
        call datime(day)
        write(6,*)'DelPhi exited at ',day(12:19)
	end
