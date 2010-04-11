	subroutine omalt(sf1,sf2,qval,db,sixth,it,om1,om2,spec,salt
     &  ,nhgp,ncrg,nsp)
c
c
	dimension sf1(nhgp),sf2(nhgp),qval(ncrg),db(6,nsp)
c
c
c	if(mod(it,5).ne.0) goto 999
c
	om3=1/(1-om2*spec*0.25)
c
	if(om1.lt.1.e-6) om3=1./(1.-om2*spec*0.5)
c
	om4=om3/om2
c
	om2=om3
	om1=1.0-om2
c
	if(salt.gt.0.0) then
	if(mod(it,2).eq.1) then
        do ix=1,nhgp
          sf1(ix)=sf1(ix)*om4
	end do
	else
	do ix=1,nhgp
          sf2(ix)=sf2(ix)*om4
	end do
	end if
	end if
c
        do ix=1,ncrg
          qval(ix)=qval(ix)*om4
	end do
c
        do iy=1,6
        do ix=1,nsp
          db(iy,ix)=db(iy,ix)*om4
	end do
	end do
c
        sixth=sixth*om4
c
c
999	continue
c
	return
	end
