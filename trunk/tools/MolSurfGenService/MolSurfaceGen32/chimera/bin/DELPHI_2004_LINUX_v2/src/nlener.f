	subroutine nlener(ergnl,igridout)
	include 'qdiffpar4.h'
	include 'qlog.h'
c
	real phimap(igrid,igrid,igrid),goff,gx,gy,gz
        logical*1 idebmap(igrid,igrid,igrid)
        integer i,j,k,n,igridout,saved
        real sout(4,1),ergnl,ergosm,ergsolv,phi,tmp
        real carica,espp1,espp2,espm1,espm2,cs1,cs2,p1,p2,m1,m2,carica2
        real cutedgesi,cutedgesj,cutedgesk
        integer z1p,z1m,z2p,z2m

c Secondly, scan all the grid points and calculate ergnl

        saved=0

        ergsolv=0.0
        ergosm=0.0
        n=0
        goff = (igrid + 1.)/2.
        gx=-goff/scale+oldmid(1)
        gy=-goff/scale+oldmid(2)
        gz=-goff/scale+oldmid(3)
        c=scale*scale*scale
        dhi5=-chi5/6.
        dhi4=-chi4/5.
        dhi3=-chi3/4.
        dhi2=-chi2/3.
        dhi1=-chi1/2.
        if (logions)i_sout=memalloc(i_sout,4*4*igrid*igrid*igrid)

        do k=1,igrid
           cutedgesk=1.
           if (k.eq.1.or.k.eq.igrid) cutedgesk=.5
        do j=1,igrid
           cutedgesj=cutedgesk
           if (j.eq.1.or.j.eq.igrid) cutedgesj=cutedgesk*.5
        do i=1,igrid
           cutedgesi=cutedgesj
           if (i.eq.1.or.i.eq.igrid) cutedgesi=cutedgesj*.5
          if(idebmap(i,j,k)) then 
            phi=phimap(i,j,k)

c           esp..=exp(..)-1
c           p1=-z1p*phi
c           espp1=sinh(p1)+2.*sinh(p1/2)**2
c           m1=z1m*phi
c           espm1=sinh(m1)+2.*sinh(m1/2)**2

c           carica2=0.0
c           if(cs2.gt.0.) then
c             p2=-z2p*phi
c             espp2=sinh(p2)+2.*sinh(p2/2)**2
c             m2=z2m*phi
c             espm2=sinh(m2)+2.*sinh(m2/2)**2
c             ergosm=ergosm-cs2*(z2m*espp2+z2p*espm2)
c             carica2=-2.*cs2*z2p*sinh(sum2*phi)*exp(diff2*phi)
c           end if

c           add the osmotic pressure term ergosm in kt units
c           ergosm=ergosm-cs1*(z1m*espp1+z1p*espm1)
c           ergosmb=ergosmb-2.*cs1*exp(-.5*z1p*phi)*sinh(-.5*z1p*phi)
c           if (ergosmb.ne.ergosm)  write(6,*)'azzz',ergosmb,ergosm
c           carica=carica2-2.*cs1*z1p*sinh(sum1*phi)*exp(diff1*phi)
c Horner scheme for charge and osmotic term
            tmpcar=chi5  *phi+chi4
            tmpcar=tmpcar*phi+chi3
            tmpcar=tmpcar*phi+chi2
            tmpcar=tmpcar*phi+chi1
            carica=cutedgesi*tmpcar*phi/c

            tmpcar=dhi5  *phi+dhi4
            tmpcar=tmpcar*phi+dhi3
            tmpcar=tmpcar*phi+dhi2
            tmpcar=tmpcar*phi+dhi1
            ergosm=ergosm+cutedgesi*tmpcar*phi*phi      
 
            if (logions) then
c             if the gp is in solution and the contribution is higher
c             than a threshold, then put this information in a list
              x=float(i)/scale + gx
              y=float(j)/scale + gy
              z=float(k)/scale + gz

              n=n+1
              sout(1,n)=x
              sout(2,n)=y
              sout(3,n)=z
              sout(4,n)=carica
c             else
c               saved=saved+1
c             end if
            end if

            ergsolv=ergsolv-carica*phi
          end if
        end do
        end do
        end do
        ergsolv=ergsolv*.5*.0006023
        ergosm=-ergosm*.0006023/c

        igridout=n

        if (logions)then
c          if (debug) then
c            write(6,*)'saved grid point calculations',saved
c            write(6,*)'number of g.p. in solution contributing to the
c     &energy',igridout
c          end if
          i_sout=memalloc(i_sout,4*4*igridout)
        end if

        write(6,*)'rho*phi/2 term in solution :      ',-ergsolv,'kt'

        write(6,*)'osmotic pressure term      :      ',-ergosm,'kt'

        ergnl=ergnl+ergosm+ergsolv
	return
	end
