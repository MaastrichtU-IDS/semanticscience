	subroutine phicon
c
	include "qdiffpar4.h"
	include "qlog.h"
	
	real phimap(igrid,igrid,igrid),tmp,deb
        logical*1 idebmap(igrid,igrid,igrid)
c
c convert potentials to concentrations
c
	  sixth = 1./6.
          tmp=abs(chi2*chi4)
	  if(rionst.gt.0.0) then
	    write(6,*)'  '
	    write(6,*)'converting potentials to '
	    write(6,*)'net charge concentrations...'
	    write(6,*)'  '
c IF nonlinear equation is used then use the exponential form
c otherwise use the linear form
c NB use same number of terms in expansion
c of sinh as for iteration in itit.f
            write(6,*)'PHICON: this option has not been tested yet'
c
	    if(nnit.ne.0) then
              if (tmp.lt.1.e-6) then
	        do 9037 iz = 1,igrid
	          do 9038 iy = 1,igrid
		    do 9039 ix = 1,igrid
c use first three terms of sinh
                      if (idebmap(ix,iy,iz)) then
                        phi = phimap(ix,iy,iz)
                        phisq = phi**2
c Horner scheme for charge and osmotic term
                        temp = phisq*chi5 + chi3
                        temp = temp*phisq + chi1
                        phimap(ix,iy,iz)=temp*phi     
                      else
                        phimap(ix,iy,iz)=0.0
		      end if
9039	            continue
9038	          continue
9037	        continue
              else
c b+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c asymmetric salt
                do 8037 iz = 1,igrid
                  do 8038 iy = 1,igrid
                    do 8039 ix = 1,igrid
                      if (idebmap(ix,iy,iz)) then
                        phi = phimap(ix,iy,iz)
c Horner scheme for charge and osmotic term
                        temp = phi*chi5 + chi4
                        temp = phi*temp + chi3
                        temp = phi*temp + chi2
                        temp = temp*phi + chi1
                        phimap(ix,iy,iz)=temp*phi   
                      else
                        phimap(ix,iy,iz)=0.0
                      end if          
8039                continue
8038              continue
8037            continue
              end if
c e++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	  else
	    do 9137 iz = 1,igrid
	      do 9138 iy = 1,igrid
	        do 9139 ix = 1,igrid
                  if (idebmap(ix,iy,iz)) then
                    phi = phimap(ix,iy,iz)
                    phimap(ix,iy,iz)=chi1*phi
                  else
                    phimap(ix,iy,iz)=0.0
                  end if       
9139	        continue
9138	      continue
9137	    continue
	  end if
	end if
c
c
	if(rionst.eq.0.0) then
	write(6,*) "cannot convert from potentials to concentrations"
	write(6,*) "if the ionic strenth is zero!"
	end if
c
c
	return
	end
