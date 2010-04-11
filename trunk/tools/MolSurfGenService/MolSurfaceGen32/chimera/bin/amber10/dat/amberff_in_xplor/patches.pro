 REMARKS Amber topology for proteins 
 REMARKS FILENAME=patches.pro
 
 set echo=false end
 
 PRESIDUE NTER ! add standard N-terminus 
 
 ADD ANGLe +HT1  +N    +HT2
 ADD ANGLe +HT1  +N    +HT3
 ADD ANGLe +HT2  +N    +HT3
 ADD ANGLe +HT2  +N    +CA
 ADD ANGLe +HT1  +N    +CA
 ADD ANGLe +HT3  +N    +CA

 ADD DIHEdral +HT1  +N    +CA   +C
 ADD DIHEdral +HT2  +N    +CA   +C
 ADD DIHEdral +HT3  +N    +CA   +C
 ADD DIHEdral +HT1  +N    +CA   +CB
 ADD DIHEdral +HT2  +N    +CA   +CB
 ADD DIHEdral +HT3  +N    +CA   +CB
 ADD DIHEdral +HT1  +N    +CA   +HA
 ADD DIHEdral +HT2  +N    +CA   +HA
 ADD DIHEdral +HT3  +N    +CA   +HA
 
 
 END {NTER}
 !-----------------------------------------------------------
 
 PRESIDUE NTR2 ! apply to N-terminus and adjacent residue
 
 DELEte DIHEdral  -N    -CA   -C    +N !triple
 DELEte DIHEdral  -N    -CA   -C    +N !triple
 DELEte DIHEdral  -N    -CA   -C    +N !triple
 
 ADD DIHEdral  -N    -CA   -C    +N  !single
 
 END {NTR2}
 
 !-----------------------------------------------------------

 PRESIDUE GLYP ! Glycine N-terminus 

 ADD  ANGLe +HT1  +N    +HT2
 ADD  ANGLe +HT1  +N    +HT3
 ADD  ANGLe +HT2  +N    +HT3
 ADD  ANGLe +HT1  +N    +CA
 ADD  ANGLe +HT2  +N    +CA
 ADD  ANGLe +HT3  +N    +CA

 ADD  DIHEdral +HT1  +N    +CA   +C
 ADD  DIHEdral +HT2  +N    +CA   +C
 ADD  DIHEdral +HT3  +N    +CA   +C
 ADD  DIHEdral +HT1  +N    +CA   +HA1
 ADD  DIHEdral +HT2  +N    +CA   +HA1
 ADD  DIHEdral +HT3  +N    +CA   +HA1
 ADD  DIHEdral +HT1  +N    +CA   +HA2
 ADD  DIHEdral +HT2  +N    +CA   +HA2
 ADD  DIHEdral +HT3  +N    +CA   +HA2
 
 END {GLYP}
 
 !-----------------------------------------------------------
 
 PRESIDUE PROP ! Proline N-Terminal 
  
 ADD ANGLe +HN1  +N    +HN2
 ADD ANGLe +HN1  +N    +CA
 ADD ANGLe +HN2  +N    +CA
 ADD ANGLe +HN1  +N    +CD
 ADD ANGLe +HN2  +N    +CD

 DELE DIHEdral +N   +CA    +C    +O

 ADD DIHEdral +HN1  +N    +CA   +C
 ADD DIHEdral +HN2  +N    +CA   +C
 ADD DIHEdral +HN1  +N    +CA   +HA
 ADD DIHEdral +HN2  +N    +CA   +HA
 ADD DIHEdral +HN1  +N    +CA   +CB
 ADD DIHEdral +HN2  +N    +CA   +CB
 ADD DIHEdral +HN1  +N    +CD   +CG
 ADD DIHEdral +HN2  +N    +CD   +CG
 ADD DIHEdral +HN1  +N    +CD   +HD1
 ADD DIHEdral +HN2  +N    +CD   +HD1
 ADD DIHEdral +HN1  +N    +CD   +HD2
 ADD DIHEdral +HN2  +N    +CD   +HD2
 
 END {PROP}
 
 !-----------------------------------------------------------
 
 PRESIDUE CTER ! standard C-terminus 

 ADD ANGLe -CA   -C   -OT1
 ADD ANGLe -CA   -C   -OT2
 ADD ANGLe -OT1  -C   -OT2

 ADD DIHEdral -N    -CA    -C   -OT2
 ADD DIHEdral -N    -CA    -C   -OT1
 ADD DIHEdral -CB   -CA    -C   -OT2
 ADD DIHEdral -CB   -CA    -C   -OT1
 ADD DIHEdral -HA   -CA    -C   -OT2
 ADD DIHEdral -HA   -CA    -C   -OT1
  
 END {CTER }
 
 
!-----------------------------------------------------------
  
 PRESIDUE LINK ! linkage for IMAGES or for joining segments 
	       ! 1 refers to previous (N terminal) 
	       ! 2 refers to next (C terminal) 
	       ! use in a patch st        
 
 
 ADD  BOND  1C    2N     
 
 ADD  ANGLE  1C    2N    2CA    
 ADD  ANGLE  1C    2N    2HN    
 ADD  ANGLE  1CA   1C    2N     
 ADD  ANGLE  1O    1C    2N     
 

 ADD  DIHEDRAL  1C    2N    2CA   2C     
 ADD  DIHEDRAL  1C    2N    2CA   2HA     
 ADD  DIHEDRAL  1C    2N    2CA   2CB  ! 
 ADD  DIHEDRAL  1C    2N    2CA   2CB  ! triple dihedral
 ADD  DIHEDRAL  1C    2N    2CA   2CB  ! 
 ADD  DIHEDRAL  1HA   1CA   1C    2N      
 ADD  DIHEDRAL  1N    1CA   1C    2N     !  
 ADD  DIHEDRAL  1N    1CA   1C    2N     ! triple dihedral
 ADD  DIHEDRAL  1N    1CA   1C    2N     ! 
 ADD  DIHEDRAL  1CB   1CA   1C    2N   ! double dihedral
 ADD  DIHEDRAL  1CB   1CA   1C    2N   !  
 ADD  DIHEDRAL  1CA   1C    2N    2HN    
 ADD  DIHEDRAL  1CA   1C    2N    2CA     
 ADD  DIHEDRAL  1O    1C    2N    2HN    ! double dihedral
 ADD  DIHEDRAL  1O    1C    2N    2HN    ! 
 ADD  DIHEDRAL  1O    1C    2N    2CA    

 ADD  IMPROPER  1C    2CA   2N    2HN     
 ADD  IMPROPER  1CA    2N    1C   1O   
 
 ADD  IC  1N    1CA    1C    2N        .0000     .00  180.00     .00    .0000  
 ADD  IC  2N    1CA    *1C   1O        .0000     .00  180.00     .00    .0000  
 ADD  IC  1CA   1C     2N    2CA       .0000     .00  180.00     .00    .0000  
 ADD  IC  1C    2N     2CA   2C        .0000     .00  180.00     .00    .0000  
 ADD  IC  1C    2CA    *2N   2HN       .0000     .00  180.00     .00    .0000  
 
 
 END {LINK}
 
 !-----------------------------------------------------------
 
 PRESidue PEPT { PEPTide bond link, for all 
                amino acids ...*(-)     (+)*...
                                 \ PEPT /

                except the  *(-) - (+)PRO link        }

      ADD BOND -C     +N

      ADD ANGLE -CA -C +N
      ADD ANGLE -O  -C +N
      ADD ANGLE -C  +N +CA
      ADD ANGLE -C  +N +HN

      ADD DIHEdral  -C    +N    +CA   +C
      ADD DIHEdral  -C    +N    +CA   +HA
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -HA   -CA   -C    +N
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -CB   -CA   -C    +N    ! double dihedral
      ADD DIHEdral  -CB   -CA   -C    +N    ! double dihedral
      ADD DIHEdral  -CA   -C    +N    +HN
      ADD DIHEdral  -CA   -C    +N    +CA   
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +CA

      ADD  IMPROPER  -C    +CA   +N    +HN     
      ADD  IMPROPER  -CA    +N    -C   -O   

 ADD  IC  -N    -CA    -C    +N      .0000     .00  180.00     .00    .0000
 ADD  IC  -CA    -C    +N    +CA     .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +N     +CA   +C      .0000     .00  180.00     .00    .0000
 ADD  IC  +N    -CA    *-C   -O      .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +CA    *+N   +HN     .0000     .00  180.00     .00    .0000

 END {PEPT}

 !------------------------------------------------------------------
 
 PRESidue PPG1 { for ...*(-) - (+) GLY LINK
               same as PEPT except replacement HA,CB with HA1 HA2
               at the (+) positions, required for proper dihedral setup }

! corrected

      ADD BOND -C     +N

      ADD ANGLE -CA -C +N
      ADD ANGLE -O  -C +N
      ADD ANGLE -C  +N +CA
      ADD ANGLE -C  +N +HN

      ADD DIHEdral  -C    +N    +CA   +C
      ADD DIHEdral  -C    +N    +CA   +HA1
      ADD DIHEdral  -C    +N    +CA   +HA2
      ADD DIHEdral  -HA   -CA   -C    +N
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -CB   -CA   -C    +N    ! double dihedral
      ADD DIHEdral  -CB   -CA   -C    +N    ! double dihedral      
      ADD DIHEdral  -CA   -C    +N    +HN
      ADD DIHEdral  -CA   -C    +N    +CA  
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +CA

      ADD  IMPROPER  -C    +CA   +N    +HN     
      ADD  IMPROPER  -CA    +N    -C   -O   

 ADD  IC  -N    -CA    -C    +N      .0000     .00  180.00     .00    .0000
 ADD  IC  -CA    -C    +N    +CA     .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +N     +CA   +C      .0000     .00  180.00     .00    .0000
 ADD  IC  +N    -CA    *-C   -O      .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +CA    *+N   +HN     .0000     .00  180.00     .00    .0000

 END {PPG1}
 !------------------------------------------------------------------
 
 PRESidue PPG2 { for ... GLY(-) - (+)* LINK
               same as PEPT except replacement HA,CB with HA1 HA2
               at the (-) positions, required for proper dihedral setup }

!corrected

      ADD BOND -C     +N

      ADD ANGLE -CA -C +N
      ADD ANGLE -O  -C +N
      ADD ANGLE -C  +N +CA
      ADD ANGLE -C  +N +HN

      ADD DIHEdral  -C    +N    +CA   +C
      ADD DIHEdral  -C    +N    +CA   +HA
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -HA1  -CA   -C    +N
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -HA2  -CA   -C    +N
      ADD DIHEdral  -CA   -C    +N    +HN
      ADD DIHEdral  -CA   -C    +N    +CA
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +CA

      ADD  IMPROPER  -C    +CA   +N    +HN     
      ADD  IMPROPER  -CA    +N    -C   -O   

 ADD  IC  -N    -CA    -C    +N      .0000     .00  180.00     .00    .0000
 ADD  IC  -CA    -C    +N    +CA     .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +N     +CA   +C      .0000     .00  180.00     .00    .0000
 ADD  IC  +N    -CA    *-C   -O      .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +CA    *+N   +HN     .0000     .00  180.00     .00    .0000

 END {PPG2}
 !------------------------------------------------------------------
 
 PRESidue PEPP  { for  ...*(-) - (+)PRO  link
               same as PEPT except replacement H by CD
               and improper +N +CA +CD -C              }

! corrected

      ADD BOND -C +N 

      ADD ANGLE -CA -C +N
      ADD ANGLE -O  -C +N
      ADD ANGLE -C  +N +CA
      ADD ANGLE -C  +N +CD

      ADD DIHEdral  -C    +N    +CA   +C
      ADD DIHEdral  -C    +N    +CA   +HA
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -HA   -CA   -C    +N     
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -CB   -CA   -C    +N    ! double dihedral
      ADD DIHEdral  -CB   -CA   -C    +N    ! double dihedral

      ADD DIHEdral  -CA   -C    +N    +CD    ! 
      ADD DIHEdral  -CA   -C    +N    +CA    ! 
      ADD DIHEdral  -O    -C    +N    +CD    !
      ADD DIHEdral  -O    -C    +N    +CA    ! 

      ADD DIHEdral  -C    +N    +CD   +CG    ! for proline
      ADD DIHEdral  -C    +N    +CD   +CG    ! for proline
      ADD DIHEdral  -C    +N    +CD   +CG    ! for proline

      ADD DIHEdral  -C    +N    +CD   +HD1   ! for proline
      ADD DIHEdral  -C    +N    +CD   +HD2   ! for proline

      ADD IMPROPER  -C   +CD   +N   +CA
      ADD IMPROPER  -CA   +N   -C    -O


 ADD  IC  -N    -CA    -C    +N      .0000     .00  180.00     .00    .0000
 ADD  IC  -CA    -C    +N    +CA     .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +N     +CA   +C      .0000     .00  -80.00     .00    .0000
 ADD  IC  +N    -CA    *-C   -O      .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +CA    *+N   +CD     .0000     .00  180.00     .00    .0000

 END {PEPP}
 !------------------------------------------------------------------

 PRESidue PPGG { for ... GLY(-) - (+) GLY LINK
               same as PEPT except replacement HA,CB with HA1 HA2
               at the (+) and (-) positions, 
	       required for proper dihedral setup } 
						{ PDA 5-5-94 }

!corrected

      ADD BOND -C     +N

      ADD ANGLE -CA -C +N
      ADD ANGLE -O  -C +N
      ADD ANGLE -C  +N +CA
      ADD ANGLE -C  +N +HN

      ADD DIHEdral  -C    +N    +CA   +C
      ADD DIHEdral  -C    +N    +CA   +HA1
      ADD DIHEdral  -C    +N    +CA   +HA2     
       
      ADD DIHEdral  -HA1  -CA   -C    +N
      ADD DIHEdral  -HA2  -CA   -C    +N
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +HN  ! double dihedral
      ADD DIHEdral  -O    -C    +N    +CA
      
      ADD DIHEdral  -CA   -C    +N    +HN
      ADD DIHEdral  -CA   -C    +N    +CA   

      ADD  IMPROPER  -C    +CA   +N    +HN     
      ADD  IMPROPER  -CA    +N    -C   -O   

 ADD  IC  -N    -CA    -C    +N      .0000     .00  180.00     .00    .0000
 ADD  IC  -CA    -C    +N    +CA     .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +N     +CA   +C      .0000     .00  180.00     .00    .0000
 ADD  IC  +N    -CA    *-C   -O      .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +CA    *+N   +HN     .0000     .00  180.00     .00    .0000

 END {PPGG}
 !------------------------------------------------------------------

 PRESidue PPGP  { for  ... GLY(-) - (+)PRO  link
               same as PEPT except replacement +H by +CD
                            and -HA by -HA1 and -CB by -HA2
               and improper +N +CA +CD -C              }
							 { PDA 5-5-94 }
! corrected

      ADD BOND -C +N 

      ADD ANGLE -CA -C +N
      ADD ANGLE -O  -C +N
      ADD ANGLE -C  +N +CA
      ADD ANGLE -C  +N +CD

      ADD DIHEdral  -C    +N    +CA   +C
      ADD DIHEdral  -C    +N    +CA   +HA
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -C    +N    +CA   +CB  !triple
      ADD DIHEdral  -HA1  -CA   -C    +N     
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -N    -CA   -C    +N !triple
      ADD DIHEdral  -HA2  -CA   -C    +N 
      ADD DIHEdral  -CA   -C    +N    +CD    ! multiple dihedral
      ADD DIHEdral  -CA   -C    +N    +CA    ! multiple dihedral
      ADD DIHEdral  -O    -C    +N    +CD    ! multiple dihedral
      ADD DIHEdral  -O    -C    +N    +CA    ! multiple dihedral

      ADD DIHEdral  -C    +N    +CD   +CG    ! for proline
      ADD DIHEdral  -C    +N    +CD   +CG    ! for proline
      ADD DIHEdral  -C    +N    +CD   +CG    ! for proline

      ADD DIHEdral  -C    +N    +CD   +HD1   ! for proline
      ADD DIHEdral  -C    +N    +CD   +HD2   ! for proline

      ADD IMPROPER  -C   +CD   +N   +CA
      ADD IMPROPER  -CA   +N   -C    -O

 ADD  IC  -N    -CA    -C    +N      .0000     .00  180.00     .00    .0000
 ADD  IC  -CA    -C    +N    +CA     .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +N     +CA   +C      .0000     .00  -80.00     .00    .0000
 ADD  IC  +N    -CA    *-C   -O      .0000     .00  180.00     .00    .0000
 ADD  IC  -C    +CA    *+N   +CD     .0000     .00  180.00     .00    .0000

 END {PPGP}
 !------------------------------------------------------------------
 
 PRESIDUE DISU ! patch for disulfides. Patch must be 1-CYX and 2-CYX.

! DELE ATOM  1HG     END 
! DELE ATOM  2HG     END 
 
 ADD  BOND  1SG   2SG    
 
 ADD  ANGLE  1CB   1SG   2SG    
 ADD  ANGLE  1SG   2SG   2CB    
 
 ADD  DIHEDRAL  1HB1  1CB   1SG   2SG    
 ADD  DIHEDRAL  1HB2  1CB   1SG   2SG    
 ADD  DIHEDRAL  2HB1  2CB   2SG   1SG    
 ADD  DIHEDRAL  2HB2  2CB   2SG   1SG    
 ADD  DIHEDRAL  1CA   1CB   1SG   2SG    
 ADD  DIHEDRAL  1SG   2SG   2CB   2CA    
 ADD  DIHEDRAL  1CB   1SG   2SG   2CB    ! multiple dihedral
 ADD  DIHEDRAL  1CB   1SG   2SG   2CB    ! multiple dihedral
 
 ADD  IC  1CA   1CB    1SG   2SG       .0000     .00  180.00     .00    .0000  
 ADD  IC  1CB   1SG    2SG   2CB       .0000     .00   90.00     .00    .0000  
 ADD  IC  1SG   2SG    2CB   2CA       .0000     .00  180.00     .00    .0000  
 
 
 END {DISU}
 
 !------------------------------------------------------------------
 

 SET ECHO=TRUE END 
