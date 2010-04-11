
          -------------------------------------------------------
          Amber 7  SANDER                   Scripps/UCSF 2000
          -------------------------------------------------------

|      Fri Jan  4 15:18:56 2002

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
  ntt    = 1,                                                                  
  ntpr   = 1000,                                                               
  nsnb   = 5,                                                                  
  temp0  = 300.,                                                               
  cut    = 7.5,                                                                
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

     Largest sphere to fit in unit cell has radius =    10.000
     Calculating ew_coeff from dsum_tol,cutoff
     Box X =   20.000   Box Y =   20.000   Box Z =   20.000
     Alpha =   90.000   Beta =   90.000   Gamma =   90.000
     NFFT1 =   20       NFFT2 =   20       NFFT3 =   20
     Cutoff=    7.500   Tol   =0.100E-04
     Ewald Coefficient =  0.37334

     Interpolation order =    4
| New format PARM file being parsed.
| Version =    1.000 Date = 01/02/02 Time = 14:34:36
 NATOM  =     750 NTYPES =       4 NBONH =     500 MBONA  =     125
 NTHETH =     875 MTHETA =       0 NPHIH =     375 MPHIA  =       0
 NHPARM =       0 NPARM  =       0 NNB   =    2000 NRES   =     125
 NBONA  =     125 NTHETA =       0 NPHIA =       0 NUMBND =       3
 NUMANG =       3 NPTRA  =       1 NATYP =       4 NPHB   =       0
 IFBOX  =       1 NMXRS  =       6 IFCAP =       0 NEXTRA =       0


   EWALD MEMORY USE:

|    Total heap storage needed        =        345
|    Adjacent nonbond minimum mask    =       4000
|    Max number of pointers           =         25
|    List build maxmask               =       8000
|    Maximage  =       1100

   EWALD LOCMEM POINTER OFFSETS
|      Real memory needed by PME        =        345
|      Size of EEDTABLE                 =      21000
|      Real memory needed by EEDTABLE   =      84000
|      Integer memory needed by ADJ     =       8000
|      Integer memory used by local nonb=      37471
|      Real memory used by local nonb   =      12300

|    MAX NONBOND PAIRS =    5000000

|     Memory Use     Allocated         Used
|     Real             2000000       132381
|     Hollerith         500000         4627
|     Integer          3500000        75116

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

     NTB   =    2       BOXX  =   20.000
     BOXY  =   20.000   BOXZ  =   20.000

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

     CUT   =    7.500   SCNB  =    2.000
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

     VRAND=    0

     NATOM =     750  NRES =    125

     Water definition for fast triangulated model:
     Resname = WAT ; Oxygen_name = O   ; Hyd1_name = H1  ; Hyd2_name = H2  
| EXTRA_PTS: numextra =      0
| EXTRA PTS fill_bonded: num11-14 =      0   625   875   375
| EXTRA_PTS, build_14: num of 14 terms =    375

   3.  ATOMIC COORDINATES AND VELOCITIES

                                                                                
 begin time read from input coords =     0.000 ps

 Number of triangulated 3-point waters found:        0

     Sum of charges from parm topology file =   0.00000007
     Forcing neutrality...
 ---------------------------------------------------
 APPROXIMATING switch and d/dx switch using CUBIC SPLINE INTERPOLATION
 using   5000.0 points per unit in tabled values
 TESTING RELATIVE ERROR over r ranging from 0.0 to cutoff
| CHECK switch(x): max rel err =   0.1990E-14   at   2.461500
| CHECK d/dx switch(x): max rel err =   0.7670E-11   at   2.772760
 ---------------------------------------------------
     Total number of mask terms =       1875
     Total number of mask terms =       3750
| Local SIZE OF NONBOND LIST =     124489
| TOTAL SIZE OF NONBOND LIST =     124489

 NSTEP =      0 TIME(PS) =     0.000  TEMP(K) =     0.00  PRESS = 44653.2
 Etot   =     428.9493  EKtot   =       0.0000  EPtot      =     428.9493
 BOND   =       0.4626  ANGLE   =      14.8589  DIHED      =      33.3247
 1-4 NB =       0.0000  1-4 EEL =     670.3169  VDWAALS    =     600.2065
 EELEC  =    -890.2203  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =       0.0000  VIRIAL  =   -7712.9437  VOLUME     =    8000.0000
                                                Density    =       0.8309
 Ewald error estimate:   0.2537E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   1000 TIME(PS) =     1.000  TEMP(K) =   265.80  PRESS =   -63.4
 Etot   =     372.2664  EKtot   =     461.3755  EPtot      =     -89.1092
 BOND   =      16.1932  ANGLE   =     139.2339  DIHED      =      41.8614
 1-4 NB =       0.0000  1-4 EEL =     663.6650  VDWAALS    =    -218.3962
 EELEC  =    -731.6665  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     152.5413  VIRIAL  =     165.3717  VOLUME     =    9379.3806
                                                Density    =       0.7087
 Ewald error estimate:   0.1678E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   2000 TIME(PS) =     2.000  TEMP(K) =   283.01  PRESS =   -87.5
 Etot   =     426.7063  EKtot   =     491.2475  EPtot      =     -64.5412
 BOND   =      27.9264  ANGLE   =     121.5311  DIHED      =      39.0979
 1-4 NB =       0.0000  1-4 EEL =     663.9368  VDWAALS    =    -219.4032
 EELEC  =    -697.6303  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.6134  VIRIAL  =     156.1943  VOLUME     =    9310.3581
                                                Density    =       0.7140
 Ewald error estimate:   0.9358E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   3000 TIME(PS) =     3.000  TEMP(K) =   276.63  PRESS =   186.8
 Etot   =     466.4826  EKtot   =     480.1808  EPtot      =     -13.6982
 BOND   =      32.6875  ANGLE   =     155.4391  DIHED      =      39.5924
 1-4 NB =       0.0000  1-4 EEL =     665.9123  VDWAALS    =    -223.4197
 EELEC  =    -683.9098  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.8533  VIRIAL  =      98.4288  VOLUME     =    9278.4772
                                                Density    =       0.7164
 Ewald error estimate:   0.1944E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   4000 TIME(PS) =     4.000  TEMP(K) =   302.50  PRESS =   346.4
 Etot   =     482.9448  EKtot   =     525.0846  EPtot      =     -42.1398
 BOND   =      33.5986  ANGLE   =     144.9523  DIHED      =      38.0105
 1-4 NB =       0.0000  1-4 EEL =     666.1117  VDWAALS    =    -203.6621
 EELEC  =    -721.1508  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.3558  VIRIAL  =      62.4873  VOLUME     =    9340.7692
                                                Density    =       0.7116
 Ewald error estimate:   0.9824E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   5000 TIME(PS) =     5.000  TEMP(K) =   295.40  PRESS =   137.6
 Etot   =     490.6547  EKtot   =     512.7611  EPtot      =     -22.1064
 BOND   =      32.6789  ANGLE   =     161.2692  DIHED      =      41.0556
 1-4 NB =       0.0000  1-4 EEL =     667.6761  VDWAALS    =    -223.1718
 EELEC  =    -701.6144  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.0025  VIRIAL  =     103.4905  VOLUME     =    9257.9836
                                                Density    =       0.7180
 Ewald error estimate:   0.5273E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   6000 TIME(PS) =     6.000  TEMP(K) =   305.72  PRESS =   424.0
 Etot   =     494.6214  EKtot   =     530.6663  EPtot      =     -36.0448
 BOND   =      39.3771  ANGLE   =     169.0972  DIHED      =      36.9618
 1-4 NB =       0.0000  1-4 EEL =     667.5595  VDWAALS    =    -213.8923
 EELEC  =    -735.1480  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.9772  VIRIAL  =      52.3381  VOLUME     =    9026.9665
                                                Density    =       0.7364
 Ewald error estimate:   0.7907E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   7000 TIME(PS) =     7.000  TEMP(K) =   291.01  PRESS =   206.8
 Etot   =     504.5573  EKtot   =     505.1314  EPtot      =      -0.5742
 BOND   =      32.6538  ANGLE   =     190.3174  DIHED      =      41.7795
 1-4 NB =       0.0000  1-4 EEL =     668.2686  VDWAALS    =    -225.3112
 EELEC  =    -708.2823  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.6892  VIRIAL  =      94.9410  VOLUME     =    9126.2023
                                                Density    =       0.7284
 Ewald error estimate:   0.1543E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   8000 TIME(PS) =     8.000  TEMP(K) =   302.75  PRESS =   250.6
 Etot   =     499.0413  EKtot   =     525.5167  EPtot      =     -26.4754
 BOND   =      34.7246  ANGLE   =     173.6040  DIHED      =      38.2682
 1-4 NB =       0.0000  1-4 EEL =     666.6846  VDWAALS    =    -205.6321
 EELEC  =    -734.1246  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.2004  VIRIAL  =      80.8111  VOLUME     =    9311.0648
                                                Density    =       0.7139
 Ewald error estimate:   0.5342E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   9000 TIME(PS) =     9.000  TEMP(K) =   309.45  PRESS =   -31.4
 Etot   =     491.6527  EKtot   =     537.1389  EPtot      =     -45.4861
 BOND   =      33.2141  ANGLE   =     179.4997  DIHED      =      36.0183
 1-4 NB =       0.0000  1-4 EEL =     667.0128  VDWAALS    =    -207.2281
 EELEC  =    -754.0030  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.1912  VIRIAL  =     133.4533  VOLUME     =    9228.2391
                                                Density    =       0.7203
 Ewald error estimate:   0.3784E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  10000 TIME(PS) =    10.000  TEMP(K) =   285.66  PRESS =  -132.4
 Etot   =     492.1276  EKtot   =     495.8563  EPtot      =      -3.7287
 BOND   =      33.8824  ANGLE   =     194.5198  DIHED      =      44.3373
 1-4 NB =       0.0000  1-4 EEL =     667.1170  VDWAALS    =    -224.1066
 EELEC  =    -719.4786  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     115.5802  VIRIAL  =     141.3983  VOLUME     =    9033.7625
                                                Density    =       0.7358
 Ewald error estimate:   0.7571E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  11000 TIME(PS) =    11.000  TEMP(K) =   297.74  PRESS =  -410.9
 Etot   =     484.0963  EKtot   =     516.8272  EPtot      =     -32.7308
 BOND   =      36.7932  ANGLE   =     197.1265  DIHED      =      34.9662
 1-4 NB =       0.0000  1-4 EEL =     668.3186  VDWAALS    =    -242.9814
 EELEC  =    -726.9539  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.0947  VIRIAL  =     201.6181  VOLUME     =    8851.3656
                                                Density    =       0.7510
 Ewald error estimate:   0.3851E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  12000 TIME(PS) =    12.000  TEMP(K) =   288.04  PRESS =    17.1
 Etot   =     477.1488  EKtot   =     499.9830  EPtot      =     -22.8342
 BOND   =      34.3123  ANGLE   =     204.9564  DIHED      =      43.6258
 1-4 NB =       0.0000  1-4 EEL =     668.4029  VDWAALS    =    -219.9871
 EELEC  =    -754.1444  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.0983  VIRIAL  =     126.8126  VOLUME     =    8918.1415
                                                Density    =       0.7454
 Ewald error estimate:   0.2083E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  13000 TIME(PS) =    13.000  TEMP(K) =   296.55  PRESS =   -34.6
 Etot   =     473.9980  EKtot   =     514.7557  EPtot      =     -40.7577
 BOND   =      35.8185  ANGLE   =     201.2644  DIHED      =      42.8722
 1-4 NB =       0.0000  1-4 EEL =     670.4173  VDWAALS    =    -209.6982
 EELEC  =    -781.4319  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     122.2222  VIRIAL  =     128.9621  VOLUME     =    9025.9541
                                                Density    =       0.7365
 Ewald error estimate:   0.4392E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  14000 TIME(PS) =    14.000  TEMP(K) =   305.86  PRESS =   718.9
 Etot   =     471.7935  EKtot   =     530.9225  EPtot      =     -59.1291
 BOND   =      40.8052  ANGLE   =     193.9980  DIHED      =      39.4672
 1-4 NB =       0.0000  1-4 EEL =     668.9493  VDWAALS    =    -191.6504
 EELEC  =    -810.6984  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     116.1356  VIRIAL  =     -21.6267  VOLUME     =    8875.1051
                                                Density    =       0.7490
 Ewald error estimate:   0.2121E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  15000 TIME(PS) =    15.000  TEMP(K) =   291.13  PRESS =  -336.8
 Etot   =     458.7043  EKtot   =     505.3481  EPtot      =     -46.6439
 BOND   =      40.3052  ANGLE   =     207.9210  DIHED      =      40.1127
 1-4 NB =       0.0000  1-4 EEL =     668.7865  VDWAALS    =    -261.3241
 EELEC  =    -742.4452  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     122.1141  VIRIAL  =     183.2328  VOLUME     =    8403.7888
                                                Density    =       0.7910
 Ewald error estimate:   0.5516E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  16000 TIME(PS) =    16.000  TEMP(K) =   310.02  PRESS =  -582.8
 Etot   =     453.0970  EKtot   =     538.1306  EPtot      =     -85.0335
 BOND   =      35.4577  ANGLE   =     214.7183  DIHED      =      37.3384
 1-4 NB =       0.0000  1-4 EEL =     667.7950  VDWAALS    =    -240.4400
 EELEC  =    -799.9030  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.3038  VIRIAL  =     227.8680  VOLUME     =    8468.6431
                                                Density    =       0.7849
 Ewald error estimate:   0.2299E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  17000 TIME(PS) =    17.000  TEMP(K) =   305.19  PRESS =   329.5
 Etot   =     449.6143  EKtot   =     529.7499  EPtot      =     -80.1356
 BOND   =      43.7928  ANGLE   =     200.1102  DIHED      =      39.0702
 1-4 NB =       0.0000  1-4 EEL =     667.0901  VDWAALS    =    -222.4137
 EELEC  =    -807.7853  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.6809  VIRIAL  =      72.3012  VOLUME     =    8487.2632
                                                Density    =       0.7832
 Ewald error estimate:   0.4672E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  18000 TIME(PS) =    18.000  TEMP(K) =   297.31  PRESS = -1152.5
 Etot   =     445.6398  EKtot   =     516.0736  EPtot      =     -70.4337
 BOND   =      33.4389  ANGLE   =     219.2551  DIHED      =      36.8955
 1-4 NB =       0.0000  1-4 EEL =     669.2985  VDWAALS    =    -258.5890
 EELEC  =    -770.7329  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.6604  VIRIAL  =     334.4509  VOLUME     =    8551.1609
                                                Density    =       0.7774
 Ewald error estimate:   0.2913E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  19000 TIME(PS) =    19.000  TEMP(K) =   310.21  PRESS =  -559.7
 Etot   =     434.4980  EKtot   =     538.4673  EPtot      =    -103.9694
 BOND   =      36.2102  ANGLE   =     215.1975  DIHED      =      43.7219
 1-4 NB =       0.0000  1-4 EEL =     667.2713  VDWAALS    =    -236.5885
 EELEC  =    -829.7818  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.3963  VIRIAL  =     234.0603  VOLUME     =    8412.2770
                                                Density    =       0.7902
 Ewald error estimate:   0.2918E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  20000 TIME(PS) =    20.000  TEMP(K) =   305.64  PRESS =  -217.8
 Etot   =     430.5134  EKtot   =     530.5403  EPtot      =    -100.0269
 BOND   =      37.1357  ANGLE   =     213.5293  DIHED      =      35.6132
 1-4 NB =       0.0000  1-4 EEL =     667.5066  VDWAALS    =    -232.4446
 EELEC  =    -821.3671  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     119.8603  VIRIAL  =     159.3819  VOLUME     =    8404.9878
                                                Density    =       0.7909
 Ewald error estimate:   0.8086E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  21000 TIME(PS) =    21.000  TEMP(K) =   302.02  PRESS =   686.0
 Etot   =     423.0962  EKtot   =     524.2566  EPtot      =    -101.1604
 BOND   =      39.8968  ANGLE   =     225.4999  DIHED      =      40.1309
 1-4 NB =       0.0000  1-4 EEL =     667.9225  VDWAALS    =    -225.6121
 EELEC  =    -848.9983  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     119.1517  VIRIAL  =      -2.0730  VOLUME     =    8184.3087
                                                Density    =       0.8122
 Ewald error estimate:   0.4442E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  22000 TIME(PS) =    22.000  TEMP(K) =   298.20  PRESS =   -25.0
 Etot   =     419.9779  EKtot   =     517.6188  EPtot      =     -97.6409
 BOND   =      33.8151  ANGLE   =     230.9447  DIHED      =      43.8651
 1-4 NB =       0.0000  1-4 EEL =     666.5746  VDWAALS    =    -232.0247
 EELEC  =    -840.8157  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      91.5505  VIRIAL  =      96.0637  VOLUME     =    8370.7539
                                                Density    =       0.7941
 Ewald error estimate:   0.2984E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  23000 TIME(PS) =    23.000  TEMP(K) =   286.84  PRESS =   -68.3
 Etot   =     418.7738  EKtot   =     497.8963  EPtot      =     -79.1225
 BOND   =      41.0409  ANGLE   =     223.3590  DIHED      =      41.2952
 1-4 NB =       0.0000  1-4 EEL =     666.0670  VDWAALS    =    -243.5669
 EELEC  =    -807.3176  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     105.0833  VIRIAL  =     117.2184  VOLUME     =    8222.9463
                                                Density    =       0.8084
 Ewald error estimate:   0.6219E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  24000 TIME(PS) =    24.000  TEMP(K) =   292.03  PRESS =  -143.7
 Etot   =     422.9499  EKtot   =     506.9126  EPtot      =     -83.9627
 BOND   =      45.8108  ANGLE   =     234.7520  DIHED      =      36.7835
 1-4 NB =       0.0000  1-4 EEL =     664.3604  VDWAALS    =    -230.1538
 EELEC  =    -835.5156  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     113.3456  VIRIAL  =     139.1485  VOLUME     =    8314.7653
                                                Density    =       0.7995
 Ewald error estimate:   0.5483E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  25000 TIME(PS) =    25.000  TEMP(K) =   305.18  PRESS =  -331.4
 Etot   =     417.1810  EKtot   =     529.7305  EPtot      =    -112.5495
 BOND   =      49.7283  ANGLE   =     218.1466  DIHED      =      42.3564
 1-4 NB =       0.0000  1-4 EEL =     665.4308  VDWAALS    =    -243.0086
 EELEC  =    -845.2030  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      96.0120  VIRIAL  =     153.5062  VOLUME     =    8036.1243
                                                Density    =       0.8272
 Ewald error estimate:   0.7350E-06
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  26000 TIME(PS) =    26.000  TEMP(K) =   291.37  PRESS =   535.0
 Etot   =     416.6345  EKtot   =     505.7704  EPtot      =     -89.1359
 BOND   =      41.0054  ANGLE   =     234.9295  DIHED      =      32.2234
 1-4 NB =       0.0000  1-4 EEL =     664.6896  VDWAALS    =    -243.9754
 EELEC  =    -818.0084  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     107.9730  VIRIAL  =      15.0022  VOLUME     =    8048.4055
                                                Density    =       0.8259
 Ewald error estimate:   0.2134E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  27000 TIME(PS) =    27.000  TEMP(K) =   297.20  PRESS =   310.0
 Etot   =     410.2981  EKtot   =     515.8849  EPtot      =    -105.5868
 BOND   =      37.5584  ANGLE   =     238.1100  DIHED      =      36.0339
 1-4 NB =       0.0000  1-4 EEL =     665.0694  VDWAALS    =    -252.4649
 EELEC  =    -829.8936  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     115.1908  VIRIAL  =      61.7487  VOLUME     =    7983.5613
                                                Density    =       0.8326
 Ewald error estimate:   0.3749E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  28000 TIME(PS) =    28.000  TEMP(K) =   292.20  PRESS =  -404.3
 Etot   =     404.3351  EKtot   =     507.2048  EPtot      =    -102.8697
 BOND   =      39.4999  ANGLE   =     234.6828  DIHED      =      39.3751
 1-4 NB =       0.0000  1-4 EEL =     667.9067  VDWAALS    =    -250.7547
 EELEC  =    -833.5794  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     111.0429  VIRIAL  =     181.3508  VOLUME     =    8054.1137
                                                Density    =       0.8253
 Ewald error estimate:   0.6987E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  29000 TIME(PS) =    29.000  TEMP(K) =   303.83  PRESS =  -108.1
 Etot   =     403.4683  EKtot   =     527.3901  EPtot      =    -123.9219
 BOND   =      37.8286  ANGLE   =     222.2317  DIHED      =      41.1000
 1-4 NB =       0.0000  1-4 EEL =     667.5364  VDWAALS    =    -247.9669
 EELEC  =    -844.6516  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     113.7060  VIRIAL  =     132.4788  VOLUME     =    8045.5676
                                                Density    =       0.8262
 Ewald error estimate:   0.4159E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  30000 TIME(PS) =    30.000  TEMP(K) =   291.73  PRESS =  -485.6
 Etot   =     401.5487  EKtot   =     506.3928  EPtot      =    -104.8441
 BOND   =      37.1800  ANGLE   =     251.8111  DIHED      =      38.3634
 1-4 NB =       0.0000  1-4 EEL =     668.1428  VDWAALS    =    -251.9889
 EELEC  =    -848.3526  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     113.7880  VIRIAL  =     198.5568  VOLUME     =    8085.7204
                                                Density    =       0.8221
 Ewald error estimate:   0.3534E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  31000 TIME(PS) =    31.000  TEMP(K) =   298.08  PRESS =  -326.6
 Etot   =     403.9579  EKtot   =     517.4057  EPtot      =    -113.4478
 BOND   =      35.5320  ANGLE   =     248.8795  DIHED      =      35.9358
 1-4 NB =       0.0000  1-4 EEL =     669.4088  VDWAALS    =    -247.9200
 EELEC  =    -855.2841  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     105.7909  VIRIAL  =     162.2245  VOLUME     =    8002.0706
                                                Density    =       0.8307
 Ewald error estimate:   0.5256E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  32000 TIME(PS) =    32.000  TEMP(K) =   293.65  PRESS =   367.0
 Etot   =     402.0388  EKtot   =     509.7275  EPtot      =    -107.6887
 BOND   =      40.3547  ANGLE   =     242.7742  DIHED      =      44.2774
 1-4 NB =       0.0000  1-4 EEL =     669.3470  VDWAALS    =    -236.1061
 EELEC  =    -868.3360  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      99.4899  VIRIAL  =      35.9334  VOLUME     =    8021.2996
                                                Density    =       0.8287
 Ewald error estimate:   0.2595E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  33000 TIME(PS) =    33.000  TEMP(K) =   298.98  PRESS =    59.7
 Etot   =     394.3848  EKtot   =     518.9688  EPtot      =    -124.5841
 BOND   =      37.6554  ANGLE   =     223.4367  DIHED      =      38.9368
 1-4 NB =       0.0000  1-4 EEL =     664.4404  VDWAALS    =    -239.8063
 EELEC  =    -849.2471  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      97.1390  VIRIAL  =      86.7013  VOLUME     =    8099.4439
                                                Density    =       0.8207
 Ewald error estimate:   0.4094E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  34000 TIME(PS) =    34.000  TEMP(K) =   311.03  PRESS =   302.4
 Etot   =     395.5861  EKtot   =     539.8852  EPtot      =    -144.2991
 BOND   =      36.7757  ANGLE   =     215.9273  DIHED      =      45.1616
 1-4 NB =       0.0000  1-4 EEL =     667.1171  VDWAALS    =    -244.1269
 EELEC  =    -865.1539  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     110.2102  VIRIAL  =      57.9783  VOLUME     =    8000.7909
                                                Density    =       0.8308
 Ewald error estimate:   0.7038E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  35000 TIME(PS) =    35.000  TEMP(K) =   312.39  PRESS =  -875.0
 Etot   =     391.8465  EKtot   =     542.2568  EPtot      =    -150.4102
 BOND   =      45.2861  ANGLE   =     221.3402  DIHED      =      40.6722
 1-4 NB =       0.0000  1-4 EEL =     668.0922  VDWAALS    =    -260.1849
 EELEC  =    -865.6160  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      98.0438  VIRIAL  =     247.3814  VOLUME     =    7904.5534
                                                Density    =       0.8409
 Ewald error estimate:   0.1355E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  36000 TIME(PS) =    36.000  TEMP(K) =   295.75  PRESS =   261.4
 Etot   =     389.3317  EKtot   =     513.3742  EPtot      =    -124.0424
 BOND   =      48.0928  ANGLE   =     233.3143  DIHED      =      40.2948
 1-4 NB =       0.0000  1-4 EEL =     668.8279  VDWAALS    =    -234.0293
 EELEC  =    -880.5428  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     100.6978  VIRIAL  =      55.2599  VOLUME     =    8050.9658
                                                Density    =       0.8256
 Ewald error estimate:   0.5886E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  37000 TIME(PS) =    37.000  TEMP(K) =   297.49  PRESS =   417.1
 Etot   =     390.7877  EKtot   =     516.3806  EPtot      =    -125.5930
 BOND   =      43.2025  ANGLE   =     242.6857  DIHED      =      32.9489
 1-4 NB =       0.0000  1-4 EEL =     666.4025  VDWAALS    =    -227.0276
 EELEC  =    -883.8049  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     104.3460  VIRIAL  =      32.2528  VOLUME     =    8005.1348
                                                Density    =       0.8304
 Ewald error estimate:   0.9350E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  38000 TIME(PS) =    38.000  TEMP(K) =   299.87  PRESS =   -78.1
 Etot   =     390.5754  EKtot   =     520.5199  EPtot      =    -129.9445
 BOND   =      50.9217  ANGLE   =     221.2796  DIHED      =      37.1973
 1-4 NB =       0.0000  1-4 EEL =     665.7605  VDWAALS    =    -252.1277
 EELEC  =    -852.9758  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     116.9013  VIRIAL  =     130.2835  VOLUME     =    7939.3662
                                                Density    =       0.8373
 Ewald error estimate:   0.3598E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  39000 TIME(PS) =    39.000  TEMP(K) =   303.93  PRESS =  -607.7
 Etot   =     393.2481  EKtot   =     527.5592  EPtot      =    -134.3112
 BOND   =      41.0884  ANGLE   =     219.2322  DIHED      =      42.2293
 1-4 NB =       0.0000  1-4 EEL =     665.9259  VDWAALS    =    -265.5901
 EELEC  =    -837.1969  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     106.2378  VIRIAL  =     210.4093  VOLUME     =    7938.6707
                                                Density    =       0.8373
 Ewald error estimate:   0.7556E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  40000 TIME(PS) =    40.000  TEMP(K) =   295.36  PRESS =   621.8
 Etot   =     397.9106  EKtot   =     512.6974  EPtot      =    -114.7869
 BOND   =      40.3605  ANGLE   =     229.6521  DIHED      =      40.9917
 1-4 NB =       0.0000  1-4 EEL =     667.0285  VDWAALS    =    -238.5252
 EELEC  =    -854.2944  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     100.7996  VIRIAL  =      -6.2645  VOLUME     =    7974.2378
                                                Density    =       0.8336
 Ewald error estimate:   0.3993E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  41000 TIME(PS) =    41.000  TEMP(K) =   296.95  PRESS =  -157.4
 Etot   =     399.6149  EKtot   =     515.4503  EPtot      =    -115.8354
 BOND   =      40.5038  ANGLE   =     235.7919  DIHED      =      35.7902
 1-4 NB =       0.0000  1-4 EEL =     666.3343  VDWAALS    =    -253.5384
 EELEC  =    -840.7172  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     107.7688  VIRIAL  =     134.8689  VOLUME     =    7976.4466
                                                Density    =       0.8334
 Ewald error estimate:   0.7431E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  42000 TIME(PS) =    42.000  TEMP(K) =   282.74  PRESS =   237.1
 Etot   =     402.5949  EKtot   =     490.7860  EPtot      =     -88.1911
 BOND   =      36.7216  ANGLE   =     242.6111  DIHED      =      42.2801
 1-4 NB =       0.0000  1-4 EEL =     665.0872  VDWAALS    =    -249.1722
 EELEC  =    -825.7188  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     102.6797  VIRIAL  =      61.7805  VOLUME     =    7988.7997
                                                Density    =       0.8321
 Ewald error estimate:   0.9161E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  43000 TIME(PS) =    43.000  TEMP(K) =   302.83  PRESS =   146.8
 Etot   =     403.8516  EKtot   =     525.6483  EPtot      =    -121.7967
 BOND   =      39.5706  ANGLE   =     215.4464  DIHED      =      37.9821
 1-4 NB =       0.0000  1-4 EEL =     665.1869  VDWAALS    =    -233.5689
 EELEC  =    -846.4139  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      97.3401  VIRIAL  =      71.1544  VOLUME     =    8263.9799
                                                Density    =       0.8044
 Ewald error estimate:   0.8727E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  44000 TIME(PS) =    44.000  TEMP(K) =   296.81  PRESS =   472.7
 Etot   =     405.4088  EKtot   =     515.2117  EPtot      =    -109.8029
 BOND   =      35.3881  ANGLE   =     230.7563  DIHED      =      36.9638
 1-4 NB =       0.0000  1-4 EEL =     665.6524  VDWAALS    =    -248.7636
 EELEC  =    -829.7999  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     111.2807  VIRIAL  =      29.4081  VOLUME     =    8021.5144
                                                Density    =       0.8287
 Ewald error estimate:   0.7134E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  45000 TIME(PS) =    45.000  TEMP(K) =   303.24  PRESS =   576.0
 Etot   =     404.5926  EKtot   =     526.3692  EPtot      =    -121.7766
 BOND   =      41.6658  ANGLE   =     228.4506  DIHED      =      33.8700
 1-4 NB =       0.0000  1-4 EEL =     666.7917  VDWAALS    =    -248.1014
 EELEC  =    -844.4534  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     112.2493  VIRIAL  =      13.9743  VOLUME     =    7902.4674
                                                Density    =       0.8412
 Ewald error estimate:   0.1029E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  46000 TIME(PS) =    46.000  TEMP(K) =   278.45  PRESS =   403.3
 Etot   =     402.5156  EKtot   =     483.3436  EPtot      =     -80.8280
 BOND   =      51.1383  ANGLE   =     231.2851  DIHED      =      42.0079
 1-4 NB =       0.0000  1-4 EEL =     667.3065  VDWAALS    =    -242.5510
 EELEC  =    -830.0148  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      90.1069  VIRIAL  =      20.2459  VOLUME     =    8022.5927
                                                Density    =       0.8286
 Ewald error estimate:   0.1943E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  47000 TIME(PS) =    47.000  TEMP(K) =   294.86  PRESS =  -142.8
 Etot   =     403.3960  EKtot   =     511.8196  EPtot      =    -108.4236
 BOND   =      36.9057  ANGLE   =     237.6544  DIHED      =      38.0704
 1-4 NB =       0.0000  1-4 EEL =     666.6838  VDWAALS    =    -235.6525
 EELEC  =    -852.0854  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     113.5414  VIRIAL  =     138.6802  VOLUME     =    8152.5359
                                                Density    =       0.8154
 Ewald error estimate:   0.2768E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  48000 TIME(PS) =    48.000  TEMP(K) =   297.13  PRESS =  -395.7
 Etot   =     402.7992  EKtot   =     515.7675  EPtot      =    -112.9683
 BOND   =      43.9806  ANGLE   =     220.7433  DIHED      =      37.5910
 1-4 NB =       0.0000  1-4 EEL =     667.3196  VDWAALS    =    -264.4164
 EELEC  =    -818.1864  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     109.3777  VIRIAL  =     177.2188  VOLUME     =    7940.6317
                                                Density    =       0.8371
 Ewald error estimate:   0.3962E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  49000 TIME(PS) =    49.000  TEMP(K) =   299.85  PRESS =  -219.3
 Etot   =     402.1461  EKtot   =     520.4867  EPtot      =    -118.3407
 BOND   =      48.0278  ANGLE   =     235.8895  DIHED      =      36.9588
 1-4 NB =       0.0000  1-4 EEL =     668.6765  VDWAALS    =    -246.6274
 EELEC  =    -861.2657  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     106.2484  VIRIAL  =     144.4534  VOLUME     =    8067.4397
                                                Density    =       0.8240
 Ewald error estimate:   0.4828E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =   302.54  PRESS =   241.1
 Etot   =     398.2964  EKtot   =     525.1589  EPtot      =    -126.8625
 BOND   =      44.6681  ANGLE   =     222.3437  DIHED      =      34.2370
 1-4 NB =       0.0000  1-4 EEL =     668.0242  VDWAALS    =    -234.2341
 EELEC  =    -861.9015  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     107.2951  VIRIAL  =      65.0672  VOLUME     =    8110.6221
                                                Density    =       0.8196
 Ewald error estimate:   0.7895E-03
 ------------------------------------------------------------------------------


      A V E R A G E S   O V E R   50000 S T E P S


 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =   296.25  PRESS =     2.3
 Etot   =     427.3370  EKtot   =     514.2339  EPtot      =     -86.8969
 BOND   =      38.6008  ANGLE   =     211.7991  DIHED      =      38.9764
 1-4 NB =       0.0000  1-4 EEL =     666.3177  VDWAALS    =    -236.3897
 EELEC  =    -806.2012  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     114.6184  VIRIAL  =     114.2218  VOLUME     =    8409.7643
                                                Density    =       0.7930
 Ewald error estimate:   0.3831E-03
 ------------------------------------------------------------------------------


      R M S  F L U C T U A T I O N S


 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =    11.24  PRESS =   519.2
 Etot   =      38.6447  EKtot   =      19.5070  EPtot      =      40.2589
 BOND   =       6.0183  ANGLE   =      31.6012  DIHED      =       3.8211
 1-4 NB =       0.0000  1-4 EEL =       1.7185  VDWAALS    =      18.2059
 EELEC  =      56.5681  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      15.4243  VIRIAL  =      94.3940  VOLUME     =     492.6313
                                                Density    =       0.0445
 Ewald error estimate:   0.2955E-03
 ------------------------------------------------------------------------------

|
|>>>>>>>>PROFILE of TIMES>>>>>>>>>>>>>>>>>  
|
|                Ewald setup time           0.08 ( 0.17% of List )
|                Check list validity        4.53 ( 9.22% of List )
|                Map frac coords            0.08 ( 0.17% of List )
|                Grid unit cell             0.15 ( 0.31% of List )
|                Grid image cell            0.18 ( 0.37% of List )
|                Build the list            43.77 (89.02% of List )
|                Other                      0.37 ( 0.75% of List )
|             List time                 49.17 ( 2.69% of Nonbo)
|                Direct Ewald time       1057.89 (59.45% of Ewald)
|                Adjust Ewald time         30.95 ( 1.74% of Ewald)
|                Self Ewald time            0.50 ( 0.03% of Ewald)
|                Finish NB virial           3.03 ( 0.17% of Ewald)
|                   Fill Bspline coeffs       13.32 ( 1.96% of Recip)
|                   Fill charge grid         239.43 (35.22% of Recip)
|                   Scalar sum                97.95 (14.41% of Recip)
|                   Grad sum                 239.83 (35.28% of Recip)
|                   FFT time                  88.63 (13.04% of Recip)
|                   Other                      0.62 ( 0.09% of Recip)
|                Recip Ewald time         679.78 (38.20% of Ewald)
|                Other                      7.25 ( 0.41% of Ewald)
|             Ewald time              1779.40 (97.28% of Nonbo)
|             Other                      0.52 ( 0.03% of Nonbo)
|          Nonbond force           1829.09 (97.80% of Force)
|          Bond energy                1.20 ( 0.06% of Force)
|          Angle energy              16.00 ( 0.86% of Force)
|          Dihedral energy           16.31 ( 0.87% of Force)
|          Noe calc time              0.20 ( 0.01% of Force)
|          Other                      7.47 ( 0.40% of Force)
|       Force time              1870.27 (98.23% of Runmd)
|       Shake time                13.41 ( 0.70% of Runmd)
|       Verlet update time         7.57 ( 0.40% of Runmd)
|       Ekcmr time                 9.07 ( 0.48% of Runmd)
|       Other                      3.58 ( 0.19% of Runmd)
|    Runmd Time              1903.90 (100.0% of Total)
| Total time              1903.97 (100.0% of ALL  )

| Highest rstack allocated:      41020
| Highest istack allocated:      31750

|     Setup wallclock           5 seconds
|     Nonsetup wallclock     1943 seconds
