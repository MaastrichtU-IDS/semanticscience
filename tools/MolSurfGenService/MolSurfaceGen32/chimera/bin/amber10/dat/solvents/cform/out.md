
          -------------------------------------------------------
          Amber 7  SANDER                   Scripps/UCSF 2000
          -------------------------------------------------------

|      Mon Jan  7 16:17:24 2002

  [-O]verwriting output

File Assignments:
|  MDIN: in.md                                                                 
| MDOUT: out.md                                                                
|INPCRD: crd.min                                                               
|  PARM: parm.top                                                              
|RESTRT: crd.md                                                                
|  REFC: refc                                                                  
| MDVEL: mdvel                                                                 
|  MDEN: mden                                                                  
| MDCRD: mdcrd                                                                 
|MDINFO: mdinfo                                                                

|INPDIP: inpdip                                                                
|RSTDIP: rstdip                                                                
|
 
 Here is the input file:
 
 molecular dynamics                                                            
 $cntrl                                                                        
  irest  = 0, ntx    = 1,                                                      
  ntb    = 2, ntp    = 1,                                                      
  nstlim = 50000,                                                              
  dt     = 0.001,                                                              
  ntpr   = 1000,                                                               
  vrand  = 500,                                                                
  npscal = 1,                                                                  
  iwrap  = 1,                                                                  
  ntt    = 1,                                                                  
  nsnb   = 5,                                                                  
  temp0  = 300.,                                                               
  cut    = 14.0,                                                               
  scee   = 1.2,                                                                
  ntf    = 2,                                                                  
  ntc    = 2,                                                                  
 $end                                                                          
                                                                               
-------------------------------------------------------------------------------

 molecular dynamics                                                             

| Flags:                                                                        


   1.  RESOURCE   USE: 

 getting new box info from bottom of inpcrd
| peek_ewald_inpcrd: Box info found

   EWALD SPECIFIC INPUT:

     Largest sphere to fit in unit cell has radius =    29.000
     Calculating ew_coeff from dsum_tol,cutoff
     Box X =   58.000   Box Y =   58.000   Box Z =   58.000
     Alpha =   90.000   Beta =   90.000   Gamma =   90.000
     NFFT1 =   60       NFFT2 =   60       NFFT3 =   60
     Cutoff=   14.000   Tol   =0.100E-04
     Ewald Coefficient =  0.19234

     Interpolation order =    4
| New format PARM file being parsed.
| Version =    1.000 Date = 01/01/02 Time = 15:28:44
 NATOM  =    6875 NTYPES =       3 NBONH =    1375 MBONA  =    4125
 NTHETH =    4125 MTHETA =    4125 NPHIH =       0 MPHIA  =       0
 NHPARM =       0 NPARM  =       0 NNB   =   15125 NRES   =    1375
 NBONA  =    4125 NTHETA =    4125 NPHIA =       0 NUMBND =       2
 NUMANG =       2 NPTRA  =       0 NATYP =       3 NPHB   =       0
 IFBOX  =       1 NMXRS  =       5 IFCAP =       0 NEXTRA =       0


   EWALD MEMORY USE:

|    Total heap storage needed        =        945
|    Adjacent nonbond minimum mask    =      30250
|    Max number of pointers           =         25
|    List build maxmask               =      60500
|    Maximage  =      10069

   EWALD LOCMEM POINTER OFFSETS
|      Real memory needed by PME        =        945
|      Size of EEDTABLE                 =      20195
|      Real memory needed by EEDTABLE   =      80780
|      Integer memory needed by ADJ     =      60500
|      Integer memory used by local nonb=     254152
|      Real memory used by local nonb   =     112707

|    MAX NONBOND PAIRS =    5000000

|     Memory Use     Allocated         Used
|     Real             2000000       520410
|     Hollerith         500000        42627
|     Integer          3500000       467665

|     Max Nonbonded Pairs: 5000000
| Duplicated    0 dihedrals
| Duplicated    0 dihedrals

     BOX TYPE: RECTILINEAR


   2.  CONTROL  DATA  FOR  THE  RUN

                                                                                

     TIMLIM=  999999.   IREST =    0       IBELLY=    0
     IMIN  =    0
     IPOL  =    0

     NTX   =    1       NTXO  =    1
     IG    =    71277   TEMPI =     0.00   HEAT  =    0.000

     NTB   =    2       BOXX  =   58.000
     BOXY  =   58.000   BOXZ  =   58.000

     NTT   =    1       TEMP0 =  300.000
     DTEMP =    0.000   TAUTP =    1.000
     VLIMIT=   20.000

     NTP   =    1       PRES0 =    1.000   COMP  =   44.600
     TAUP  =    0.200   NPSCAL=    1

     NSCM  =    1000

     NSTLIM=  50000     NTU   =    1
     T     =    0.000   DT    =   0.00100

     NTC   =    2       TOL   =   0.00001  JFASTW =    0

     NTF   =    2       NSNB  =    5

     CUT   =   14.000   SCNB  =    2.000
     SCEE  =    1.200   DIELC =    1.000

     NTPR  =    1000    NTWR  =     500    NTWX  =       0
     NTWV  =       0    NTWE  =       0    IOUTFM=       0
     NTWPRT=       0    NTAVE =       0

     NTR   =    0       NTRX  =    1
     TAUR  =   0.00000     NMROPT=    0       PENCUT=   0.10000

     IVCAP =    0       MATCAP=    0       FCAP  =    1.500

   OTHER DATA:

     IFCAP =    0       NATCAP=    0       CUTCAP=    0.000
     XCAP  =    0.000   YCAP  =    0.000   ZCAP  =    0.000

     VRAND=  500

     NATOM =    6875  NRES =   1375

     Water definition for fast triangulated model:
     Resname = WAT ; Oxygen_name = O   ; Hyd1_name = H1  ; Hyd2_name = H2  
| EXTRA_PTS: numextra =      0
| EXTRA PTS fill_bonded: num11-14 =      0  5500  8250     0
| EXTRA_PTS, build_14: num of 14 terms =      0

   3.  ATOMIC COORDINATES AND VELOCITIES

                                                                                
 begin time read from input coords =     0.000 ps

 Number of triangulated 3-point waters found:        0

     Sum of charges from parm topology file =   0.00000000
     Forcing neutrality...
 ---------------------------------------------------
 APPROXIMATING switch and d/dx switch using CUBIC SPLINE INTERPOLATION
 using   5000.0 points per unit in tabled values
 TESTING RELATIVE ERROR over r ranging from 0.0 to cutoff
| CHECK switch(x): max rel err =   0.1990E-14   at   2.461500
| CHECK d/dx switch(x): max rel err =   0.7232E-11   at   2.688040
 ---------------------------------------------------
     Total number of mask terms =      13750
     Total number of mask terms =      27500
| Local SIZE OF NONBOND LIST =    2065435
| TOTAL SIZE OF NONBOND LIST =    2065435

 NSTEP =      0 TIME(PS) =     0.000  TEMP(K) =     0.00  PRESS = -2180.1
 Etot   =  -11261.2926  EKtot   =       0.0000  EPtot      =  -11261.2926
 BOND   =      29.8974  ANGLE   =      23.3683  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11087.0918
 EELEC  =    -227.4665  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =       0.0000  VIRIAL  =    9184.2222  VOLUME     =  195112.0000
                                                Density    =       1.3969
 Ewald error estimate:   0.2070E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step      500
Setting new random velocities at step     1000
check COM velocity, temp:        0.002286     0.02(Removed)

 NSTEP =   1000 TIME(PS) =     1.000  TEMP(K) =   110.43  PRESS =   255.2
 Etot   =   -7320.1910  EKtot   =    2111.8953  EPtot      =   -9432.0864
 BOND   =     810.5146  ANGLE   =    1279.5619  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11285.2419
 EELEC  =    -236.9209  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1113.1480  VIRIAL  =     110.5273  VOLUME     =  181969.7533
                                                Density    =       1.4978
 Ewald error estimate:   0.1577E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     1500
Setting new random velocities at step     2000
check COM velocity, temp:        0.006185     0.16(Removed)

 NSTEP =   2000 TIME(PS) =     2.000  TEMP(K) =   132.08  PRESS =    86.1
 Etot   =   -6173.0482  EKtot   =    2525.8428  EPtot      =   -8698.8910
 BOND   =    1046.4097  ANGLE   =    1653.9855  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11175.5805
 EELEC  =    -223.7057  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1107.0245  VIRIAL  =     766.3507  VOLUME     =  183285.8985
                                                Density    =       1.4870
 Ewald error estimate:   0.3033E-03
 ------------------------------------------------------------------------------

Setting new random velocities at step     2500
Setting new random velocities at step     3000
check COM velocity, temp:        0.000747     0.00(Removed)

 NSTEP =   3000 TIME(PS) =     3.000  TEMP(K) =   133.69  PRESS =   -30.7
 Etot   =   -5946.4316  EKtot   =    2556.6061  EPtot      =   -8503.0377
 BOND   =    1088.9328  ANGLE   =    1793.6523  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11147.4207
 EELEC  =    -238.2021  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1162.4679  VIRIAL  =    1284.0786  VOLUME     =  183746.7370
                                                Density    =       1.4833
 Ewald error estimate:   0.1572E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     3500
Setting new random velocities at step     4000
check COM velocity, temp:        0.001796     0.01(Removed)

 NSTEP =   4000 TIME(PS) =     4.000  TEMP(K) =   133.10  PRESS =   113.4
 Etot   =   -5936.9618  EKtot   =    2545.3832  EPtot      =   -8482.3450
 BOND   =    1122.5602  ANGLE   =    1832.4121  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11192.9536
 EELEC  =    -244.3637  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1109.8845  VIRIAL  =     662.3153  VOLUME     =  182794.9741
                                                Density    =       1.4910
 Ewald error estimate:   0.2401E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     4500
Setting new random velocities at step     5000
check COM velocity, temp:        0.001030     0.00(Removed)

 NSTEP =   5000 TIME(PS) =     5.000  TEMP(K) =   132.95  PRESS =    -7.1
 Etot   =   -5971.6928  EKtot   =    2542.4918  EPtot      =   -8514.1846
 BOND   =    1084.9042  ANGLE   =    1852.7682  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11222.5277
 EELEC  =    -229.3292  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1153.7341  VIRIAL  =    1181.8820  VOLUME     =  182760.7221
                                                Density    =       1.4913
 Ewald error estimate:   0.2526E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     5500
Setting new random velocities at step     6000
check COM velocity, temp:        0.001903     0.02(Removed)

 NSTEP =   6000 TIME(PS) =     6.000  TEMP(K) =   132.54  PRESS =    11.4
 Etot   =   -5922.7510  EKtot   =    2534.6365  EPtot      =   -8457.3875
 BOND   =    1089.6156  ANGLE   =    1937.8206  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11247.5008
 EELEC  =    -237.3228  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1122.5650  VIRIAL  =    1077.7481  VOLUME     =  182448.7326
                                                Density    =       1.4938
 Ewald error estimate:   0.6717E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     6500
Setting new random velocities at step     7000
check COM velocity, temp:        0.002952     0.04(Removed)

 NSTEP =   7000 TIME(PS) =     7.000  TEMP(K) =   135.30  PRESS =    25.6
 Etot   =   -5923.1919  EKtot   =    2587.5221  EPtot      =   -8510.7140
 BOND   =    1082.6989  ANGLE   =    1903.9559  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11251.5153
 EELEC  =    -245.8536  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1137.0385  VIRIAL  =    1036.2156  VOLUME     =  182110.0165
                                                Density    =       1.4966
 Ewald error estimate:   0.1821E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     7500
Setting new random velocities at step     8000
check COM velocity, temp:        0.002854     0.03(Removed)

 NSTEP =   8000 TIME(PS) =     8.000  TEMP(K) =   134.28  PRESS =    38.4
 Etot   =   -5999.3741  EKtot   =    2567.8585  EPtot      =   -8567.2326
 BOND   =    1116.8966  ANGLE   =    1846.6091  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11287.6919
 EELEC  =    -243.0464  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1144.4391  VIRIAL  =     993.7860  VOLUME     =  181724.3407
                                                Density    =       1.4998
 Ewald error estimate:   0.3557E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     8500
Setting new random velocities at step     9000
check COM velocity, temp:        0.003711     0.06(Removed)

 NSTEP =   9000 TIME(PS) =     9.000  TEMP(K) =   133.29  PRESS =    88.5
 Etot   =   -5927.8347  EKtot   =    2548.9176  EPtot      =   -8476.7523
 BOND   =    1108.1493  ANGLE   =    1907.2470  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11250.6240
 EELEC  =    -241.5246  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1109.0753  VIRIAL  =     761.4902  VOLUME     =  181867.3049
                                                Density    =       1.4986
 Ewald error estimate:   0.3638E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step     9500
Setting new random velocities at step    10000
check COM velocity, temp:        0.003117     0.04(Removed)

 NSTEP =  10000 TIME(PS) =    10.000  TEMP(K) =   135.30  PRESS =   142.0
 Etot   =   -5899.1283  EKtot   =    2587.4208  EPtot      =   -8486.5491
 BOND   =    1159.3159  ANGLE   =    1897.0709  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11304.4156
 EELEC  =    -238.5203  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1103.9158  VIRIAL  =     548.4389  VOLUME     =  181177.6575
                                                Density    =       1.5043
 Ewald error estimate:   0.1285E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    10500
Setting new random velocities at step    11000
check COM velocity, temp:        0.002755     0.03(Removed)

 NSTEP =  11000 TIME(PS) =    11.000  TEMP(K) =   134.42  PRESS =    34.7
 Etot   =   -6051.2622  EKtot   =    2570.5932  EPtot      =   -8621.8554
 BOND   =    1138.5663  ANGLE   =    1884.9039  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11388.6601
 EELEC  =    -256.6655  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1150.4252  VIRIAL  =    1015.2692  VOLUME     =  180609.9033
                                                Density    =       1.5091
 Ewald error estimate:   0.3021E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    11500
Setting new random velocities at step    12000
check COM velocity, temp:        0.002877     0.04(Removed)

 NSTEP =  12000 TIME(PS) =    12.000  TEMP(K) =   133.53  PRESS =    97.3
 Etot   =   -6070.8777  EKtot   =    2553.6163  EPtot      =   -8624.4941
 BOND   =    1109.9770  ANGLE   =    1871.2026  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11348.5083
 EELEC  =    -257.1654  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1117.0863  VIRIAL  =     737.4764  VOLUME     =  180785.7048
                                                Density    =       1.5076
 Ewald error estimate:   0.1791E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    12500
Setting new random velocities at step    13000
check COM velocity, temp:        0.002695     0.03(Removed)

 NSTEP =  13000 TIME(PS) =    13.000  TEMP(K) =   135.95  PRESS =   -27.7
 Etot   =   -6061.0653  EKtot   =    2599.7908  EPtot      =   -8660.8561
 BOND   =    1111.2327  ANGLE   =    1868.8422  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11400.5757
 EELEC  =    -240.3553  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1152.8214  VIRIAL  =    1260.6907  VOLUME     =  180651.5589
                                                Density    =       1.5087
 Ewald error estimate:   0.5767E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    13500
Setting new random velocities at step    14000
check COM velocity, temp:        0.002461     0.03(Removed)

 NSTEP =  14000 TIME(PS) =    14.000  TEMP(K) =   134.36  PRESS =    83.5
 Etot   =   -5904.2491  EKtot   =    2569.5427  EPtot      =   -8473.7918
 BOND   =    1147.5482  ANGLE   =    1895.6091  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11268.7117
 EELEC  =    -248.2374  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1121.9935  VIRIAL  =     794.5823  VOLUME     =  181534.3116
                                                Density    =       1.5014
 Ewald error estimate:   0.1981E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    14500
Setting new random velocities at step    15000
check COM velocity, temp:        0.001394     0.01(Removed)

 NSTEP =  15000 TIME(PS) =    15.000  TEMP(K) =   134.87  PRESS =    -8.3
 Etot   =   -5976.1532  EKtot   =    2579.1899  EPtot      =   -8555.3431
 BOND   =    1157.8790  ANGLE   =    1870.4262  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11353.2043
 EELEC  =    -230.4440  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1160.0055  VIRIAL  =    1192.4223  VOLUME     =  181022.7906
                                                Density    =       1.5056
 Ewald error estimate:   0.5235E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    15500
Setting new random velocities at step    16000
check COM velocity, temp:        0.001843     0.01(Removed)

 NSTEP =  16000 TIME(PS) =    16.000  TEMP(K) =   132.31  PRESS =   -42.2
 Etot   =   -6076.4724  EKtot   =    2530.1812  EPtot      =   -8606.6536
 BOND   =    1108.6495  ANGLE   =    1930.3520  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11407.3957
 EELEC  =    -238.2593  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1166.9237  VIRIAL  =    1331.2536  VOLUME     =  180554.7952
                                                Density    =       1.5095
 Ewald error estimate:   0.2921E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    16500
Setting new random velocities at step    17000
check COM velocity, temp:        0.003399     0.05(Removed)

 NSTEP =  17000 TIME(PS) =    17.000  TEMP(K) =   134.25  PRESS =    53.5
 Etot   =   -5981.7674  EKtot   =    2567.3871  EPtot      =   -8549.1545
 BOND   =    1137.8215  ANGLE   =    1906.1874  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11367.9523
 EELEC  =    -225.2111  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1108.0383  VIRIAL  =     899.3846  VOLUME     =  180672.6059
                                                Density    =       1.5085
 Ewald error estimate:   0.1185E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    17500
Setting new random velocities at step    18000
check COM velocity, temp:        0.002235     0.02(Removed)

 NSTEP =  18000 TIME(PS) =    18.000  TEMP(K) =   134.68  PRESS =    45.1
 Etot   =   -6002.2979  EKtot   =    2575.5933  EPtot      =   -8577.8911
 BOND   =    1119.1138  ANGLE   =    1934.2672  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11389.9192
 EELEC  =    -241.3529  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1163.3369  VIRIAL  =     987.6841  VOLUME     =  180463.9509
                                                Density    =       1.5103
 Ewald error estimate:   0.2857E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    18500
Setting new random velocities at step    19000
check COM velocity, temp:        0.004084     0.07(Removed)

 NSTEP =  19000 TIME(PS) =    19.000  TEMP(K) =   133.28  PRESS =   -28.5
 Etot   =   -6102.9025  EKtot   =    2548.7659  EPtot      =   -8651.6684
 BOND   =    1160.2673  ANGLE   =    1841.0896  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11406.0150
 EELEC  =    -247.0103  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1127.4335  VIRIAL  =    1238.4544  VOLUME     =  180526.3457
                                                Density    =       1.5098
 Ewald error estimate:   0.4789E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    19500
Setting new random velocities at step    20000
check COM velocity, temp:        0.000621     0.00(Removed)

 NSTEP =  20000 TIME(PS) =    20.000  TEMP(K) =   132.36  PRESS =    46.3
 Etot   =   -6075.9515  EKtot   =    2531.2046  EPtot      =   -8607.1562
 BOND   =    1209.1297  ANGLE   =    1852.9494  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11415.0420
 EELEC  =    -254.1933  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1103.7609  VIRIAL  =     923.5623  VOLUME     =  180095.8304
                                                Density    =       1.5134
 Ewald error estimate:   0.1772E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    20500
Setting new random velocities at step    21000
check COM velocity, temp:        0.001931     0.02(Removed)

 NSTEP =  21000 TIME(PS) =    21.000  TEMP(K) =   134.44  PRESS =   -55.4
 Etot   =   -6025.6130  EKtot   =    2570.9573  EPtot      =   -8596.5703
 BOND   =    1163.9610  ANGLE   =    1879.3940  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11393.7166
 EELEC  =    -246.2087  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1110.0630  VIRIAL  =    1326.0362  VOLUME     =  180668.6374
                                                Density    =       1.5086
 Ewald error estimate:   0.2043E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    21500
Setting new random velocities at step    22000
check COM velocity, temp:        0.002940     0.04(Removed)

 NSTEP =  22000 TIME(PS) =    22.000  TEMP(K) =   131.96  PRESS =    86.1
 Etot   =   -5977.7845  EKtot   =    2523.5465  EPtot      =   -8501.3309
 BOND   =    1141.2316  ANGLE   =    1914.8808  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11311.6969
 EELEC  =    -245.7464  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1124.9933  VIRIAL  =     788.6297  VOLUME     =  181024.7026
                                                Density    =       1.5056
 Ewald error estimate:   0.1356E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    22500
Setting new random velocities at step    23000
check COM velocity, temp:        0.002888     0.04(Removed)

 NSTEP =  23000 TIME(PS) =    23.000  TEMP(K) =   134.52  PRESS =    18.5
 Etot   =   -6016.6358  EKtot   =    2572.6044  EPtot      =   -8589.2403
 BOND   =    1127.8821  ANGLE   =    1884.8865  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11358.4383
 EELEC  =    -243.5705  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1103.9241  VIRIAL  =    1031.5005  VOLUME     =  180944.0652
                                                Density    =       1.5063
 Ewald error estimate:   0.4521E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    23500
Setting new random velocities at step    24000
check COM velocity, temp:        0.002518     0.03(Removed)

 NSTEP =  24000 TIME(PS) =    24.000  TEMP(K) =   133.27  PRESS =    -5.2
 Etot   =   -6028.6818  EKtot   =    2548.6231  EPtot      =   -8577.3049
 BOND   =    1155.6810  ANGLE   =    1907.2231  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11408.1721
 EELEC  =    -232.0368  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1093.4386  VIRIAL  =    1113.8627  VOLUME     =  180283.7398
                                                Density    =       1.5118
 Ewald error estimate:   0.4637E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    24500
Setting new random velocities at step    25000
check COM velocity, temp:        0.002624     0.03(Removed)

 NSTEP =  25000 TIME(PS) =    25.000  TEMP(K) =   133.83  PRESS =   -27.1
 Etot   =   -6059.9293  EKtot   =    2559.4189  EPtot      =   -8619.3482
 BOND   =    1126.5536  ANGLE   =    1901.3389  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11406.7027
 EELEC  =    -240.5381  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1154.6593  VIRIAL  =    1260.4840  VOLUME     =  180548.0566
                                                Density    =       1.5096
 Ewald error estimate:   0.1878E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    25500
Setting new random velocities at step    26000
check COM velocity, temp:        0.002172     0.02(Removed)

 NSTEP =  26000 TIME(PS) =    26.000  TEMP(K) =   136.88  PRESS =   -86.2
 Etot   =   -6054.1452  EKtot   =    2617.7353  EPtot      =   -8671.8805
 BOND   =    1146.2040  ANGLE   =    1894.6144  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11458.2961
 EELEC  =    -254.4027  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1136.2176  VIRIAL  =    1471.1931  VOLUME     =  180044.3238
                                                Density    =       1.5138
 Ewald error estimate:   0.4523E-03
 ------------------------------------------------------------------------------

Setting new random velocities at step    26500
Setting new random velocities at step    27000
check COM velocity, temp:        0.003184     0.04(Removed)

 NSTEP =  27000 TIME(PS) =    27.000  TEMP(K) =   135.41  PRESS =     5.9
 Etot   =   -6097.5974  EKtot   =    2589.4809  EPtot      =   -8687.0783
 BOND   =    1121.3927  ANGLE   =    1861.7753  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11433.5652
 EELEC  =    -236.6812  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1124.0318  VIRIAL  =    1100.9356  VOLUME     =  180202.4444
                                                Density    =       1.5125
 Ewald error estimate:   0.6182E-03
 ------------------------------------------------------------------------------

Setting new random velocities at step    27500
Setting new random velocities at step    28000
check COM velocity, temp:        0.003291     0.05(Removed)

 NSTEP =  28000 TIME(PS) =    28.000  TEMP(K) =   133.28  PRESS =    -5.0
 Etot   =   -6011.0133  EKtot   =    2548.8353  EPtot      =   -8559.8485
 BOND   =    1140.8847  ANGLE   =    1914.2820  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11382.4371
 EELEC  =    -232.5781  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1072.9632  VIRIAL  =    1092.4908  VOLUME     =  180579.6121
                                                Density    =       1.5093
 Ewald error estimate:   0.1993E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    28500
Setting new random velocities at step    29000
check COM velocity, temp:        0.003533     0.05(Removed)

 NSTEP =  29000 TIME(PS) =    29.000  TEMP(K) =   135.84  PRESS =    43.5
 Etot   =   -5981.8400  EKtot   =    2597.7265  EPtot      =   -8579.5665
 BOND   =    1136.4091  ANGLE   =    1892.6987  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11354.8111
 EELEC  =    -253.8630  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1068.1844  VIRIAL  =     898.5010  VOLUME     =  180784.3488
                                                Density    =       1.5076
 Ewald error estimate:   0.1729E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    29500
Setting new random velocities at step    30000
check COM velocity, temp:        0.001405     0.01(Removed)

 NSTEP =  30000 TIME(PS) =    30.000  TEMP(K) =   134.58  PRESS =    16.5
 Etot   =   -6107.8377  EKtot   =    2573.6309  EPtot      =   -8681.4686
 BOND   =    1102.8839  ANGLE   =    1891.3363  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11421.9384
 EELEC  =    -253.7503  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1105.9193  VIRIAL  =    1041.8196  VOLUME     =  180229.3787
                                                Density    =       1.5122
 Ewald error estimate:   0.4021E-03
 ------------------------------------------------------------------------------

Setting new random velocities at step    30500
Setting new random velocities at step    31000
check COM velocity, temp:        0.002263     0.02(Removed)

 NSTEP =  31000 TIME(PS) =    31.000  TEMP(K) =   131.21  PRESS =    29.8
 Etot   =   -6057.3163  EKtot   =    2509.1964  EPtot      =   -8566.5126
 BOND   =    1149.3879  ANGLE   =    1912.3410  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11381.3296
 EELEC  =    -246.9118  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1105.3289  VIRIAL  =     989.1918  VOLUME     =  180337.2168
                                                Density    =       1.5113
 Ewald error estimate:   0.3475E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    31500
Setting new random velocities at step    32000
check COM velocity, temp:        0.000295     0.00(Removed)

 NSTEP =  32000 TIME(PS) =    32.000  TEMP(K) =   133.01  PRESS =    70.8
 Etot   =   -6048.0433  EKtot   =    2543.7236  EPtot      =   -8591.7669
 BOND   =    1114.1312  ANGLE   =    1928.4415  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11398.9783
 EELEC  =    -235.3614  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1105.5366  VIRIAL  =     830.1206  VOLUME     =  180103.0100
                                                Density    =       1.5133
 Ewald error estimate:   0.1118E-03
 ------------------------------------------------------------------------------

Setting new random velocities at step    32500
Setting new random velocities at step    33000
check COM velocity, temp:        0.004704     0.09(Removed)

 NSTEP =  33000 TIME(PS) =    33.000  TEMP(K) =   133.39  PRESS =    58.7
 Etot   =   -6084.8756  EKtot   =    2550.9606  EPtot      =   -8635.8362
 BOND   =    1164.8825  ANGLE   =    1907.8020  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11474.6097
 EELEC  =    -233.9110  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1121.9662  VIRIAL  =     894.4079  VOLUME     =  179397.3145
                                                Density    =       1.5193
 Ewald error estimate:   0.3080E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    33500
Setting new random velocities at step    34000
check COM velocity, temp:        0.002793     0.03(Removed)

 NSTEP =  34000 TIME(PS) =    34.000  TEMP(K) =   134.90  PRESS =     8.8
 Etot   =   -6040.9445  EKtot   =    2579.8166  EPtot      =   -8620.7611
 BOND   =    1106.3784  ANGLE   =    1910.9354  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11393.6833
 EELEC  =    -244.3916  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1128.6110  VIRIAL  =    1094.4881  VOLUME     =  180463.7465
                                                Density    =       1.5103
 Ewald error estimate:   0.1946E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    34500
Setting new random velocities at step    35000
check COM velocity, temp:        0.005142     0.11(Removed)

 NSTEP =  35000 TIME(PS) =    35.000  TEMP(K) =   135.18  PRESS =   -49.4
 Etot   =   -6021.9323  EKtot   =    2585.0969  EPtot      =   -8607.0292
 BOND   =    1148.1926  ANGLE   =    1891.6495  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11401.3248
 EELEC  =    -245.5465  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1137.0370  VIRIAL  =    1329.6477  VOLUME     =  180622.8216
                                                Density    =       1.5089
 Ewald error estimate:   0.1651E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    35500
Setting new random velocities at step    36000
check COM velocity, temp:        0.002881     0.04(Removed)

 NSTEP =  36000 TIME(PS) =    36.000  TEMP(K) =   134.72  PRESS =    49.2
 Etot   =   -5989.4323  EKtot   =    2576.2959  EPtot      =   -8565.7282
 BOND   =    1177.9363  ANGLE   =    1882.7137  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11386.0817
 EELEC  =    -240.2966  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1086.6029  VIRIAL  =     894.8570  VOLUME     =  180462.7102
                                                Density    =       1.5103
 Ewald error estimate:   0.2289E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    36500
Setting new random velocities at step    37000
check COM velocity, temp:        0.002102     0.02(Removed)

 NSTEP =  37000 TIME(PS) =    37.000  TEMP(K) =   134.72  PRESS =   -19.3
 Etot   =   -5954.4019  EKtot   =    2576.3367  EPtot      =   -8530.7386
 BOND   =    1130.0542  ANGLE   =    1914.5398  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11333.6890
 EELEC  =    -241.6436  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1142.5979  VIRIAL  =    1217.9611  VOLUME     =  181260.0974
                                                Density    =       1.5036
 Ewald error estimate:   0.1494E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    37500
Setting new random velocities at step    38000
check COM velocity, temp:        0.002637     0.03(Removed)

 NSTEP =  38000 TIME(PS) =    38.000  TEMP(K) =   132.76  PRESS =    15.7
 Etot   =   -5994.8019  EKtot   =    2538.9005  EPtot      =   -8533.7024
 BOND   =    1167.2543  ANGLE   =    1875.1670  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11335.0761
 EELEC  =    -241.0477  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1141.9813  VIRIAL  =    1080.6938  VOLUME     =  180997.0943
                                                Density    =       1.5058
 Ewald error estimate:   0.3466E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    38500
Setting new random velocities at step    39000
check COM velocity, temp:        0.001578     0.01(Removed)

 NSTEP =  39000 TIME(PS) =    39.000  TEMP(K) =   134.17  PRESS =    44.8
 Etot   =   -6030.2985  EKtot   =    2565.8146  EPtot      =   -8596.1131
 BOND   =    1145.9947  ANGLE   =    1868.1671  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11364.6134
 EELEC  =    -245.6615  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1128.5067  VIRIAL  =     953.6393  VOLUME     =  180718.9857
                                                Density    =       1.5081
 Ewald error estimate:   0.5685E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    39500
Setting new random velocities at step    40000
check COM velocity, temp:        0.001265     0.01(Removed)

 NSTEP =  40000 TIME(PS) =    40.000  TEMP(K) =   134.81  PRESS =     7.4
 Etot   =   -6030.9958  EKtot   =    2578.0110  EPtot      =   -8609.0068
 BOND   =    1127.6180  ANGLE   =    1901.4358  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11400.0693
 EELEC  =    -237.9913  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1120.6243  VIRIAL  =    1091.6855  VOLUME     =  180476.6182
                                                Density    =       1.5102
 Ewald error estimate:   0.9236E-03
 ------------------------------------------------------------------------------

Setting new random velocities at step    40500
Setting new random velocities at step    41000
check COM velocity, temp:        0.001785     0.01(Removed)

 NSTEP =  41000 TIME(PS) =    41.000  TEMP(K) =   135.22  PRESS =    11.3
 Etot   =   -6061.7867  EKtot   =    2585.8361  EPtot      =   -8647.6228
 BOND   =    1097.8101  ANGLE   =    1903.8280  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11407.1888
 EELEC  =    -242.0721  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1101.9646  VIRIAL  =    1057.8253  VOLUME     =  180373.0084
                                                Density    =       1.5110
 Ewald error estimate:   0.3442E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    41500
Setting new random velocities at step    42000
check COM velocity, temp:        0.003524     0.05(Removed)

 NSTEP =  42000 TIME(PS) =    42.000  TEMP(K) =   135.90  PRESS =   -37.8
 Etot   =   -5979.6291  EKtot   =    2598.9209  EPtot      =   -8578.5500
 BOND   =    1153.2524  ANGLE   =    1924.7982  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11408.5950
 EELEC  =    -248.0056  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1133.9480  VIRIAL  =    1281.1364  VOLUME     =  180577.5840
                                                Density    =       1.5093
 Ewald error estimate:   0.2406E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    42500
Setting new random velocities at step    43000
check COM velocity, temp:        0.003543     0.05(Removed)

 NSTEP =  43000 TIME(PS) =    43.000  TEMP(K) =   134.38  PRESS =    39.7
 Etot   =   -5981.6671  EKtot   =    2569.9101  EPtot      =   -8551.5771
 BOND   =    1128.1072  ANGLE   =    1943.7643  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11369.1875
 EELEC  =    -254.2610  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1099.8821  VIRIAL  =     945.2993  VOLUME     =  180545.7311
                                                Density    =       1.5096
 Ewald error estimate:   0.3488E-03
 ------------------------------------------------------------------------------

Setting new random velocities at step    43500
Setting new random velocities at step    44000
check COM velocity, temp:        0.002456     0.03(Removed)

 NSTEP =  44000 TIME(PS) =    44.000  TEMP(K) =   134.82  PRESS =     2.9
 Etot   =   -5924.4540  EKtot   =    2578.3229  EPtot      =   -8502.7769
 BOND   =    1116.3406  ANGLE   =    1938.9357  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11310.7001
 EELEC  =    -247.3531  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1162.7083  VIRIAL  =    1151.2720  VOLUME     =  181280.1527
                                                Density    =       1.5035
 Ewald error estimate:   0.1747E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    44500
Setting new random velocities at step    45000
check COM velocity, temp:        0.003574     0.05(Removed)

 NSTEP =  45000 TIME(PS) =    45.000  TEMP(K) =   132.77  PRESS =   -21.3
 Etot   =   -5987.6019  EKtot   =    2539.1186  EPtot      =   -8526.7204
 BOND   =    1170.9612  ANGLE   =    1906.0647  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11357.3835
 EELEC  =    -246.3629  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1152.7348  VIRIAL  =    1235.8547  VOLUME     =  180846.2838
                                                Density    =       1.5071
 Ewald error estimate:   0.3414E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    45500
Setting new random velocities at step    46000
check COM velocity, temp:        0.001126     0.01(Removed)

 NSTEP =  46000 TIME(PS) =    46.000  TEMP(K) =   133.41  PRESS =    50.1
 Etot   =   -6074.1043  EKtot   =    2551.2616  EPtot      =   -8625.3659
 BOND   =    1127.4497  ANGLE   =    1887.3359  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11387.9393
 EELEC  =    -252.2122  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1141.7905  VIRIAL  =     946.5088  VOLUME     =  180392.3689
                                                Density    =       1.5109
 Ewald error estimate:   0.4582E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    46500
Setting new random velocities at step    47000
check COM velocity, temp:        0.002505     0.03(Removed)

 NSTEP =  47000 TIME(PS) =    47.000  TEMP(K) =   134.74  PRESS =    28.2
 Etot   =   -6037.9430  EKtot   =    2576.7630  EPtot      =   -8614.7060
 BOND   =    1120.3947  ANGLE   =    1890.3081  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11385.6228
 EELEC  =    -239.7861  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1148.6660  VIRIAL  =    1039.0193  VOLUME     =  180373.9921
                                                Density    =       1.5110
 Ewald error estimate:   0.2219E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    47500
Setting new random velocities at step    48000
check COM velocity, temp:        0.005242     0.12(Removed)

 NSTEP =  48000 TIME(PS) =    48.000  TEMP(K) =   132.78  PRESS =    18.3
 Etot   =   -6032.1543  EKtot   =    2539.2005  EPtot      =   -8571.3548
 BOND   =    1147.3643  ANGLE   =    1925.3952  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11406.5829
 EELEC  =    -237.5314  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1148.8634  VIRIAL  =    1077.5425  VOLUME     =  180230.1510
                                                Density    =       1.5122
 Ewald error estimate:   0.8058E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    48500
Setting new random velocities at step    49000
check COM velocity, temp:        0.002905     0.04(Removed)

 NSTEP =  49000 TIME(PS) =    49.000  TEMP(K) =   134.44  PRESS =    57.9
 Etot   =   -6094.6480  EKtot   =    2571.0550  EPtot      =   -8665.7030
 BOND   =    1109.2361  ANGLE   =    1900.5782  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11427.7292
 EELEC  =    -247.7882  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1120.5874  VIRIAL  =     895.9187  VOLUME     =  179811.6191
                                                Density    =       1.5158
 Ewald error estimate:   0.1849E-02
 ------------------------------------------------------------------------------

Setting new random velocities at step    49500
Setting new random velocities at step    50000
check COM velocity, temp:        0.001902     0.02(Removed)

 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =   134.43  PRESS =   -12.9
 Etot   =   -6054.0506  EKtot   =    2570.7308  EPtot      =   -8624.7814
 BOND   =    1102.9887  ANGLE   =    1930.5718  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11406.4784
 EELEC  =    -251.8634  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1172.2089  VIRIAL  =    1222.6082  VOLUME     =  180311.9989
                                                Density    =       1.5115
 Ewald error estimate:   0.2631E-02
 ------------------------------------------------------------------------------


      A V E R A G E S   O V E R   50000 S T E P S


 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =   267.53  PRESS =    -6.1
 Etot   =   -3562.8184  EKtot   =    5116.1430  EPtot      =   -8678.9614
 BOND   =    1100.9066  ANGLE   =    1845.1653  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =  -11380.8184
 EELEC  =    -244.2149  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =    1106.1639  VIRIAL  =    1130.9204  VOLUME     =  180805.1662
                                                Density    =       1.5075
 Ewald error estimate:   0.2625E-02
 ------------------------------------------------------------------------------


      R M S  F L U C T U A T I O N S


 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =    22.67  PRESS =   132.9
 Etot   =     787.8819  EKtot   =     433.4409  EPtot      =     379.4051
 BOND   =     123.9313  ANGLE   =     206.1498  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =      90.2708
 EELEC  =       8.6118  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      57.9895  VIRIAL  =     490.4777  VOLUME     =    1059.8561
                                                Density    =       0.0087
 Ewald error estimate:   0.1790E-02
 ------------------------------------------------------------------------------

|
|>>>>>>>>PROFILE of TIMES>>>>>>>>>>>>>>>>>  
|
|                Ewald setup time           0.12 ( 0.04% of List )
|                Check list validity       40.10 (14.30% of List )
|                Map frac coords            0.46 ( 0.16% of List )
|                Grid unit cell             0.36 ( 0.13% of List )
|                Grid image cell            0.32 ( 0.11% of List )
|                Build the list           238.52 (85.06% of List )
|                Other                      0.54 ( 0.19% of List )
|             List time                280.41 ( 0.74% of Nonbo)
|                Direct Ewald time      27118.78 (72.30% of Ewald)
|                Adjust Ewald time        272.04 ( 0.73% of Ewald)
|                Finish NB virial          46.78 ( 0.12% of Ewald)
|                   Fill Bspline coeffs      171.77 ( 1.71% of Recip)
|                   Fill charge grid        2420.75 (24.07% of Recip)
|                   Scalar sum              2560.91 (25.46% of Recip)
|                   Grad sum                2325.50 (23.12% of Recip)
|                   FFT time                2578.57 (25.63% of Recip)
|                   Other                      1.43 ( 0.01% of Recip)
|                Recip Ewald time       10058.94 (26.82% of Ewald)
|                Other                     11.07 ( 0.03% of Ewald)
|             Ewald time             37508.43 (99.26% of Nonbo)
|          Nonbond force          37789.32 (99.41% of Force)
|          Bond energy               26.81 ( 0.07% of Force)
|          Angle energy             152.71 ( 0.40% of Force)
|          Other                     45.01 ( 0.12% of Force)
|       Force time             38014.42 (99.26% of Runmd)
|       Shake time                46.89 ( 0.12% of Runmd)
|       Verlet update time       115.84 ( 0.30% of Runmd)
|       Ekcmr time                92.79 ( 0.24% of Runmd)
|       Other                     26.60 ( 0.07% of Runmd)
|    Runmd Time             38296.53 (100.0% of Total)
| Total time             38296.85 (100.0% of ALL  )

| Highest rstack allocated:     658315
| Highest istack allocated:     277750

|     Setup wallclock           0 seconds
|     Nonsetup wallclock    38369 seconds
