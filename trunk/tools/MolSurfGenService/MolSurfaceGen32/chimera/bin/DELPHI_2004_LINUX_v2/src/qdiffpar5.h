c---------------------------------------------------
c parameters for qdiff4.f and subroutines
c---------------------------------------------------
	parameter (nclist = 1500)
	parameter (nrlist = 1500)
c
c nrmax= maximum number of entries in radius file 
	parameter (nrmax = 1500)
c ncmax= maximum number of entries in charge file 
	parameter (ncmax = 1500)
c ncrgmx = maximum number of charged atoms 
	parameter (ncrgmx = 50000)
c ngrid= maximum grid size 
c       parameter (ngrid = 1025)   ***********IRIX64*****
        parameter (ngrid = 513)
c ngp = ngrid**3 = number of grid points 
c	parameter (ngp = 274626)
c nhgp= half ngp
c	parameter (nhgp = 137313)
c natmax = maximum number of atoms 
	parameter (natmax =100000)
c b++++++++++++++
c nmediamax = maximum number of different media
        parameter (nmediamax = 1000)
c nobjectmax = maximum number of objects
        parameter (nobjectmax = 1000)
c ndistrmax = maximum number of charge distributions    
        parameter (ndistrmax = 1000)
c ibcmax = maximum no. grid points charged and at boundary
        parameter (ibcmax = 30000)
c e+++++++++++++++
c ngcrg = maximum number of grid points that may be assigned charge 
	parameter (ngcrg =110000)
c nbgp = number of points at one box boundary = ngrid**2
c	parameter (nbgp = 4226)
c nsp = maximum number of dielectric boundary points, appox.= 5*nbgp 
c	parameter (nsp = 40000)
c---------------------------------------------------
c---------------------------------------------------
c atom names for radii table
      dimension atnam(nrmax)		
c residue names for radii table
      dimension rnam(nrmax)		
c radius table 
      dimension radt(nrmax)		
c links for radius hash table
      dimension irlink(nrlist)	
c radii id numbers in hash table
      dimension irnumb(nrlist)	
c atom names   for charge table
      dimension catnam(ncmax)		
c chain names for charge table
      dimension cchn(ncmax)		
c chain names for radii table
      dimension rchn(nrmax)		
c residue names for charge table
      dimension crnam(ncmax)		
c residue number for charge table
      dimension crnum(ncmax)		
c residue number for radii table
      dimension rrnum(nrmax)		
c charge table 
      dimension chrgvt(ncmax)		
c links for charge hash table
      dimension iclink(nclist)	
c charge entry id numbers in hash table
      dimension icnumb(nclist)	
c
c other arrays
c atmcrg contians the postions of all chrages in grid units, and the charge
c itself in the fourth field. chgpos contians the same but in angstroms
c schrg contains the induced surface charges in electrons
c	dimension atmcrg(4,ncrgmx),chgpos(3,ncrgmx),schrg(nsp)
c 	dimension phimap(ngrid,ngrid,ngrid),phimap1(nhgp),phimap2(nhgp)
c	dimension phimap3(ngp)
c	integer iepsmp(ngrid,ngrid,ngrid,3),idebmap(ngrid,ngrid,ngrid)
c	integer atsurf(nsp)
	integer atsurf(1)
c       dimension chgpos(3,ncrgmx),schrg(1)
        dimension schrg(1)
	integer limeps(2,3)
c  dimension cgbp(5,20000),atmcrg(4,ncrgmx)
        dimension gval(ngcrg)
	real oldmid(3),oldmid1(3),pmid(3)
c	logical logtab(100)
c---------------------------------------------------
c some character arrays used in the assignment of charges and radii
      character*1 chn,cchn,rchn
      character*3 crnam,rnam,res
      character*4 rnum,crnum,rrnum
      character*6 atnam,catnam,atm
c---------------------------------------------------
c---------------------------------------------------
	common
     &	/link/  irlink,irnumb,iclink,icnumb,irtot,ictot
     &	/name/  atnam,rnam,catnam,cchn,rchn,crnam,crnum,rrnum
     &	/value/ radt,chrgvt
c     &	/maps/  phimap,phimap1,phimap2,phimap3
c     &  /array/ atmcrg,chgpos,schrg
c     &  /imaps/ iepsmp,iepsmp2,idebmap,atsurf
c     &	/scale/ oldmid,scale1,oldmid1,ibc,cgbp,gval,rmmin,rmmax
     &	/scale/ oldmid,scale1,oldmid1,ibc,rmmin,rmmax,pmid
c     &  /array/atmcrg,chgpos
c     &	/log/   logtab
c---------------------------------------------------
c---------------------------------------------------

