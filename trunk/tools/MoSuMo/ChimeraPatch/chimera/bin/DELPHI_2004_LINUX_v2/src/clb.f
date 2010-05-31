	subroutine clb(nqass,ergc)
c
	include "qdiffpar4.h"
	include "qlog.h"
c
	real*8 dist1,dist2,dist3,dist,en1
c       real sqa(nqass)
        real atmcrg(4,nqass),chgpos(3,nqass)
c
	izero=0

c       do 10 i=1,nqass
c         sqa(i)=.5*(chgpos(1,i)**2 + chgpos(2,i)**2 + chgpos(3,i)**2)
c10	continue
c       sqrt2=sqrt(2.0)
	en=0.0
	do 20 i=1,nqass-1
c         temp=sqa(i)
	  dist1=chgpos(1,i)
	  dist2=chgpos(2,i)
	  dist3=chgpos(3,i)
	  en1=0.0
	  do 30 j=i+1,nqass
            dist=(dist1-chgpos(1,j))**2+(dist2-chgpos(2,j))**2+(dist3-
     &           chgpos(3,j))**2
c    prod=dist1*chgpos(1,j)+dist2*chgpos(2,j)+dist3*chgpos(3,j)
c    dist= sqa(j) + temp - prod
	    en1 = en1 + atmcrg(4,j)/sqrt(dist)
30	  continue
	  en=en + atmcrg(4,i)*en1
20	continue
c       en=en/sqrt2
	ergc=en 
	return
	end 

c b++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        subroutine clbmedia(nqass,ergc)
        include "qdiffpar4.h"
        include "qlog.h"

        integer nqass
        real*8 dist1,dist2,dist3,dist,en1
        real atmeps(nqass),sqrt8
        real atmcrg(4,nqass),chgpos(3,nqass)

        en=0.0
        do 20 i=1,nqass
          dist1=chgpos(1,i)
          dist2=chgpos(2,i)
          dist3=chgpos(3,i)
          en1=0.0
          do 30 j=1,i-1
            dist=(dist1-chgpos(1,j))**2+(dist2-chgpos(2,j))**2+(dist3-
     &           chgpos(3,j))**2
            en1 = en1 + atmcrg(4,j)/sqrt(dist)
30        continue
          do 40 j=i+1,nqass
            dist=(dist1-chgpos(1,j))**2+(dist2-chgpos(2,j))**2+(dist3-
     &           chgpos(3,j))**2
            en1 = en1 + atmcrg(4,j)/sqrt(dist)
40        continue
          en=en + atmcrg(4,i)*en1/atmeps(i)
20      continue
        en=en/2.0
        ergc=en
        return
        end
c ***************************************************************
        subroutine clbnonl(nqass,ergc,ergest,igridout)

        include "qdiffpar4.h"
        include "qlog.h"

        integer nqass,n,i,j,k,ii,jj,kk,igridout
        real*8 dist1,dist2,dist3,dist,en1
        real atmeps(nqass),sqrt8,c,x,y,z
        real sout(4,igridout)
        real atmcrg(4,nqass),chgpos(3,nqass)
        real phimap(igrid,igrid,igrid),goff

        en=0.0
        sqrt8=sqrt(8.0)
        c=.0006023


        do 20 i=1,nqass
          en1=0.0
          en2=0.0
          dist1=chgpos(1,i)
          dist2=chgpos(2,i)
          dist3=chgpos(3,i)
          do 30 j=1,i-1
            dist=(dist1-chgpos(1,j))**2+(dist2-chgpos(2,j))**2+(dist3-
     &           chgpos(3,j))**2
            en1 = en1 + atmcrg(4,j)/sqrt(dist)
30        continue
          do 40 j=i+1,nqass
            dist=(dist1-chgpos(1,j))**2+(dist2-chgpos(2,j))**2+(dist3-
     &           chgpos(3,j))**2
            en1 = en1 + atmcrg(4,j)/sqrt(dist)
40        continue
          en=en + atmcrg(4,i)*en1/atmeps(i)
c calculation for the solvent contribution
          if (rionst.gt.1.e-6) then
            do n=1,igridout
              x=sout(1,n)
              y=sout(2,n)
              z=sout(3,n)
              dist=(dist1-x)**2+(dist2-y)**2+(dist3-z)**2
              en2=en2+sout(4,n)/sqrt(dist)
            end do
            ergest=ergest+en2*atmcrg(4,i)
          end if
20      continue
        en=en/2.0
        ergest=ergest*c/(2.0*epsout)
        ergc=en
        i_sout=memalloc(i_sout,0)
        return
        end

c *************************************************************************
        subroutine clbtot(nqass,ergest,ergc)
c fatta nel caso lineare

        include "qdiffpar4.h"
        include "qlog.h"

        integer nqass,n,i,j,k,ii,jj,kk,igridout
        real*8 dist1,dist2,dist3,dist,en1
        real atmeps(nqass),sqrt8,c,x,y,z
        logical*1 idebmap(igrid,igrid,igrid)
        real sout(4,1)
        real atmcrg(4,nqass),chgpos(3,nqass)
        real phimap(igrid,igrid,igrid),goff,carica,tmp,temp
        real cutedgesi,cutedgesj,cutedgesk

        i_sout=memalloc(i_sout,4*4*igrid*igrid*igrid)
        en=0.0
        n=0
        goff = (igrid + 1.)/2.
        gx=-goff/scale+oldmid(1)
        gy=-goff/scale+oldmid(2)
        gz=-goff/scale+oldmid(3)

        c=scale*scale*scale
        tmp=-2.*rionst/c

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
            carica=phi*tmp
c             if the gp is in solution and the contribution is higher
c             than a threshold, then put this information in a list
            x=float(i)/scale + gx
            y=float(j)/scale + gy
            z=float(k)/scale + gz
            n=n+1
            sout(1,n)=x
            sout(2,n)=y
            sout(3,n)=z
            sout(4,n)=carica*cutedgesi
          end if
        end do
        end do
        end do
        igridout=n
        write(6,*)'number of g.p. in solution contributing to the
     &energy',igridout
        i_sout=memalloc(i_sout,4*4*igridout)

        do 20 i=1,nqass
          en1=0.0
          en2=0.0
          dist1=chgpos(1,i)
          dist2=chgpos(2,i)
          dist3=chgpos(3,i)
          do 30 j=1,i-1
            dist=(dist1-chgpos(1,j))**2+(dist2-chgpos(2,j))**2+(dist3-
     &           chgpos(3,j))**2
            en1 = en1 + atmcrg(4,j)/sqrt(dist)
30        continue
          do 40 j=i+1,nqass
            dist=(dist1-chgpos(1,j))**2+(dist2-chgpos(2,j))**2+(dist3-
     &           chgpos(3,j))**2
            en1 = en1 + atmcrg(4,j)/sqrt(dist)
40        continue

          en=en + atmcrg(4,i)*en1/atmeps(i)
c calculation for the solvent contribution
          do n=1,igridout
             x=sout(1,n)
             y=sout(2,n)
             z=sout(3,n)
             dist=(dist1-x)**2+(dist2-y)**2+(dist3-z)**2
             en2=en2+sout(4,n)/sqrt(dist)
          end do
          ergest=ergest+en2*atmcrg(4,i)
20      continue
        en=en/2.0
        ergest=ergest*.0006023/(2.0*epsout)
        ergc=en
        i_sout=memalloc(i_sout,0)
        return
        end
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
