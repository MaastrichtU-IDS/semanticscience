
          -------------------------------------------------------
          Amber 7  SANDER                   Scripps/UCSF 2000
          -------------------------------------------------------

|      Wed Jan  2 14:46:18 2002

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
  nstlim = 500000,                                                             
  dt     = 0.001,                                                              
  ntpr   = 1000,                                                               
  ntt    = 1,                                                                  
  nsnb   = 5,                                                                  
  temp0  = 373.,                                                               
  cut    =  8.0,                                                               
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

     Largest sphere to fit in unit cell has radius =    15.555
     Calculating ew_coeff from dsum_tol,cutoff
     Box X =   32.328   Box Y =   31.111   Box Z =   32.127
     Alpha =   90.000   Beta =   90.000   Gamma =   90.000
     NFFT1 =   32       NFFT2 =   32       NFFT3 =   32
     Cutoff=    8.000   Tol   =0.100E-04
     Ewald Coefficient =  0.34864

     Interpolation order =    4
| New format PARM file being parsed.
| Version =    1.000 Date = 01/02/02 Time = 14:31:50
 NATOM  =    1500 NTYPES =       7 NBONH =     875 MBONA  =     500
 NTHETH =    1750 MTHETA =     500 NPHIH =    2000 MPHIA  =     375
 NHPARM =       0 NPARM  =       0 NNB   =    5750 NRES   =     125
 NBONA  =     500 NTHETA =     500 NPHIA =     375 NUMBND =       7
 NUMANG =      10 NPTRA  =       5 NATYP =       7 NPHB   =       0
 IFBOX  =       1 NMXRS  =      12 IFCAP =       0 NEXTRA =       0


   EWALD MEMORY USE:

|    Total heap storage needed        =        525
|    Adjacent nonbond minimum mask    =      11500
|    Max number of pointers           =         25
|    List build maxmask               =      23000
|    Maximage  =       2194

   EWALD LOCMEM POINTER OFFSETS
|      Real memory needed by PME        =        525
|      Size of EEDTABLE                 =      20918
|      Real memory needed by EEDTABLE   =      83672
|      Integer memory needed by ADJ     =      23000
|      Integer memory used by local nonb=     104718
|      Real memory used by local nonb   =      24582

|    MAX NONBOND PAIRS =    5000000

|     Memory Use     Allocated         Used
|     Real             2000000       180551
|     Hollerith         500000         9127
|     Integer          3500000       197396

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

     NTB   =    2       BOXX  =   32.328
     BOXY  =   31.111   BOXZ  =   32.127

     NTT   =    1       TEMP0 =  373.000
     DTEMP =    0.000   TAUTP =    1.000
     VLIMIT=   20.000

     NTP   =    1       PRES0 =    1.000   COMP  =   44.600
     TAUP  =    0.200   NPSCAL=    1

     NSCM  =    1000

     NSTLIM= 500000     NTU   =    1
     T     =    0.000   DT    =   0.00100

     NTC   =    2       TOL   =   0.00001  JFASTW =    0

     NTF   =    2       NSNB  =    5

     CUT   =    8.000   SCNB  =    2.000
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

     NATOM =    1500  NRES =    125

     Water definition for fast triangulated model:
     Resname = WAT ; Oxygen_name = O   ; Hyd1_name = H1  ; Hyd2_name = H2  
| EXTRA_PTS: numextra =      0
| EXTRA PTS fill_bonded: num11-14 =      0  1375  2250  2250
| EXTRA_PTS, build_14: num of 14 terms =   2000

   3.  ATOMIC COORDINATES AND VELOCITIES

                                                                                
 begin time read from input coords =     0.000 ps

 Number of triangulated 3-point waters found:        0

     Sum of charges from parm topology file =   0.00000041
     Forcing neutrality...
 ---------------------------------------------------
 APPROXIMATING switch and d/dx switch using CUBIC SPLINE INTERPOLATION
 using   5000.0 points per unit in tabled values
 TESTING RELATIVE ERROR over r ranging from 0.0 to cutoff
| CHECK switch(x): max rel err =   0.1990E-14   at   2.461500
| CHECK d/dx switch(x): max rel err =   0.7670E-11   at   2.772760
 ---------------------------------------------------
     Total number of mask terms =       5625
     Total number of mask terms =      11250
| Local SIZE OF NONBOND LIST =     166574
| TOTAL SIZE OF NONBOND LIST =     166574

 NSTEP =      0 TIME(PS) =     0.000  TEMP(K) =     0.00  PRESS =  -324.2
 Etot   =    -896.6843  EKtot   =       0.0000  EPtot      =    -896.6843
 BOND   =      10.2638  ANGLE   =      71.1073  DIHED      =      30.8594
 1-4 NB =     137.6103  1-4 EEL =    2468.6349  VDWAALS    =    -505.0372
 EELEC  =   -3110.1228  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =       0.0000  VIRIAL  =     226.1501  VOLUME     =   32311.9361
                                                Density    =       0.4690
 Ewald error estimate:   0.8164E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   1000 TIME(PS) =     1.000  TEMP(K) =   190.20  PRESS =  -197.4
 Etot   =     -38.4671  EKtot   =     684.4886  EPtot      =    -722.9557
 BOND   =      33.6784  ANGLE   =     111.7822  DIHED      =      75.8198
 1-4 NB =     159.0597  1-4 EEL =    2484.1318  VDWAALS    =    -498.5922
 EELEC  =   -3088.8354  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     220.8212  VIRIAL  =     355.7920  VOLUME     =   31668.6084
                                                Density    =       0.4785
 Ewald error estimate:   0.6138E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   2000 TIME(PS) =     2.000  TEMP(K) =   255.70  PRESS =   174.0
 Etot   =     501.5999  EKtot   =     920.2216  EPtot      =    -418.6216
 BOND   =      50.0137  ANGLE   =     193.4751  DIHED      =      88.8896
 1-4 NB =     148.8421  1-4 EEL =    2468.1609  VDWAALS    =    -388.7857
 EELEC  =   -2979.2173  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     236.5723  VIRIAL  =     117.3083  VOLUME     =   31740.8514
                                                Density    =       0.4774
 Ewald error estimate:   0.1016E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   3000 TIME(PS) =     3.000  TEMP(K) =   295.79  PRESS =    15.9
 Etot   =     825.9341  EKtot   =    1064.4997  EPtot      =    -238.5655
 BOND   =      55.7090  ANGLE   =     277.8761  DIHED      =     139.4665
 1-4 NB =     162.1117  1-4 EEL =    2470.9263  VDWAALS    =    -389.8610
 EELEC  =   -2954.7942  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     279.3819  VIRIAL  =     268.5839  VOLUME     =   31492.1568
                                                Density    =       0.4812
 Ewald error estimate:   0.1194E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   4000 TIME(PS) =     4.000  TEMP(K) =   325.20  PRESS =    14.6
 Etot   =    1055.8789  EKtot   =    1170.3247  EPtot      =    -114.4458
 BOND   =      87.0453  ANGLE   =     316.4644  DIHED      =     158.2307
 1-4 NB =     153.4442  1-4 EEL =    2457.8185  VDWAALS    =    -384.1497
 EELEC  =   -2903.2991  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     252.5821  VIRIAL  =     242.5648  VOLUME     =   31684.2357
                                                Density    =       0.4783
 Ewald error estimate:   0.5824E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   5000 TIME(PS) =     5.000  TEMP(K) =   339.94  PRESS =   116.1
 Etot   =    1195.3665  EKtot   =    1223.3774  EPtot      =     -28.0109
 BOND   =     113.8599  ANGLE   =     374.4469  DIHED      =     163.2886
 1-4 NB =     156.7608  1-4 EEL =    2461.1476  VDWAALS    =    -364.0175
 EELEC  =   -2933.4973  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     270.2543  VIRIAL  =     190.2022  VOLUME     =   31932.4931
                                                Density    =       0.4746
 Ewald error estimate:   0.5275E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   6000 TIME(PS) =     6.000  TEMP(K) =   360.08  PRESS =  -343.3
 Etot   =    1289.0197  EKtot   =    1295.8516  EPtot      =      -6.8318
 BOND   =     128.9420  ANGLE   =     418.8418  DIHED      =     155.9963
 1-4 NB =     162.6182  1-4 EEL =    2468.4383  VDWAALS    =    -400.0060
 EELEC  =   -2941.6624  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     258.2524  VIRIAL  =     496.9736  VOLUME     =   32210.5332
                                                Density    =       0.4705
 Ewald error estimate:   0.1299E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   7000 TIME(PS) =     7.000  TEMP(K) =   343.84  PRESS =     6.8
 Etot   =    1336.0817  EKtot   =    1237.4249  EPtot      =      98.6569
 BOND   =     136.2110  ANGLE   =     458.0645  DIHED      =     156.9467
 1-4 NB =     169.5195  1-4 EEL =    2479.3999  VDWAALS    =    -371.4044
 EELEC  =   -2930.0803  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     226.9699  VIRIAL  =     222.3078  VOLUME     =   31547.2990
                                                Density    =       0.4804
 Ewald error estimate:   0.1887E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   8000 TIME(PS) =     8.000  TEMP(K) =   360.11  PRESS =  -170.1
 Etot   =    1374.0113  EKtot   =    1295.9666  EPtot      =      78.0447
 BOND   =     146.0683  ANGLE   =     495.6608  DIHED      =     165.6044
 1-4 NB =     149.8454  1-4 EEL =    2455.3984  VDWAALS    =    -413.0348
 EELEC  =   -2921.4979  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     210.2091  VIRIAL  =     322.9114  VOLUME     =   30689.5292
                                                Density    =       0.4938
 Ewald error estimate:   0.4659E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   9000 TIME(PS) =     9.000  TEMP(K) =   370.69  PRESS =  -268.6
 Etot   =    1377.3242  EKtot   =    1334.0231  EPtot      =      43.3011
 BOND   =     152.5062  ANGLE   =     516.1628  DIHED      =     160.6628
 1-4 NB =     161.3111  1-4 EEL =    2469.2840  VDWAALS    =    -423.4673
 EELEC  =   -2993.1584  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     217.2703  VIRIAL  =     387.8784  VOLUME     =   29414.3815
                                                Density    =       0.5152
 Ewald error estimate:   0.2702E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  10000 TIME(PS) =    10.000  TEMP(K) =   368.65  PRESS =  -358.0
 Etot   =    1389.8447  EKtot   =    1326.7046  EPtot      =      63.1401
 BOND   =     140.2194  ANGLE   =     564.7772  DIHED      =     146.8203
 1-4 NB =     157.4410  1-4 EEL =    2470.6201  VDWAALS    =    -444.5859
 EELEC  =   -2972.1522  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     211.7540  VIRIAL  =     432.2419  VOLUME     =   28524.2861
                                                Density    =       0.5313
 Ewald error estimate:   0.8211E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  11000 TIME(PS) =    11.000  TEMP(K) =   371.29  PRESS =  -296.5
 Etot   =    1365.4836  EKtot   =    1336.2175  EPtot      =      29.2661
 BOND   =     164.0793  ANGLE   =     559.1714  DIHED      =     159.2419
 1-4 NB =     159.5591  1-4 EEL =    2470.1638  VDWAALS    =    -464.0849
 EELEC  =   -3018.8645  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     207.5882  VIRIAL  =     381.6086  VOLUME     =   27179.0646
                                                Density    =       0.5576
 Ewald error estimate:   0.3288E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  12000 TIME(PS) =    12.000  TEMP(K) =   370.22  PRESS =  -240.9
 Etot   =    1328.1399  EKtot   =    1332.3360  EPtot      =      -4.1961
 BOND   =     174.3544  ANGLE   =     565.1973  DIHED      =     183.0891
 1-4 NB =     159.7903  1-4 EEL =    2477.8883  VDWAALS    =    -488.3591
 EELEC  =   -3076.1564  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     187.4804  VIRIAL  =     322.7667  VOLUME     =   26014.2188
                                                Density    =       0.5825
 Ewald error estimate:   0.1425E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  13000 TIME(PS) =    13.000  TEMP(K) =   370.34  PRESS =  -448.2
 Etot   =    1305.8516  EKtot   =    1332.7875  EPtot      =     -26.9359
 BOND   =     165.6224  ANGLE   =     595.5980  DIHED      =     160.5385
 1-4 NB =     152.5930  1-4 EEL =    2468.6358  VDWAALS    =    -504.0016
 EELEC  =   -3065.9221  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     193.8476  VIRIAL  =     441.9657  VOLUME     =   25637.9223
                                                Density    =       0.5911
 Ewald error estimate:   0.2453E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  14000 TIME(PS) =    14.000  TEMP(K) =   376.18  PRESS =  -172.7
 Etot   =    1287.1793  EKtot   =    1353.7903  EPtot      =     -66.6111
 BOND   =     170.8287  ANGLE   =     598.1464  DIHED      =     159.7628
 1-4 NB =     155.5612  1-4 EEL =    2457.0855  VDWAALS    =    -508.8044
 EELEC  =   -3099.1912  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     159.4513  VIRIAL  =     249.8054  VOLUME     =   24237.2953
                                                Density    =       0.6252
 Ewald error estimate:   0.1129E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  15000 TIME(PS) =    15.000  TEMP(K) =   364.78  PRESS =    12.6
 Etot   =    1259.0757  EKtot   =    1312.7773  EPtot      =     -53.7015
 BOND   =     179.5308  ANGLE   =     626.6228  DIHED      =     154.3683
 1-4 NB =     161.0027  1-4 EEL =    2472.2088  VDWAALS    =    -543.8479
 EELEC  =   -3103.5871  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     189.2100  VIRIAL  =     183.0246  VOLUME     =   22718.3127
                                                Density    =       0.6671
 Ewald error estimate:   0.8803E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  16000 TIME(PS) =    16.000  TEMP(K) =   379.49  PRESS =  -132.2
 Etot   =    1234.9773  EKtot   =    1365.6925  EPtot      =    -130.7152
 BOND   =     180.6855  ANGLE   =     614.6809  DIHED      =     137.8999
 1-4 NB =     162.5709  1-4 EEL =    2472.7197  VDWAALS    =    -562.5561
 EELEC  =   -3136.7159  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     173.4131  VIRIAL  =     235.0392  VOLUME     =   21592.0362
                                                Density    =       0.7018
 Ewald error estimate:   0.1796E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  17000 TIME(PS) =    17.000  TEMP(K) =   376.84  PRESS =   189.6
 Etot   =    1211.8027  EKtot   =    1356.1668  EPtot      =    -144.3641
 BOND   =     192.6775  ANGLE   =     621.0357  DIHED      =     157.6021
 1-4 NB =     157.0227  1-4 EEL =    2475.1905  VDWAALS    =    -591.0875
 EELEC  =   -3156.8051  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     174.3905  VIRIAL  =      89.5862  VOLUME     =   20714.0315
                                                Density    =       0.7316
 Ewald error estimate:   0.1028E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  18000 TIME(PS) =    18.000  TEMP(K) =   385.22  PRESS =   372.1
 Etot   =    1179.1410  EKtot   =    1386.3479  EPtot      =    -207.2068
 BOND   =     187.1877  ANGLE   =     647.7535  DIHED      =     118.0881
 1-4 NB =     163.3724  1-4 EEL =    2467.2832  VDWAALS    =    -610.2066
 EELEC  =   -3180.6852  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     169.3168  VIRIAL  =       6.9687  VOLUME     =   20208.8470
                                                Density    =       0.7499
 Ewald error estimate:   0.1019E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  19000 TIME(PS) =    19.000  TEMP(K) =   374.66  PRESS =  -168.9
 Etot   =    1141.6611  EKtot   =    1348.3222  EPtot      =    -206.6611
 BOND   =     192.8532  ANGLE   =     649.2360  DIHED      =     138.1655
 1-4 NB =     168.2480  1-4 EEL =    2472.3306  VDWAALS    =    -632.2657
 EELEC  =   -3195.2287  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     170.4076  VIRIAL  =     242.1754  VOLUME     =   19680.4488
                                                Density    =       0.7700
 Ewald error estimate:   0.4098E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  20000 TIME(PS) =    20.000  TEMP(K) =   382.44  PRESS =  -289.9
 Etot   =    1117.7164  EKtot   =    1376.3156  EPtot      =    -258.5992
 BOND   =     185.5882  ANGLE   =     621.7730  DIHED      =     158.5743
 1-4 NB =     150.7561  1-4 EEL =    2468.6051  VDWAALS    =    -657.2401
 EELEC  =   -3186.6557  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     180.7388  VIRIAL  =     302.2283  VOLUME     =   19412.1672
                                                Density    =       0.7807
 Ewald error estimate:   0.1709E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  21000 TIME(PS) =    21.000  TEMP(K) =   373.33  PRESS =  -497.8
 Etot   =    1101.6548  EKtot   =    1343.5392  EPtot      =    -241.8844
 BOND   =     198.4834  ANGLE   =     638.5905  DIHED      =     136.6208
 1-4 NB =     159.1014  1-4 EEL =    2460.0198  VDWAALS    =    -671.0551
 EELEC  =   -3163.6452  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     173.9805  VIRIAL  =     381.8159  VOLUME     =   19335.4963
                                                Density    =       0.7838
 Ewald error estimate:   0.3668E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  22000 TIME(PS) =    22.000  TEMP(K) =   365.91  PRESS =   456.3
 Etot   =    1089.2039  EKtot   =    1316.8558  EPtot      =    -227.6520
 BOND   =     202.9912  ANGLE   =     644.2261  DIHED      =     147.7231
 1-4 NB =     157.7067  1-4 EEL =    2473.4097  VDWAALS    =    -679.2132
 EELEC  =   -3174.4955  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     151.1862  VIRIAL  =     -32.5725  VOLUME     =   18653.1027
                                                Density    =       0.8124
 Ewald error estimate:   0.4610E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  23000 TIME(PS) =    23.000  TEMP(K) =   384.73  PRESS =  -191.0
 Etot   =    1078.0042  EKtot   =    1384.5789  EPtot      =    -306.5747
 BOND   =     184.3511  ANGLE   =     646.7435  DIHED      =     146.9774
 1-4 NB =     159.0189  1-4 EEL =    2463.1289  VDWAALS    =    -672.2889
 EELEC  =   -3234.5057  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     161.2832  VIRIAL  =     238.9422  VOLUME     =   18833.1157
                                                Density    =       0.8047
 Ewald error estimate:   0.5889E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  24000 TIME(PS) =    24.000  TEMP(K) =   375.23  PRESS =  -238.2
 Etot   =    1054.4680  EKtot   =    1350.3870  EPtot      =    -295.9190
 BOND   =     191.3658  ANGLE   =     643.9857  DIHED      =     159.4753
 1-4 NB =     165.0237  1-4 EEL =    2481.0999  VDWAALS    =    -702.7030
 EELEC  =   -3234.1665  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     151.0270  VIRIAL  =     244.0201  VOLUME     =   18078.9652
                                                Density    =       0.8382
 Ewald error estimate:   0.2427E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  25000 TIME(PS) =    25.000  TEMP(K) =   374.51  PRESS =   -54.1
 Etot   =    1028.3222  EKtot   =    1347.7994  EPtot      =    -319.4772
 BOND   =     224.9274  ANGLE   =     656.9114  DIHED      =     138.2213
 1-4 NB =     158.4437  1-4 EEL =    2457.5917  VDWAALS    =    -742.6856
 EELEC  =   -3212.8872  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     160.0786  VIRIAL  =     180.6567  VOLUME     =   17614.7856
                                                Density    =       0.8603
 Ewald error estimate:   0.6655E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  26000 TIME(PS) =    26.000  TEMP(K) =   371.50  PRESS =     1.5
 Etot   =    1019.8638  EKtot   =    1336.9583  EPtot      =    -317.0945
 BOND   =     193.5412  ANGLE   =     684.9911  DIHED      =     123.4861
 1-4 NB =     163.2788  1-4 EEL =    2476.8252  VDWAALS    =    -727.3859
 EELEC  =   -3231.8310  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     160.6520  VIRIAL  =     160.0849  VOLUME     =   17745.8965
                                                Density    =       0.8540
 Ewald error estimate:   0.2405E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  27000 TIME(PS) =    27.000  TEMP(K) =   366.49  PRESS =   296.8
 Etot   =    1008.5439  EKtot   =    1318.9337  EPtot      =    -310.3898
 BOND   =     208.3852  ANGLE   =     674.5636  DIHED      =     142.2489
 1-4 NB =     153.3005  1-4 EEL =    2456.8843  VDWAALS    =    -719.5859
 EELEC  =   -3226.1864  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.1669  VIRIAL  =      21.7196  VOLUME     =   17705.4864
                                                Density    =       0.8559
 Ewald error estimate:   0.1305E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  28000 TIME(PS) =    28.000  TEMP(K) =   367.49  PRESS =   430.4
 Etot   =    1012.8460  EKtot   =    1322.5295  EPtot      =    -309.6835
 BOND   =     208.4279  ANGLE   =     669.9460  DIHED      =     155.2764
 1-4 NB =     150.3886  1-4 EEL =    2455.0095  VDWAALS    =    -726.3213
 EELEC  =   -3222.4105  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.2083  VIRIAL  =     -27.7599  VOLUME     =   17753.3694
                                                Density    =       0.8536
 Ewald error estimate:   0.1651E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  29000 TIME(PS) =    29.000  TEMP(K) =   376.30  PRESS =   127.3
 Etot   =    1011.2517  EKtot   =    1354.2190  EPtot      =    -342.9674
 BOND   =     211.4618  ANGLE   =     634.9100  DIHED      =     145.0332
 1-4 NB =     167.5840  1-4 EEL =    2466.3039  VDWAALS    =    -729.0090
 EELEC  =   -3239.2512  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.0597  VIRIAL  =      94.2580  VOLUME     =   17756.5052
                                                Density    =       0.8535
 Ewald error estimate:   0.7930E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  30000 TIME(PS) =    30.000  TEMP(K) =   363.27  PRESS =  -289.9
 Etot   =    1009.7382  EKtot   =    1307.3492  EPtot      =    -297.6110
 BOND   =     189.1366  ANGLE   =     693.6378  DIHED      =     154.5001
 1-4 NB =     163.8259  1-4 EEL =    2478.9081  VDWAALS    =    -732.1585
 EELEC  =   -3245.4611  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.5352  VIRIAL  =     249.0961  VOLUME     =   17821.6854
                                                Density    =       0.8503
 Ewald error estimate:   0.3118E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  31000 TIME(PS) =    31.000  TEMP(K) =   374.67  PRESS =    48.2
 Etot   =    1006.5086  EKtot   =    1348.3632  EPtot      =    -341.8547
 BOND   =     180.2926  ANGLE   =     672.8767  DIHED      =     147.7433
 1-4 NB =     162.1490  1-4 EEL =    2481.2549  VDWAALS    =    -731.4352
 EELEC  =   -3254.7359  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.6012  VIRIAL  =     124.2549  VOLUME     =   17615.6636
                                                Density    =       0.8603
 Ewald error estimate:   0.9947E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  32000 TIME(PS) =    32.000  TEMP(K) =   376.54  PRESS =  -355.4
 Etot   =    1003.4265  EKtot   =    1355.0907  EPtot      =    -351.6643
 BOND   =     188.7249  ANGLE   =     634.1258  DIHED      =     163.3328
 1-4 NB =     173.8041  1-4 EEL =    2482.0468  VDWAALS    =    -742.6047
 EELEC  =   -3251.0940  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.9939  VIRIAL  =     286.1989  VOLUME     =   17749.1454
                                                Density    =       0.8538
 Ewald error estimate:   0.2005E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  33000 TIME(PS) =    33.000  TEMP(K) =   369.29  PRESS =   235.8
 Etot   =     994.4731  EKtot   =    1329.0016  EPtot      =    -334.5284
 BOND   =     206.7281  ANGLE   =     688.0326  DIHED      =     134.1211
 1-4 NB =     158.3854  1-4 EEL =    2468.8970  VDWAALS    =    -727.6726
 EELEC  =   -3263.0200  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.0301  VIRIAL  =      55.6408  VOLUME     =   17756.8147
                                                Density    =       0.8534
 Ewald error estimate:   0.1280E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  34000 TIME(PS) =    34.000  TEMP(K) =   368.13  PRESS =    61.3
 Etot   =     994.8123  EKtot   =    1324.8257  EPtot      =    -330.0133
 BOND   =     213.6468  ANGLE   =     669.8259  DIHED      =     142.8390
 1-4 NB =     160.0603  1-4 EEL =    2460.8275  VDWAALS    =    -724.2323
 EELEC  =   -3252.9806  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.1221  VIRIAL  =     120.4748  VOLUME     =   17854.0901
                                                Density    =       0.8488
 Ewald error estimate:   0.2381E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  35000 TIME(PS) =    35.000  TEMP(K) =   369.01  PRESS =   -48.9
 Etot   =    1005.3086  EKtot   =    1327.9841  EPtot      =    -322.6755
 BOND   =     217.5625  ANGLE   =     665.5866  DIHED      =     127.9047
 1-4 NB =     158.0324  1-4 EEL =    2472.7251  VDWAALS    =    -715.1636
 EELEC  =   -3249.3232  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.8004  VIRIAL  =     150.7825  VOLUME     =   17974.2473
                                                Density    =       0.8431
 Ewald error estimate:   0.2055E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  36000 TIME(PS) =    36.000  TEMP(K) =   377.19  PRESS =  -308.5
 Etot   =     989.6153  EKtot   =    1357.4245  EPtot      =    -367.8093
 BOND   =     206.2457  ANGLE   =     695.4952  DIHED      =     141.5739
 1-4 NB =     160.7120  1-4 EEL =    2474.8753  VDWAALS    =    -752.2660
 EELEC  =   -3294.4453  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     160.3831  VIRIAL  =     276.2245  VOLUME     =   17393.3368
                                                Density    =       0.8713
 Ewald error estimate:   0.2988E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  37000 TIME(PS) =    37.000  TEMP(K) =   366.55  PRESS =  -399.3
 Etot   =     986.9219  EKtot   =    1319.1438  EPtot      =    -332.2219
 BOND   =     206.3545  ANGLE   =     674.2882  DIHED      =     135.1105
 1-4 NB =     172.0753  1-4 EEL =    2491.3324  VDWAALS    =    -745.7261
 EELEC  =   -3265.6567  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.3883  VIRIAL  =     276.5155  VOLUME     =   17529.9384
                                                Density    =       0.8645
 Ewald error estimate:   0.1956E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  38000 TIME(PS) =    38.000  TEMP(K) =   382.17  PRESS =   147.8
 Etot   =     985.3703  EKtot   =    1375.3521  EPtot      =    -389.9818
 BOND   =     192.7574  ANGLE   =     660.2319  DIHED      =     149.4917
 1-4 NB =     162.7139  1-4 EEL =    2462.8768  VDWAALS    =    -749.9503
 EELEC  =   -3268.1031  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.7033  VIRIAL  =      83.8685  VOLUME     =   17498.0249
                                                Density    =       0.8661
 Ewald error estimate:   0.4381E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  39000 TIME(PS) =    39.000  TEMP(K) =   374.12  PRESS =    61.0
 Etot   =     978.1002  EKtot   =    1346.3984  EPtot      =    -368.2982
 BOND   =     175.4214  ANGLE   =     693.5242  DIHED      =     119.6970
 1-4 NB =     162.5646  1-4 EEL =    2478.4669  VDWAALS    =    -729.9009
 EELEC  =   -3268.0712  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.8170  VIRIAL  =     106.7273  VOLUME     =   17533.4606
                                                Density    =       0.8643
 Ewald error estimate:   0.1674E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  40000 TIME(PS) =    40.000  TEMP(K) =   376.53  PRESS =  -233.5
 Etot   =     980.3363  EKtot   =    1355.0702  EPtot      =    -374.7339
 BOND   =     180.8089  ANGLE   =     665.2017  DIHED      =     131.8164
 1-4 NB =     164.8962  1-4 EEL =    2474.0584  VDWAALS    =    -753.5106
 EELEC  =   -3238.0048  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.8157  VIRIAL  =     226.8526  VOLUME     =   17464.2297
                                                Density    =       0.8677
 Ewald error estimate:   0.8543E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  41000 TIME(PS) =    41.000  TEMP(K) =   374.93  PRESS =   589.8
 Etot   =     985.7482  EKtot   =    1349.2917  EPtot      =    -363.5435
 BOND   =     187.6435  ANGLE   =     652.4445  DIHED      =     147.5046
 1-4 NB =     162.3774  1-4 EEL =    2473.0917  VDWAALS    =    -703.3407
 EELEC  =   -3283.2645  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.8697  VIRIAL  =     -75.4024  VOLUME     =   17688.6473
                                                Density    =       0.8567
 Ewald error estimate:   0.6001E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  42000 TIME(PS) =    42.000  TEMP(K) =   370.25  PRESS =  -353.3
 Etot   =     994.0138  EKtot   =    1332.4729  EPtot      =    -338.4591
 BOND   =     204.8334  ANGLE   =     664.4590  DIHED      =     142.5524
 1-4 NB =     158.8873  1-4 EEL =    2471.4980  VDWAALS    =    -734.7503
 EELEC  =   -3245.9389  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.2397  VIRIAL  =     275.5955  VOLUME     =   17743.2496
                                                Density    =       0.8541
 Ewald error estimate:   0.4816E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  43000 TIME(PS) =    43.000  TEMP(K) =   363.20  PRESS =    63.8
 Etot   =     992.1307  EKtot   =    1307.0843  EPtot      =    -314.9537
 BOND   =     222.0801  ANGLE   =     689.6256  DIHED      =     142.6112
 1-4 NB =     157.6353  1-4 EEL =    2474.3090  VDWAALS    =    -735.7767
 EELEC  =   -3265.4382  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     162.1542  VIRIAL  =     137.6621  VOLUME     =   17780.8771
                                                Density    =       0.8523
 Ewald error estimate:   0.2212E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  44000 TIME(PS) =    44.000  TEMP(K) =   380.18  PRESS =  -343.4
 Etot   =     987.8472  EKtot   =    1368.1958  EPtot      =    -380.3486
 BOND   =     196.0314  ANGLE   =     648.5733  DIHED      =     145.8516
 1-4 NB =     162.4308  1-4 EEL =    2476.7800  VDWAALS    =    -754.3668
 EELEC  =   -3255.6489  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     163.4574  VIRIAL  =     293.0502  VOLUME     =   17477.6978
                                                Density    =       0.8671
 Ewald error estimate:   0.6744E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  45000 TIME(PS) =    45.000  TEMP(K) =   365.63  PRESS =   479.2
 Etot   =     981.2565  EKtot   =    1315.8346  EPtot      =    -334.5780
 BOND   =     219.7968  ANGLE   =     672.4978  DIHED      =     151.2957
 1-4 NB =     165.3939  1-4 EEL =    2460.1918  VDWAALS    =    -713.5682
 EELEC  =   -3290.1858  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.6362  VIRIAL  =     -57.0578  VOLUME     =   17755.0887
                                                Density    =       0.8535
 Ewald error estimate:   0.1857E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  46000 TIME(PS) =    46.000  TEMP(K) =   373.50  PRESS =   -53.7
 Etot   =     977.5942  EKtot   =    1344.1553  EPtot      =    -366.5611
 BOND   =     212.7103  ANGLE   =     659.5369  DIHED      =     145.6854
 1-4 NB =     155.3139  1-4 EEL =    2465.5758  VDWAALS    =    -741.1735
 EELEC  =   -3264.2101  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.0913  VIRIAL  =     157.3706  VOLUME     =   17497.4263
                                                Density    =       0.8661
 Ewald error estimate:   0.3906E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  47000 TIME(PS) =    47.000  TEMP(K) =   361.68  PRESS =   375.8
 Etot   =     977.4680  EKtot   =    1301.6292  EPtot      =    -324.1612
 BOND   =     201.0365  ANGLE   =     694.4488  DIHED      =     137.3749
 1-4 NB =     167.8836  1-4 EEL =    2477.0791  VDWAALS    =    -726.1969
 EELEC  =   -3275.7872  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.2155  VIRIAL  =     -15.2432  VOLUME     =   17556.5907
                                                Density    =       0.8632
 Ewald error estimate:   0.3066E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  48000 TIME(PS) =    48.000  TEMP(K) =   378.22  PRESS =   204.2
 Etot   =     970.6453  EKtot   =    1361.1236  EPtot      =    -390.4783
 BOND   =     184.3084  ANGLE   =     687.2725  DIHED      =     123.2553
 1-4 NB =     155.9397  1-4 EEL =    2468.0426  VDWAALS    =    -743.1280
 EELEC  =   -3266.1686  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.3064  VIRIAL  =      52.6117  VOLUME     =   17396.8011
                                                Density    =       0.8711
 Ewald error estimate:   0.6732E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  49000 TIME(PS) =    49.000  TEMP(K) =   377.57  PRESS =  -144.0
 Etot   =     971.8785  EKtot   =    1358.8118  EPtot      =    -386.9333
 BOND   =     178.1851  ANGLE   =     672.4520  DIHED      =     132.3073
 1-4 NB =     155.7960  1-4 EEL =    2469.9754  VDWAALS    =    -754.6426
 EELEC  =   -3241.0066  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.3188  VIRIAL  =     195.4783  VOLUME     =   17425.0062
                                                Density    =       0.8697
 Ewald error estimate:   0.2232E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =   365.99  PRESS =  -263.7
 Etot   =     979.2409  EKtot   =    1317.1186  EPtot      =    -337.8777
 BOND   =     198.1851  ANGLE   =     711.2424  DIHED      =     138.0681
 1-4 NB =     155.7233  1-4 EEL =    2466.7699  VDWAALS    =    -766.4511
 EELEC  =   -3241.4154  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     152.5296  VIRIAL  =     250.6430  VOLUME     =   17233.7958
                                                Density    =       0.8793
 Ewald error estimate:   0.9462E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  51000 TIME(PS) =    51.000  TEMP(K) =   365.34  PRESS =  -259.5
 Etot   =     977.3377  EKtot   =    1314.7905  EPtot      =    -337.4528
 BOND   =     220.0973  ANGLE   =     692.6727  DIHED      =     152.2218
 1-4 NB =     148.0470  1-4 EEL =    2456.1874  VDWAALS    =    -768.1156
 EELEC  =   -3238.5634  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.4961  VIRIAL  =     227.9272  VOLUME     =   17208.0998
                                                Density    =       0.8807
 Ewald error estimate:   0.4883E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  52000 TIME(PS) =    52.000  TEMP(K) =   365.90  PRESS =   152.9
 Etot   =     970.6370  EKtot   =    1316.8031  EPtot      =    -346.1661
 BOND   =     208.9213  ANGLE   =     689.8218  DIHED      =     153.9654
 1-4 NB =     160.2187  1-4 EEL =    2468.2235  VDWAALS    =    -739.6229
 EELEC  =   -3287.6938  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.0002  VIRIAL  =      78.5975  VOLUME     =   17386.6503
                                                Density    =       0.8716
 Ewald error estimate:   0.4374E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  53000 TIME(PS) =    53.000  TEMP(K) =   378.72  PRESS =  -221.6
 Etot   =     972.2574  EKtot   =    1362.9323  EPtot      =    -390.6749
 BOND   =     211.0767  ANGLE   =     664.3480  DIHED      =     145.9987
 1-4 NB =     163.4258  1-4 EEL =    2469.8416  VDWAALS    =    -763.8823
 EELEC  =   -3281.4833  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.8489  VIRIAL  =     229.2010  VOLUME     =   17211.6554
                                                Density    =       0.8805
 Ewald error estimate:   0.1963E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  54000 TIME(PS) =    54.000  TEMP(K) =   371.68  PRESS =    29.5
 Etot   =     966.6685  EKtot   =    1337.5855  EPtot      =    -370.9170
 BOND   =     177.2869  ANGLE   =     711.0813  DIHED      =     138.3233
 1-4 NB =     177.9402  1-4 EEL =    2484.5891  VDWAALS    =    -766.8314
 EELEC  =   -3293.3064  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     155.8534  VIRIAL  =     144.9445  VOLUME     =   17101.7196
                                                Density    =       0.8861
 Ewald error estimate:   0.6753E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  55000 TIME(PS) =    55.000  TEMP(K) =   358.43  PRESS =   -44.6
 Etot   =     965.3111  EKtot   =    1289.9211  EPtot      =    -324.6100
 BOND   =     221.0122  ANGLE   =     678.2284  DIHED      =     177.5268
 1-4 NB =     163.7814  1-4 EEL =    2473.9884  VDWAALS    =    -751.9636
 EELEC  =   -3287.1836  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.9639  VIRIAL  =     151.5505  VOLUME     =   17220.6536
                                                Density    =       0.8800
 Ewald error estimate:   0.4425E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  56000 TIME(PS) =    56.000  TEMP(K) =   379.49  PRESS =  -329.5
 Etot   =     964.0719  EKtot   =    1365.6937  EPtot      =    -401.6217
 BOND   =     168.5676  ANGLE   =     686.1633  DIHED      =     144.4672
 1-4 NB =     168.5826  1-4 EEL =    2482.6234  VDWAALS    =    -761.2494
 EELEC  =   -3290.7765  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.1596  VIRIAL  =     261.1752  VOLUME     =   17151.0176
                                                Density    =       0.8836
 Ewald error estimate:   0.6801E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  57000 TIME(PS) =    57.000  TEMP(K) =   370.24  PRESS =  -246.5
 Etot   =     957.3184  EKtot   =    1332.4211  EPtot      =    -375.1027
 BOND   =     181.2640  ANGLE   =     696.2982  DIHED      =     148.7260
 1-4 NB =     158.8157  1-4 EEL =    2470.3061  VDWAALS    =    -771.6193
 EELEC  =   -3258.8934  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.4889  VIRIAL  =     223.5917  VOLUME     =   17120.5176
                                                Density    =       0.8852
 Ewald error estimate:   0.1225E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  58000 TIME(PS) =    58.000  TEMP(K) =   370.39  PRESS =  -207.6
 Etot   =     954.9439  EKtot   =    1332.9740  EPtot      =    -378.0300
 BOND   =     192.3248  ANGLE   =     691.2409  DIHED      =     153.2685
 1-4 NB =     157.5147  1-4 EEL =    2470.9238  VDWAALS    =    -766.9753
 EELEC  =   -3276.3274  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.2229  VIRIAL  =     197.9074  VOLUME     =   17106.4617
                                                Density    =       0.8859
 Ewald error estimate:   0.1395E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  59000 TIME(PS) =    59.000  TEMP(K) =   369.98  PRESS =  -577.0
 Etot   =     958.8376  EKtot   =    1331.5035  EPtot      =    -372.6658
 BOND   =     180.8349  ANGLE   =     695.9221  DIHED      =     136.9122
 1-4 NB =     170.8228  1-4 EEL =    2478.5615  VDWAALS    =    -803.7255
 EELEC  =   -3231.9940  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.9984  VIRIAL  =     340.3073  VOLUME     =   16960.3847
                                                Density    =       0.8935
 Ewald error estimate:   0.8236E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  60000 TIME(PS) =    60.000  TEMP(K) =   366.16  PRESS =   317.5
 Etot   =     952.6538  EKtot   =    1317.7424  EPtot      =    -365.0886
 BOND   =     210.6745  ANGLE   =     678.3695  DIHED      =     149.2715
 1-4 NB =     163.2068  1-4 EEL =    2475.1964  VDWAALS    =    -745.2645
 EELEC  =   -3296.5427  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.4438  VIRIAL  =      16.9295  VOLUME     =   17287.9055
                                                Density    =       0.8766
 Ewald error estimate:   0.3029E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  61000 TIME(PS) =    61.000  TEMP(K) =   371.46  PRESS =  -227.2
 Etot   =     958.9277  EKtot   =    1336.8270  EPtot      =    -377.8993
 BOND   =     212.0800  ANGLE   =     674.3095  DIHED      =     135.1126
 1-4 NB =     172.7263  1-4 EEL =    2470.1407  VDWAALS    =    -727.7517
 EELEC  =   -3314.5167  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.7681  VIRIAL  =     217.1980  VOLUME     =   17618.0955
                                                Density    =       0.8602
 Ewald error estimate:   0.4715E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  62000 TIME(PS) =    62.000  TEMP(K) =   380.38  PRESS =   -53.1
 Etot   =     963.3282  EKtot   =    1368.9303  EPtot      =    -405.6022
 BOND   =     194.8637  ANGLE   =     664.3505  DIHED      =     135.4951
 1-4 NB =     161.5013  1-4 EEL =    2490.9554  VDWAALS    =    -743.4921
 EELEC  =   -3309.2762  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     118.8878  VIRIAL  =     138.8565  VOLUME     =   17421.7565
                                                Density    =       0.8699
 Ewald error estimate:   0.2889E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  63000 TIME(PS) =    63.000  TEMP(K) =   384.23  PRESS =   -95.3
 Etot   =     965.3000  EKtot   =    1382.7771  EPtot      =    -417.4771
 BOND   =     191.1290  ANGLE   =     656.5987  DIHED      =     135.4267
 1-4 NB =     161.1540  1-4 EEL =    2480.7968  VDWAALS    =    -729.6143
 EELEC  =   -3312.9681  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.2133  VIRIAL  =     166.1881  VOLUME     =   17487.1518
                                                Density    =       0.8666
 Ewald error estimate:   0.3967E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  64000 TIME(PS) =    64.000  TEMP(K) =   361.31  PRESS =    84.7
 Etot   =     963.5748  EKtot   =    1300.2664  EPtot      =    -336.6917
 BOND   =     217.6967  ANGLE   =     689.8461  DIHED      =     146.1360
 1-4 NB =     159.5437  1-4 EEL =    2472.3523  VDWAALS    =    -749.6751
 EELEC  =   -3272.5914  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     116.1123  VIRIAL  =      84.3314  VOLUME     =   17379.0845
                                                Density    =       0.8720
 Ewald error estimate:   0.8802E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  65000 TIME(PS) =    65.000  TEMP(K) =   375.06  PRESS =   -66.0
 Etot   =     971.8113  EKtot   =    1349.7591  EPtot      =    -377.9477
 BOND   =     180.8872  ANGLE   =     682.8142  DIHED      =     145.5428
 1-4 NB =     166.7196  1-4 EEL =    2477.4627  VDWAALS    =    -750.6246
 EELEC  =   -3280.7496  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.4576  VIRIAL  =     156.2723  VOLUME     =   17404.1198
                                                Density    =       0.8707
 Ewald error estimate:   0.2973E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  66000 TIME(PS) =    66.000  TEMP(K) =   371.61  PRESS =    33.4
 Etot   =     964.6729  EKtot   =    1337.3554  EPtot      =    -372.6825
 BOND   =     200.3270  ANGLE   =     708.6966  DIHED      =     136.5570
 1-4 NB =     159.8246  1-4 EEL =    2464.5709  VDWAALS    =    -748.3375
 EELEC  =   -3294.3211  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.7561  VIRIAL  =     123.2358  VOLUME     =   17338.3976
                                                Density    =       0.8740
 Ewald error estimate:   0.1667E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  67000 TIME(PS) =    67.000  TEMP(K) =   386.47  PRESS =    68.1
 Etot   =     957.4552  EKtot   =    1390.8286  EPtot      =    -433.3734
 BOND   =     200.0901  ANGLE   =     673.0760  DIHED      =     134.4995
 1-4 NB =     162.2451  1-4 EEL =    2458.5190  VDWAALS    =    -748.5718
 EELEC  =   -3313.2312  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.8563  VIRIAL  =     114.3485  VOLUME     =   17343.8789
                                                Density    =       0.8738
 Ewald error estimate:   0.3127E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  68000 TIME(PS) =    68.000  TEMP(K) =   376.51  PRESS =   416.6
 Etot   =     958.1703  EKtot   =    1354.9899  EPtot      =    -396.8197
 BOND   =     184.6891  ANGLE   =     677.5915  DIHED      =     124.8056
 1-4 NB =     158.6204  1-4 EEL =    2477.2588  VDWAALS    =    -752.7982
 EELEC  =   -3266.9868  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.9576  VIRIAL  =     -28.4663  VOLUME     =   17167.3220
                                                Density    =       0.8827
 Ewald error estimate:   0.8026E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  69000 TIME(PS) =    69.000  TEMP(K) =   371.66  PRESS =  -131.7
 Etot   =     965.0720  EKtot   =    1337.5207  EPtot      =    -372.4487
 BOND   =     187.1894  ANGLE   =     685.5068  DIHED      =     140.5888
 1-4 NB =     163.4913  1-4 EEL =    2478.7256  VDWAALS    =    -742.5439
 EELEC  =   -3285.4066  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.1401  VIRIAL  =     175.9129  VOLUME     =   17504.6679
                                                Density    =       0.8657
 Ewald error estimate:   0.1006E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  70000 TIME(PS) =    70.000  TEMP(K) =   365.34  PRESS =   111.9
 Etot   =     967.4820  EKtot   =    1314.7963  EPtot      =    -347.3144
 BOND   =     198.4199  ANGLE   =     711.7172  DIHED      =     151.3372
 1-4 NB =     149.7588  1-4 EEL =    2458.7240  VDWAALS    =    -745.2779
 EELEC  =   -3271.9935  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     162.0851  VIRIAL  =     119.5915  VOLUME     =   17590.4592
                                                Density    =       0.8615
 Ewald error estimate:   0.2293E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  71000 TIME(PS) =    71.000  TEMP(K) =   369.31  PRESS =  -238.7
 Etot   =     981.5911  EKtot   =    1329.0757  EPtot      =    -347.4846
 BOND   =     196.0361  ANGLE   =     689.0385  DIHED      =     141.3878
 1-4 NB =     160.6016  1-4 EEL =    2478.4434  VDWAALS    =    -730.8065
 EELEC  =   -3282.1854  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.9045  VIRIAL  =     218.0856  VOLUME     =   17888.5088
                                                Density    =       0.8472
 Ewald error estimate:   0.4413E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  72000 TIME(PS) =    72.000  TEMP(K) =   372.66  PRESS =    25.7
 Etot   =     982.7248  EKtot   =    1341.1311  EPtot      =    -358.4062
 BOND   =     186.3601  ANGLE   =     673.6651  DIHED      =     144.1108
 1-4 NB =     166.6042  1-4 EEL =    2487.3852  VDWAALS    =    -734.9776
 EELEC  =   -3281.5540  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.8922  VIRIAL  =     127.1399  VOLUME     =   17594.1809
                                                Density    =       0.8613
 Ewald error estimate:   0.6691E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  73000 TIME(PS) =    73.000  TEMP(K) =   382.36  PRESS =  -317.6
 Etot   =     983.7238  EKtot   =    1376.0526  EPtot      =    -392.3288
 BOND   =     185.1974  ANGLE   =     681.5138  DIHED      =     129.5432
 1-4 NB =     171.2131  1-4 EEL =    2492.9699  VDWAALS    =    -754.3886
 EELEC  =   -3298.3776  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.5379  VIRIAL  =     250.8553  VOLUME     =   17400.7398
                                                Density    =       0.8709
 Ewald error estimate:   0.3290E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  74000 TIME(PS) =    74.000  TEMP(K) =   381.87  PRESS =   335.3
 Etot   =     980.5844  EKtot   =    1374.2714  EPtot      =    -393.6870
 BOND   =     216.6382  ANGLE   =     635.9871  DIHED      =     131.5927
 1-4 NB =     165.1858  1-4 EEL =    2475.8581  VDWAALS    =    -711.1164
 EELEC  =   -3307.8325  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.9997  VIRIAL  =      11.5146  VOLUME     =   17748.1306
                                                Density    =       0.8539
 Ewald error estimate:   0.2477E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  75000 TIME(PS) =    75.000  TEMP(K) =   377.53  PRESS =   530.0
 Etot   =     972.9126  EKtot   =    1358.6574  EPtot      =    -385.7448
 BOND   =     197.8739  ANGLE   =     685.1785  DIHED      =     136.8649
 1-4 NB =     158.5352  1-4 EEL =    2459.8444  VDWAALS    =    -725.1247
 EELEC  =   -3298.9169  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.7800  VIRIAL  =     -61.9541  VOLUME     =   17453.6905
                                                Density    =       0.8683
 Ewald error estimate:   0.1143E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  76000 TIME(PS) =    76.000  TEMP(K) =   372.55  PRESS =  -304.8
 Etot   =     973.9097  EKtot   =    1340.7392  EPtot      =    -366.8294
 BOND   =     204.0446  ANGLE   =     655.3991  DIHED      =     146.5438
 1-4 NB =     162.0058  1-4 EEL =    2471.2293  VDWAALS    =    -743.5043
 EELEC  =   -3262.5477  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.6251  VIRIAL  =     254.3021  VOLUME     =   17578.7848
                                                Density    =       0.8621
 Ewald error estimate:   0.1067E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  77000 TIME(PS) =    77.000  TEMP(K) =   379.27  PRESS =   -36.7
 Etot   =     977.7332  EKtot   =    1364.9279  EPtot      =    -387.1947
 BOND   =     200.7176  ANGLE   =     660.8604  DIHED      =     163.4301
 1-4 NB =     153.3835  1-4 EEL =    2469.9231  VDWAALS    =    -731.8945
 EELEC  =   -3303.6148  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.5382  VIRIAL  =     152.4850  VOLUME     =   17610.7282
                                                Density    =       0.8605
 Ewald error estimate:   0.3072E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  78000 TIME(PS) =    78.000  TEMP(K) =   375.51  PRESS =   223.1
 Etot   =     975.2961  EKtot   =    1351.3975  EPtot      =    -376.1014
 BOND   =     203.6153  ANGLE   =     657.6053  DIHED      =     142.8859
 1-4 NB =     162.8148  1-4 EEL =    2471.9025  VDWAALS    =    -711.8829
 EELEC  =   -3303.0422  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.1913  VIRIAL  =      58.3988  VOLUME     =   17603.0756
                                                Density    =       0.8609
 Ewald error estimate:   0.1993E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  79000 TIME(PS) =    79.000  TEMP(K) =   358.25  PRESS =  -196.2
 Etot   =     973.4722  EKtot   =    1289.2589  EPtot      =    -315.7868
 BOND   =     201.4078  ANGLE   =     677.2244  DIHED      =     160.5958
 1-4 NB =     170.6256  1-4 EEL =    2474.8019  VDWAALS    =    -736.1415
 EELEC  =   -3264.3009  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.7212  VIRIAL  =     207.8003  VOLUME     =   17724.2890
                                                Density    =       0.8550
 Ewald error estimate:   0.1529E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  80000 TIME(PS) =    80.000  TEMP(K) =   364.46  PRESS =  -190.3
 Etot   =     965.6406  EKtot   =    1311.6133  EPtot      =    -345.9727
 BOND   =     201.2480  ANGLE   =     695.2182  DIHED      =     150.4340
 1-4 NB =     148.1182  1-4 EEL =    2463.3192  VDWAALS    =    -759.1292
 EELEC  =   -3245.1812  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.1403  VIRIAL  =     215.6842  VOLUME     =   17413.6908
                                                Density    =       0.8703
 Ewald error estimate:   0.8586E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  81000 TIME(PS) =    81.000  TEMP(K) =   363.65  PRESS =   -30.6
 Etot   =     962.8911  EKtot   =    1308.6999  EPtot      =    -345.8088
 BOND   =     196.3698  ANGLE   =     698.3039  DIHED      =     153.5205
 1-4 NB =     157.3015  1-4 EEL =    2465.7980  VDWAALS    =    -754.2975
 EELEC  =   -3262.8050  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.4722  VIRIAL  =     153.9428  VOLUME     =   17347.9932
                                                Density    =       0.8735
 Ewald error estimate:   0.2220E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  82000 TIME(PS) =    82.000  TEMP(K) =   370.13  PRESS =   -84.6
 Etot   =     962.1097  EKtot   =    1332.0175  EPtot      =    -369.9078
 BOND   =     206.1897  ANGLE   =     680.9739  DIHED      =     139.3241
 1-4 NB =     163.5019  1-4 EEL =    2461.6716  VDWAALS    =    -742.0120
 EELEC  =   -3279.5570  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.4362  VIRIAL  =     174.3978  VOLUME     =   17488.8880
                                                Density    =       0.8665
 Ewald error estimate:   0.4220E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  83000 TIME(PS) =    83.000  TEMP(K) =   363.35  PRESS =   -10.3
 Etot   =     965.9938  EKtot   =    1307.6140  EPtot      =    -341.6202
 BOND   =     184.9169  ANGLE   =     704.2573  DIHED      =     136.8296
 1-4 NB =     160.3456  1-4 EEL =    2471.1690  VDWAALS    =    -727.4867
 EELEC  =   -3271.6518  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.3078  VIRIAL  =     139.2442  VOLUME     =   17678.4460
                                                Density    =       0.8572
 Ewald error estimate:   0.3439E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  84000 TIME(PS) =    84.000  TEMP(K) =   369.85  PRESS =  -225.7
 Etot   =     967.5311  EKtot   =    1331.0223  EPtot      =    -363.4912
 BOND   =     195.5343  ANGLE   =     662.0703  DIHED      =     160.5475
 1-4 NB =     166.2270  1-4 EEL =    2478.2801  VDWAALS    =    -746.8305
 EELEC  =   -3279.3199  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.0111  VIRIAL  =     221.9770  VOLUME     =   17437.4455
                                                Density    =       0.8691
 Ewald error estimate:   0.9090E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  85000 TIME(PS) =    85.000  TEMP(K) =   364.69  PRESS =   475.8
 Etot   =     960.3410  EKtot   =    1312.4449  EPtot      =    -352.1039
 BOND   =     204.1353  ANGLE   =     713.6248  DIHED      =     130.2288
 1-4 NB =     158.6346  1-4 EEL =    2461.6756  VDWAALS    =    -726.7444
 EELEC  =   -3293.6586  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.0132  VIRIAL  =     -35.5496  VOLUME     =   17285.1581
                                                Density    =       0.8767
 Ewald error estimate:   0.2317E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  86000 TIME(PS) =    86.000  TEMP(K) =   365.50  PRESS =   569.6
 Etot   =     955.2639  EKtot   =    1315.3658  EPtot      =    -360.1018
 BOND   =     196.0181  ANGLE   =     712.3141  DIHED      =     144.2977
 1-4 NB =     158.7129  1-4 EEL =    2474.4089  VDWAALS    =    -726.4799
 EELEC  =   -3319.3736  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.3233  VIRIAL  =     -79.5143  VOLUME     =   17305.9827
                                                Density    =       0.8757
 Ewald error estimate:   0.6923E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  87000 TIME(PS) =    87.000  TEMP(K) =   378.84  PRESS =  -365.6
 Etot   =     942.4566  EKtot   =    1363.3603  EPtot      =    -420.9037
 BOND   =     187.7406  ANGLE   =     674.3958  DIHED      =     134.6700
 1-4 NB =     160.2445  1-4 EEL =    2468.1895  VDWAALS    =    -764.0448
 EELEC  =   -3282.0993  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.5121  VIRIAL  =     281.8226  VOLUME     =   17268.2210
                                                Density    =       0.8776
 Ewald error estimate:   0.1965E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  88000 TIME(PS) =    88.000  TEMP(K) =   363.92  PRESS =  -163.6
 Etot   =     940.4717  EKtot   =    1309.6709  EPtot      =    -369.1992
 BOND   =     199.7398  ANGLE   =     712.7296  DIHED      =     149.0223
 1-4 NB =     157.3026  1-4 EEL =    2462.7533  VDWAALS    =    -753.4477
 EELEC  =   -3297.2991  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.9162  VIRIAL  =     192.8101  VOLUME     =   17238.8153
                                                Density    =       0.8791
 Ewald error estimate:   0.4153E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  89000 TIME(PS) =    89.000  TEMP(K) =   369.39  PRESS =  -131.0
 Etot   =     940.1999  EKtot   =    1329.3456  EPtot      =    -389.1456
 BOND   =     201.0285  ANGLE   =     669.7371  DIHED      =     154.4130
 1-4 NB =     163.8679  1-4 EEL =    2477.6549  VDWAALS    =    -742.3166
 EELEC  =   -3313.5303  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.4263  VIRIAL  =     174.2898  VOLUME     =   17273.6474
                                                Density    =       0.8773
 Ewald error estimate:   0.1548E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  90000 TIME(PS) =    90.000  TEMP(K) =   371.22  PRESS =   188.9
 Etot   =     944.8060  EKtot   =    1335.9503  EPtot      =    -391.1443
 BOND   =     223.9592  ANGLE   =     653.6996  DIHED      =     136.1993
 1-4 NB =     159.0002  1-4 EEL =    2478.2911  VDWAALS    =    -726.8469
 EELEC  =   -3315.4467  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.7484  VIRIAL  =      57.7642  VOLUME     =   17402.3365
                                                Density    =       0.8708
 Ewald error estimate:   0.3225E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  91000 TIME(PS) =    91.000  TEMP(K) =   363.97  PRESS =   346.0
 Etot   =     949.8813  EKtot   =    1309.8469  EPtot      =    -359.9656
 BOND   =     184.7052  ANGLE   =     709.1075  DIHED      =     135.9702
 1-4 NB =     167.8029  1-4 EEL =    2473.2357  VDWAALS    =    -727.1015
 EELEC  =   -3303.6855  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.9217  VIRIAL  =      -1.5457  VOLUME     =   17465.7905
                                                Density    =       0.8677
 Ewald error estimate:   0.4934E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  92000 TIME(PS) =    92.000  TEMP(K) =   374.47  PRESS =   -92.6
 Etot   =     956.3178  EKtot   =    1347.6314  EPtot      =    -391.3136
 BOND   =     188.0929  ANGLE   =     676.6027  DIHED      =     130.9634
 1-4 NB =     158.2917  1-4 EEL =    2483.3641  VDWAALS    =    -722.5120
 EELEC  =   -3306.1164  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.2474  VIRIAL  =     170.5880  VOLUME     =   17678.2438
                                                Density    =       0.8572
 Ewald error estimate:   0.1948E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  93000 TIME(PS) =    93.000  TEMP(K) =   366.48  PRESS =   -16.0
 Etot   =     965.5087  EKtot   =    1318.8737  EPtot      =    -353.3650
 BOND   =     220.9991  ANGLE   =     671.0561  DIHED      =     135.3695
 1-4 NB =     165.5146  1-4 EEL =    2456.9918  VDWAALS    =    -728.8908
 EELEC  =   -3274.4052  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     122.3597  VIRIAL  =     128.4610  VOLUME     =   17638.9090
                                                Density    =       0.8591
 Ewald error estimate:   0.1030E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  94000 TIME(PS) =    94.000  TEMP(K) =   368.08  PRESS =   181.0
 Etot   =     975.5148  EKtot   =    1324.6423  EPtot      =    -349.1275
 BOND   =     198.4076  ANGLE   =     689.3470  DIHED      =     129.0023
 1-4 NB =     167.2157  1-4 EEL =    2466.3538  VDWAALS    =    -721.7106
 EELEC  =   -3277.7433  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     150.6754  VIRIAL  =      81.6429  VOLUME     =   17663.9069
                                                Density    =       0.8579
 Ewald error estimate:   0.3790E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  95000 TIME(PS) =    95.000  TEMP(K) =   368.83  PRESS =    50.7
 Etot   =     977.4774  EKtot   =    1327.3490  EPtot      =    -349.8716
 BOND   =     186.2803  ANGLE   =     664.7190  DIHED      =     150.5445
 1-4 NB =     166.2163  1-4 EEL =    2476.6677  VDWAALS    =    -736.0533
 EELEC  =   -3258.2462  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     152.5125  VIRIAL  =     133.3204  VOLUME     =   17529.6464
                                                Density    =       0.8645
 Ewald error estimate:   0.2275E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  96000 TIME(PS) =    96.000  TEMP(K) =   372.59  PRESS =  -419.3
 Etot   =     978.7798  EKtot   =    1340.8741  EPtot      =    -362.0943
 BOND   =     189.0863  ANGLE   =     652.1344  DIHED      =     147.2211
 1-4 NB =     171.5982  1-4 EEL =    2487.7919  VDWAALS    =    -761.8903
 EELEC  =   -3248.0359  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.4364  VIRIAL  =     303.5020  VOLUME     =   17349.8143
                                                Density    =       0.8735
 Ewald error estimate:   0.1942E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  97000 TIME(PS) =    97.000  TEMP(K) =   370.86  PRESS =  -368.0
 Etot   =     973.6602  EKtot   =    1334.6658  EPtot      =    -361.0057
 BOND   =     196.4723  ANGLE   =     671.8311  DIHED      =     150.4131
 1-4 NB =     152.9576  1-4 EEL =    2469.3888  VDWAALS    =    -737.6017
 EELEC  =   -3264.4668  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     153.9155  VIRIAL  =     293.1954  VOLUME     =   17528.8746
                                                Density    =       0.8645
 Ewald error estimate:   0.2494E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  98000 TIME(PS) =    98.000  TEMP(K) =   389.82  PRESS =  -548.6
 Etot   =     973.8095  EKtot   =    1402.8982  EPtot      =    -429.0887
 BOND   =     203.6292  ANGLE   =     667.2305  DIHED      =     125.6527
 1-4 NB =     152.2656  1-4 EEL =    2451.6735  VDWAALS    =    -759.2365
 EELEC  =   -3270.3036  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.4560  VIRIAL  =     355.6486  VOLUME     =   17406.5886
                                                Density    =       0.8706
 Ewald error estimate:   0.3472E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  99000 TIME(PS) =    99.000  TEMP(K) =   365.85  PRESS =   272.3
 Etot   =     967.9124  EKtot   =    1316.6209  EPtot      =    -348.7085
 BOND   =     224.2850  ANGLE   =     693.7586  DIHED      =     134.7752
 1-4 NB =     152.2897  1-4 EEL =    2457.1667  VDWAALS    =    -747.4587
 EELEC  =   -3263.5250  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.9578  VIRIAL  =      33.0616  VOLUME     =   17331.1056
                                                Density    =       0.8744
 Ewald error estimate:   0.2215E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 100000 TIME(PS) =   100.000  TEMP(K) =   379.57  PRESS =   128.7
 Etot   =     960.0674  EKtot   =    1365.9907  EPtot      =    -405.9232
 BOND   =     184.1691  ANGLE   =     707.3262  DIHED      =     131.8942
 1-4 NB =     155.3033  1-4 EEL =    2454.8104  VDWAALS    =    -759.2924
 EELEC  =   -3280.1340  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.7652  VIRIAL  =      95.0502  VOLUME     =   17165.0709
                                                Density    =       0.8829
 Ewald error estimate:   0.1588E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 101000 TIME(PS) =   101.000  TEMP(K) =   374.08  PRESS =   -19.0
 Etot   =     962.5739  EKtot   =    1346.2382  EPtot      =    -383.6643
 BOND   =     186.1272  ANGLE   =     698.3245  DIHED      =     134.0586
 1-4 NB =     153.3301  1-4 EEL =    2459.3219  VDWAALS    =    -751.5613
 EELEC  =   -3263.2653  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.9938  VIRIAL  =     153.1261  VOLUME     =   17427.2484
                                                Density    =       0.8696
 Ewald error estimate:   0.3910E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 102000 TIME(PS) =   102.000  TEMP(K) =   368.20  PRESS =  -208.5
 Etot   =     961.8780  EKtot   =    1325.0902  EPtot      =    -363.2122
 BOND   =     203.1637  ANGLE   =     688.7896  DIHED      =     130.3640
 1-4 NB =     154.0550  1-4 EEL =    2474.1727  VDWAALS    =    -769.9138
 EELEC  =   -3243.8434  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.9199  VIRIAL  =     214.9147  VOLUME     =   17102.2704
                                                Density    =       0.8861
 Ewald error estimate:   0.5963E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 103000 TIME(PS) =   103.000  TEMP(K) =   374.12  PRESS =    36.6
 Etot   =     961.8121  EKtot   =    1346.3746  EPtot      =    -384.5625
 BOND   =     198.3308  ANGLE   =     673.1394  DIHED      =     140.4593
 1-4 NB =     161.4342  1-4 EEL =    2466.1506  VDWAALS    =    -747.6959
 EELEC  =   -3276.3809  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     156.9359  VIRIAL  =     143.2850  VOLUME     =   17285.7257
                                                Density    =       0.8767
 Ewald error estimate:   0.7536E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 104000 TIME(PS) =   104.000  TEMP(K) =   367.67  PRESS =  -413.7
 Etot   =     969.9642  EKtot   =    1323.1799  EPtot      =    -353.2157
 BOND   =     186.1858  ANGLE   =     690.1728  DIHED      =     140.1857
 1-4 NB =     161.3806  1-4 EEL =    2470.1210  VDWAALS    =    -758.0118
 EELEC  =   -3243.2499  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.9464  VIRIAL  =     287.7306  VOLUME     =   17551.7715
                                                Density    =       0.8634
 Ewald error estimate:   0.4988E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 105000 TIME(PS) =   105.000  TEMP(K) =   367.48  PRESS =  -200.2
 Etot   =     969.8917  EKtot   =    1322.4783  EPtot      =    -352.5866
 BOND   =     200.5968  ANGLE   =     709.2333  DIHED      =     136.3605
 1-4 NB =     157.6937  1-4 EEL =    2450.2345  VDWAALS    =    -737.4421
 EELEC  =   -3269.2634  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     120.4626  VIRIAL  =     196.7000  VOLUME     =   17634.8715
                                                Density    =       0.8593
 Ewald error estimate:   0.1262E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 106000 TIME(PS) =   106.000  TEMP(K) =   378.55  PRESS =  -292.6
 Etot   =     975.7801  EKtot   =    1362.3190  EPtot      =    -386.5388
 BOND   =     180.1090  ANGLE   =     691.6939  DIHED      =     132.0664
 1-4 NB =     162.3341  1-4 EEL =    2472.3323  VDWAALS    =    -765.0099
 EELEC  =   -3260.0646  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.2115  VIRIAL  =     251.8222  VOLUME     =   17350.3608
                                                Density    =       0.8734
 Ewald error estimate:   0.1339E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 107000 TIME(PS) =   107.000  TEMP(K) =   371.60  PRESS =  -545.9
 Etot   =     981.8013  EKtot   =    1337.3297  EPtot      =    -355.5284
 BOND   =     182.3580  ANGLE   =     677.2290  DIHED      =     156.0160
 1-4 NB =     160.0167  1-4 EEL =    2478.7715  VDWAALS    =    -731.2326
 EELEC  =   -3278.6869  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     150.2405  VIRIAL  =     360.2787  VOLUME     =   17820.9297
                                                Density    =       0.8504
 Ewald error estimate:   0.2550E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 108000 TIME(PS) =   108.000  TEMP(K) =   375.96  PRESS =  -564.8
 Etot   =     984.4899  EKtot   =    1353.0065  EPtot      =    -368.5166
 BOND   =     197.9898  ANGLE   =     692.0061  DIHED      =     135.1192
 1-4 NB =     164.2839  1-4 EEL =    2461.1082  VDWAALS    =    -753.9657
 EELEC  =   -3265.0580  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     158.3662  VIRIAL  =     372.0814  VOLUME     =   17525.3976
                                                Density    =       0.8647
 Ewald error estimate:   0.1411E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 109000 TIME(PS) =   109.000  TEMP(K) =   361.35  PRESS =   390.4
 Etot   =     977.3681  EKtot   =    1300.4208  EPtot      =    -323.0527
 BOND   =     199.2187  ANGLE   =     696.3957  DIHED      =     140.4698
 1-4 NB =     159.5306  1-4 EEL =    2482.4312  VDWAALS    =    -739.5552
 EELEC  =   -3261.5435  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.2624  VIRIAL  =     -14.5854  VOLUME     =   17304.5634
                                                Density    =       0.8757
 Ewald error estimate:   0.2110E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 110000 TIME(PS) =   110.000  TEMP(K) =   382.99  PRESS =   -26.1
 Etot   =     970.6807  EKtot   =    1378.2920  EPtot      =    -407.6113
 BOND   =     189.1562  ANGLE   =     661.5361  DIHED      =     140.6323
 1-4 NB =     165.6624  1-4 EEL =    2473.9461  VDWAALS    =    -753.1507
 EELEC  =   -3285.3936  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.4362  VIRIAL  =     156.1570  VOLUME     =   17250.9499
                                                Density    =       0.8785
 Ewald error estimate:   0.3352E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 111000 TIME(PS) =   111.000  TEMP(K) =   378.56  PRESS =  -346.6
 Etot   =     968.4209  EKtot   =    1362.3633  EPtot      =    -393.9423
 BOND   =     187.5815  ANGLE   =     665.2992  DIHED      =     131.0141
 1-4 NB =     162.6193  1-4 EEL =    2479.7930  VDWAALS    =    -747.3288
 EELEC  =   -3272.9205  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.2492  VIRIAL  =     271.6293  VOLUME     =   17420.8568
                                                Density    =       0.8699
 Ewald error estimate:   0.1369E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 112000 TIME(PS) =   112.000  TEMP(K) =   376.38  PRESS =    67.6
 Etot   =     961.8275  EKtot   =    1354.5265  EPtot      =    -392.6990
 BOND   =     186.9608  ANGLE   =     668.7853  DIHED      =     144.5037
 1-4 NB =     170.8235  1-4 EEL =    2479.2198  VDWAALS    =    -762.4459
 EELEC  =   -3280.5462  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.3174  VIRIAL  =     112.2479  VOLUME     =   17177.7457
                                                Density    =       0.8822
 Ewald error estimate:   0.9555E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 113000 TIME(PS) =   113.000  TEMP(K) =   378.94  PRESS =   155.6
 Etot   =     950.7528  EKtot   =    1363.7268  EPtot      =    -412.9740
 BOND   =     173.2411  ANGLE   =     681.4291  DIHED      =     140.3363
 1-4 NB =     164.9543  1-4 EEL =    2481.6880  VDWAALS    =    -772.0941
 EELEC  =   -3282.5286  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.2267  VIRIAL  =      71.2014  VOLUME     =   16976.3067
                                                Density    =       0.8927
 Ewald error estimate:   0.1730E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 114000 TIME(PS) =   114.000  TEMP(K) =   375.77  PRESS =    79.4
 Etot   =     950.3454  EKtot   =    1352.3229  EPtot      =    -401.9775
 BOND   =     203.0200  ANGLE   =     682.3939  DIHED      =     129.5446
 1-4 NB =     166.1805  1-4 EEL =    2473.2764  VDWAALS    =    -738.7156
 EELEC  =   -3317.6774  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     111.5592  VIRIAL  =      81.6815  VOLUME     =   17433.5381
                                                Density    =       0.8693
 Ewald error estimate:   0.1103E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 115000 TIME(PS) =   115.000  TEMP(K) =   376.41  PRESS =  -261.2
 Etot   =     952.0331  EKtot   =    1354.6251  EPtot      =    -402.5920
 BOND   =     204.5255  ANGLE   =     676.9217  DIHED      =     137.4434
 1-4 NB =     158.4653  1-4 EEL =    2463.8907  VDWAALS    =    -760.7253
 EELEC  =   -3283.1134  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.8998  VIRIAL  =     231.9696  VOLUME     =   17214.0393
                                                Density    =       0.8803
 Ewald error estimate:   0.3394E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 116000 TIME(PS) =   116.000  TEMP(K) =   366.02  PRESS =    54.3
 Etot   =     955.4810  EKtot   =    1317.2449  EPtot      =    -361.7639
 BOND   =     208.9685  ANGLE   =     664.6412  DIHED      =     148.8450
 1-4 NB =     160.7192  1-4 EEL =    2483.9995  VDWAALS    =    -739.9159
 EELEC  =   -3289.0214  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.1784  VIRIAL  =     118.8591  VOLUME     =   17345.4983
                                                Density    =       0.8737
 Ewald error estimate:   0.1581E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 117000 TIME(PS) =   117.000  TEMP(K) =   382.01  PRESS =  -301.7
 Etot   =     952.3124  EKtot   =    1374.7672  EPtot      =    -422.4548
 BOND   =     193.1114  ANGLE   =     676.4073  DIHED      =     125.8056
 1-4 NB =     154.6539  1-4 EEL =    2469.7117  VDWAALS    =    -782.5029
 EELEC  =   -3259.6417  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.1298  VIRIAL  =     237.7741  VOLUME     =   17137.4490
                                                Density    =       0.8843
 Ewald error estimate:   0.1357E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 118000 TIME(PS) =   118.000  TEMP(K) =   362.75  PRESS =   203.2
 Etot   =     961.3248  EKtot   =    1305.4784  EPtot      =    -344.1535
 BOND   =     203.5223  ANGLE   =     716.2097  DIHED      =     134.2543
 1-4 NB =     162.2725  1-4 EEL =    2464.1011  VDWAALS    =    -746.1848
 EELEC  =   -3278.3286  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.8403  VIRIAL  =      49.4928  VOLUME     =   17404.5189
                                                Density    =       0.8707
 Ewald error estimate:   0.1887E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 119000 TIME(PS) =   119.000  TEMP(K) =   381.57  PRESS =  -214.5
 Etot   =     962.6676  EKtot   =    1373.1902  EPtot      =    -410.5225
 BOND   =     204.0564  ANGLE   =     661.6765  DIHED      =     135.0921
 1-4 NB =     161.5851  1-4 EEL =    2476.3761  VDWAALS    =    -761.7377
 EELEC  =   -3287.5710  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.7438  VIRIAL  =     206.1985  VOLUME     =   17155.1119
                                                Density    =       0.8834
 Ewald error estimate:   0.1138E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 120000 TIME(PS) =   120.000  TEMP(K) =   379.75  PRESS =  -412.7
 Etot   =     962.7411  EKtot   =    1366.6330  EPtot      =    -403.8919
 BOND   =     218.4372  ANGLE   =     677.1661  DIHED      =     129.1712
 1-4 NB =     156.6295  1-4 EEL =    2466.8490  VDWAALS    =    -767.1364
 EELEC  =   -3285.0086  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.9996  VIRIAL  =     281.8134  VOLUME     =   17150.8965
                                                Density    =       0.8836
 Ewald error estimate:   0.1139E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 121000 TIME(PS) =   121.000  TEMP(K) =   373.82  PRESS =  -661.4
 Etot   =     959.4698  EKtot   =    1345.2890  EPtot      =    -385.8191
 BOND   =     192.9922  ANGLE   =     707.0634  DIHED      =     135.3759
 1-4 NB =     164.7126  1-4 EEL =    2483.5761  VDWAALS    =    -769.3006
 EELEC  =   -3300.2386  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.2714  VIRIAL  =     378.4495  VOLUME     =   17167.8141
                                                Density    =       0.8827
 Ewald error estimate:   0.1777E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 122000 TIME(PS) =   122.000  TEMP(K) =   369.20  PRESS =   -61.8
 Etot   =     957.8054  EKtot   =    1328.6934  EPtot      =    -370.8880
 BOND   =     185.3227  ANGLE   =     712.4770  DIHED      =     147.8684
 1-4 NB =     157.0872  1-4 EEL =    2454.4696  VDWAALS    =    -769.6833
 EELEC  =   -3258.4296  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     119.8975  VIRIAL  =     142.6918  VOLUME     =   17090.5293
                                                Density    =       0.8867
 Ewald error estimate:   0.1278E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 123000 TIME(PS) =   123.000  TEMP(K) =   370.31  PRESS =   112.7
 Etot   =     959.3415  EKtot   =    1332.6813  EPtot      =    -373.3399
 BOND   =     205.8802  ANGLE   =     677.2235  DIHED      =     131.8473
 1-4 NB =     155.9805  1-4 EEL =    2467.1327  VDWAALS    =    -762.1580
 EELEC  =   -3249.2461  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.4388  VIRIAL  =      97.5872  VOLUME     =   17199.0810
                                                Density    =       0.8811
 Ewald error estimate:   0.1775E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 124000 TIME(PS) =   124.000  TEMP(K) =   368.50  PRESS =  -402.5
 Etot   =     960.8174  EKtot   =    1326.1553  EPtot      =    -365.3379
 BOND   =     198.7932  ANGLE   =     718.5131  DIHED      =     149.9396
 1-4 NB =     153.0254  1-4 EEL =    2459.2857  VDWAALS    =    -781.7849
 EELEC  =   -3263.1099  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.5937  VIRIAL  =     297.6581  VOLUME     =   17037.0920
                                                Density    =       0.8895
 Ewald error estimate:   0.1804E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 125000 TIME(PS) =   125.000  TEMP(K) =   368.30  PRESS =   135.0
 Etot   =     954.2220  EKtot   =    1325.4385  EPtot      =    -371.2164
 BOND   =     186.1829  ANGLE   =     687.3849  DIHED      =     145.3873
 1-4 NB =     157.7498  1-4 EEL =    2475.7055  VDWAALS    =    -755.6952
 EELEC  =   -3267.9316  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.5469  VIRIAL  =      95.4464  VOLUME     =   17183.0957
                                                Density    =       0.8819
 Ewald error estimate:   0.3395E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 126000 TIME(PS) =   126.000  TEMP(K) =   378.16  PRESS =  -261.1
 Etot   =     954.5208  EKtot   =    1360.9252  EPtot      =    -406.4044
 BOND   =     211.0260  ANGLE   =     643.2316  DIHED      =     132.4304
 1-4 NB =     161.3573  1-4 EEL =    2479.2047  VDWAALS    =    -764.5543
 EELEC  =   -3269.1001  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.9623  VIRIAL  =     232.3371  VOLUME     =   17273.6070
                                                Density    =       0.8773
 Ewald error estimate:   0.2308E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 127000 TIME(PS) =   127.000  TEMP(K) =   363.02  PRESS =   -94.7
 Etot   =     958.5490  EKtot   =    1306.4417  EPtot      =    -347.8927
 BOND   =     198.9875  ANGLE   =     672.2018  DIHED      =     140.3057
 1-4 NB =     168.2054  1-4 EEL =    2483.0009  VDWAALS    =    -751.4544
 EELEC  =   -3259.1395  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.6461  VIRIAL  =     182.9644  VOLUME     =   17278.3361
                                                Density    =       0.8771
 Ewald error estimate:   0.1914E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 128000 TIME(PS) =   128.000  TEMP(K) =   374.07  PRESS =  -373.7
 Etot   =     966.3023  EKtot   =    1346.1967  EPtot      =    -379.8944
 BOND   =     179.2610  ANGLE   =     684.2387  DIHED      =     147.4129
 1-4 NB =     168.2440  1-4 EEL =    2475.8558  VDWAALS    =    -764.6919
 EELEC  =   -3270.2150  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.1766  VIRIAL  =     264.9414  VOLUME     =   17322.1529
                                                Density    =       0.8749
 Ewald error estimate:   0.2378E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 129000 TIME(PS) =   129.000  TEMP(K) =   373.67  PRESS =   459.0
 Etot   =     963.9432  EKtot   =    1344.7671  EPtot      =    -380.8240
 BOND   =     196.1295  ANGLE   =     656.9952  DIHED      =     153.3579
 1-4 NB =     163.8100  1-4 EEL =    2477.6163  VDWAALS    =    -736.3717
 EELEC  =   -3292.3612  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.3002  VIRIAL  =     -33.5563  VOLUME     =   17238.6776
                                                Density    =       0.8791
 Ewald error estimate:   0.2033E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 130000 TIME(PS) =   130.000  TEMP(K) =   364.23  PRESS =  -232.4
 Etot   =     971.1443  EKtot   =    1310.7987  EPtot      =    -339.6544
 BOND   =     223.1887  ANGLE   =     683.5512  DIHED      =     155.2847
 1-4 NB =     166.2449  1-4 EEL =    2485.1678  VDWAALS    =    -748.7259
 EELEC  =   -3304.3657  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.8434  VIRIAL  =     231.0120  VOLUME     =   17373.8751
                                                Density    =       0.8722
 Ewald error estimate:   0.6939E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 131000 TIME(PS) =   131.000  TEMP(K) =   374.56  PRESS =  -165.4
 Etot   =     967.3866  EKtot   =    1347.9647  EPtot      =    -380.5781
 BOND   =     191.9337  ANGLE   =     684.6643  DIHED      =     160.3291
 1-4 NB =     155.6632  1-4 EEL =    2465.9022  VDWAALS    =    -770.6168
 EELEC  =   -3268.4537  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.1778  VIRIAL  =     207.2720  VOLUME     =   17105.0695
                                                Density    =       0.8860
 Ewald error estimate:   0.7452E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 132000 TIME(PS) =   132.000  TEMP(K) =   370.86  PRESS =   567.7
 Etot   =     968.5730  EKtot   =    1334.6374  EPtot      =    -366.0644
 BOND   =     213.5473  ANGLE   =     693.3542  DIHED      =     137.8540
 1-4 NB =     159.9182  1-4 EEL =    2462.8883  VDWAALS    =    -758.3144
 EELEC  =   -3275.3119  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.7337  VIRIAL  =     -61.3463  VOLUME     =   17140.4798
                                                Density    =       0.8841
 Ewald error estimate:   0.3619E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 133000 TIME(PS) =   133.000  TEMP(K) =   372.00  PRESS =    94.2
 Etot   =     964.3151  EKtot   =    1338.7508  EPtot      =    -374.4357
 BOND   =     191.0553  ANGLE   =     705.6070  DIHED      =     123.6266
 1-4 NB =     164.8562  1-4 EEL =    2471.9206  VDWAALS    =    -744.2007
 EELEC  =   -3287.3006  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     122.1225  VIRIAL  =      86.9306  VOLUME     =   17297.4112
                                                Density    =       0.8761
 Ewald error estimate:   0.4350E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 134000 TIME(PS) =   134.000  TEMP(K) =   364.37  PRESS =     9.1
 Etot   =     961.5247  EKtot   =    1311.3133  EPtot      =    -349.7886
 BOND   =     187.6420  ANGLE   =     707.3255  DIHED      =     153.3378
 1-4 NB =     158.1951  1-4 EEL =    2462.4966  VDWAALS    =    -764.9618
 EELEC  =   -3253.8238  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.7666  VIRIAL  =     125.4029  VOLUME     =   17128.2331
                                                Density    =       0.8848
 Ewald error estimate:   0.1769E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 135000 TIME(PS) =   135.000  TEMP(K) =   372.21  PRESS =  -436.4
 Etot   =     964.3009  EKtot   =    1339.4963  EPtot      =    -375.1954
 BOND   =     181.4549  ANGLE   =     690.5896  DIHED      =     145.2746
 1-4 NB =     160.7409  1-4 EEL =    2479.7299  VDWAALS    =    -757.4654
 EELEC  =   -3275.5200  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.8938  VIRIAL  =     294.1901  VOLUME     =   17329.5462
                                                Density    =       0.8745
 Ewald error estimate:   0.4915E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 136000 TIME(PS) =   136.000  TEMP(K) =   370.98  PRESS =  -152.4
 Etot   =     957.2789  EKtot   =    1335.0999  EPtot      =    -377.8210
 BOND   =     180.6187  ANGLE   =     697.0656  DIHED      =     150.2205
 1-4 NB =     160.8028  1-4 EEL =    2467.3126  VDWAALS    =    -773.1720
 EELEC  =   -3260.6692  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.0479  VIRIAL  =     194.2568  VOLUME     =   17085.4249
                                                Density    =       0.8870
 Ewald error estimate:   0.1322E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 137000 TIME(PS) =   137.000  TEMP(K) =   361.27  PRESS =   -75.2
 Etot   =     962.5728  EKtot   =    1300.1405  EPtot      =    -337.5677
 BOND   =     207.1318  ANGLE   =     670.3757  DIHED      =     160.1731
 1-4 NB =     170.9313  1-4 EEL =    2480.1424  VDWAALS    =    -733.0650
 EELEC  =   -3293.2570  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.6771  VIRIAL  =     153.1196  VOLUME     =   17523.3374
                                                Density    =       0.8648
 Ewald error estimate:   0.1235E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 138000 TIME(PS) =   138.000  TEMP(K) =   375.58  PRESS =   191.7
 Etot   =     954.8777  EKtot   =    1351.6411  EPtot      =    -396.7634
 BOND   =     185.9753  ANGLE   =     666.8980  DIHED      =     144.3097
 1-4 NB =     162.7949  1-4 EEL =    2458.2120  VDWAALS    =    -746.1720
 EELEC  =   -3268.7813  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.4596  VIRIAL  =      54.2847  VOLUME     =   17195.7782
                                                Density    =       0.8813
 Ewald error estimate:   0.1876E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 139000 TIME(PS) =   139.000  TEMP(K) =   368.83  PRESS =  -310.5
 Etot   =     956.4140  EKtot   =    1327.3386  EPtot      =    -370.9246
 BOND   =     190.3427  ANGLE   =     682.0225  DIHED      =     129.5122
 1-4 NB =     173.2079  1-4 EEL =    2495.3690  VDWAALS    =    -737.4303
 EELEC  =   -3303.9486  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.3680  VIRIAL  =     248.8271  VOLUME     =   17519.7307
                                                Density    =       0.8650
 Ewald error estimate:   0.8272E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 140000 TIME(PS) =   140.000  TEMP(K) =   368.19  PRESS =  -163.9
 Etot   =     964.6540  EKtot   =    1325.0600  EPtot      =    -360.4059
 BOND   =     185.8521  ANGLE   =     687.5933  DIHED      =     142.2973
 1-4 NB =     167.9817  1-4 EEL =    2462.2865  VDWAALS    =    -754.8099
 EELEC  =   -3251.6069  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.0957  VIRIAL  =     199.4387  VOLUME     =   17334.4591
                                                Density    =       0.8742
 Ewald error estimate:   0.2605E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 141000 TIME(PS) =   141.000  TEMP(K) =   377.82  PRESS =  -131.4
 Etot   =     962.2409  EKtot   =    1359.7072  EPtot      =    -397.4663
 BOND   =     190.3771  ANGLE   =     674.7294  DIHED      =     132.6465
 1-4 NB =     162.2288  1-4 EEL =    2477.1025  VDWAALS    =    -760.9119
 EELEC  =   -3273.6387  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.0277  VIRIAL  =     185.6937  VOLUME     =   17151.9768
                                                Density    =       0.8835
 Ewald error estimate:   0.9804E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 142000 TIME(PS) =   142.000  TEMP(K) =   378.17  PRESS =  -348.9
 Etot   =     957.9418  EKtot   =    1360.9457  EPtot      =    -403.0039
 BOND   =     190.7877  ANGLE   =     662.0636  DIHED      =     140.7931
 1-4 NB =     159.1134  1-4 EEL =    2472.7084  VDWAALS    =    -753.7748
 EELEC  =   -3274.6953  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.1298  VIRIAL  =     255.8290  VOLUME     =   17480.0533
                                                Density    =       0.8670
 Ewald error estimate:   0.3059E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 143000 TIME(PS) =   143.000  TEMP(K) =   367.50  PRESS =   256.1
 Etot   =     965.8361  EKtot   =    1322.5482  EPtot      =    -356.7120
 BOND   =     196.7318  ANGLE   =     707.9959  DIHED      =     135.6267
 1-4 NB =     160.7284  1-4 EEL =    2464.6075  VDWAALS    =    -724.7744
 EELEC  =   -3297.6278  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.0543  VIRIAL  =      47.2770  VOLUME     =   17503.2298
                                                Density    =       0.8658
 Ewald error estimate:   0.2491E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 144000 TIME(PS) =   144.000  TEMP(K) =   362.05  PRESS =   547.0
 Etot   =     967.5350  EKtot   =    1302.9446  EPtot      =    -335.4096
 BOND   =     204.7209  ANGLE   =     662.9941  DIHED      =     138.5074
 1-4 NB =     162.6323  1-4 EEL =    2467.0824  VDWAALS    =    -705.1821
 EELEC  =   -3266.1646  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.5385  VIRIAL  =     -83.3072  VOLUME     =   17853.3254
                                                Density    =       0.8488
 Ewald error estimate:   0.9259E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 145000 TIME(PS) =   145.000  TEMP(K) =   366.97  PRESS =   236.9
 Etot   =     969.5280  EKtot   =    1320.6552  EPtot      =    -351.1271
 BOND   =     204.3782  ANGLE   =     671.3269  DIHED      =     153.1388
 1-4 NB =     157.9424  1-4 EEL =    2461.0990  VDWAALS    =    -696.5230
 EELEC  =   -3302.4895  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.4674  VIRIAL  =      42.9369  VOLUME     =   17893.8335
                                                Density    =       0.8469
 Ewald error estimate:   0.1840E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 146000 TIME(PS) =   146.000  TEMP(K) =   378.22  PRESS =  -646.9
 Etot   =     975.0283  EKtot   =    1361.1252  EPtot      =    -386.0968
 BOND   =     190.2331  ANGLE   =     642.7280  DIHED      =     148.9378
 1-4 NB =     161.9433  1-4 EEL =    2487.1919  VDWAALS    =    -740.1082
 EELEC  =   -3277.0226  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     152.2456  VIRIAL  =     400.5210  VOLUME     =   17776.3628
                                                Density    =       0.8525
 Ewald error estimate:   0.2568E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 147000 TIME(PS) =   147.000  TEMP(K) =   376.82  PRESS =   144.4
 Etot   =     960.7288  EKtot   =    1356.1008  EPtot      =    -395.3720
 BOND   =     193.8685  ANGLE   =     670.3091  DIHED      =     153.6291
 1-4 NB =     158.8756  1-4 EEL =    2452.5886  VDWAALS    =    -737.8693
 EELEC  =   -3286.7736  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     171.4258  VIRIAL  =     117.0299  VOLUME     =   17448.6925
                                                Density    =       0.8685
 Ewald error estimate:   0.6377E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 148000 TIME(PS) =   148.000  TEMP(K) =   368.10  PRESS =   330.6
 Etot   =     961.0631  EKtot   =    1324.7156  EPtot      =    -363.6526
 BOND   =     182.4514  ANGLE   =     673.7766  DIHED      =     137.7093
 1-4 NB =     165.8231  1-4 EEL =    2493.8634  VDWAALS    =    -740.0011
 EELEC  =   -3277.2753  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.5440  VIRIAL  =       7.0396  VOLUME     =   17299.8148
                                                Density    =       0.8760
 Ewald error estimate:   0.3174E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 149000 TIME(PS) =   149.000  TEMP(K) =   364.40  PRESS =  -161.8
 Etot   =     970.3431  EKtot   =    1311.4126  EPtot      =    -341.0695
 BOND   =     214.7594  ANGLE   =     705.3089  DIHED      =     126.1397
 1-4 NB =     166.0898  1-4 EEL =    2480.0945  VDWAALS    =    -752.2242
 EELEC  =   -3281.2377  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.5400  VIRIAL  =     209.2645  VOLUME     =   17379.8704
                                                Density    =       0.8719
 Ewald error estimate:   0.1595E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 150000 TIME(PS) =   150.000  TEMP(K) =   364.64  PRESS =   213.4
 Etot   =     966.9101  EKtot   =    1312.2695  EPtot      =    -345.3594
 BOND   =     188.1718  ANGLE   =     687.1201  DIHED      =     141.1983
 1-4 NB =     171.6035  1-4 EEL =    2481.6774  VDWAALS    =    -729.0417
 EELEC  =   -3286.0887  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.0638  VIRIAL  =      51.8796  VOLUME     =   17618.9623
                                                Density    =       0.8601
 Ewald error estimate:   0.9950E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 151000 TIME(PS) =   151.000  TEMP(K) =   363.00  PRESS =  -217.3
 Etot   =     973.8393  EKtot   =    1306.3511  EPtot      =    -332.5118
 BOND   =     197.1771  ANGLE   =     705.4132  DIHED      =     140.9303
 1-4 NB =     156.2460  1-4 EEL =    2468.1665  VDWAALS    =    -714.9768
 EELEC  =   -3285.4681  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.4144  VIRIAL  =     217.0701  VOLUME     =   17832.2569
                                                Density    =       0.8498
 Ewald error estimate:   0.6866E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 152000 TIME(PS) =   152.000  TEMP(K) =   372.34  PRESS =  -458.0
 Etot   =     977.3967  EKtot   =    1339.9660  EPtot      =    -362.5693
 BOND   =     190.9137  ANGLE   =     687.3142  DIHED      =     144.7452
 1-4 NB =     159.1280  1-4 EEL =    2454.5291  VDWAALS    =    -747.5083
 EELEC  =   -3251.6912  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.7312  VIRIAL  =     319.5645  VOLUME     =   17577.9651
                                                Density    =       0.8621
 Ewald error estimate:   0.4994E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 153000 TIME(PS) =   153.000  TEMP(K) =   370.91  PRESS =  -691.7
 Etot   =     975.3528  EKtot   =    1334.8228  EPtot      =    -359.4701
 BOND   =     195.8440  ANGLE   =     680.1866  DIHED      =     152.2844
 1-4 NB =     165.6090  1-4 EEL =    2472.5594  VDWAALS    =    -762.2832
 EELEC  =   -3263.6703  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     122.2991  VIRIAL  =     383.0566  VOLUME     =   17460.8483
                                                Density    =       0.8679
 Ewald error estimate:   0.2395E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 154000 TIME(PS) =   154.000  TEMP(K) =   357.89  PRESS =   -58.5
 Etot   =     968.4373  EKtot   =    1287.9724  EPtot      =    -319.5351
 BOND   =     225.6573  ANGLE   =     695.9493  DIHED      =     150.4104
 1-4 NB =     157.1997  1-4 EEL =    2461.4926  VDWAALS    =    -759.8060
 EELEC  =   -3250.4385  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.4788  VIRIAL  =     156.2386  VOLUME     =   17231.5353
                                                Density    =       0.8795
 Ewald error estimate:   0.1502E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 155000 TIME(PS) =   155.000  TEMP(K) =   368.14  PRESS =   231.6
 Etot   =     965.9334  EKtot   =    1324.8721  EPtot      =    -358.9387
 BOND   =     179.9040  ANGLE   =     679.9195  DIHED      =     145.3155
 1-4 NB =     157.0787  1-4 EEL =    2470.9568  VDWAALS    =    -740.1538
 EELEC  =   -3251.9595  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.5409  VIRIAL  =      46.6396  VOLUME     =   17376.7575
                                                Density    =       0.8721
 Ewald error estimate:   0.3447E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 156000 TIME(PS) =   156.000  TEMP(K) =   380.52  PRESS =  -332.0
 Etot   =     968.2654  EKtot   =    1369.4326  EPtot      =    -401.1672
 BOND   =     175.8755  ANGLE   =     696.8715  DIHED      =     153.2606
 1-4 NB =     165.2880  1-4 EEL =    2459.7173  VDWAALS    =    -757.5827
 EELEC  =   -3294.5974  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     160.1801  VIRIAL  =     283.8473  VOLUME     =   17251.8119
                                                Density    =       0.8784
 Ewald error estimate:   0.1514E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 157000 TIME(PS) =   157.000  TEMP(K) =   370.86  PRESS =   402.8
 Etot   =     968.2057  EKtot   =    1334.6533  EPtot      =    -366.4477
 BOND   =     193.9307  ANGLE   =     665.5124  DIHED      =     145.3356
 1-4 NB =     158.2990  1-4 EEL =    2463.0755  VDWAALS    =    -724.9276
 EELEC  =   -3267.6733  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.6003  VIRIAL  =     -26.7522  VOLUME     =   17518.1083
                                                Density    =       0.8651
 Ewald error estimate:   0.1403E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 158000 TIME(PS) =   158.000  TEMP(K) =   373.96  PRESS =   251.4
 Etot   =     972.6979  EKtot   =    1345.8141  EPtot      =    -373.1162
 BOND   =     178.0929  ANGLE   =     672.5816  DIHED      =     135.3113
 1-4 NB =     160.1213  1-4 EEL =    2475.0634  VDWAALS    =    -724.5535
 EELEC  =   -3269.7333  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.2085  VIRIAL  =      40.8060  VOLUME     =   17763.0568
                                                Density    =       0.8531
 Ewald error estimate:   0.1995E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 159000 TIME(PS) =   159.000  TEMP(K) =   379.78  PRESS =   -60.2
 Etot   =     967.9176  EKtot   =    1366.7449  EPtot      =    -398.8274
 BOND   =     192.7518  ANGLE   =     672.3236  DIHED      =     134.4086
 1-4 NB =     159.2701  1-4 EEL =    2456.4696  VDWAALS    =    -741.5945
 EELEC  =   -3272.4566  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.8879  VIRIAL  =     171.6965  VOLUME     =   17552.0308
                                                Density    =       0.8634
 Ewald error estimate:   0.2315E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 160000 TIME(PS) =   160.000  TEMP(K) =   370.84  PRESS =   -51.6
 Etot   =     971.2685  EKtot   =    1334.5720  EPtot      =    -363.3035
 BOND   =     203.8547  ANGLE   =     680.8837  DIHED      =     143.1444
 1-4 NB =     161.8751  1-4 EEL =    2473.1265  VDWAALS    =    -755.1790
 EELEC  =   -3271.0089  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.6334  VIRIAL  =     161.9058  VOLUME     =   17286.7614
                                                Density    =       0.8766
 Ewald error estimate:   0.1069E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 161000 TIME(PS) =   161.000  TEMP(K) =   374.61  PRESS =   -41.4
 Etot   =     966.4445  EKtot   =    1348.1553  EPtot      =    -381.7108
 BOND   =     179.6077  ANGLE   =     673.9867  DIHED      =     139.1391
 1-4 NB =     166.1326  1-4 EEL =    2488.9166  VDWAALS    =    -730.5777
 EELEC  =   -3298.9158  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.3869  VIRIAL  =     148.0127  VOLUME     =   17480.8365
                                                Density    =       0.8669
 Ewald error estimate:   0.2489E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 162000 TIME(PS) =   162.000  TEMP(K) =   375.34  PRESS =   266.1
 Etot   =     966.0443  EKtot   =    1350.7616  EPtot      =    -384.7173
 BOND   =     179.3176  ANGLE   =     673.5829  DIHED      =     137.5532
 1-4 NB =     164.4440  1-4 EEL =    2473.8236  VDWAALS    =    -744.8948
 EELEC  =   -3268.5438  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.8624  VIRIAL  =      35.0494  VOLUME     =   17372.6067
                                                Density    =       0.8723
 Ewald error estimate:   0.3514E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 163000 TIME(PS) =   163.000  TEMP(K) =   368.78  PRESS =   -20.8
 Etot   =     970.9801  EKtot   =    1327.1573  EPtot      =    -356.1773
 BOND   =     182.1813  ANGLE   =     690.4633  DIHED      =     146.6643
 1-4 NB =     174.6327  1-4 EEL =    2485.3745  VDWAALS    =    -751.1590
 EELEC  =   -3284.3343  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.7472  VIRIAL  =     138.5320  VOLUME     =   17356.8054
                                                Density    =       0.8731
 Ewald error estimate:   0.1753E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 164000 TIME(PS) =   164.000  TEMP(K) =   372.64  PRESS =   195.7
 Etot   =     971.5843  EKtot   =    1341.0490  EPtot      =    -369.4647
 BOND   =     204.2593  ANGLE   =     670.8806  DIHED      =     147.2160
 1-4 NB =     159.9188  1-4 EEL =    2462.1241  VDWAALS    =    -741.6921
 EELEC  =   -3272.1713  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.4116  VIRIAL  =      54.1736  VOLUME     =   17329.5427
                                                Density    =       0.8745
 Ewald error estimate:   0.2277E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 165000 TIME(PS) =   165.000  TEMP(K) =   377.52  PRESS =  -371.6
 Etot   =     976.5551  EKtot   =    1358.6318  EPtot      =    -382.0767
 BOND   =     195.9670  ANGLE   =     647.3464  DIHED      =     147.6960
 1-4 NB =     165.3124  1-4 EEL =    2477.2010  VDWAALS    =    -753.5498
 EELEC  =   -3262.0497  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.8175  VIRIAL  =     285.3558  VOLUME     =   17518.2320
                                                Density    =       0.8651
 Ewald error estimate:   0.1393E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 166000 TIME(PS) =   166.000  TEMP(K) =   366.54  PRESS =   740.5
 Etot   =     981.3464  EKtot   =    1319.1043  EPtot      =    -337.7580
 BOND   =     224.3993  ANGLE   =     651.8183  DIHED      =     141.4109
 1-4 NB =     157.6857  1-4 EEL =    2460.7650  VDWAALS    =    -717.9116
 EELEC  =   -3255.9257  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.4412  VIRIAL  =    -153.2215  VOLUME     =   17679.9326
                                                Density    =       0.8571
 Ewald error estimate:   0.1534E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 167000 TIME(PS) =   167.000  TEMP(K) =   377.89  PRESS =  -104.1
 Etot   =     975.0443  EKtot   =    1359.9452  EPtot      =    -384.9009
 BOND   =     196.1636  ANGLE   =     653.5003  DIHED      =     149.2002
 1-4 NB =     172.3050  1-4 EEL =    2471.7934  VDWAALS    =    -758.6706
 EELEC  =   -3269.1928  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.4107  VIRIAL  =     183.2005  VOLUME     =   17250.8365
                                                Density    =       0.8785
 Ewald error estimate:   0.7732E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 168000 TIME(PS) =   168.000  TEMP(K) =   371.29  PRESS =   -35.1
 Etot   =     976.1677  EKtot   =    1336.1829  EPtot      =    -360.0152
 BOND   =     193.0460  ANGLE   =     680.0637  DIHED      =     134.6044
 1-4 NB =     161.4975  1-4 EEL =    2482.7171  VDWAALS    =    -748.0183
 EELEC  =   -3263.9255  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.3559  VIRIAL  =     157.5587  VOLUME     =   17426.1287
                                                Density    =       0.8696
 Ewald error estimate:   0.5088E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 169000 TIME(PS) =   169.000  TEMP(K) =   367.59  PRESS =   429.5
 Etot   =     980.4345  EKtot   =    1322.8706  EPtot      =    -342.4361
 BOND   =     190.8664  ANGLE   =     685.6326  DIHED      =     142.5266
 1-4 NB =     159.7262  1-4 EEL =    2473.8014  VDWAALS    =    -732.9637
 EELEC  =   -3262.0256  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.1950  VIRIAL  =     -29.2553  VOLUME     =   17625.9424
                                                Density    =       0.8598
 Ewald error estimate:   0.5120E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 170000 TIME(PS) =   170.000  TEMP(K) =   363.21  PRESS =  -150.0
 Etot   =     990.8019  EKtot   =    1307.1279  EPtot      =    -316.3260
 BOND   =     203.8642  ANGLE   =     681.6045  DIHED      =     143.9025
 1-4 NB =     156.7970  1-4 EEL =    2470.3909  VDWAALS    =    -743.4810
 EELEC  =   -3229.4039  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.6778  VIRIAL  =     202.9673  VOLUME     =   17689.6582
                                                Density    =       0.8567
 Ewald error estimate:   0.2342E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 171000 TIME(PS) =   171.000  TEMP(K) =   362.54  PRESS =  -512.9
 Etot   =     990.7153  EKtot   =    1304.6930  EPtot      =    -313.9778
 BOND   =     202.3071  ANGLE   =     691.1122  DIHED      =     140.2788
 1-4 NB =     160.7221  1-4 EEL =    2477.0159  VDWAALS    =    -764.9222
 EELEC  =   -3220.4918  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     156.8077  VIRIAL  =     350.7517  VOLUME     =   17512.7889
                                                Density    =       0.8653
 Ewald error estimate:   0.8256E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 172000 TIME(PS) =   172.000  TEMP(K) =   367.18  PRESS =  -202.1
 Etot   =     988.1085  EKtot   =    1321.4068  EPtot      =    -333.2983
 BOND   =     196.1898  ANGLE   =     701.7306  DIHED      =     137.4854
 1-4 NB =     172.5726  1-4 EEL =    2460.0361  VDWAALS    =    -748.6626
 EELEC  =   -3252.6501  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.3623  VIRIAL  =     217.6627  VOLUME     =   17489.6914
                                                Density    =       0.8665
 Ewald error estimate:   0.2598E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 173000 TIME(PS) =   173.000  TEMP(K) =   365.54  PRESS =   281.2
 Etot   =     984.6453  EKtot   =    1315.5212  EPtot      =    -330.8759
 BOND   =     215.2873  ANGLE   =     711.6879  DIHED      =     139.9422
 1-4 NB =     145.1213  1-4 EEL =    2457.8675  VDWAALS    =    -744.3880
 EELEC  =   -3256.3940  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.9927  VIRIAL  =      24.8749  VOLUME     =   17475.9824
                                                Density    =       0.8672
 Ewald error estimate:   0.7615E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 174000 TIME(PS) =   174.000  TEMP(K) =   385.40  PRESS =   208.4
 Etot   =     979.7922  EKtot   =    1386.9961  EPtot      =    -407.2040
 BOND   =     183.7876  ANGLE   =     667.2466  DIHED      =     135.1260
 1-4 NB =     155.6393  1-4 EEL =    2456.9900  VDWAALS    =    -755.7559
 EELEC  =   -3250.2376  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.2669  VIRIAL  =      64.8783  VOLUME     =   17201.7648
                                                Density    =       0.8810
 Ewald error estimate:   0.5298E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 175000 TIME(PS) =   175.000  TEMP(K) =   367.16  PRESS =   -75.6
 Etot   =     987.2840  EKtot   =    1321.3403  EPtot      =    -334.0563
 BOND   =     216.4357  ANGLE   =     684.9262  DIHED      =     144.7781
 1-4 NB =     159.3696  1-4 EEL =    2466.6691  VDWAALS    =    -740.1893
 EELEC  =   -3266.0457  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.5268  VIRIAL  =     155.1102  VOLUME     =   17515.6345
                                                Density    =       0.8652
 Ewald error estimate:   0.1954E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 176000 TIME(PS) =   176.000  TEMP(K) =   379.84  PRESS =   426.3
 Etot   =     977.2934  EKtot   =    1366.9818  EPtot      =    -389.6883
 BOND   =     205.8878  ANGLE   =     647.9447  DIHED      =     141.6139
 1-4 NB =     155.5732  1-4 EEL =    2463.7781  VDWAALS    =    -731.5887
 EELEC  =   -3272.8973  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.0758  VIRIAL  =     -11.6072  VOLUME     =   17458.5621
                                                Density    =       0.8680
 Ewald error estimate:   0.6538E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 177000 TIME(PS) =   177.000  TEMP(K) =   372.21  PRESS =   -23.3
 Etot   =     975.2348  EKtot   =    1339.5055  EPtot      =    -364.2707
 BOND   =     176.2266  ANGLE   =     670.5170  DIHED      =     147.5879
 1-4 NB =     163.6766  1-4 EEL =    2487.0455  VDWAALS    =    -743.2630
 EELEC  =   -3266.0613  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.8730  VIRIAL  =     140.6679  VOLUME     =   17487.7247
                                                Density    =       0.8666
 Ewald error estimate:   0.7737E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 178000 TIME(PS) =   178.000  TEMP(K) =   372.33  PRESS =   180.6
 Etot   =     973.3913  EKtot   =    1339.9253  EPtot      =    -366.5340
 BOND   =     188.6997  ANGLE   =     652.2806  DIHED      =     154.6456
 1-4 NB =     170.2316  1-4 EEL =    2472.1902  VDWAALS    =    -736.1822
 EELEC  =   -3268.3995  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.3672  VIRIAL  =      60.0803  VOLUME     =   17509.6025
                                                Density    =       0.8655
 Ewald error estimate:   0.1778E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 179000 TIME(PS) =   179.000  TEMP(K) =   366.16  PRESS =   -12.7
 Etot   =     977.2954  EKtot   =    1317.7401  EPtot      =    -340.4447
 BOND   =     200.7208  ANGLE   =     704.6849  DIHED      =     151.4809
 1-4 NB =     157.1013  1-4 EEL =    2458.0152  VDWAALS    =    -743.7438
 EELEC  =   -3268.7040  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.2948  VIRIAL  =     134.0576  VOLUME     =   17416.3778
                                                Density    =       0.8701
 Ewald error estimate:   0.1767E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 180000 TIME(PS) =   180.000  TEMP(K) =   371.01  PRESS =  -151.3
 Etot   =     976.9322  EKtot   =    1335.1908  EPtot      =    -358.2586
 BOND   =     216.4713  ANGLE   =     694.3845  DIHED      =     129.9028
 1-4 NB =     158.4528  1-4 EEL =    2473.6204  VDWAALS    =    -747.1777
 EELEC  =   -3283.9128  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.9528  VIRIAL  =     195.1067  VOLUME     =   17492.0701
                                                Density    =       0.8664
 Ewald error estimate:   0.1533E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 181000 TIME(PS) =   181.000  TEMP(K) =   374.34  PRESS =  -157.4
 Etot   =     971.8590  EKtot   =    1347.1875  EPtot      =    -375.3285
 BOND   =     206.6522  ANGLE   =     671.0292  DIHED      =     135.2478
 1-4 NB =     161.6529  1-4 EEL =    2473.8463  VDWAALS    =    -765.0507
 EELEC  =   -3258.7062  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.4313  VIRIAL  =     189.5388  VOLUME     =   17395.5651
                                                Density    =       0.8712
 Ewald error estimate:   0.9579E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 182000 TIME(PS) =   182.000  TEMP(K) =   364.17  PRESS =   179.6
 Etot   =     966.6975  EKtot   =    1310.5728  EPtot      =    -343.8753
 BOND   =     218.3398  ANGLE   =     712.1681  DIHED      =     125.9862
 1-4 NB =     155.7490  1-4 EEL =    2455.8805  VDWAALS    =    -757.8945
 EELEC  =   -3254.1044  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.8223  VIRIAL  =      73.1686  VOLUME     =   17447.1523
                                                Density    =       0.8686
 Ewald error estimate:   0.1628E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 183000 TIME(PS) =   183.000  TEMP(K) =   369.02  PRESS =  -137.3
 Etot   =     959.9871  EKtot   =    1328.0365  EPtot      =    -368.0494
 BOND   =     194.4980  ANGLE   =     699.5351  DIHED      =     147.2110
 1-4 NB =     160.2222  1-4 EEL =    2472.6321  VDWAALS    =    -745.0001
 EELEC  =   -3297.1477  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.7770  VIRIAL  =     177.4141  VOLUME     =   17412.7477
                                                Density    =       0.8703
 Ewald error estimate:   0.8291E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 184000 TIME(PS) =   184.000  TEMP(K) =   368.85  PRESS =  -459.5
 Etot   =     962.1002  EKtot   =    1327.4049  EPtot      =    -365.3047
 BOND   =     203.2322  ANGLE   =     678.3132  DIHED      =     154.3431
 1-4 NB =     160.6436  1-4 EEL =    2472.3828  VDWAALS    =    -752.8390
 EELEC  =   -3281.3806  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.2090  VIRIAL  =     300.6141  VOLUME     =   17577.8861
                                                Density    =       0.8621
 Ewald error estimate:   0.7470E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 185000 TIME(PS) =   185.000  TEMP(K) =   371.23  PRESS =   216.6
 Etot   =     965.2496  EKtot   =    1335.9697  EPtot      =    -370.7201
 BOND   =     188.5087  ANGLE   =     659.2106  DIHED      =     157.5594
 1-4 NB =     160.6822  1-4 EEL =    2473.4934  VDWAALS    =    -751.8376
 EELEC  =   -3258.3369  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.0038  VIRIAL  =      43.9683  VOLUME     =   17331.4197
                                                Density    =       0.8744
 Ewald error estimate:   0.2239E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 186000 TIME(PS) =   186.000  TEMP(K) =   371.83  PRESS =   375.0
 Etot   =     965.4090  EKtot   =    1338.1346  EPtot      =    -372.7256
 BOND   =     200.4687  ANGLE   =     686.0340  DIHED      =     142.6367
 1-4 NB =     165.2802  1-4 EEL =    2471.3951  VDWAALS    =    -752.0254
 EELEC  =   -3286.5149  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.6491  VIRIAL  =       8.9098  VOLUME     =   17135.3913
                                                Density    =       0.8844
 Ewald error estimate:   0.1090E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 187000 TIME(PS) =   187.000  TEMP(K) =   363.18  PRESS =   -95.0
 Etot   =     972.6453  EKtot   =    1307.0290  EPtot      =    -334.3837
 BOND   =     203.8058  ANGLE   =     701.2770  DIHED      =     145.4559
 1-4 NB =     161.6645  1-4 EEL =    2470.1206  VDWAALS    =    -738.1270
 EELEC  =   -3278.5804  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.3947  VIRIAL  =     168.4561  VOLUME     =   17587.3263
                                                Density    =       0.8617
 Ewald error estimate:   0.2534E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 188000 TIME(PS) =   188.000  TEMP(K) =   368.95  PRESS =   -76.3
 Etot   =     975.4402  EKtot   =    1327.7859  EPtot      =    -352.3457
 BOND   =     190.3735  ANGLE   =     700.3752  DIHED      =     137.3488
 1-4 NB =     165.1252  1-4 EEL =    2473.5859  VDWAALS    =    -755.2682
 EELEC  =   -3263.8861  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.9014  VIRIAL  =     160.4611  VOLUME     =   17339.6177
                                                Density    =       0.8740
 Ewald error estimate:   0.5692E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 189000 TIME(PS) =   189.000  TEMP(K) =   372.15  PRESS =   276.5
 Etot   =     977.6327  EKtot   =    1339.2982  EPtot      =    -361.6655
 BOND   =     202.0257  ANGLE   =     687.4011  DIHED      =     132.4465
 1-4 NB =     160.5637  1-4 EEL =    2460.7545  VDWAALS    =    -757.4162
 EELEC  =   -3247.4408  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.5440  VIRIAL  =      21.4970  VOLUME     =   17090.2780
                                                Density    =       0.8867
 Ewald error estimate:   0.7782E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 190000 TIME(PS) =   190.000  TEMP(K) =   377.17  PRESS =   -94.2
 Etot   =     978.8298  EKtot   =    1357.3594  EPtot      =    -378.5296
 BOND   =     197.9640  ANGLE   =     669.6540  DIHED      =     171.9658
 1-4 NB =     155.4108  1-4 EEL =    2466.2759  VDWAALS    =    -763.7921
 EELEC  =   -3276.0080  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.6425  VIRIAL  =     158.3931  VOLUME     =   17088.2157
                                                Density    =       0.8868
 Ewald error estimate:   0.1467E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 191000 TIME(PS) =   191.000  TEMP(K) =   371.85  PRESS =   381.7
 Etot   =     970.4711  EKtot   =    1338.2161  EPtot      =    -367.7450
 BOND   =     199.6789  ANGLE   =     662.5551  DIHED      =     163.1381
 1-4 NB =     156.1488  1-4 EEL =    2473.5349  VDWAALS    =    -751.3700
 EELEC  =   -3271.4309  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.8692  VIRIAL  =     -16.4013  VOLUME     =   17143.1545
                                                Density    =       0.8840
 Ewald error estimate:   0.3913E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 192000 TIME(PS) =   192.000  TEMP(K) =   363.72  PRESS =   459.9
 Etot   =     964.4908  EKtot   =    1308.9646  EPtot      =    -344.4738
 BOND   =     214.6082  ANGLE   =     686.3274  DIHED      =     139.3868
 1-4 NB =     161.0471  1-4 EEL =    2458.2643  VDWAALS    =    -758.3934
 EELEC  =   -3245.7141  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.0991  VIRIAL  =     -41.9236  VOLUME     =   17121.1773
                                                Density    =       0.8851
 Ewald error estimate:   0.6637E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 193000 TIME(PS) =   193.000  TEMP(K) =   373.48  PRESS =   514.0
 Etot   =     957.2920  EKtot   =    1344.0730  EPtot      =    -386.7811
 BOND   =     190.3120  ANGLE   =     685.9127  DIHED      =     129.7459
 1-4 NB =     165.5484  1-4 EEL =    2475.4281  VDWAALS    =    -778.5796
 EELEC  =   -3255.1485  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.7271  VIRIAL  =     -55.8207  VOLUME     =   16809.2101
                                                Density    =       0.9015
 Ewald error estimate:   0.2388E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 194000 TIME(PS) =   194.000  TEMP(K) =   374.98  PRESS =  -177.7
 Etot   =     958.1811  EKtot   =    1349.4854  EPtot      =    -391.3043
 BOND   =     192.2504  ANGLE   =     681.8401  DIHED      =     136.6090
 1-4 NB =     172.2464  1-4 EEL =    2487.2235  VDWAALS    =    -774.3338
 EELEC  =   -3287.1399  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.3083  VIRIAL  =     212.0442  VOLUME     =   17130.5152
                                                Density    =       0.8846
 Ewald error estimate:   0.2381E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 195000 TIME(PS) =   195.000  TEMP(K) =   369.80  PRESS =   264.1
 Etot   =     958.1528  EKtot   =    1330.8387  EPtot      =    -372.6858
 BOND   =     193.8769  ANGLE   =     671.3026  DIHED      =     145.9421
 1-4 NB =     160.8885  1-4 EEL =    2473.5694  VDWAALS    =    -736.0833
 EELEC  =   -3282.1820  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.7014  VIRIAL  =      37.3197  VOLUME     =   17604.0986
                                                Density    =       0.8608
 Ewald error estimate:   0.2156E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 196000 TIME(PS) =   196.000  TEMP(K) =   374.34  PRESS =   -95.4
 Etot   =     958.4616  EKtot   =    1347.1676  EPtot      =    -388.7060
 BOND   =     209.5396  ANGLE   =     674.3735  DIHED      =     141.1565
 1-4 NB =     156.8352  1-4 EEL =    2474.8550  VDWAALS    =    -752.0035
 EELEC  =   -3293.4622  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.9154  VIRIAL  =     176.7373  VOLUME     =   17391.5737
                                                Density    =       0.8714
 Ewald error estimate:   0.1665E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 197000 TIME(PS) =   197.000  TEMP(K) =   375.84  PRESS =   -97.7
 Etot   =     949.4617  EKtot   =    1352.5784  EPtot      =    -403.1167
 BOND   =     176.3041  ANGLE   =     695.4134  DIHED      =     140.1255
 1-4 NB =     161.7989  1-4 EEL =    2463.8626  VDWAALS    =    -741.9088
 EELEC  =   -3298.7124  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.9480  VIRIAL  =     175.9643  VOLUME     =   17553.5055
                                                Density    =       0.8633
 Ewald error estimate:   0.1742E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 198000 TIME(PS) =   198.000  TEMP(K) =   373.78  PRESS =  -113.8
 Etot   =     953.8293  EKtot   =    1345.1507  EPtot      =    -391.3214
 BOND   =     172.7072  ANGLE   =     707.9858  DIHED      =     138.0985
 1-4 NB =     165.2673  1-4 EEL =    2479.1976  VDWAALS    =    -720.4422
 EELEC  =   -3334.1358  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.2652  VIRIAL  =     183.8690  VOLUME     =   17747.1811
                                                Density    =       0.8539
 Ewald error estimate:   0.1371E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 199000 TIME(PS) =   199.000  TEMP(K) =   360.93  PRESS =   146.2
 Etot   =     954.4900  EKtot   =    1298.9082  EPtot      =    -344.4182
 BOND   =     224.8093  ANGLE   =     711.9814  DIHED      =     151.8136
 1-4 NB =     155.3648  1-4 EEL =    2458.0152  VDWAALS    =    -732.3349
 EELEC  =   -3314.0677  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.2923  VIRIAL  =      85.5761  VOLUME     =   17331.8140
                                                Density    =       0.8744
 Ewald error estimate:   0.1743E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 200000 TIME(PS) =   200.000  TEMP(K) =   375.11  PRESS =   278.0
 Etot   =     953.8882  EKtot   =    1349.9453  EPtot      =    -396.0571
 BOND   =     179.6779  ANGLE   =     698.4833  DIHED      =     135.0675
 1-4 NB =     163.2119  1-4 EEL =    2478.3334  VDWAALS    =    -735.5839
 EELEC  =   -3315.2472  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.7985  VIRIAL  =      41.5548  VOLUME     =   17369.2810
                                                Density    =       0.8725
 Ewald error estimate:   0.1665E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 201000 TIME(PS) =   201.000  TEMP(K) =   377.30  PRESS =   259.6
 Etot   =     961.1655  EKtot   =    1357.8229  EPtot      =    -396.6574
 BOND   =     192.1902  ANGLE   =     677.4325  DIHED      =     132.0850
 1-4 NB =     159.0996  1-4 EEL =    2469.3560  VDWAALS    =    -720.9293
 EELEC  =   -3305.8915  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.6289  VIRIAL  =      38.5486  VOLUME     =   17676.0484
                                                Density    =       0.8573
 Ewald error estimate:   0.1215E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 202000 TIME(PS) =   202.000  TEMP(K) =   371.27  PRESS =  -201.8
 Etot   =     958.5530  EKtot   =    1336.1134  EPtot      =    -377.5604
 BOND   =     190.6321  ANGLE   =     677.1416  DIHED      =     149.8249
 1-4 NB =     167.2253  1-4 EEL =    2483.7415  VDWAALS    =    -741.0937
 EELEC  =   -3305.0321  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.2050  VIRIAL  =     216.9885  VOLUME     =   17626.9012
                                                Density    =       0.8597
 Ewald error estimate:   0.2036E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 203000 TIME(PS) =   203.000  TEMP(K) =   372.48  PRESS =  -144.3
 Etot   =     958.4961  EKtot   =    1340.4859  EPtot      =    -381.9898
 BOND   =     204.6425  ANGLE   =     664.7544  DIHED      =     150.5447
 1-4 NB =     173.9222  1-4 EEL =    2480.3015  VDWAALS    =    -752.6739
 EELEC  =   -3303.4813  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.2006  VIRIAL  =     199.0871  VOLUME     =   17300.3753
                                                Density    =       0.8760
 Ewald error estimate:   0.2233E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 204000 TIME(PS) =   204.000  TEMP(K) =   374.15  PRESS =  -182.9
 Etot   =     954.9483  EKtot   =    1346.4818  EPtot      =    -391.5335
 BOND   =     218.0257  ANGLE   =     654.6088  DIHED      =     156.8736
 1-4 NB =     162.8951  1-4 EEL =    2476.3399  VDWAALS    =    -743.1732
 EELEC  =   -3317.1035  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.4175  VIRIAL  =     211.8781  VOLUME     =   17331.6020
                                                Density    =       0.8744
 Ewald error estimate:   0.1318E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 205000 TIME(PS) =   205.000  TEMP(K) =   377.28  PRESS =   -93.8
 Etot   =     962.1278  EKtot   =    1357.7413  EPtot      =    -395.6136
 BOND   =     193.0006  ANGLE   =     670.4711  DIHED      =     138.4978
 1-4 NB =     157.4953  1-4 EEL =    2465.9669  VDWAALS    =    -749.3488
 EELEC  =   -3271.6966  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.2113  VIRIAL  =     171.5514  VOLUME     =   17448.4870
                                                Density    =       0.8685
 Ewald error estimate:   0.3130E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 206000 TIME(PS) =   206.000  TEMP(K) =   369.28  PRESS =   290.2
 Etot   =     959.9500  EKtot   =    1328.9764  EPtot      =    -369.0264
 BOND   =     207.2180  ANGLE   =     669.1986  DIHED      =     160.3562
 1-4 NB =     161.2900  1-4 EEL =    2468.4598  VDWAALS    =    -743.3060
 EELEC  =   -3292.2430  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.6802  VIRIAL  =      17.5519  VOLUME     =   17419.2927
                                                Density    =       0.8700
 Ewald error estimate:   0.9504E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 207000 TIME(PS) =   207.000  TEMP(K) =   359.27  PRESS =   -24.9
 Etot   =     959.6943  EKtot   =    1292.9405  EPtot      =    -333.2461
 BOND   =     195.6896  ANGLE   =     694.9817  DIHED      =     143.7703
 1-4 NB =     170.1152  1-4 EEL =    2478.8943  VDWAALS    =    -747.0956
 EELEC  =   -3269.6017  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.0650  VIRIAL  =     133.4081  VOLUME     =   17363.0841
                                                Density    =       0.8728
 Ewald error estimate:   0.3241E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 208000 TIME(PS) =   208.000  TEMP(K) =   364.36  PRESS =     9.5
 Etot   =     959.9242  EKtot   =    1311.2428  EPtot      =    -351.3186
 BOND   =     216.7647  ANGLE   =     687.4944  DIHED      =     135.4207
 1-4 NB =     161.6576  1-4 EEL =    2471.5537  VDWAALS    =    -740.4371
 EELEC  =   -3283.7725  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.5449  VIRIAL  =     133.9580  VOLUME     =   17440.3365
                                                Density    =       0.8689
 Ewald error estimate:   0.3555E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 209000 TIME(PS) =   209.000  TEMP(K) =   372.68  PRESS =   -63.0
 Etot   =     954.9155  EKtot   =    1341.1967  EPtot      =    -386.2812
 BOND   =     182.1164  ANGLE   =     674.4766  DIHED      =     149.0033
 1-4 NB =     169.8606  1-4 EEL =    2482.2843  VDWAALS    =    -760.7816
 EELEC  =   -3283.2407  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.5247  VIRIAL  =     168.9219  VOLUME     =   17213.3037
                                                Density    =       0.8804
 Ewald error estimate:   0.1128E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 210000 TIME(PS) =   210.000  TEMP(K) =   378.15  PRESS =  -168.5
 Etot   =     951.9075  EKtot   =    1360.8939  EPtot      =    -408.9864
 BOND   =     192.5759  ANGLE   =     674.5600  DIHED      =     146.6245
 1-4 NB =     158.7014  1-4 EEL =    2470.6506  VDWAALS    =    -776.5514
 EELEC  =   -3275.5474  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.2616  VIRIAL  =     203.6021  VOLUME     =   17139.4176
                                                Density    =       0.8842
 Ewald error estimate:   0.2445E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 211000 TIME(PS) =   211.000  TEMP(K) =   360.00  PRESS =  -305.0
 Etot   =     949.1225  EKtot   =    1295.5527  EPtot      =    -346.4301
 BOND   =     208.9423  ANGLE   =     669.4060  DIHED      =     154.6456
 1-4 NB =     174.3903  1-4 EEL =    2491.5239  VDWAALS    =    -775.1714
 EELEC  =   -3270.1668  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.5285  VIRIAL  =     236.2345  VOLUME     =   17114.0519
                                                Density    =       0.8855
 Ewald error estimate:   0.1481E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 212000 TIME(PS) =   212.000  TEMP(K) =   377.54  PRESS =  -589.0
 Etot   =     950.6057  EKtot   =    1358.6939  EPtot      =    -408.0882
 BOND   =     198.8004  ANGLE   =     673.6982  DIHED      =     160.2275
 1-4 NB =     159.3882  1-4 EEL =    2460.9259  VDWAALS    =    -769.2268
 EELEC  =   -3291.9016  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.1024  VIRIAL  =     366.4815  VOLUME     =   17406.6952
                                                Density    =       0.8706
 Ewald error estimate:   0.3832E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 213000 TIME(PS) =   213.000  TEMP(K) =   372.48  PRESS =  -295.8
 Etot   =     950.0628  EKtot   =    1340.4718  EPtot      =    -390.4090
 BOND   =     191.6698  ANGLE   =     671.1257  DIHED      =     147.2229
 1-4 NB =     162.0116  1-4 EEL =    2467.6815  VDWAALS    =    -780.3468
 EELEC  =   -3249.7737  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     112.7519  VIRIAL  =     221.9911  VOLUME     =   17105.2985
                                                Density    =       0.8859
 Ewald error estimate:   0.1768E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 214000 TIME(PS) =   214.000  TEMP(K) =   375.54  PRESS =   524.2
 Etot   =     943.8262  EKtot   =    1351.5111  EPtot      =    -407.6848
 BOND   =     205.6472  ANGLE   =     672.8138  DIHED      =     125.3720
 1-4 NB =     164.8100  1-4 EEL =    2476.6084  VDWAALS    =    -773.6397
 EELEC  =   -3279.2964  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.1110  VIRIAL  =     -57.0271  VOLUME     =   16888.7972
                                                Density    =       0.8973
 Ewald error estimate:   0.9864E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 215000 TIME(PS) =   215.000  TEMP(K) =   368.97  PRESS =    -7.5
 Etot   =     943.8783  EKtot   =    1327.8501  EPtot      =    -383.9717
 BOND   =     175.2191  ANGLE   =     714.1511  DIHED      =     155.5809
 1-4 NB =     165.6580  1-4 EEL =    2475.6613  VDWAALS    =    -768.9535
 EELEC  =   -3301.2885  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.5725  VIRIAL  =     132.3429  VOLUME     =   17042.7325
                                                Density    =       0.8892
 Ewald error estimate:   0.2057E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 216000 TIME(PS) =   216.000  TEMP(K) =   372.80  PRESS =   138.5
 Etot   =     954.0545  EKtot   =    1341.6433  EPtot      =    -387.5888
 BOND   =     188.5521  ANGLE   =     730.9691  DIHED      =     131.8709
 1-4 NB =     152.4122  1-4 EEL =    2436.6724  VDWAALS    =    -758.4212
 EELEC  =   -3269.6443  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     118.1762  VIRIAL  =      66.7093  VOLUME     =   17213.9221
                                                Density    =       0.8804
 Ewald error estimate:   0.3742E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 217000 TIME(PS) =   217.000  TEMP(K) =   374.95  PRESS =   122.9
 Etot   =     957.7459  EKtot   =    1349.3703  EPtot      =    -391.6244
 BOND   =     194.5149  ANGLE   =     693.6501  DIHED      =     124.2285
 1-4 NB =     158.2084  1-4 EEL =    2476.0033  VDWAALS    =    -740.8674
 EELEC  =   -3297.3621  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.1139  VIRIAL  =      85.8971  VOLUME     =   17416.5257
                                                Density    =       0.8701
 Ewald error estimate:   0.8096E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 218000 TIME(PS) =   218.000  TEMP(K) =   376.52  PRESS =   160.0
 Etot   =     958.4717  EKtot   =    1355.0062  EPtot      =    -396.5345
 BOND   =     188.7760  ANGLE   =     657.6128  DIHED      =     143.1507
 1-4 NB =     177.5369  1-4 EEL =    2474.6459  VDWAALS    =    -745.0126
 EELEC  =   -3293.2442  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.3533  VIRIAL  =      85.7286  VOLUME     =   17264.7971
                                                Density    =       0.8778
 Ewald error estimate:   0.1064E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 219000 TIME(PS) =   219.000  TEMP(K) =   361.96  PRESS =   108.8
 Etot   =     957.4410  EKtot   =    1302.6337  EPtot      =    -345.1927
 BOND   =     200.8879  ANGLE   =     702.2436  DIHED      =     147.9628
 1-4 NB =     154.3071  1-4 EEL =    2475.9419  VDWAALS    =    -769.9405
 EELEC  =   -3256.5955  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.1245  VIRIAL  =      81.0688  VOLUME     =   17045.2792
                                                Density    =       0.8891
 Ewald error estimate:   0.7210E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 220000 TIME(PS) =   220.000  TEMP(K) =   367.45  PRESS =  -130.0
 Etot   =     964.7240  EKtot   =    1322.3978  EPtot      =    -357.6738
 BOND   =     219.9364  ANGLE   =     674.9814  DIHED      =     146.6749
 1-4 NB =     170.9964  1-4 EEL =    2463.6448  VDWAALS    =    -746.2407
 EELEC  =   -3287.6670  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.4658  VIRIAL  =     175.4429  VOLUME     =   17449.5210
                                                Density    =       0.8685
 Ewald error estimate:   0.3349E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 221000 TIME(PS) =   221.000  TEMP(K) =   372.42  PRESS =    18.8
 Etot   =     966.4403  EKtot   =    1340.2670  EPtot      =    -373.8267
 BOND   =     203.8592  ANGLE   =     689.6117  DIHED      =     158.5184
 1-4 NB =     159.7774  1-4 EEL =    2466.3993  VDWAALS    =    -756.5295
 EELEC  =   -3295.4632  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.6420  VIRIAL  =     119.6284  VOLUME     =   17287.7862
                                                Density    =       0.8766
 Ewald error estimate:   0.1825E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 222000 TIME(PS) =   222.000  TEMP(K) =   373.76  PRESS =   -12.6
 Etot   =     969.5468  EKtot   =    1345.0954  EPtot      =    -375.5486
 BOND   =     196.8950  ANGLE   =     658.5302  DIHED      =     162.4500
 1-4 NB =     156.2597  1-4 EEL =    2472.7101  VDWAALS    =    -775.7967
 EELEC  =   -3246.5970  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.5797  VIRIAL  =     132.2313  VOLUME     =   17032.9521
                                                Density    =       0.8897
 Ewald error estimate:   0.2104E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 223000 TIME(PS) =   223.000  TEMP(K) =   374.02  PRESS =  -421.8
 Etot   =     971.0527  EKtot   =    1346.0426  EPtot      =    -374.9899
 BOND   =     194.5486  ANGLE   =     696.3930  DIHED      =     138.7358
 1-4 NB =     159.4217  1-4 EEL =    2469.4212  VDWAALS    =    -773.3448
 EELEC  =   -3260.1654  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.1849  VIRIAL  =     300.7985  VOLUME     =   17307.6032
                                                Density    =       0.8756
 Ewald error estimate:   0.2956E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 224000 TIME(PS) =   224.000  TEMP(K) =   384.25  PRESS =  -476.9
 Etot   =     961.5258  EKtot   =    1382.8491  EPtot      =    -421.3233
 BOND   =     197.3849  ANGLE   =     681.0273  DIHED      =     133.7389
 1-4 NB =     161.8840  1-4 EEL =    2472.7582  VDWAALS    =    -768.9352
 EELEC  =   -3299.1816  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.6411  VIRIAL  =     318.7716  VOLUME     =   17106.4877
                                                Density    =       0.8859
 Ewald error estimate:   0.1549E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 225000 TIME(PS) =   225.000  TEMP(K) =   376.95  PRESS =  -218.9
 Etot   =     953.3769  EKtot   =    1356.5839  EPtot      =    -403.2070
 BOND   =     190.5829  ANGLE   =     689.8380  DIHED      =     142.1164
 1-4 NB =     161.9478  1-4 EEL =    2457.1619  VDWAALS    =    -785.9107
 EELEC  =   -3258.9432  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.7951  VIRIAL  =     210.7590  VOLUME     =   16918.8961
                                                Density    =       0.8957
 Ewald error estimate:   0.1272E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 226000 TIME(PS) =   226.000  TEMP(K) =   383.28  PRESS =    81.2
 Etot   =     948.1538  EKtot   =    1379.3564  EPtot      =    -431.2026
 BOND   =     197.7944  ANGLE   =     643.6142  DIHED      =     148.3297
 1-4 NB =     164.4940  1-4 EEL =    2474.6578  VDWAALS    =    -770.4278
 EELEC  =   -3289.6648  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.3111  VIRIAL  =     118.5482  VOLUME     =   16967.7530
                                                Density    =       0.8931
 Ewald error estimate:   0.1165E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 227000 TIME(PS) =   227.000  TEMP(K) =   369.21  PRESS =    75.9
 Etot   =     945.5872  EKtot   =    1328.6966  EPtot      =    -383.1094
 BOND   =     223.1384  ANGLE   =     644.2425  DIHED      =     151.6663
 1-4 NB =     170.0321  1-4 EEL =    2484.6722  VDWAALS    =    -753.7113
 EELEC  =   -3303.1495  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     166.5550  VIRIAL  =     138.3938  VOLUME     =   17194.6714
                                                Density    =       0.8813
 Ewald error estimate:   0.1863E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 228000 TIME(PS) =   228.000  TEMP(K) =   369.11  PRESS =  -102.9
 Etot   =     949.1404  EKtot   =    1328.3595  EPtot      =    -379.2191
 BOND   =     203.1207  ANGLE   =     663.7658  DIHED      =     156.0701
 1-4 NB =     172.1922  1-4 EEL =    2472.6407  VDWAALS    =    -749.2197
 EELEC  =   -3297.7888  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.4276  VIRIAL  =     177.0030  VOLUME     =   17362.5136
                                                Density    =       0.8728
 Ewald error estimate:   0.2513E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 229000 TIME(PS) =   229.000  TEMP(K) =   365.75  PRESS =   311.0
 Etot   =     942.5868  EKtot   =    1316.2480  EPtot      =    -373.6612
 BOND   =     198.9646  ANGLE   =     692.4408  DIHED      =     137.4548
 1-4 NB =     156.9679  1-4 EEL =    2472.2549  VDWAALS    =    -753.9481
 EELEC  =   -3277.7961  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.1439  VIRIAL  =      19.0617  VOLUME     =   17138.5846
                                                Density    =       0.8842
 Ewald error estimate:   0.5996E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 230000 TIME(PS) =   230.000  TEMP(K) =   378.37  PRESS =  -362.6
 Etot   =     946.7826  EKtot   =    1361.6761  EPtot      =    -414.8935
 BOND   =     188.6766  ANGLE   =     667.9778  DIHED      =     143.1632
 1-4 NB =     166.6314  1-4 EEL =    2477.6133  VDWAALS    =    -765.2693
 EELEC  =   -3293.6865  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.2469  VIRIAL  =     281.1950  VOLUME     =   17239.1859
                                                Density    =       0.8791
 Ewald error estimate:   0.3161E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 231000 TIME(PS) =   231.000  TEMP(K) =   368.46  PRESS =    55.8
 Etot   =     954.2581  EKtot   =    1326.0036  EPtot      =    -371.7455
 BOND   =     191.3764  ANGLE   =     681.6163  DIHED      =     145.1001
 1-4 NB =     158.2756  1-4 EEL =    2467.4871  VDWAALS    =    -771.9291
 EELEC  =   -3243.6720  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.1437  VIRIAL  =     119.4751  VOLUME     =   17164.1920
                                                Density    =       0.8829
 Ewald error estimate:   0.1988E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 232000 TIME(PS) =   232.000  TEMP(K) =   366.39  PRESS =   196.0
 Etot   =     969.8652  EKtot   =    1318.5718  EPtot      =    -348.7066
 BOND   =     216.6414  ANGLE   =     677.2586  DIHED      =     142.4917
 1-4 NB =     161.1719  1-4 EEL =    2462.6083  VDWAALS    =    -753.1536
 EELEC  =   -3255.7250  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.8973  VIRIAL  =      74.2250  VOLUME     =   17174.9206
                                                Density    =       0.8824
 Ewald error estimate:   0.4162E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 233000 TIME(PS) =   233.000  TEMP(K) =   367.20  PRESS =   -83.9
 Etot   =     977.3558  EKtot   =    1321.4767  EPtot      =    -344.1209
 BOND   =     180.6021  ANGLE   =     684.1415  DIHED      =     143.1393
 1-4 NB =     165.9820  1-4 EEL =    2489.4390  VDWAALS    =    -731.4176
 EELEC  =   -3276.0072  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.1742  VIRIAL  =     176.1101  VOLUME     =   17630.7075
                                                Density    =       0.8595
 Ewald error estimate:   0.2293E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 234000 TIME(PS) =   234.000  TEMP(K) =   362.26  PRESS =   352.5
 Etot   =     975.3911  EKtot   =    1303.7139  EPtot      =    -328.3227
 BOND   =     200.8667  ANGLE   =     664.7776  DIHED      =     150.6853
 1-4 NB =     157.1922  1-4 EEL =    2479.8331  VDWAALS    =    -719.7602
 EELEC  =   -3261.9175  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.3593  VIRIAL  =       2.4894  VOLUME     =   17590.6122
                                                Density    =       0.8615
 Ewald error estimate:   0.1530E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 235000 TIME(PS) =   235.000  TEMP(K) =   375.22  PRESS =  -385.2
 Etot   =     985.8288  EKtot   =    1350.3539  EPtot      =    -364.5251
 BOND   =     208.3212  ANGLE   =     669.3730  DIHED      =     135.1318
 1-4 NB =     163.6280  1-4 EEL =    2477.7934  VDWAALS    =    -733.9136
 EELEC  =   -3284.8589  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.2231  VIRIAL  =     295.8145  VOLUME     =   17867.4390
                                                Density    =       0.8482
 Ewald error estimate:   0.1680E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 236000 TIME(PS) =   236.000  TEMP(K) =   366.05  PRESS =     2.5
 Etot   =     986.7089  EKtot   =    1317.3427  EPtot      =    -330.6338
 BOND   =     203.7475  ANGLE   =     701.6368  DIHED      =     129.4396
 1-4 NB =     157.7127  1-4 EEL =    2460.2357  VDWAALS    =    -721.9257
 EELEC  =   -3261.4805  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.8933  VIRIAL  =     148.9265  VOLUME     =   17755.5085
                                                Density    =       0.8535
 Ewald error estimate:   0.2382E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 237000 TIME(PS) =   237.000  TEMP(K) =   365.61  PRESS =  -192.6
 Etot   =     978.6757  EKtot   =    1315.7569  EPtot      =    -337.0813
 BOND   =     186.2778  ANGLE   =     710.9256  DIHED      =     140.4556
 1-4 NB =     161.6184  1-4 EEL =    2477.7581  VDWAALS    =    -750.8403
 EELEC  =   -3263.2766  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.8069  VIRIAL  =     203.2209  VOLUME     =   17410.3924
                                                Density    =       0.8704
 Ewald error estimate:   0.1591E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 238000 TIME(PS) =   238.000  TEMP(K) =   376.30  PRESS =   -22.9
 Etot   =     982.7392  EKtot   =    1354.2311  EPtot      =    -371.4919
 BOND   =     205.0132  ANGLE   =     671.9304  DIHED      =     140.4024
 1-4 NB =     158.3309  1-4 EEL =    2456.8675  VDWAALS    =    -722.3994
 EELEC  =   -3281.6370  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.1883  VIRIAL  =     148.9885  VOLUME     =   17826.7501
                                                Density    =       0.8501
 Ewald error estimate:   0.2217E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 239000 TIME(PS) =   239.000  TEMP(K) =   374.70  PRESS =   733.4
 Etot   =     979.4454  EKtot   =    1348.4543  EPtot      =    -369.0090
 BOND   =     188.7212  ANGLE   =     672.2733  DIHED      =     124.6662
 1-4 NB =     161.5978  1-4 EEL =    2478.5529  VDWAALS    =    -696.7018
 EELEC  =   -3298.1185  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.5759  VIRIAL  =    -152.0842  VOLUME     =   17850.4238
                                                Density    =       0.8490
 Ewald error estimate:   0.2403E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 240000 TIME(PS) =   240.000  TEMP(K) =   378.32  PRESS =   169.1
 Etot   =     977.5517  EKtot   =    1361.5015  EPtot      =    -383.9498
 BOND   =     190.1051  ANGLE   =     697.1482  DIHED      =     141.0081
 1-4 NB =     158.7397  1-4 EEL =    2468.7270  VDWAALS    =    -728.9740
 EELEC  =   -3310.7039  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.7953  VIRIAL  =      72.6675  VOLUME     =   17560.7496
                                                Density    =       0.8630
 Ewald error estimate:   0.2598E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 241000 TIME(PS) =   241.000  TEMP(K) =   371.33  PRESS =   307.4
 Etot   =     970.4350  EKtot   =    1336.3485  EPtot      =    -365.9135
 BOND   =     208.8505  ANGLE   =     665.3346  DIHED      =     153.3695
 1-4 NB =     164.5715  1-4 EEL =    2473.0766  VDWAALS    =    -728.4672
 EELEC  =   -3302.6491  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.5984  VIRIAL  =      21.4627  VOLUME     =   17496.9210
                                                Density    =       0.8661
 Ewald error estimate:   0.2407E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 242000 TIME(PS) =   242.000  TEMP(K) =   376.56  PRESS =    21.6
 Etot   =     971.9593  EKtot   =    1355.1736  EPtot      =    -383.2143
 BOND   =     181.7316  ANGLE   =     678.4003  DIHED      =     144.2145
 1-4 NB =     166.2265  1-4 EEL =    2481.6156  VDWAALS    =    -730.2492
 EELEC  =   -3305.1537  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.0640  VIRIAL  =     139.7929  VOLUME     =   17698.2259
                                                Density    =       0.8563
 Ewald error estimate:   0.1622E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 243000 TIME(PS) =   243.000  TEMP(K) =   383.35  PRESS =   251.5
 Etot   =     965.8175  EKtot   =    1379.5888  EPtot      =    -413.7713
 BOND   =     182.1258  ANGLE   =     662.5149  DIHED      =     166.8709
 1-4 NB =     159.7069  1-4 EEL =    2466.7180  VDWAALS    =    -715.6078
 EELEC  =   -3336.1000  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.4473  VIRIAL  =      37.1063  VOLUME     =   17739.8020
                                                Density    =       0.8543
 Ewald error estimate:   0.2111E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 244000 TIME(PS) =   244.000  TEMP(K) =   369.48  PRESS =   165.5
 Etot   =     951.5589  EKtot   =    1329.6859  EPtot      =    -378.1270
 BOND   =     187.2112  ANGLE   =     679.3136  DIHED      =     155.5106
 1-4 NB =     159.3328  1-4 EEL =    2478.1066  VDWAALS    =    -724.3833
 EELEC  =   -3313.2185  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     113.8200  VIRIAL  =      50.9823  VOLUME     =   17586.5387
                                                Density    =       0.8617
 Ewald error estimate:   0.1447E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 245000 TIME(PS) =   245.000  TEMP(K) =   369.14  PRESS =   984.3
 Etot   =     953.9990  EKtot   =    1328.4717  EPtot      =    -374.4727
 BOND   =     194.3499  ANGLE   =     692.9740  DIHED      =     134.9963
 1-4 NB =     158.9337  1-4 EEL =    2460.1472  VDWAALS    =    -706.6424
 EELEC  =   -3309.2314  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     157.9131  VIRIAL  =    -215.4734  VOLUME     =   17569.1891
                                                Density    =       0.8626
 Ewald error estimate:   0.1425E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 246000 TIME(PS) =   246.000  TEMP(K) =   366.82  PRESS =  -614.8
 Etot   =     951.9742  EKtot   =    1320.1269  EPtot      =    -368.1526
 BOND   =     202.5764  ANGLE   =     672.8949  DIHED      =     158.5115
 1-4 NB =     172.6336  1-4 EEL =    2489.3644  VDWAALS    =    -759.3240
 EELEC  =   -3304.8095  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.0515  VIRIAL  =     366.6796  VOLUME     =   17299.6872
                                                Density    =       0.8760
 Ewald error estimate:   0.1993E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 247000 TIME(PS) =   247.000  TEMP(K) =   368.74  PRESS =  -256.7
 Etot   =     955.2371  EKtot   =    1327.0086  EPtot      =    -371.7714
 BOND   =     189.0428  ANGLE   =     682.6279  DIHED      =     147.3811
 1-4 NB =     169.6061  1-4 EEL =    2490.6056  VDWAALS    =    -740.8754
 EELEC  =   -3310.1597  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     151.2044  VIRIAL  =     248.5839  VOLUME     =   17567.6652
                                                Density    =       0.8626
 Ewald error estimate:   0.3488E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 248000 TIME(PS) =   248.000  TEMP(K) =   378.59  PRESS =  -250.2
 Etot   =     949.4002  EKtot   =    1362.4550  EPtot      =    -413.0548
 BOND   =     196.5021  ANGLE   =     653.5521  DIHED      =     139.9335
 1-4 NB =     160.9704  1-4 EEL =    2468.6059  VDWAALS    =    -756.4617
 EELEC  =   -3276.1571  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.5609  VIRIAL  =     218.6257  VOLUME     =   17410.2924
                                                Density    =       0.8704
 Ewald error estimate:   0.1292E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 249000 TIME(PS) =   249.000  TEMP(K) =   368.21  PRESS =  -368.6
 Etot   =     951.5588  EKtot   =    1325.1291  EPtot      =    -373.5703
 BOND   =     193.6172  ANGLE   =     687.8679  DIHED      =     147.6573
 1-4 NB =     156.5218  1-4 EEL =    2477.3102  VDWAALS    =    -761.8367
 EELEC  =   -3274.7080  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     117.7611  VIRIAL  =     255.2888  VOLUME     =   17279.0628
                                                Density    =       0.8770
 Ewald error estimate:   0.1673E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 250000 TIME(PS) =   250.000  TEMP(K) =   359.38  PRESS =   468.1
 Etot   =     960.0813  EKtot   =    1293.3238  EPtot      =    -333.2425
 BOND   =     208.3076  ANGLE   =     704.9321  DIHED      =     132.2683
 1-4 NB =     160.8390  1-4 EEL =    2471.7342  VDWAALS    =    -731.2800
 EELEC  =   -3280.0437  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.8829  VIRIAL  =     -34.8163  VOLUME     =   17484.4897
                                                Density    =       0.8667
 Ewald error estimate:   0.3928E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 251000 TIME(PS) =   251.000  TEMP(K) =   363.32  PRESS =  -206.0
 Etot   =     963.4207  EKtot   =    1307.5008  EPtot      =    -344.0801
 BOND   =     204.0833  ANGLE   =     690.8056  DIHED      =     139.4710
 1-4 NB =     164.0055  1-4 EEL =    2469.9745  VDWAALS    =    -750.4294
 EELEC  =   -3261.9906  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.8578  VIRIAL  =     212.6960  VOLUME     =   17503.5654
                                                Density    =       0.8658
 Ewald error estimate:   0.1670E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 252000 TIME(PS) =   252.000  TEMP(K) =   377.82  PRESS =   157.1
 Etot   =     968.6520  EKtot   =    1359.6934  EPtot      =    -391.0414
 BOND   =     197.1886  ANGLE   =     670.2988  DIHED      =     131.1552
 1-4 NB =     167.6856  1-4 EEL =    2480.3388  VDWAALS    =    -736.2630
 EELEC  =   -3301.4455  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.1296  VIRIAL  =      75.9036  VOLUME     =   17457.3536
                                                Density    =       0.8681
 Ewald error estimate:   0.1133E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 253000 TIME(PS) =   253.000  TEMP(K) =   374.07  PRESS =   177.5
 Etot   =     965.7493  EKtot   =    1346.2172  EPtot      =    -380.4680
 BOND   =     202.5415  ANGLE   =     680.3669  DIHED      =     138.9146
 1-4 NB =     159.4055  1-4 EEL =    2464.6615  VDWAALS    =    -710.6605
 EELEC  =   -3315.6975  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     120.3891  VIRIAL  =      52.8521  VOLUME     =   17625.4764
                                                Density    =       0.8598
 Ewald error estimate:   0.2033E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 254000 TIME(PS) =   254.000  TEMP(K) =   373.74  PRESS =  -330.9
 Etot   =     964.3837  EKtot   =    1345.0183  EPtot      =    -380.6346
 BOND   =     189.4786  ANGLE   =     700.3200  DIHED      =     124.8407
 1-4 NB =     157.3231  1-4 EEL =    2463.1213  VDWAALS    =    -750.9877
 EELEC  =   -3264.7308  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.5393  VIRIAL  =     266.3484  VOLUME     =   17471.2444
                                                Density    =       0.8674
 Ewald error estimate:   0.3166E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 255000 TIME(PS) =   255.000  TEMP(K) =   361.14  PRESS =  -603.9
 Etot   =     968.8669  EKtot   =    1299.6639  EPtot      =    -330.7971
 BOND   =     198.0988  ANGLE   =     722.0177  DIHED      =     137.5192
 1-4 NB =     162.4582  1-4 EEL =    2455.7472  VDWAALS    =    -740.3967
 EELEC  =   -3266.2414  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.8670  VIRIAL  =     366.4248  VOLUME     =   17683.0875
                                                Density    =       0.8570
 Ewald error estimate:   0.2584E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 256000 TIME(PS) =   256.000  TEMP(K) =   368.70  PRESS =  -145.4
 Etot   =     971.8033  EKtot   =    1326.8712  EPtot      =    -355.0679
 BOND   =     194.6892  ANGLE   =     674.7853  DIHED      =     140.5332
 1-4 NB =     172.3932  1-4 EEL =    2479.4694  VDWAALS    =    -743.7844
 EELEC  =   -3273.1538  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.0472  VIRIAL  =     187.9313  VOLUME     =   17479.7585
                                                Density    =       0.8670
 Ewald error estimate:   0.2968E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 257000 TIME(PS) =   257.000  TEMP(K) =   368.25  PRESS =    91.7
 Etot   =     964.3393  EKtot   =    1325.2654  EPtot      =    -360.9261
 BOND   =     175.9508  ANGLE   =     710.3408  DIHED      =     157.2337
 1-4 NB =     159.7232  1-4 EEL =    2457.7587  VDWAALS    =    -752.0936
 EELEC  =   -3269.8397  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.8750  VIRIAL  =     113.3355  VOLUME     =   17448.4666
                                                Density    =       0.8685
 Ewald error estimate:   0.7535E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 258000 TIME(PS) =   258.000  TEMP(K) =   370.56  PRESS =   -68.8
 Etot   =     963.2812  EKtot   =    1333.5892  EPtot      =    -370.3081
 BOND   =     192.8456  ANGLE   =     676.0126  DIHED      =     149.4086
 1-4 NB =     167.2920  1-4 EEL =    2477.9596  VDWAALS    =    -731.3879
 EELEC  =   -3302.4386  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.3068  VIRIAL  =     170.4648  VOLUME     =   17599.2659
                                                Density    =       0.8611
 Ewald error estimate:   0.7854E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 259000 TIME(PS) =   259.000  TEMP(K) =   376.27  PRESS =   100.3
 Etot   =     958.7622  EKtot   =    1354.1360  EPtot      =    -395.3738
 BOND   =     187.5936  ANGLE   =     656.9453  DIHED      =     148.7362
 1-4 NB =     166.6682  1-4 EEL =    2486.2363  VDWAALS    =    -739.3229
 EELEC  =   -3302.2305  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.4378  VIRIAL  =      96.8293  VOLUME     =   17358.6933
                                                Density    =       0.8730
 Ewald error estimate:   0.5024E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 260000 TIME(PS) =   260.000  TEMP(K) =   371.65  PRESS =  -254.4
 Etot   =     960.8058  EKtot   =    1337.5047  EPtot      =    -376.6989
 BOND   =     206.9981  ANGLE   =     671.5236  DIHED      =     151.8933
 1-4 NB =     155.0338  1-4 EEL =    2458.9861  VDWAALS    =    -743.9727
 EELEC  =   -3277.1611  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.7635  VIRIAL  =     235.5796  VOLUME     =   17622.7181
                                                Density    =       0.8599
 Ewald error estimate:   0.3959E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 261000 TIME(PS) =   261.000  TEMP(K) =   366.05  PRESS =  -486.7
 Etot   =     966.6743  EKtot   =    1317.3347  EPtot      =    -350.6605
 BOND   =     200.3776  ANGLE   =     683.0254  DIHED      =     142.7605
 1-4 NB =     173.6604  1-4 EEL =    2482.0644  VDWAALS    =    -736.5706
 EELEC  =   -3295.9781  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.4778  VIRIAL  =     331.4659  VOLUME     =   17795.2043
                                                Density    =       0.8516
 Ewald error estimate:   0.1976E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 262000 TIME(PS) =   262.000  TEMP(K) =   358.48  PRESS =     3.6
 Etot   =     971.2704  EKtot   =    1290.0919  EPtot      =    -318.8216
 BOND   =     207.6033  ANGLE   =     711.7058  DIHED      =     147.2333
 1-4 NB =     153.1041  1-4 EEL =    2450.4766  VDWAALS    =    -725.8740
 EELEC  =   -3263.0706  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.3368  VIRIAL  =     142.9435  VOLUME     =   17685.8109
                                                Density    =       0.8569
 Ewald error estimate:   0.1355E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 263000 TIME(PS) =   263.000  TEMP(K) =   368.82  PRESS =    59.1
 Etot   =     978.7630  EKtot   =    1327.3145  EPtot      =    -348.5515
 BOND   =     191.6456  ANGLE   =     671.1313  DIHED      =     172.8772
 1-4 NB =     167.1643  1-4 EEL =    2484.5512  VDWAALS    =    -726.5940
 EELEC  =   -3309.3272  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.5192  VIRIAL  =     119.7833  VOLUME     =   17805.2014
                                                Density    =       0.8511
 Ewald error estimate:   0.2439E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 264000 TIME(PS) =   264.000  TEMP(K) =   369.38  PRESS =   132.1
 Etot   =     977.6835  EKtot   =    1329.3138  EPtot      =    -351.6303
 BOND   =     216.8501  ANGLE   =     661.7508  DIHED      =     157.2901
 1-4 NB =     153.0929  1-4 EEL =    2477.4064  VDWAALS    =    -723.6821
 EELEC  =   -3294.3384  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.0444  VIRIAL  =      88.6800  VOLUME     =   17657.6539
                                                Density    =       0.8582
 Ewald error estimate:   0.6964E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 265000 TIME(PS) =   265.000  TEMP(K) =   368.43  PRESS =  -212.0
 Etot   =     969.2860  EKtot   =    1325.8977  EPtot      =    -356.6117
 BOND   =     195.5082  ANGLE   =     715.3358  DIHED      =     139.2762
 1-4 NB =     157.1879  1-4 EEL =    2468.2575  VDWAALS    =    -749.8926
 EELEC  =   -3282.2847  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.3486  VIRIAL  =     227.9240  VOLUME     =   17386.2717
                                                Density    =       0.8716
 Ewald error estimate:   0.1472E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 266000 TIME(PS) =   266.000  TEMP(K) =   370.84  PRESS =  -213.4
 Etot   =     974.2401  EKtot   =    1334.5917  EPtot      =    -360.3516
 BOND   =     193.5591  ANGLE   =     692.3388  DIHED      =     132.1572
 1-4 NB =     171.9440  1-4 EEL =    2473.9205  VDWAALS    =    -744.0309
 EELEC  =   -3280.2403  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.1764  VIRIAL  =     210.8087  VOLUME     =   17502.6256
                                                Density    =       0.8658
 Ewald error estimate:   0.1703E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 267000 TIME(PS) =   267.000  TEMP(K) =   370.48  PRESS =   306.3
 Etot   =     961.2276  EKtot   =    1333.2792  EPtot      =    -372.0516
 BOND   =     208.4766  ANGLE   =     656.4671  DIHED      =     146.5398
 1-4 NB =     178.3498  1-4 EEL =    2489.3323  VDWAALS    =    -723.8865
 EELEC  =   -3327.3308  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.3124  VIRIAL  =      21.6179  VOLUME     =   17345.2731
                                                Density    =       0.8737
 Ewald error estimate:   0.2087E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 268000 TIME(PS) =   268.000  TEMP(K) =   365.39  PRESS =  -144.0
 Etot   =     957.6055  EKtot   =    1314.9772  EPtot      =    -357.3716
 BOND   =     193.2600  ANGLE   =     724.3977  DIHED      =     140.0379
 1-4 NB =     166.9854  1-4 EEL =    2473.0208  VDWAALS    =    -744.9503
 EELEC  =   -3310.1231  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.9066  VIRIAL  =     175.9311  VOLUME     =   17377.2473
                                                Density    =       0.8721
 Ewald error estimate:   0.2681E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 269000 TIME(PS) =   269.000  TEMP(K) =   373.95  PRESS =   -87.8
 Etot   =     948.8935  EKtot   =    1345.7823  EPtot      =    -396.8888
 BOND   =     168.9775  ANGLE   =     712.7817  DIHED      =     122.5372
 1-4 NB =     161.1127  1-4 EEL =    2473.4622  VDWAALS    =    -757.3135
 EELEC  =   -3278.4466  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     158.1729  VIRIAL  =     191.1715  VOLUME     =   17409.3160
                                                Density    =       0.8705
 Ewald error estimate:   0.1702E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 270000 TIME(PS) =   270.000  TEMP(K) =   377.43  PRESS =   189.3
 Etot   =     950.0888  EKtot   =    1358.3048  EPtot      =    -408.2160
 BOND   =     182.7261  ANGLE   =     695.4844  DIHED      =     120.8317
 1-4 NB =     164.0908  1-4 EEL =    2486.0968  VDWAALS    =    -761.4838
 EELEC  =   -3295.9619  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     152.6485  VIRIAL  =      82.6919  VOLUME     =   17114.5268
                                                Density    =       0.8855
 Ewald error estimate:   0.2962E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 271000 TIME(PS) =   271.000  TEMP(K) =   381.67  PRESS =  -519.7
 Etot   =     949.3608  EKtot   =    1373.5584  EPtot      =    -424.1976
 BOND   =     203.7978  ANGLE   =     664.0766  DIHED      =     138.4586
 1-4 NB =     158.0300  1-4 EEL =    2452.3026  VDWAALS    =    -763.4050
 EELEC  =   -3277.4582  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.6922  VIRIAL  =     335.7937  VOLUME     =   17298.5877
                                                Density    =       0.8760
 Ewald error estimate:   0.1341E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 272000 TIME(PS) =   272.000  TEMP(K) =   374.05  PRESS =   262.0
 Etot   =     955.5672  EKtot   =    1346.1224  EPtot      =    -390.5552
 BOND   =     203.7454  ANGLE   =     682.7444  DIHED      =     126.6309
 1-4 NB =     151.1016  1-4 EEL =    2468.9116  VDWAALS    =    -726.7351
 EELEC  =   -3296.9540  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.6268  VIRIAL  =      36.1445  VOLUME     =   17589.3339
                                                Density    =       0.8616
 Ewald error estimate:   0.6979E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 273000 TIME(PS) =   273.000  TEMP(K) =   378.52  PRESS =  -361.0
 Etot   =     960.4861  EKtot   =    1362.2238  EPtot      =    -401.7377
 BOND   =     171.4335  ANGLE   =     667.8854  DIHED      =     141.6739
 1-4 NB =     160.3306  1-4 EEL =    2478.8506  VDWAALS    =    -765.6043
 EELEC  =   -3256.3073  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.1108  VIRIAL  =     267.0938  VOLUME     =   17318.5050
                                                Density    =       0.8750
 Ewald error estimate:   0.3891E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 274000 TIME(PS) =   274.000  TEMP(K) =   363.41  PRESS =  -150.8
 Etot   =     961.0255  EKtot   =    1307.8264  EPtot      =    -346.8009
 BOND   =     225.0684  ANGLE   =     729.2328  DIHED      =     138.7742
 1-4 NB =     159.4207  1-4 EEL =    2464.2177  VDWAALS    =    -756.2861
 EELEC  =   -3307.2286  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.7765  VIRIAL  =     188.6655  VOLUME     =   17168.5682
                                                Density    =       0.8827
 Ewald error estimate:   0.1032E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 275000 TIME(PS) =   275.000  TEMP(K) =   384.81  PRESS =  -756.4
 Etot   =     949.0790  EKtot   =    1384.8722  EPtot      =    -435.7931
 BOND   =     201.1777  ANGLE   =     692.3906  DIHED      =     133.0008
 1-4 NB =     159.1688  1-4 EEL =    2474.9238  VDWAALS    =    -787.6879
 EELEC  =   -3308.7669  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.8960  VIRIAL  =     427.0690  VOLUME     =   17033.6502
                                                Density    =       0.8897
 Ewald error estimate:   0.2724E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 276000 TIME(PS) =   276.000  TEMP(K) =   390.28  PRESS =    19.9
 Etot   =     937.1658  EKtot   =    1404.5509  EPtot      =    -467.3852
 BOND   =     192.9969  ANGLE   =     650.5087  DIHED      =     129.8894
 1-4 NB =     163.2032  1-4 EEL =    2484.5334  VDWAALS    =    -785.1863
 EELEC  =   -3303.3304  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.9009  VIRIAL  =     140.6625  VOLUME     =   16864.5830
                                                Density    =       0.8986
 Ewald error estimate:   0.1720E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 277000 TIME(PS) =   277.000  TEMP(K) =   365.51  PRESS =  -311.1
 Etot   =     942.6145  EKtot   =    1315.3944  EPtot      =    -372.7799
 BOND   =     211.5949  ANGLE   =     697.7037  DIHED      =     124.8095
 1-4 NB =     161.4992  1-4 EEL =    2469.5728  VDWAALS    =    -762.4187
 EELEC  =   -3275.5413  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.4425  VIRIAL  =     240.4978  VOLUME     =   17278.1964
                                                Density    =       0.8771
 Ewald error estimate:   0.1653E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 278000 TIME(PS) =   278.000  TEMP(K) =   369.71  PRESS =  -252.7
 Etot   =     943.3787  EKtot   =    1330.5259  EPtot      =    -387.1472
 BOND   =     207.9683  ANGLE   =     706.6650  DIHED      =     129.3086
 1-4 NB =     156.7843  1-4 EEL =    2472.6002  VDWAALS    =    -756.6488
 EELEC  =   -3303.8248  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.5543  VIRIAL  =     233.3248  VOLUME     =   17182.9590
                                                Density    =       0.8819
 Ewald error estimate:   0.1357E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 279000 TIME(PS) =   279.000  TEMP(K) =   365.55  PRESS =  -209.4
 Etot   =     953.8363  EKtot   =    1315.5406  EPtot      =    -361.7043
 BOND   =     211.9761  ANGLE   =     692.5905  DIHED      =     136.0553
 1-4 NB =     161.1782  1-4 EEL =    2467.6708  VDWAALS    =    -743.7485
 EELEC  =   -3287.4267  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.4582  VIRIAL  =     210.8919  VOLUME     =   17570.1669
                                                Density    =       0.8625
 Ewald error estimate:   0.4877E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 280000 TIME(PS) =   280.000  TEMP(K) =   375.16  PRESS =   -25.4
 Etot   =     956.6663  EKtot   =    1350.1251  EPtot      =    -393.4588
 BOND   =     204.0796  ANGLE   =     653.6893  DIHED      =     131.1421
 1-4 NB =     168.8192  1-4 EEL =    2486.5542  VDWAALS    =    -745.0255
 EELEC  =   -3292.7176  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     152.6835  VIRIAL  =     162.3264  VOLUME     =   17572.5631
                                                Density    =       0.8624
 Ewald error estimate:   0.1072E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 281000 TIME(PS) =   281.000  TEMP(K) =   370.80  PRESS =   285.2
 Etot   =     954.2855  EKtot   =    1334.4467  EPtot      =    -380.1613
 BOND   =     204.9903  ANGLE   =     668.2910  DIHED      =     138.3141
 1-4 NB =     167.6105  1-4 EEL =    2474.2105  VDWAALS    =    -744.3592
 EELEC  =   -3289.2185  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     105.9430  VIRIAL  =      -0.2295  VOLUME     =   17240.2028
                                                Density    =       0.8790
 Ewald error estimate:   0.8211E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 282000 TIME(PS) =   282.000  TEMP(K) =   370.36  PRESS =  -139.1
 Etot   =     955.8464  EKtot   =    1332.8616  EPtot      =    -377.0153
 BOND   =     197.2301  ANGLE   =     663.8436  DIHED      =     152.2824
 1-4 NB =     167.5778  1-4 EEL =    2488.4606  VDWAALS    =    -745.5472
 EELEC  =   -3300.8625  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.8893  VIRIAL  =     188.8353  VOLUME     =   17296.1630
                                                Density    =       0.8762
 Ewald error estimate:   0.1866E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 283000 TIME(PS) =   283.000  TEMP(K) =   363.42  PRESS =   617.6
 Etot   =     958.1757  EKtot   =    1307.8841  EPtot      =    -349.7084
 BOND   =     210.2245  ANGLE   =     683.5088  DIHED      =     145.9741
 1-4 NB =     166.1867  1-4 EEL =    2465.6943  VDWAALS    =    -730.4052
 EELEC  =   -3290.8916  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     108.6255  VIRIAL  =    -121.6619  VOLUME     =   17270.2027
                                                Density    =       0.8775
 Ewald error estimate:   0.1329E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 284000 TIME(PS) =   284.000  TEMP(K) =   369.19  PRESS =  -282.4
 Etot   =     966.3328  EKtot   =    1328.6306  EPtot      =    -362.2978
 BOND   =     197.8859  ANGLE   =     694.6261  DIHED      =     120.7761
 1-4 NB =     163.7864  1-4 EEL =    2478.7861  VDWAALS    =    -769.2013
 EELEC  =   -3248.9571  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.6589  VIRIAL  =     243.2246  VOLUME     =   17311.0162
                                                Density    =       0.8754
 Ewald error estimate:   0.7929E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 285000 TIME(PS) =   285.000  TEMP(K) =   369.72  PRESS =  -597.9
 Etot   =     971.7400  EKtot   =    1330.5326  EPtot      =    -358.7926
 BOND   =     208.9418  ANGLE   =     672.7950  DIHED      =     136.0187
 1-4 NB =     177.4399  1-4 EEL =    2483.6173  VDWAALS    =    -762.3974
 EELEC  =   -3275.2078  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.2289  VIRIAL  =     365.6874  VOLUME     =   17308.8889
                                                Density    =       0.8755
 Ewald error estimate:   0.1639E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 286000 TIME(PS) =   286.000  TEMP(K) =   371.22  PRESS =  -392.3
 Etot   =     974.8632  EKtot   =    1335.9417  EPtot      =    -361.0785
 BOND   =     190.1628  ANGLE   =     690.0891  DIHED      =     169.0107
 1-4 NB =     152.2938  1-4 EEL =    2465.3203  VDWAALS    =    -776.4086
 EELEC  =   -3251.5465  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.0355  VIRIAL  =     284.1749  VOLUME     =   17254.3087
                                                Density    =       0.8783
 Ewald error estimate:   0.1491E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 287000 TIME(PS) =   287.000  TEMP(K) =   371.36  PRESS =    74.5
 Etot   =     977.0054  EKtot   =    1336.4351  EPtot      =    -359.4297
 BOND   =     193.1801  ANGLE   =     684.7757  DIHED      =     156.0903
 1-4 NB =     161.9935  1-4 EEL =    2470.2672  VDWAALS    =    -753.1887
 EELEC  =   -3272.5479  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.3838  VIRIAL  =      99.5356  VOLUME     =   17310.8891
                                                Density    =       0.8754
 Ewald error estimate:   0.2710E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 288000 TIME(PS) =   288.000  TEMP(K) =   377.38  PRESS =  -337.9
 Etot   =     967.1921  EKtot   =    1358.1209  EPtot      =    -390.9288
 BOND   =     218.0339  ANGLE   =     667.8811  DIHED      =     129.3311
 1-4 NB =     172.0916  1-4 EEL =    2476.4223  VDWAALS    =    -754.0867
 EELEC  =   -3300.6022  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.9890  VIRIAL  =     265.5002  VOLUME     =   17205.8968
                                                Density    =       0.8808
 Ewald error estimate:   0.1383E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 289000 TIME(PS) =   289.000  TEMP(K) =   383.28  PRESS =    52.8
 Etot   =     954.4324  EKtot   =    1379.3501  EPtot      =    -424.9177
 BOND   =     206.0684  ANGLE   =     650.6926  DIHED      =     134.9182
 1-4 NB =     151.6080  1-4 EEL =    2465.0551  VDWAALS    =    -753.2563
 EELEC  =   -3280.0037  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.4334  VIRIAL  =     128.6651  VOLUME     =   17331.2527
                                                Density    =       0.8744
 Ewald error estimate:   0.1513E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 290000 TIME(PS) =   290.000  TEMP(K) =   371.34  PRESS =    24.7
 Etot   =     954.1186  EKtot   =    1336.3826  EPtot      =    -382.2641
 BOND   =     202.9495  ANGLE   =     665.4604  DIHED      =     131.8617
 1-4 NB =     174.7162  1-4 EEL =    2482.2524  VDWAALS    =    -739.0033
 EELEC  =   -3300.5010  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.2807  VIRIAL  =     137.9701  VOLUME     =   17491.1187
                                                Density    =       0.8664
 Ewald error estimate:   0.1596E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 291000 TIME(PS) =   291.000  TEMP(K) =   372.71  PRESS =  -349.2
 Etot   =     962.7254  EKtot   =    1341.3065  EPtot      =    -378.5810
 BOND   =     185.0691  ANGLE   =     684.8096  DIHED      =     149.0296
 1-4 NB =     163.4248  1-4 EEL =    2477.0232  VDWAALS    =    -755.8706
 EELEC  =   -3282.0667  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.0277  VIRIAL  =     266.4540  VOLUME     =   17430.0261
                                                Density    =       0.8694
 Ewald error estimate:   0.2232E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 292000 TIME(PS) =   292.000  TEMP(K) =   365.46  PRESS =   161.7
 Etot   =     962.9529  EKtot   =    1315.2279  EPtot      =    -352.2750
 BOND   =     204.2788  ANGLE   =     681.3473  DIHED      =     141.1182
 1-4 NB =     166.7110  1-4 EEL =    2478.1002  VDWAALS    =    -756.8819
 EELEC  =   -3266.9487  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.0864  VIRIAL  =      69.9300  VOLUME     =   17226.9462
                                                Density    =       0.8797
 Ewald error estimate:   0.3328E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 293000 TIME(PS) =   293.000  TEMP(K) =   375.87  PRESS =   105.1
 Etot   =     952.9460  EKtot   =    1352.6738  EPtot      =    -399.7278
 BOND   =     195.7140  ANGLE   =     684.4933  DIHED      =     138.5235
 1-4 NB =     160.8273  1-4 EEL =    2475.1427  VDWAALS    =    -735.9937
 EELEC  =   -3318.4348  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     153.8448  VIRIAL  =     113.9880  VOLUME     =   17567.5500
                                                Density    =       0.8626
 Ewald error estimate:   0.1038E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 294000 TIME(PS) =   294.000  TEMP(K) =   372.06  PRESS =   -26.1
 Etot   =     957.4849  EKtot   =    1338.9727  EPtot      =    -381.4878
 BOND   =     186.7061  ANGLE   =     643.0163  DIHED      =     144.1690
 1-4 NB =     169.9325  1-4 EEL =    2477.4898  VDWAALS    =    -717.5177
 EELEC  =   -3285.2838  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.5798  VIRIAL  =     141.5439  VOLUME     =   17673.0004
                                                Density    =       0.8575
 Ewald error estimate:   0.2069E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 295000 TIME(PS) =   295.000  TEMP(K) =   364.40  PRESS =   128.4
 Etot   =     963.4192  EKtot   =    1311.3894  EPtot      =    -347.9702
 BOND   =     190.4965  ANGLE   =     710.9125  DIHED      =     139.0098
 1-4 NB =     162.2248  1-4 EEL =    2470.3947  VDWAALS    =    -745.5166
 EELEC  =   -3275.4918  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.9592  VIRIAL  =      91.8298  VOLUME     =   17360.5713
                                                Density    =       0.8729
 Ewald error estimate:   0.2084E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 296000 TIME(PS) =   296.000  TEMP(K) =   363.33  PRESS =  -461.0
 Etot   =     962.6674  EKtot   =    1307.5685  EPtot      =    -344.9011
 BOND   =     225.1641  ANGLE   =     694.1607  DIHED      =     145.0228
 1-4 NB =     166.8184  1-4 EEL =    2462.8291  VDWAALS    =    -761.4794
 EELEC  =   -3277.4166  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.2656  VIRIAL  =     312.6856  VOLUME     =   17223.0857
                                                Density    =       0.8799
 Ewald error estimate:   0.4127E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 297000 TIME(PS) =   297.000  TEMP(K) =   369.08  PRESS =  -396.2
 Etot   =     968.5729  EKtot   =    1328.2456  EPtot      =    -359.6727
 BOND   =     225.2947  ANGLE   =     673.5916  DIHED      =     154.2851
 1-4 NB =     156.0193  1-4 EEL =    2458.5981  VDWAALS    =    -772.0355
 EELEC  =   -3255.4259  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.7229  VIRIAL  =     290.2958  VOLUME     =   17250.1685
                                                Density    =       0.8785
 Ewald error estimate:   0.7663E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 298000 TIME(PS) =   298.000  TEMP(K) =   363.47  PRESS =   -14.7
 Etot   =     965.0742  EKtot   =    1308.0686  EPtot      =    -342.9944
 BOND   =     215.7743  ANGLE   =     677.5802  DIHED      =     145.1228
 1-4 NB =     160.1941  1-4 EEL =    2463.6770  VDWAALS    =    -748.1512
 EELEC  =   -3257.1916  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.8767  VIRIAL  =     129.4034  VOLUME     =   17366.7056
                                                Density    =       0.8726
 Ewald error estimate:   0.1301E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 299000 TIME(PS) =   299.000  TEMP(K) =   373.40  PRESS =    55.9
 Etot   =     962.0853  EKtot   =    1343.7756  EPtot      =    -381.6903
 BOND   =     207.0339  ANGLE   =     676.1176  DIHED      =     131.4206
 1-4 NB =     157.2364  1-4 EEL =    2481.5123  VDWAALS    =    -750.4863
 EELEC  =   -3284.5246  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.7231  VIRIAL  =     114.9099  VOLUME     =   17241.2586
                                                Density    =       0.8790
 Ewald error estimate:   0.2517E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 300000 TIME(PS) =   300.000  TEMP(K) =   377.26  PRESS =   104.9
 Etot   =     954.0186  EKtot   =    1357.6966  EPtot      =    -403.6780
 BOND   =     203.1847  ANGLE   =     694.6381  DIHED      =     128.3536
 1-4 NB =     149.1830  1-4 EEL =    2459.3291  VDWAALS    =    -764.6779
 EELEC  =   -3273.6886  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     119.4968  VIRIAL  =      80.8001  VOLUME     =   17081.7046
                                                Density    =       0.8872
 Ewald error estimate:   0.5929E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 301000 TIME(PS) =   301.000  TEMP(K) =   363.73  PRESS =  -430.1
 Etot   =     956.8209  EKtot   =    1308.9796  EPtot      =    -352.1587
 BOND   =     210.1344  ANGLE   =     718.7670  DIHED      =     143.5367
 1-4 NB =     164.8667  1-4 EEL =    2468.6029  VDWAALS    =    -775.7631
 EELEC  =   -3282.3033  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.9778  VIRIAL  =     294.5242  VOLUME     =   17181.5362
                                                Density    =       0.8820
 Ewald error estimate:   0.3423E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 302000 TIME(PS) =   302.000  TEMP(K) =   379.19  PRESS =     1.8
 Etot   =     949.5666  EKtot   =    1364.6415  EPtot      =    -415.0749
 BOND   =     197.8405  ANGLE   =     677.6719  DIHED      =     132.7874
 1-4 NB =     162.5980  1-4 EEL =    2473.2160  VDWAALS    =    -764.2580
 EELEC  =   -3294.9307  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.9533  VIRIAL  =     139.2931  VOLUME     =   17120.5970
                                                Density    =       0.8852
 Ewald error estimate:   0.3459E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 303000 TIME(PS) =   303.000  TEMP(K) =   378.62  PRESS =  -126.5
 Etot   =     948.1670  EKtot   =    1362.5827  EPtot      =    -414.4157
 BOND   =     203.4768  ANGLE   =     678.0887  DIHED      =     131.7549
 1-4 NB =     164.0173  1-4 EEL =    2471.8187  VDWAALS    =    -783.4365
 EELEC  =   -3280.1355  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.1249  VIRIAL  =     195.4991  VOLUME     =   16981.9499
                                                Density    =       0.8924
 Ewald error estimate:   0.2075E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 304000 TIME(PS) =   304.000  TEMP(K) =   368.45  PRESS =   377.1
 Etot   =     943.7038  EKtot   =    1325.9634  EPtot      =    -382.2596
 BOND   =     193.3977  ANGLE   =     720.8899  DIHED      =     132.1787
 1-4 NB =     150.4265  1-4 EEL =    2443.4170  VDWAALS    =    -783.1808
 EELEC  =   -3239.3887  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.1988  VIRIAL  =      -4.3914  VOLUME     =   16898.4622
                                                Density    =       0.8968
 Ewald error estimate:   0.3329E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 305000 TIME(PS) =   305.000  TEMP(K) =   371.36  PRESS =  -259.3
 Etot   =     946.3209  EKtot   =    1336.4343  EPtot      =    -390.1134
 BOND   =     204.5685  ANGLE   =     707.7409  DIHED      =     133.4992
 1-4 NB =     159.0644  1-4 EEL =    2460.4264  VDWAALS    =    -778.0072
 EELEC  =   -3277.4056  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.3404  VIRIAL  =     230.5823  VOLUME     =   17010.0975
                                                Density    =       0.8909
 Ewald error estimate:   0.2666E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 306000 TIME(PS) =   306.000  TEMP(K) =   370.33  PRESS =   253.6
 Etot   =     946.9415  EKtot   =    1332.7305  EPtot      =    -385.7890
 BOND   =     201.8450  ANGLE   =     697.0072  DIHED      =     143.5045
 1-4 NB =     155.7299  1-4 EEL =    2468.9828  VDWAALS    =    -766.1123
 EELEC  =   -3286.7461  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.6584  VIRIAL  =      45.2819  VOLUME     =   17050.8924
                                                Density    =       0.8888
 Ewald error estimate:   0.2147E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 307000 TIME(PS) =   307.000  TEMP(K) =   364.03  PRESS =   569.2
 Etot   =     954.6940  EKtot   =    1310.0849  EPtot      =    -355.3909
 BOND   =     194.1443  ANGLE   =     671.8136  DIHED      =     165.8588
 1-4 NB =     170.9092  1-4 EEL =    2466.1228  VDWAALS    =    -745.5250
 EELEC  =   -3278.7146  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.2081  VIRIAL  =     -81.6673  VOLUME     =   17238.6586
                                                Density    =       0.8791
 Ewald error estimate:   0.1472E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 308000 TIME(PS) =   308.000  TEMP(K) =   378.03  PRESS =   -18.7
 Etot   =     955.9828  EKtot   =    1360.4596  EPtot      =    -404.4768
 BOND   =     200.7487  ANGLE   =     681.3403  DIHED      =     136.5999
 1-4 NB =     155.8083  1-4 EEL =    2469.7661  VDWAALS    =    -771.4182
 EELEC  =   -3277.3219  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.6449  VIRIAL  =     136.5458  VOLUME     =   17091.5654
                                                Density    =       0.8867
 Ewald error estimate:   0.3335E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 309000 TIME(PS) =   309.000  TEMP(K) =   361.78  PRESS =   228.7
 Etot   =     953.9569  EKtot   =    1301.9748  EPtot      =    -348.0179
 BOND   =     199.1213  ANGLE   =     695.8118  DIHED      =     142.8702
 1-4 NB =     166.1720  1-4 EEL =    2473.9280  VDWAALS    =    -740.3386
 EELEC  =   -3285.5827  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.0723  VIRIAL  =      58.0057  VOLUME     =   17430.1761
                                                Density    =       0.8694
 Ewald error estimate:   0.5237E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 310000 TIME(PS) =   310.000  TEMP(K) =   370.60  PRESS =   -84.6
 Etot   =     960.0321  EKtot   =    1333.7338  EPtot      =    -373.7017
 BOND   =     201.9120  ANGLE   =     657.1505  DIHED      =     133.9291
 1-4 NB =     178.6270  1-4 EEL =    2486.5995  VDWAALS    =    -741.7935
 EELEC  =   -3290.1264  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.1248  VIRIAL  =     171.2155  VOLUME     =   17576.7501
                                                Density    =       0.8622
 Ewald error estimate:   0.1641E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 311000 TIME(PS) =   311.000  TEMP(K) =   373.06  PRESS =   204.4
 Etot   =     962.2711  EKtot   =    1342.5829  EPtot      =    -380.3118
 BOND   =     193.0636  ANGLE   =     685.5538  DIHED      =     133.3262
 1-4 NB =     157.7796  1-4 EEL =    2460.9247  VDWAALS    =    -736.8179
 EELEC  =   -3274.1418  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.1399  VIRIAL  =      56.0018  VOLUME     =   17476.8727
                                                Density    =       0.8671
 Ewald error estimate:   0.7075E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 312000 TIME(PS) =   312.000  TEMP(K) =   382.26  PRESS =  -569.2
 Etot   =     969.8553  EKtot   =    1375.6697  EPtot      =    -405.8144
 BOND   =     192.4258  ANGLE   =     652.9827  DIHED      =     139.8678
 1-4 NB =     161.8388  1-4 EEL =    2483.1347  VDWAALS    =    -759.4004
 EELEC  =   -3276.6638  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.6555  VIRIAL  =     349.9167  VOLUME     =   17435.2391
                                                Density    =       0.8692
 Ewald error estimate:   0.5112E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 313000 TIME(PS) =   313.000  TEMP(K) =   373.43  PRESS =   330.8
 Etot   =     961.6987  EKtot   =    1343.9040  EPtot      =    -382.2054
 BOND   =     204.4135  ANGLE   =     695.5236  DIHED      =     138.5359
 1-4 NB =     142.4852  1-4 EEL =    2441.0010  VDWAALS    =    -737.7373
 EELEC  =   -3266.4272  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     114.7002  VIRIAL  =      -9.6181  VOLUME     =   17406.1698
                                                Density    =       0.8706
 Ewald error estimate:   0.2226E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 314000 TIME(PS) =   314.000  TEMP(K) =   374.47  PRESS =   220.5
 Etot   =     965.8627  EKtot   =    1347.6401  EPtot      =    -381.7773
 BOND   =     193.7937  ANGLE   =     683.6536  DIHED      =     143.5368
 1-4 NB =     154.3710  1-4 EEL =    2466.4507  VDWAALS    =    -754.7155
 EELEC  =   -3268.8677  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.9189  VIRIAL  =      66.5287  VOLUME     =   17302.0038
                                                Density    =       0.8759
 Ewald error estimate:   0.1140E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 315000 TIME(PS) =   315.000  TEMP(K) =   371.97  PRESS =   -52.1
 Etot   =     971.1546  EKtot   =    1338.6480  EPtot      =    -367.4935
 BOND   =     212.1509  ANGLE   =     651.4487  DIHED      =     145.9217
 1-4 NB =     151.8040  1-4 EEL =    2450.9212  VDWAALS    =    -747.7197
 EELEC  =   -3232.0204  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.4381  VIRIAL  =     156.1191  VOLUME     =   17507.9582
                                                Density    =       0.8656
 Ewald error estimate:   0.1118E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 316000 TIME(PS) =   316.000  TEMP(K) =   369.39  PRESS =  -555.6
 Etot   =     987.7027  EKtot   =    1329.3624  EPtot      =    -341.6597
 BOND   =     210.8258  ANGLE   =     691.3651  DIHED      =     131.4372
 1-4 NB =     153.3838  1-4 EEL =    2457.2678  VDWAALS    =    -752.2446
 EELEC  =   -3233.6949  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.5270  VIRIAL  =     352.5350  VOLUME     =   17589.0861
                                                Density    =       0.8616
 Ewald error estimate:   0.1127E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 317000 TIME(PS) =   317.000  TEMP(K) =   371.61  PRESS =   207.2
 Etot   =     986.0956  EKtot   =    1337.3427  EPtot      =    -351.2471
 BOND   =     200.4928  ANGLE   =     704.0386  DIHED      =     136.0140
 1-4 NB =     154.3945  1-4 EEL =    2446.4838  VDWAALS    =    -739.2303
 EELEC  =   -3253.4405  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.2404  VIRIAL  =      67.7579  VOLUME     =   17544.2219
                                                Density    =       0.8638
 Ewald error estimate:   0.1937E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 318000 TIME(PS) =   318.000  TEMP(K) =   371.26  PRESS =  -247.1
 Etot   =     981.1114  EKtot   =    1336.1019  EPtot      =    -354.9905
 BOND   =     218.3747  ANGLE   =     673.3894  DIHED      =     144.7121
 1-4 NB =     150.5921  1-4 EEL =    2467.0318  VDWAALS    =    -764.0074
 EELEC  =   -3245.0831  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.4680  VIRIAL  =     230.3342  VOLUME     =   17405.8912
                                                Density    =       0.8706
 Ewald error estimate:   0.7862E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 319000 TIME(PS) =   319.000  TEMP(K) =   382.53  PRESS =  -874.7
 Etot   =     976.4545  EKtot   =    1376.6668  EPtot      =    -400.2123
 BOND   =     202.4048  ANGLE   =     678.1361  DIHED      =     130.9873
 1-4 NB =     167.0697  1-4 EEL =    2465.3919  VDWAALS    =    -775.6158
 EELEC  =   -3268.5863  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     154.2586  VIRIAL  =     480.5912  VOLUME     =   17279.9833
                                                Density    =       0.8770
 Ewald error estimate:   0.1738E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 320000 TIME(PS) =   320.000  TEMP(K) =   383.75  PRESS =   -91.5
 Etot   =     963.9160  EKtot   =    1381.0475  EPtot      =    -417.1315
 BOND   =     188.9619  ANGLE   =     660.0171  DIHED      =     148.0610
 1-4 NB =     163.6336  1-4 EEL =    2467.4537  VDWAALS    =    -770.8629
 EELEC  =   -3274.3961  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.7609  VIRIAL  =     172.7389  VOLUME     =   17203.9336
                                                Density    =       0.8809
 Ewald error estimate:   0.3079E-06
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 321000 TIME(PS) =   321.000  TEMP(K) =   373.21  PRESS =   255.0
 Etot   =     959.9404  EKtot   =    1343.1045  EPtot      =    -383.1641
 BOND   =     203.2838  ANGLE   =     675.9469  DIHED      =     126.6541
 1-4 NB =     156.6417  1-4 EEL =    2477.8394  VDWAALS    =    -753.6047
 EELEC  =   -3269.9253  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.6622  VIRIAL  =      55.1720  VOLUME     =   17163.2778
                                                Density    =       0.8830
 Ewald error estimate:   0.9308E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 322000 TIME(PS) =   322.000  TEMP(K) =   361.25  PRESS =    50.8
 Etot   =     963.3238  EKtot   =    1300.0574  EPtot      =    -336.7335
 BOND   =     212.9542  ANGLE   =     682.9479  DIHED      =     145.0639
 1-4 NB =     166.5605  1-4 EEL =    2479.8031  VDWAALS    =    -757.9307
 EELEC  =   -3266.1325  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.0029  VIRIAL  =     123.1539  VOLUME     =   17171.1176
                                                Density    =       0.8825
 Ewald error estimate:   0.4547E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 323000 TIME(PS) =   323.000  TEMP(K) =   377.47  PRESS =   401.7
 Etot   =     964.1559  EKtot   =    1358.4370  EPtot      =    -394.2812
 BOND   =     179.2901  ANGLE   =     685.4330  DIHED      =     148.1121
 1-4 NB =     166.0921  1-4 EEL =    2472.8057  VDWAALS    =    -755.8704
 EELEC  =   -3290.1438  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.7724  VIRIAL  =      -5.3884  VOLUME     =   17080.6119
                                                Density    =       0.8872
 Ewald error estimate:   0.4069E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 324000 TIME(PS) =   324.000  TEMP(K) =   366.68  PRESS =  -131.1
 Etot   =     957.6097  EKtot   =    1319.6031  EPtot      =    -361.9933
 BOND   =     176.7996  ANGLE   =     713.1885  DIHED      =     160.8161
 1-4 NB =     162.2262  1-4 EEL =    2462.5826  VDWAALS    =    -768.1818
 EELEC  =   -3269.4245  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     120.0883  VIRIAL  =     168.5830  VOLUME     =   17127.2140
                                                Density    =       0.8848
 Ewald error estimate:   0.1944E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 325000 TIME(PS) =   325.000  TEMP(K) =   368.29  PRESS =   340.5
 Etot   =     953.7176  EKtot   =    1325.4194  EPtot      =    -371.7018
 BOND   =     190.9861  ANGLE   =     682.2402  DIHED      =     151.1809
 1-4 NB =     165.1483  1-4 EEL =    2482.9108  VDWAALS    =    -738.6442
 EELEC  =   -3305.5239  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.8545  VIRIAL  =       7.5237  VOLUME     =   17182.1191
                                                Density    =       0.8820
 Ewald error estimate:   0.3073E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 326000 TIME(PS) =   326.000  TEMP(K) =   377.64  PRESS =   -12.4
 Etot   =     958.1547  EKtot   =    1359.0411  EPtot      =    -400.8864
 BOND   =     206.0523  ANGLE   =     664.6594  DIHED      =     136.7067
 1-4 NB =     157.5683  1-4 EEL =    2466.6054  VDWAALS    =    -749.8038
 EELEC  =   -3282.6748  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.1389  VIRIAL  =     151.8043  VOLUME     =   17385.8754
                                                Density    =       0.8716
 Ewald error estimate:   0.1553E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 327000 TIME(PS) =   327.000  TEMP(K) =   359.44  PRESS =   314.1
 Etot   =     961.6490  EKtot   =    1293.5537  EPtot      =    -331.9047
 BOND   =     200.9712  ANGLE   =     698.1756  DIHED      =     161.9228
 1-4 NB =     165.6672  1-4 EEL =    2475.8179  VDWAALS    =    -733.8228
 EELEC  =   -3300.6366  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.1263  VIRIAL  =       8.2413  VOLUME     =   17384.5359
                                                Density    =       0.8717
 Ewald error estimate:   0.5211E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 328000 TIME(PS) =   328.000  TEMP(K) =   369.78  PRESS =   195.6
 Etot   =     961.1135  EKtot   =    1330.7765  EPtot      =    -369.6630
 BOND   =     208.3382  ANGLE   =     668.9479  DIHED      =     142.7233
 1-4 NB =     161.3578  1-4 EEL =    2461.4768  VDWAALS    =    -734.5450
 EELEC  =   -3277.9620  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.5247  VIRIAL  =      60.9658  VOLUME     =   17419.8740
                                                Density    =       0.8699
 Ewald error estimate:   0.9581E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 329000 TIME(PS) =   329.000  TEMP(K) =   368.51  PRESS =  -144.2
 Etot   =     970.3384  EKtot   =    1326.1842  EPtot      =    -355.8458
 BOND   =     196.9682  ANGLE   =     677.2134  DIHED      =     159.0051
 1-4 NB =     165.4077  1-4 EEL =    2475.1036  VDWAALS    =    -762.9201
 EELEC  =   -3266.6238  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     122.8472  VIRIAL  =     176.8084  VOLUME     =   17328.8337
                                                Density    =       0.8745
 Ewald error estimate:   0.3352E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 330000 TIME(PS) =   330.000  TEMP(K) =   372.17  PRESS =   261.9
 Etot   =     969.3982  EKtot   =    1339.3803  EPtot      =    -369.9821
 BOND   =     209.5405  ANGLE   =     659.4710  DIHED      =     160.8551
 1-4 NB =     163.0389  1-4 EEL =    2474.7321  VDWAALS    =    -744.3435
 EELEC  =   -3293.2762  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.9658  VIRIAL  =      33.7318  VOLUME     =   17197.1900
                                                Density    =       0.8812
 Ewald error estimate:   0.1764E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 331000 TIME(PS) =   331.000  TEMP(K) =   374.79  PRESS =    19.4
 Etot   =     967.3358  EKtot   =    1348.8107  EPtot      =    -381.4749
 BOND   =     185.8587  ANGLE   =     669.5919  DIHED      =     123.7412
 1-4 NB =     171.2436  1-4 EEL =    2490.1940  VDWAALS    =    -760.0713
 EELEC  =   -3262.0331  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.0634  VIRIAL  =     137.8767  VOLUME     =   17134.8793
                                                Density    =       0.8844
 Ewald error estimate:   0.1150E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 332000 TIME(PS) =   332.000  TEMP(K) =   371.23  PRESS =   123.1
 Etot   =     970.0336  EKtot   =    1335.9851  EPtot      =    -365.9514
 BOND   =     197.1263  ANGLE   =     660.3914  DIHED      =     143.7525
 1-4 NB =     181.6372  1-4 EEL =    2490.2277  VDWAALS    =    -739.4249
 EELEC  =   -3299.6616  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     154.6713  VIRIAL  =     108.7009  VOLUME     =   17289.3196
                                                Density    =       0.8765
 Ewald error estimate:   0.3349E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 333000 TIME(PS) =   333.000  TEMP(K) =   372.49  PRESS =  -125.3
 Etot   =     972.2150  EKtot   =    1340.5152  EPtot      =    -368.3002
 BOND   =     206.4975  ANGLE   =     675.8068  DIHED      =     136.4383
 1-4 NB =     162.6868  1-4 EEL =    2476.7535  VDWAALS    =    -734.9517
 EELEC  =   -3291.5315  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     161.6880  VIRIAL  =     209.2321  VOLUME     =   17568.2157
                                                Density    =       0.8626
 Ewald error estimate:   0.2111E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 334000 TIME(PS) =   334.000  TEMP(K) =   367.21  PRESS =   -25.8
 Etot   =     970.5349  EKtot   =    1321.5032  EPtot      =    -350.9683
 BOND   =     209.3145  ANGLE   =     702.3227  DIHED      =     141.3612
 1-4 NB =     155.4433  1-4 EEL =    2458.4108  VDWAALS    =    -758.0343
 EELEC  =   -3259.7866  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.8511  VIRIAL  =     150.5466  VOLUME     =   17402.6202
                                                Density    =       0.8708
 Ewald error estimate:   0.2387E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 335000 TIME(PS) =   335.000  TEMP(K) =   377.59  PRESS =   -98.6
 Etot   =     974.9542  EKtot   =    1358.8798  EPtot      =    -383.9256
 BOND   =     183.2901  ANGLE   =     662.3562  DIHED      =     129.8945
 1-4 NB =     167.1183  1-4 EEL =    2472.8288  VDWAALS    =    -730.6130
 EELEC  =   -3268.8004  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     150.1429  VIRIAL  =     187.7836  VOLUME     =   17683.5811
                                                Density    =       0.8570
 Ewald error estimate:   0.3590E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 336000 TIME(PS) =   336.000  TEMP(K) =   370.25  PRESS =    97.7
 Etot   =     971.3054  EKtot   =    1332.4737  EPtot      =    -361.1683
 BOND   =     195.6485  ANGLE   =     696.1749  DIHED      =     135.2057
 1-4 NB =     154.9603  1-4 EEL =    2454.7734  VDWAALS    =    -758.1538
 EELEC  =   -3239.7774  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.5699  VIRIAL  =      91.9474  VOLUME     =   17365.3962
                                                Density    =       0.8727
 Ewald error estimate:   0.1319E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 337000 TIME(PS) =   337.000  TEMP(K) =   364.64  PRESS =  -388.5
 Etot   =     968.3109  EKtot   =    1312.2682  EPtot      =    -343.9573
 BOND   =     209.5456  ANGLE   =     690.7435  DIHED      =     143.2305
 1-4 NB =     162.8298  1-4 EEL =    2469.1966  VDWAALS    =    -753.3358
 EELEC  =   -3266.1675  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.1063  VIRIAL  =     281.1890  VOLUME     =   17296.4529
                                                Density    =       0.8762
 Ewald error estimate:   0.6356E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 338000 TIME(PS) =   338.000  TEMP(K) =   377.74  PRESS =  -474.6
 Etot   =     970.4662  EKtot   =    1359.4298  EPtot      =    -388.9637
 BOND   =     200.5967  ANGLE   =     671.4508  DIHED      =     138.3280
 1-4 NB =     165.1046  1-4 EEL =    2478.3583  VDWAALS    =    -754.0423
 EELEC  =   -3288.7599  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.7445  VIRIAL  =     321.1789  VOLUME     =   17411.8618
                                                Density    =       0.8703
 Ewald error estimate:   0.8922E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 339000 TIME(PS) =   339.000  TEMP(K) =   370.49  PRESS =   362.8
 Etot   =     961.9975  EKtot   =    1333.3256  EPtot      =    -371.3281
 BOND   =     212.3394  ANGLE   =     686.3210  DIHED      =     160.4071
 1-4 NB =     163.6382  1-4 EEL =    2468.5400  VDWAALS    =    -726.7231
 EELEC  =   -3335.8507  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.6017  VIRIAL  =      -8.3348  VOLUME     =   17351.4932
                                                Density    =       0.8734
 Ewald error estimate:   0.4401E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 340000 TIME(PS) =   340.000  TEMP(K) =   376.39  PRESS =  -175.8
 Etot   =     955.3995  EKtot   =    1354.5607  EPtot      =    -399.1612
 BOND   =     181.6811  ANGLE   =     686.6216  DIHED      =     138.2958
 1-4 NB =     167.0894  1-4 EEL =    2469.2643  VDWAALS    =    -766.0054
 EELEC  =   -3276.1078  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     151.4155  VIRIAL  =     216.6032  VOLUME     =   17175.5540
                                                Density    =       0.8823
 Ewald error estimate:   0.1055E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 341000 TIME(PS) =   341.000  TEMP(K) =   390.54  PRESS =   -88.2
 Etot   =     951.9801  EKtot   =    1405.4592  EPtot      =    -453.4791
 BOND   =     197.6358  ANGLE   =     659.7369  DIHED      =     123.4894
 1-4 NB =     151.7223  1-4 EEL =    2461.3598  VDWAALS    =    -789.4454
 EELEC  =   -3257.9779  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.2949  VIRIAL  =     174.5032  VOLUME     =   16909.2902
                                                Density    =       0.8962
 Ewald error estimate:   0.2529E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 342000 TIME(PS) =   342.000  TEMP(K) =   366.78  PRESS =   550.3
 Etot   =     948.6307  EKtot   =    1319.9791  EPtot      =    -371.3484
 BOND   =     217.0095  ANGLE   =     694.2301  DIHED      =     131.3543
 1-4 NB =     158.4575  1-4 EEL =    2472.7734  VDWAALS    =    -764.5354
 EELEC  =   -3280.6379  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.7036  VIRIAL  =     -75.8190  VOLUME     =   16961.1226
                                                Density    =       0.8935
 Ewald error estimate:   0.1862E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 343000 TIME(PS) =   343.000  TEMP(K) =   372.90  PRESS =   191.6
 Etot   =     950.4367  EKtot   =    1342.0096  EPtot      =    -391.5729
 BOND   =     229.4312  ANGLE   =     650.0984  DIHED      =     126.2436
 1-4 NB =     162.7356  1-4 EEL =    2480.9327  VDWAALS    =    -755.9234
 EELEC  =   -3285.0911  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.7882  VIRIAL  =      71.5948  VOLUME     =   17208.3515
                                                Density    =       0.8806
 Ewald error estimate:   0.1950E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 344000 TIME(PS) =   344.000  TEMP(K) =   378.17  PRESS =    18.5
 Etot   =     956.4595  EKtot   =    1360.9468  EPtot      =    -404.4873
 BOND   =     196.6926  ANGLE   =     648.5738  DIHED      =     155.3952
 1-4 NB =     162.3392  1-4 EEL =    2475.2541  VDWAALS    =    -766.9805
 EELEC  =   -3275.7616  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.7840  VIRIAL  =     133.9057  VOLUME     =   17226.2600
                                                Density    =       0.8797
 Ewald error estimate:   0.1000E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 345000 TIME(PS) =   345.000  TEMP(K) =   360.86  PRESS =  -382.5
 Etot   =     962.7842  EKtot   =    1298.6723  EPtot      =    -335.8881
 BOND   =     232.7123  ANGLE   =     670.5642  DIHED      =     150.9098
 1-4 NB =     163.5043  1-4 EEL =    2473.0798  VDWAALS    =    -763.6141
 EELEC  =   -3263.0445  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.7404  VIRIAL  =     283.4601  VOLUME     =   17279.5751
                                                Density    =       0.8770
 Ewald error estimate:   0.1595E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 346000 TIME(PS) =   346.000  TEMP(K) =   374.04  PRESS =  -304.7
 Etot   =     967.5528  EKtot   =    1346.1073  EPtot      =    -378.5544
 BOND   =     210.9628  ANGLE   =     661.9432  DIHED      =     138.7294
 1-4 NB =     165.1872  1-4 EEL =    2467.4204  VDWAALS    =    -760.1751
 EELEC  =   -3262.6223  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.8297  VIRIAL  =     254.0871  VOLUME     =   17365.8095
                                                Density    =       0.8727
 Ewald error estimate:   0.2106E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 347000 TIME(PS) =   347.000  TEMP(K) =   382.10  PRESS =   -71.5
 Etot   =     967.0259  EKtot   =    1375.0938  EPtot      =    -408.0680
 BOND   =     180.3842  ANGLE   =     677.0944  DIHED      =     138.0059
 1-4 NB =     163.0020  1-4 EEL =    2471.7569  VDWAALS    =    -733.0407
 EELEC  =   -3305.2705  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     151.6297  VIRIAL  =     178.9057  VOLUME     =   17677.7190
                                                Density    =       0.8573
 Ewald error estimate:   0.1115E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 348000 TIME(PS) =   348.000  TEMP(K) =   373.79  PRESS =   145.1
 Etot   =     962.1048  EKtot   =    1345.1791  EPtot      =    -383.0743
 BOND   =     188.3757  ANGLE   =     660.1964  DIHED      =     136.1390
 1-4 NB =     160.6628  1-4 EEL =    2471.1788  VDWAALS    =    -739.2699
 EELEC  =   -3260.3571  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.2642  VIRIAL  =      75.2368  VOLUME     =   17559.3193
                                                Density    =       0.8630
 Ewald error estimate:   0.2492E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 349000 TIME(PS) =   349.000  TEMP(K) =   373.90  PRESS =   156.8
 Etot   =     971.2341  EKtot   =    1345.6098  EPtot      =    -374.3757
 BOND   =     213.7490  ANGLE   =     646.3190  DIHED      =     136.6199
 1-4 NB =     158.4702  1-4 EEL =    2472.5987  VDWAALS    =    -724.7044
 EELEC  =   -3277.4282  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.2372  VIRIAL  =      71.5349  VOLUME     =   17637.2218
                                                Density    =       0.8592
 Ewald error estimate:   0.2044E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 350000 TIME(PS) =   350.000  TEMP(K) =   369.89  PRESS =  -173.4
 Etot   =     968.8291  EKtot   =    1331.1741  EPtot      =    -362.3450
 BOND   =     217.1647  ANGLE   =     666.0599  DIHED      =     131.0889
 1-4 NB =     157.4436  1-4 EEL =    2471.7007  VDWAALS    =    -747.5807
 EELEC  =   -3258.2222  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.1452  VIRIAL  =     210.6744  VOLUME     =   17501.7207
                                                Density    =       0.8659
 Ewald error estimate:   0.9516E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 351000 TIME(PS) =   351.000  TEMP(K) =   375.88  PRESS =   -48.1
 Etot   =     968.1601  EKtot   =    1352.7078  EPtot      =    -384.5477
 BOND   =     227.2196  ANGLE   =     686.5717  DIHED      =     125.8687
 1-4 NB =     155.3576  1-4 EEL =    2456.4388  VDWAALS    =    -740.7155
 EELEC  =   -3295.2885  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.9507  VIRIAL  =     166.1851  VOLUME     =   17557.3882
                                                Density    =       0.8631
 Ewald error estimate:   0.1303E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 352000 TIME(PS) =   352.000  TEMP(K) =   373.86  PRESS =  -277.1
 Etot   =     969.0601  EKtot   =    1345.4603  EPtot      =    -376.4002
 BOND   =     187.8180  ANGLE   =     673.2384  DIHED      =     140.4634
 1-4 NB =     164.4795  1-4 EEL =    2483.6561  VDWAALS    =    -740.6428
 EELEC  =   -3285.4128  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.9789  VIRIAL  =     241.8560  VOLUME     =   17527.0511
                                                Density    =       0.8646
 Ewald error estimate:   0.1036E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 353000 TIME(PS) =   353.000  TEMP(K) =   376.03  PRESS =   -95.2
 Etot   =     959.4247  EKtot   =    1353.2438  EPtot      =    -393.8191
 BOND   =     197.2692  ANGLE   =     681.6237  DIHED      =     138.5862
 1-4 NB =     156.7554  1-4 EEL =    2463.9442  VDWAALS    =    -774.7392
 EELEC  =   -3257.2586  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.7811  VIRIAL  =     167.8882  VOLUME     =   17085.3608
                                                Density    =       0.8870
 Ewald error estimate:   0.6218E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 354000 TIME(PS) =   354.000  TEMP(K) =   376.43  PRESS =   309.3
 Etot   =     957.8289  EKtot   =    1354.6799  EPtot      =    -396.8510
 BOND   =     184.6006  ANGLE   =     684.1841  DIHED      =     135.4567
 1-4 NB =     155.6764  1-4 EEL =    2458.7205  VDWAALS    =    -734.1333
 EELEC  =   -3281.3559  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.1640  VIRIAL  =      28.0147  VOLUME     =   17390.3739
                                                Density    =       0.8714
 Ewald error estimate:   0.2120E-06
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 355000 TIME(PS) =   355.000  TEMP(K) =   365.12  PRESS =    56.8
 Etot   =     961.3495  EKtot   =    1314.0129  EPtot      =    -352.6634
 BOND   =     218.8408  ANGLE   =     682.2242  DIHED      =     126.8120
 1-4 NB =     158.3483  1-4 EEL =    2474.7739  VDWAALS    =    -772.8778
 EELEC  =   -3240.7848  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.7517  VIRIAL  =     103.6726  VOLUME     =   17182.5479
                                                Density    =       0.8820
 Ewald error estimate:   0.8311E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 356000 TIME(PS) =   356.000  TEMP(K) =   365.99  PRESS =   112.5
 Etot   =     961.1865  EKtot   =    1317.1417  EPtot      =    -355.9552
 BOND   =     203.3086  ANGLE   =     675.4856  DIHED      =     141.8857
 1-4 NB =     161.4346  1-4 EEL =    2481.4199  VDWAALS    =    -762.8932
 EELEC  =   -3256.5963  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.2036  VIRIAL  =      88.7181  VOLUME     =   17075.7971
                                                Density    =       0.8875
 Ewald error estimate:   0.5749E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 357000 TIME(PS) =   357.000  TEMP(K) =   374.79  PRESS =   497.8
 Etot   =     959.0425  EKtot   =    1348.7814  EPtot      =    -389.7389
 BOND   =     185.9162  ANGLE   =     670.0753  DIHED      =     141.7274
 1-4 NB =     153.6538  1-4 EEL =    2472.6559  VDWAALS    =    -751.1372
 EELEC  =   -3262.6304  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     117.3619  VIRIAL  =     -67.1367  VOLUME     =   17164.1585
                                                Density    =       0.8829
 Ewald error estimate:   0.1231E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 358000 TIME(PS) =   358.000  TEMP(K) =   385.02  PRESS =    68.2
 Etot   =     959.7361  EKtot   =    1385.6217  EPtot      =    -425.8857
 BOND   =     186.1015  ANGLE   =     683.4107  DIHED      =     135.3087
 1-4 NB =     157.1637  1-4 EEL =    2454.5486  VDWAALS    =    -753.7768
 EELEC  =   -3288.6421  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.6867  VIRIAL  =     120.3441  VOLUME     =   17215.9555
                                                Density    =       0.8802
 Ewald error estimate:   0.1838E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 359000 TIME(PS) =   359.000  TEMP(K) =   367.90  PRESS =   550.3
 Etot   =     960.8869  EKtot   =    1324.0065  EPtot      =    -363.1197
 BOND   =     190.4507  ANGLE   =     719.5372  DIHED      =     131.9306
 1-4 NB =     152.2123  1-4 EEL =    2454.2060  VDWAALS    =    -754.3905
 EELEC  =   -3257.0659  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.2459  VIRIAL  =     -68.3385  VOLUME     =   17217.3237
                                                Density    =       0.8802
 Ewald error estimate:   0.8694E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 360000 TIME(PS) =   360.000  TEMP(K) =   367.08  PRESS =  -137.8
 Etot   =     963.6391  EKtot   =    1321.0464  EPtot      =    -357.4073
 BOND   =     206.1486  ANGLE   =     681.4120  DIHED      =     133.8316
 1-4 NB =     161.1090  1-4 EEL =    2478.0756  VDWAALS    =    -741.0324
 EELEC  =   -3276.9518  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.4759  VIRIAL  =     179.6482  VOLUME     =   17530.1808
                                                Density    =       0.8645
 Ewald error estimate:   0.6362E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 361000 TIME(PS) =   361.000  TEMP(K) =   376.85  PRESS =  -526.2
 Etot   =     969.0940  EKtot   =    1356.2107  EPtot      =    -387.1167
 BOND   =     214.0422  ANGLE   =     682.9430  DIHED      =     141.3476
 1-4 NB =     162.8565  1-4 EEL =    2461.2502  VDWAALS    =    -762.0981
 EELEC  =   -3287.4581  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.2395  VIRIAL  =     323.2096  VOLUME     =   17423.9446
                                                Density    =       0.8697
 Ewald error estimate:   0.2042E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 362000 TIME(PS) =   362.000  TEMP(K) =   372.67  PRESS =   276.3
 Etot   =     964.1009  EKtot   =    1341.1485  EPtot      =    -377.0477
 BOND   =     196.8651  ANGLE   =     684.8577  DIHED      =     139.7759
 1-4 NB =     156.0612  1-4 EEL =    2464.8043  VDWAALS    =    -753.5761
 EELEC  =   -3265.8357  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.1706  VIRIAL  =      38.5146  VOLUME     =   17210.8485
                                                Density    =       0.8805
 Ewald error estimate:   0.8509E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 363000 TIME(PS) =   363.000  TEMP(K) =   369.62  PRESS =   264.1
 Etot   =     961.2746  EKtot   =    1330.1782  EPtot      =    -368.9036
 BOND   =     198.2328  ANGLE   =     700.3448  DIHED      =     128.6944
 1-4 NB =     161.5705  1-4 EEL =    2473.8788  VDWAALS    =    -747.6171
 EELEC  =   -3284.0078  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.0316  VIRIAL  =      42.6106  VOLUME     =   17260.4683
                                                Density    =       0.8780
 Ewald error estimate:   0.7881E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 364000 TIME(PS) =   364.000  TEMP(K) =   381.12  PRESS =   377.5
 Etot   =     956.4930  EKtot   =    1371.5677  EPtot      =    -415.0747
 BOND   =     178.0171  ANGLE   =     672.8101  DIHED      =     135.8553
 1-4 NB =     153.1507  1-4 EEL =    2450.0307  VDWAALS    =    -731.1487
 EELEC  =   -3273.7899  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.8000  VIRIAL  =      -4.6107  VOLUME     =   17474.1047
                                                Density    =       0.8672
 Ewald error estimate:   0.1262E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 365000 TIME(PS) =   365.000  TEMP(K) =   370.12  PRESS =   190.2
 Etot   =     960.5696  EKtot   =    1331.9845  EPtot      =    -371.4149
 BOND   =     187.3496  ANGLE   =     703.2196  DIHED      =     140.3071
 1-4 NB =     163.4659  1-4 EEL =    2482.2816  VDWAALS    =    -739.1156
 EELEC  =   -3308.9231  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.2520  VIRIAL  =      60.9686  VOLUME     =   17361.4807
                                                Density    =       0.8729
 Ewald error estimate:   0.1570E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 366000 TIME(PS) =   366.000  TEMP(K) =   368.41  PRESS =    90.4
 Etot   =     953.3729  EKtot   =    1325.8218  EPtot      =    -372.4488
 BOND   =     186.4957  ANGLE   =     707.0022  DIHED      =     135.1882
 1-4 NB =     172.7589  1-4 EEL =    2462.7977  VDWAALS    =    -758.5676
 EELEC  =   -3278.1240  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.6361  VIRIAL  =     108.2713  VOLUME     =   17097.7897
                                                Density    =       0.8863
 Ewald error estimate:   0.3396E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 367000 TIME(PS) =   367.000  TEMP(K) =   373.98  PRESS =  -408.1
 Etot   =     949.3326  EKtot   =    1345.8860  EPtot      =    -396.5534
 BOND   =     198.5695  ANGLE   =     676.4526  DIHED      =     158.1192
 1-4 NB =     162.4526  1-4 EEL =    2466.9963  VDWAALS    =    -773.9707
 EELEC  =   -3285.1730  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.3215  VIRIAL  =     283.8240  VOLUME     =   17082.3784
                                                Density    =       0.8871
 Ewald error estimate:   0.1121E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 368000 TIME(PS) =   368.000  TEMP(K) =   381.55  PRESS =  -147.3
 Etot   =     943.3777  EKtot   =    1373.1057  EPtot      =    -429.7280
 BOND   =     194.2675  ANGLE   =     672.0790  DIHED      =     145.0576
 1-4 NB =     162.0158  1-4 EEL =    2471.9635  VDWAALS    =    -787.9982
 EELEC  =   -3287.1132  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.1044  VIRIAL  =     185.5398  VOLUME     =   16797.3989
                                                Density    =       0.9022
 Ewald error estimate:   0.1812E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 369000 TIME(PS) =   369.000  TEMP(K) =   370.28  PRESS =   -63.0
 Etot   =     937.8069  EKtot   =    1332.5701  EPtot      =    -394.7632
 BOND   =     204.3762  ANGLE   =     690.4707  DIHED      =     143.6119
 1-4 NB =     154.5690  1-4 EEL =    2460.0136  VDWAALS    =    -785.3340
 EELEC  =   -3262.4706  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.2828  VIRIAL  =     152.3320  VOLUME     =   16943.7540
                                                Density    =       0.8944
 Ewald error estimate:   0.1215E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 370000 TIME(PS) =   370.000  TEMP(K) =   367.76  PRESS =   370.1
 Etot   =     942.4008  EKtot   =    1323.4955  EPtot      =    -381.0948
 BOND   =     206.2990  ANGLE   =     660.9981  DIHED      =     135.9760
 1-4 NB =     166.7292  1-4 EEL =    2479.4191  VDWAALS    =    -748.8114
 EELEC  =   -3281.7048  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.3388  VIRIAL  =      -8.0107  VOLUME     =   17185.8926
                                                Density    =       0.8818
 Ewald error estimate:   0.3316E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 371000 TIME(PS) =   371.000  TEMP(K) =   371.28  PRESS =  -145.2
 Etot   =     941.7005  EKtot   =    1336.1734  EPtot      =    -394.4729
 BOND   =     196.9946  ANGLE   =     693.0623  DIHED      =     150.9650
 1-4 NB =     155.3247  1-4 EEL =    2455.3309  VDWAALS    =    -779.9520
 EELEC  =   -3266.1983  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     118.6533  VIRIAL  =     171.6153  VOLUME     =   16891.9739
                                                Density    =       0.8971
 Ewald error estimate:   0.8684E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 372000 TIME(PS) =   372.000  TEMP(K) =   361.08  PRESS =   -46.8
 Etot   =     941.2528  EKtot   =    1299.4448  EPtot      =    -358.1921
 BOND   =     225.9826  ANGLE   =     679.9866  DIHED      =     149.2254
 1-4 NB =     164.1987  1-4 EEL =    2466.2793  VDWAALS    =    -756.8901
 EELEC  =   -3286.9745  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.3820  VIRIAL  =     154.7203  VOLUME     =   17165.9659
                                                Density    =       0.8828
 Ewald error estimate:   0.8498E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 373000 TIME(PS) =   373.000  TEMP(K) =   360.40  PRESS =   119.4
 Etot   =     952.4368  EKtot   =    1297.0045  EPtot      =    -344.5676
 BOND   =     207.2387  ANGLE   =     704.7500  DIHED      =     151.7619
 1-4 NB =     163.0353  1-4 EEL =    2483.9562  VDWAALS    =    -739.5115
 EELEC  =   -3315.7982  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.1974  VIRIAL  =     100.4782  VOLUME     =   17353.6815
                                                Density    =       0.8733
 Ewald error estimate:   0.8715E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 374000 TIME(PS) =   374.000  TEMP(K) =   369.81  PRESS =  -292.8
 Etot   =     947.9243  EKtot   =    1330.8881  EPtot      =    -382.9639
 BOND   =     209.2985  ANGLE   =     689.0811  DIHED      =     138.2525
 1-4 NB =     162.2999  1-4 EEL =    2469.1488  VDWAALS    =    -750.5407
 EELEC  =   -3300.5039  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.3145  VIRIAL  =     246.1604  VOLUME     =   17377.5410
                                                Density    =       0.8721
 Ewald error estimate:   0.2444E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 375000 TIME(PS) =   375.000  TEMP(K) =   369.41  PRESS =  -245.6
 Etot   =     948.5452  EKtot   =    1329.4180  EPtot      =    -380.8728
 BOND   =     196.3803  ANGLE   =     721.3125  DIHED      =     140.9677
 1-4 NB =     156.9469  1-4 EEL =    2465.2586  VDWAALS    =    -773.3005
 EELEC  =   -3288.4383  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.6517  VIRIAL  =     233.0975  VOLUME     =   17055.8770
                                                Density    =       0.8885
 Ewald error estimate:   0.2781E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 376000 TIME(PS) =   376.000  TEMP(K) =   371.85  PRESS =   -20.5
 Etot   =     945.3048  EKtot   =    1338.2098  EPtot      =    -392.9050
 BOND   =     200.6691  ANGLE   =     696.6013  DIHED      =     147.0138
 1-4 NB =     155.0633  1-4 EEL =    2464.1478  VDWAALS    =    -753.5187
 EELEC  =   -3302.8816  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.8089  VIRIAL  =     154.4440  VOLUME     =   17217.8332
                                                Density    =       0.8802
 Ewald error estimate:   0.2296E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 377000 TIME(PS) =   377.000  TEMP(K) =   370.14  PRESS =   149.1
 Etot   =     944.3897  EKtot   =    1332.0751  EPtot      =    -387.6854
 BOND   =     199.7644  ANGLE   =     699.5564  DIHED      =     141.6921
 1-4 NB =     155.3060  1-4 EEL =    2464.4686  VDWAALS    =    -746.5040
 EELEC  =   -3301.9689  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.1776  VIRIAL  =      93.4423  VOLUME     =   17317.2322
                                                Density    =       0.8751
 Ewald error estimate:   0.4178E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 378000 TIME(PS) =   378.000  TEMP(K) =   377.51  PRESS =   -30.0
 Etot   =     941.2508  EKtot   =    1358.5774  EPtot      =    -417.3265
 BOND   =     191.1978  ANGLE   =     672.3798  DIHED      =     158.2803
 1-4 NB =     153.5125  1-4 EEL =    2464.0907  VDWAALS    =    -754.5884
 EELEC  =   -3302.1992  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     116.7908  VIRIAL  =     127.9448  VOLUME     =   17240.2544
                                                Density    =       0.8790
 Ewald error estimate:   0.2924E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 379000 TIME(PS) =   379.000  TEMP(K) =   373.69  PRESS =   522.6
 Etot   =     938.1215  EKtot   =    1344.8240  EPtot      =    -406.7025
 BOND   =     202.6945  ANGLE   =     664.3409  DIHED      =     137.4141
 1-4 NB =     172.1362  1-4 EEL =    2478.4290  VDWAALS    =    -715.3379
 EELEC  =   -3346.3793  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.4509  VIRIAL  =     -59.5299  VOLUME     =   17546.9943
                                                Density    =       0.8636
 Ewald error estimate:   0.9009E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 380000 TIME(PS) =   380.000  TEMP(K) =   375.38  PRESS =    17.1
 Etot   =     928.9092  EKtot   =    1350.9332  EPtot      =    -422.0240
 BOND   =     192.4460  ANGLE   =     666.6856  DIHED      =     155.0762
 1-4 NB =     158.6456  1-4 EEL =    2461.6496  VDWAALS    =    -738.7652
 EELEC  =   -3317.7618  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.8683  VIRIAL  =     125.4596  VOLUME     =   17373.6843
                                                Density    =       0.8723
 Ewald error estimate:   0.9897E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 381000 TIME(PS) =   381.000  TEMP(K) =   374.99  PRESS =  -201.7
 Etot   =     939.6604  EKtot   =    1349.5113  EPtot      =    -409.8509
 BOND   =     203.2697  ANGLE   =     647.8016  DIHED      =     141.0821
 1-4 NB =     158.8779  1-4 EEL =    2484.6218  VDWAALS    =    -740.6046
 EELEC  =   -3304.8994  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.7736  VIRIAL  =     209.7640  VOLUME     =   17451.1690
                                                Density    =       0.8684
 Ewald error estimate:   0.4340E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 382000 TIME(PS) =   382.000  TEMP(K) =   360.86  PRESS =  -118.9
 Etot   =     952.8652  EKtot   =    1298.6793  EPtot      =    -345.8140
 BOND   =     194.9648  ANGLE   =     691.9270  DIHED      =     134.7999
 1-4 NB =     164.7498  1-4 EEL =    2471.9460  VDWAALS    =    -744.8044
 EELEC  =   -3259.3971  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.1966  VIRIAL  =     174.0226  VOLUME     =   17464.1984
                                                Density    =       0.8677
 Ewald error estimate:   0.1341E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 383000 TIME(PS) =   383.000  TEMP(K) =   366.04  PRESS =  -606.3
 Etot   =     953.2165  EKtot   =    1317.3091  EPtot      =    -364.0926
 BOND   =     195.5363  ANGLE   =     709.7340  DIHED      =     139.6319
 1-4 NB =     163.6534  1-4 EEL =    2460.5718  VDWAALS    =    -745.0253
 EELEC  =   -3288.1947  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.4206  VIRIAL  =     375.7514  VOLUME     =   17594.0463
                                                Density    =       0.8613
 Ewald error estimate:   0.1668E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 384000 TIME(PS) =   384.000  TEMP(K) =   376.47  PRESS =   414.1
 Etot   =     962.9407  EKtot   =    1354.8589  EPtot      =    -391.9182
 BOND   =     211.4387  ANGLE   =     647.5179  DIHED      =     155.3221
 1-4 NB =     162.1631  1-4 EEL =    2468.0272  VDWAALS    =    -727.8343
 EELEC  =   -3308.5527  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.7637  VIRIAL  =     -11.5231  VOLUME     =   17477.9494
                                                Density    =       0.8671
 Ewald error estimate:   0.8299E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 385000 TIME(PS) =   385.000  TEMP(K) =   361.31  PRESS =     8.7
 Etot   =     956.7228  EKtot   =    1300.2775  EPtot      =    -343.5547
 BOND   =     217.6264  ANGLE   =     707.1337  DIHED      =     117.8943
 1-4 NB =     167.6520  1-4 EEL =    2470.6756  VDWAALS    =    -749.5883
 EELEC  =   -3274.9484  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.2930  VIRIAL  =     128.0280  VOLUME     =   17353.6293
                                                Density    =       0.8733
 Ewald error estimate:   0.2479E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 386000 TIME(PS) =   386.000  TEMP(K) =   369.35  PRESS =    85.7
 Etot   =     948.6472  EKtot   =    1329.2052  EPtot      =    -380.5580
 BOND   =     198.8025  ANGLE   =     698.8982  DIHED      =     139.3913
 1-4 NB =     159.5156  1-4 EEL =    2476.7661  VDWAALS    =    -762.8982
 EELEC  =   -3291.0333  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.3828  VIRIAL  =     102.8387  VOLUME     =   17045.6914
                                                Density    =       0.8890
 Ewald error estimate:   0.2913E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 387000 TIME(PS) =   387.000  TEMP(K) =   377.14  PRESS =   -54.8
 Etot   =     952.4385  EKtot   =    1357.2560  EPtot      =    -404.8175
 BOND   =     211.4593  ANGLE   =     657.8582  DIHED      =     147.7195
 1-4 NB =     159.3275  1-4 EEL =    2464.7025  VDWAALS    =    -757.0709
 EELEC  =   -3288.8135  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     120.4970  VIRIAL  =     140.9136  VOLUME     =   17261.5219
                                                Density    =       0.8779
 Ewald error estimate:   0.1415E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 388000 TIME(PS) =   388.000  TEMP(K) =   374.96  PRESS =  -504.1
 Etot   =     958.1084  EKtot   =    1349.3916  EPtot      =    -391.2832
 BOND   =     187.4963  ANGLE   =     697.6149  DIHED      =     144.0429
 1-4 NB =     164.1225  1-4 EEL =    2469.0905  VDWAALS    =    -766.9369
 EELEC  =   -3286.7133  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.3886  VIRIAL  =     323.9976  VOLUME     =   17236.4651
                                                Density    =       0.8792
 Ewald error estimate:   0.1761E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 389000 TIME(PS) =   389.000  TEMP(K) =   365.81  PRESS =   300.8
 Etot   =     952.9680  EKtot   =    1316.4770  EPtot      =    -363.5090
 BOND   =     193.4554  ANGLE   =     682.9853  DIHED      =     152.9225
 1-4 NB =     154.7540  1-4 EEL =    2471.6815  VDWAALS    =    -764.6774
 EELEC  =   -3254.6303  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.5786  VIRIAL  =      24.7291  VOLUME     =   17067.1025
                                                Density    =       0.8879
 Ewald error estimate:   0.2575E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 390000 TIME(PS) =   390.000  TEMP(K) =   371.26  PRESS =   -52.7
 Etot   =     957.5371  EKtot   =    1336.1090  EPtot      =    -378.5719
 BOND   =     210.1624  ANGLE   =     672.6122  DIHED      =     152.3752
 1-4 NB =     157.4456  1-4 EEL =    2463.9347  VDWAALS    =    -753.1343
 EELEC  =   -3281.9677  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.9863  VIRIAL  =     147.7362  VOLUME     =   17368.2808
                                                Density    =       0.8725
 Ewald error estimate:   0.1871E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 391000 TIME(PS) =   391.000  TEMP(K) =   367.56  PRESS =   -77.1
 Etot   =     952.6114  EKtot   =    1322.7634  EPtot      =    -370.1520
 BOND   =     222.1265  ANGLE   =     661.9991  DIHED      =     142.4924
 1-4 NB =     164.9996  1-4 EEL =    2476.2970  VDWAALS    =    -762.4036
 EELEC  =   -3275.6630  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.3270  VIRIAL  =     155.9008  VOLUME     =   17156.2229
                                                Density    =       0.8833
 Ewald error estimate:   0.2463E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 392000 TIME(PS) =   392.000  TEMP(K) =   373.17  PRESS =   -44.2
 Etot   =     951.8661  EKtot   =    1342.9487  EPtot      =    -391.0826
 BOND   =     204.1215  ANGLE   =     696.3699  DIHED      =     126.3665
 1-4 NB =     154.3330  1-4 EEL =    2470.2046  VDWAALS    =    -771.1522
 EELEC  =   -3271.3260  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     128.5617  VIRIAL  =     144.8568  VOLUME     =   17057.3558
                                                Density    =       0.8884
 Ewald error estimate:   0.2202E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 393000 TIME(PS) =   393.000  TEMP(K) =   370.88  PRESS =  -267.4
 Etot   =     954.5169  EKtot   =    1334.7100  EPtot      =    -380.1931
 BOND   =     218.7505  ANGLE   =     673.4574  DIHED      =     147.4887
 1-4 NB =     163.0485  1-4 EEL =    2473.2243  VDWAALS    =    -758.6892
 EELEC  =   -3297.4735  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.5244  VIRIAL  =     231.7912  VOLUME     =   17195.2462
                                                Density    =       0.8813
 Ewald error estimate:   0.2240E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 394000 TIME(PS) =   394.000  TEMP(K) =   366.05  PRESS =  -117.5
 Etot   =     954.8218  EKtot   =    1317.3525  EPtot      =    -362.5307
 BOND   =     211.7831  ANGLE   =     687.4590  DIHED      =     157.7165
 1-4 NB =     167.3264  1-4 EEL =    2466.7460  VDWAALS    =    -746.5090
 EELEC  =   -3307.0527  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.3247  VIRIAL  =     175.4791  VOLUME     =   17400.0344
                                                Density    =       0.8709
 Ewald error estimate:   0.1121E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 395000 TIME(PS) =   395.000  TEMP(K) =   361.85  PRESS =  -585.0
 Etot   =     956.6587  EKtot   =    1302.2313  EPtot      =    -345.5726
 BOND   =     212.9555  ANGLE   =     705.5937  DIHED      =     146.9463
 1-4 NB =     161.6490  1-4 EEL =    2469.9977  VDWAALS    =    -760.5783
 EELEC  =   -3282.1364  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.4658  VIRIAL  =     343.1079  VOLUME     =   17390.0776
                                                Density    =       0.8714
 Ewald error estimate:   0.1642E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 396000 TIME(PS) =   396.000  TEMP(K) =   367.57  PRESS =   187.4
 Etot   =     955.9645  EKtot   =    1322.8225  EPtot      =    -366.8580
 BOND   =     202.9953  ANGLE   =     696.2483  DIHED      =     148.7808
 1-4 NB =     156.3255  1-4 EEL =    2464.7738  VDWAALS    =    -742.0771
 EELEC  =   -3293.9047  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.7767  VIRIAL  =      59.1083  VOLUME     =   17461.2055
                                                Density    =       0.8679
 Ewald error estimate:   0.6803E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 397000 TIME(PS) =   397.000  TEMP(K) =   363.43  PRESS =  -165.9
 Etot   =     952.5829  EKtot   =    1307.9281  EPtot      =    -355.3452
 BOND   =     197.8695  ANGLE   =     707.8653  DIHED      =     161.9444
 1-4 NB =     169.1791  1-4 EEL =    2469.5981  VDWAALS    =    -755.0845
 EELEC  =   -3306.7171  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.7108  VIRIAL  =     208.9267  VOLUME     =   17366.9670
                                                Density    =       0.8726
 Ewald error estimate:   0.1347E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 398000 TIME(PS) =   398.000  TEMP(K) =   377.17  PRESS =   266.4
 Etot   =     942.8490  EKtot   =    1357.3772  EPtot      =    -414.5282
 BOND   =     195.8196  ANGLE   =     654.2333  DIHED      =     153.0710
 1-4 NB =     164.9868  1-4 EEL =    2470.2265  VDWAALS    =    -742.1135
 EELEC  =   -3310.7519  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     152.9081  VIRIAL  =      54.3194  VOLUME     =   17142.9555
                                                Density    =       0.8840
 Ewald error estimate:   0.8951E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 399000 TIME(PS) =   399.000  TEMP(K) =   366.92  PRESS =   133.5
 Etot   =     934.8969  EKtot   =    1320.4883  EPtot      =    -385.5914
 BOND   =     191.6567  ANGLE   =     683.6702  DIHED      =     148.3420
 1-4 NB =     163.2180  1-4 EEL =    2472.1380  VDWAALS    =    -767.6703
 EELEC  =   -3276.9460  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.2717  VIRIAL  =      86.0086  VOLUME     =   17090.7552
                                                Density    =       0.8867
 Ewald error estimate:   0.8720E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 400000 TIME(PS) =   400.000  TEMP(K) =   366.46  PRESS =   311.3
 Etot   =     938.9930  EKtot   =    1318.8103  EPtot      =    -379.8173
 BOND   =     192.6363  ANGLE   =     671.5217  DIHED      =     143.2957
 1-4 NB =     163.6269  1-4 EEL =    2470.8479  VDWAALS    =    -754.1552
 EELEC  =   -3267.5905  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.3476  VIRIAL  =      16.8723  VOLUME     =   17182.4629
                                                Density    =       0.8820
 Ewald error estimate:   0.1599E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 401000 TIME(PS) =   401.000  TEMP(K) =   365.53  PRESS =   160.9
 Etot   =     945.9954  EKtot   =    1315.4731  EPtot      =    -369.4777
 BOND   =     179.3717  ANGLE   =     701.1973  DIHED      =     145.6493
 1-4 NB =     158.9252  1-4 EEL =    2472.5593  VDWAALS    =    -753.2619
 EELEC  =   -3273.9186  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.2455  VIRIAL  =      79.1362  VOLUME     =   17303.5890
                                                Density    =       0.8758
 Ewald error estimate:   0.4878E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 402000 TIME(PS) =   402.000  TEMP(K) =   369.79  PRESS =   230.4
 Etot   =     948.6252  EKtot   =    1330.7850  EPtot      =    -382.1598
 BOND   =     177.8667  ANGLE   =     695.1146  DIHED      =     134.3464
 1-4 NB =     158.2357  1-4 EEL =    2481.0988  VDWAALS    =    -751.5804
 EELEC  =   -3277.2415  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.6709  VIRIAL  =      53.4221  VOLUME     =   17336.2701
                                                Density    =       0.8741
 Ewald error estimate:   0.2867E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 403000 TIME(PS) =   403.000  TEMP(K) =   366.97  PRESS =  -422.9
 Etot   =     944.8597  EKtot   =    1320.6374  EPtot      =    -375.7777
 BOND   =     207.1706  ANGLE   =     713.9278  DIHED      =     146.8805
 1-4 NB =     159.1237  1-4 EEL =    2445.5018  VDWAALS    =    -759.8214
 EELEC  =   -3288.5607  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.4020  VIRIAL  =     287.3257  VOLUME     =   17294.3080
                                                Density    =       0.8763
 Ewald error estimate:   0.2525E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 404000 TIME(PS) =   404.000  TEMP(K) =   372.69  PRESS =    54.7
 Etot   =     934.9609  EKtot   =    1341.2540  EPtot      =    -406.2932
 BOND   =     193.7820  ANGLE   =     677.0664  DIHED      =     149.3354
 1-4 NB =     160.0941  1-4 EEL =    2483.5749  VDWAALS    =    -762.3040
 EELEC  =   -3307.8419  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.3522  VIRIAL  =     107.1048  VOLUME     =   17155.8550
                                                Density    =       0.8833
 Ewald error estimate:   0.1877E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 405000 TIME(PS) =   405.000  TEMP(K) =   373.27  PRESS =   161.2
 Etot   =     930.0745  EKtot   =    1343.3136  EPtot      =    -413.2390
 BOND   =     187.5045  ANGLE   =     669.5317  DIHED      =     147.7619
 1-4 NB =     162.9948  1-4 EEL =    2471.1799  VDWAALS    =    -772.8682
 EELEC  =   -3279.3436  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.3337  VIRIAL  =      74.0680  VOLUME     =   17022.9497
                                                Density    =       0.8902
 Ewald error estimate:   0.5475E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 406000 TIME(PS) =   406.000  TEMP(K) =   372.27  PRESS =  -410.7
 Etot   =     933.4770  EKtot   =    1339.7194  EPtot      =    -406.2424
 BOND   =     184.2469  ANGLE   =     683.2333  DIHED      =     155.6143
 1-4 NB =     160.9634  1-4 EEL =    2462.8968  VDWAALS    =    -771.9190
 EELEC  =   -3281.2781  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.8630  VIRIAL  =     278.1619  VOLUME     =   17174.8489
                                                Density    =       0.8824
 Ewald error estimate:   0.1779E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 407000 TIME(PS) =   407.000  TEMP(K) =   358.74  PRESS =  -252.0
 Etot   =     945.9769  EKtot   =    1291.0327  EPtot      =    -345.0558
 BOND   =     203.4969  ANGLE   =     703.0089  DIHED      =     142.1611
 1-4 NB =     161.3650  1-4 EEL =    2469.4995  VDWAALS    =    -776.9038
 EELEC  =   -3247.6833  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.7876  VIRIAL  =     215.1375  VOLUME     =   17156.5631
                                                Density    =       0.8833
 Ewald error estimate:   0.2793E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 408000 TIME(PS) =   408.000  TEMP(K) =   368.43  PRESS =    -4.3
 Etot   =     942.3869  EKtot   =    1325.9210  EPtot      =    -383.5341
 BOND   =     205.3354  ANGLE   =     672.0474  DIHED      =     155.2285
 1-4 NB =     161.8055  1-4 EEL =    2478.5698  VDWAALS    =    -751.8361
 EELEC  =   -3304.6845  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.7122  VIRIAL  =     142.3089  VOLUME     =   17233.6837
                                                Density    =       0.8793
 Ewald error estimate:   0.2773E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 409000 TIME(PS) =   409.000  TEMP(K) =   374.85  PRESS =   -26.0
 Etot   =     945.1434  EKtot   =    1349.0083  EPtot      =    -403.8648
 BOND   =     192.6383  ANGLE   =     687.3099  DIHED      =     147.0896
 1-4 NB =     162.9978  1-4 EEL =    2471.1323  VDWAALS    =    -772.9298
 EELEC  =   -3292.1029  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.0757  VIRIAL  =     144.7388  VOLUME     =   17198.1466
                                                Density    =       0.8812
 Ewald error estimate:   0.7669E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 410000 TIME(PS) =   410.000  TEMP(K) =   367.60  PRESS =   317.1
 Etot   =     942.6187  EKtot   =    1322.9094  EPtot      =    -380.2907
 BOND   =     185.4870  ANGLE   =     708.3691  DIHED      =     156.7829
 1-4 NB =     156.9556  1-4 EEL =    2466.3174  VDWAALS    =    -755.5131
 EELEC  =   -3298.6897  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.4228  VIRIAL  =      16.9752  VOLUME     =   17007.5326
                                                Density    =       0.8910
 Ewald error estimate:   0.1520E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 411000 TIME(PS) =   411.000  TEMP(K) =   376.11  PRESS =    49.4
 Etot   =     943.1220  EKtot   =    1353.5607  EPtot      =    -410.4387
 BOND   =     185.8504  ANGLE   =     677.0759  DIHED      =     138.0663
 1-4 NB =     158.9965  1-4 EEL =    2472.8432  VDWAALS    =    -757.3806
 EELEC  =   -3285.8904  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.2162  VIRIAL  =     105.8967  VOLUME     =   17168.2440
                                                Density    =       0.8827
 Ewald error estimate:   0.1404E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 412000 TIME(PS) =   412.000  TEMP(K) =   375.64  PRESS =   -27.4
 Etot   =     946.1472  EKtot   =    1351.8475  EPtot      =    -405.7003
 BOND   =     192.5774  ANGLE   =     662.7734  DIHED      =     143.7593
 1-4 NB =     155.1948  1-4 EEL =    2462.5642  VDWAALS    =    -744.4077
 EELEC  =   -3278.1616  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.0608  VIRIAL  =     135.3815  VOLUME     =   17438.3191
                                                Density    =       0.8690
 Ewald error estimate:   0.9998E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 413000 TIME(PS) =   413.000  TEMP(K) =   374.70  PRESS =  -489.4
 Etot   =     949.7316  EKtot   =    1348.4614  EPtot      =    -398.7299
 BOND   =     193.6865  ANGLE   =     690.3823  DIHED      =     147.2112
 1-4 NB =     160.1779  1-4 EEL =    2453.2104  VDWAALS    =    -761.6073
 EELEC  =   -3281.7908  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.7448  VIRIAL  =     323.2934  VOLUME     =   17181.0298
                                                Density    =       0.8820
 Ewald error estimate:   0.1344E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 414000 TIME(PS) =   414.000  TEMP(K) =   375.93  PRESS =  -568.3
 Etot   =     951.4392  EKtot   =    1352.9100  EPtot      =    -401.4708
 BOND   =     216.5889  ANGLE   =     641.7028  DIHED      =     141.7900
 1-4 NB =     176.9815  1-4 EEL =    2485.3037  VDWAALS    =    -749.2680
 EELEC  =   -3314.5698  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.6176  VIRIAL  =     352.0416  VOLUME     =   17473.6661
                                                Density    =       0.8673
 Ewald error estimate:   0.8396E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 415000 TIME(PS) =   415.000  TEMP(K) =   367.32  PRESS =   265.1
 Etot   =     955.3843  EKtot   =    1321.8950  EPtot      =    -366.5107
 BOND   =     204.4445  ANGLE   =     700.7479  DIHED      =     134.6057
 1-4 NB =     160.6880  1-4 EEL =    2473.0507  VDWAALS    =    -749.3218
 EELEC  =   -3290.7257  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     112.7552  VIRIAL  =      13.8281  VOLUME     =   17282.0811
                                                Density    =       0.8769
 Ewald error estimate:   0.6701E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 416000 TIME(PS) =   416.000  TEMP(K) =   375.43  PRESS =    19.1
 Etot   =     950.8086  EKtot   =    1351.0859  EPtot      =    -400.2773
 BOND   =     182.7672  ANGLE   =     709.9859  DIHED      =     135.6297
 1-4 NB =     152.0536  1-4 EEL =    2471.1810  VDWAALS    =    -771.8514
 EELEC  =   -3280.0433  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.8645  VIRIAL  =     122.8390  VOLUME     =   17060.2638
                                                Density    =       0.8883
 Ewald error estimate:   0.4838E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 417000 TIME(PS) =   417.000  TEMP(K) =   375.01  PRESS =  -312.2
 Etot   =     949.5600  EKtot   =    1349.5976  EPtot      =    -400.0376
 BOND   =     193.1321  ANGLE   =     669.6670  DIHED      =     143.5732
 1-4 NB =     166.5719  1-4 EEL =    2481.0740  VDWAALS    =    -757.9093
 EELEC  =   -3296.1464  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.1037  VIRIAL  =     254.2030  VOLUME     =   17372.4656
                                                Density    =       0.8723
 Ewald error estimate:   0.5104E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 418000 TIME(PS) =   418.000  TEMP(K) =   369.80  PRESS =  -301.2
 Etot   =     953.1782  EKtot   =    1330.8249  EPtot      =    -377.6467
 BOND   =     183.7715  ANGLE   =     706.6088  DIHED      =     142.0221
 1-4 NB =     163.3189  1-4 EEL =    2465.1738  VDWAALS    =    -778.2476
 EELEC  =   -3260.2942  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.6850  VIRIAL  =     236.1375  VOLUME     =   17136.9637
                                                Density    =       0.8843
 Ewald error estimate:   0.2805E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 419000 TIME(PS) =   419.000  TEMP(K) =   381.56  PRESS =   -86.3
 Etot   =     953.3347  EKtot   =    1373.1640  EPtot      =    -419.8293
 BOND   =     174.1886  ANGLE   =     671.5700  DIHED      =     150.1996
 1-4 NB =     161.2697  1-4 EEL =    2470.5592  VDWAALS    =    -756.3592
 EELEC  =   -3291.2572  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.5976  VIRIAL  =     157.6250  VOLUME     =   17195.6639
                                                Density    =       0.8813
 Ewald error estimate:   0.1227E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 420000 TIME(PS) =   420.000  TEMP(K) =   371.83  PRESS =  -219.5
 Etot   =     951.3606  EKtot   =    1338.1312  EPtot      =    -386.7706
 BOND   =     190.9573  ANGLE   =     685.8562  DIHED      =     151.1767
 1-4 NB =     166.7014  1-4 EEL =    2466.3217  VDWAALS    =    -781.1976
 EELEC  =   -3266.5865  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.1810  VIRIAL  =     208.2908  VOLUME     =   17117.2261
                                                Density    =       0.8853
 Ewald error estimate:   0.4378E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 421000 TIME(PS) =   421.000  TEMP(K) =   374.00  PRESS =  -204.3
 Etot   =     955.7330  EKtot   =    1345.9479  EPtot      =    -390.2149
 BOND   =     189.3879  ANGLE   =     675.5641  DIHED      =     145.0885
 1-4 NB =     163.7264  1-4 EEL =    2470.3906  VDWAALS    =    -759.3304
 EELEC  =   -3275.0420  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.6299  VIRIAL  =     201.9467  VOLUME     =   17302.2377
                                                Density    =       0.8759
 Ewald error estimate:   0.4611E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 422000 TIME(PS) =   422.000  TEMP(K) =   371.71  PRESS =  -388.0
 Etot   =     964.5641  EKtot   =    1337.6956  EPtot      =    -373.1314
 BOND   =     196.1533  ANGLE   =     659.5972  DIHED      =     150.0861
 1-4 NB =     157.5516  1-4 EEL =    2487.3688  VDWAALS    =    -751.2865
 EELEC  =   -3272.6018  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.9066  VIRIAL  =     277.3878  VOLUME     =   17487.5000
                                                Density    =       0.8666
 Ewald error estimate:   0.2277E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 423000 TIME(PS) =   423.000  TEMP(K) =   372.02  PRESS =  -320.6
 Etot   =     970.7077  EKtot   =    1338.8413  EPtot      =    -368.1336
 BOND   =     181.1774  ANGLE   =     697.2123  DIHED      =     148.5635
 1-4 NB =     164.7012  1-4 EEL =    2472.3813  VDWAALS    =    -757.2074
 EELEC  =   -3274.9618  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.6649  VIRIAL  =     255.6147  VOLUME     =   17470.3251
                                                Density    =       0.8674
 Ewald error estimate:   0.2088E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 424000 TIME(PS) =   424.000  TEMP(K) =   375.32  PRESS =   171.9
 Etot   =     961.8276  EKtot   =    1350.6994  EPtot      =    -388.8718
 BOND   =     202.0553  ANGLE   =     681.1127  DIHED      =     148.9789
 1-4 NB =     156.1270  1-4 EEL =    2470.2329  VDWAALS    =    -758.6736
 EELEC  =   -3288.7052  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.9304  VIRIAL  =      70.5261  VOLUME     =   17085.4028
                                                Density    =       0.8870
 Ewald error estimate:   0.4427E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 425000 TIME(PS) =   425.000  TEMP(K) =   372.94  PRESS =   367.7
 Etot   =     955.7506  EKtot   =    1342.1551  EPtot      =    -386.4045
 BOND   =     213.4158  ANGLE   =     654.9852  DIHED      =     152.6126
 1-4 NB =     159.5081  1-4 EEL =    2463.6108  VDWAALS    =    -758.3618
 EELEC  =   -3272.1752  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.0164  VIRIAL  =     -12.3810  VOLUME     =   17181.3319
                                                Density    =       0.8820
 Ewald error estimate:   0.2795E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 426000 TIME(PS) =   426.000  TEMP(K) =   373.97  PRESS =  -264.1
 Etot   =     955.1859  EKtot   =    1345.8435  EPtot      =    -390.6577
 BOND   =     217.8240  ANGLE   =     680.9460  DIHED      =     137.3960
 1-4 NB =     151.9624  1-4 EEL =    2456.8720  VDWAALS    =    -767.1001
 EELEC  =   -3268.5581  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.3361  VIRIAL  =     231.2104  VOLUME     =   17162.4741
                                                Density    =       0.8830
 Ewald error estimate:   0.1206E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 427000 TIME(PS) =   427.000  TEMP(K) =   367.45  PRESS =  -199.2
 Etot   =     968.8861  EKtot   =    1322.3663  EPtot      =    -353.4802
 BOND   =     191.7740  ANGLE   =     705.2569  DIHED      =     135.2082
 1-4 NB =     163.2678  1-4 EEL =    2467.5196  VDWAALS    =    -749.0985
 EELEC  =   -3267.4081  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.3473  VIRIAL  =     214.5945  VOLUME     =   17496.2027
                                                Density    =       0.8661
 Ewald error estimate:   0.1277E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 428000 TIME(PS) =   428.000  TEMP(K) =   372.20  PRESS =  -207.7
 Etot   =     979.1079  EKtot   =    1339.4693  EPtot      =    -360.3614
 BOND   =     186.6302  ANGLE   =     726.6612  DIHED      =     144.8635
 1-4 NB =     151.0232  1-4 EEL =    2467.0532  VDWAALS    =    -745.4915
 EELEC  =   -3291.1012  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.5346  VIRIAL  =     210.2632  VOLUME     =   17552.7530
                                                Density    =       0.8634
 Ewald error estimate:   0.1714E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 429000 TIME(PS) =   429.000  TEMP(K) =   380.16  PRESS =  -493.1
 Etot   =     975.9394  EKtot   =    1368.1382  EPtot      =    -392.1988
 BOND   =     206.0763  ANGLE   =     701.4198  DIHED      =     146.9349
 1-4 NB =     159.5833  1-4 EEL =    2459.8336  VDWAALS    =    -775.1488
 EELEC  =   -3290.8979  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.8960  VIRIAL  =     328.4920  VOLUME     =   17339.3872
                                                Density    =       0.8740
 Ewald error estimate:   0.7023E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 430000 TIME(PS) =   430.000  TEMP(K) =   371.31  PRESS =  -269.1
 Etot   =     970.4977  EKtot   =    1336.2897  EPtot      =    -365.7920
 BOND   =     209.7656  ANGLE   =     707.3301  DIHED      =     128.0550
 1-4 NB =     161.6393  1-4 EEL =    2471.7649  VDWAALS    =    -744.5632
 EELEC  =   -3299.7837  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.7518  VIRIAL  =     248.4537  VOLUME     =   17507.2438
                                                Density    =       0.8656
 Ewald error estimate:   0.5318E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 431000 TIME(PS) =   431.000  TEMP(K) =   372.07  PRESS =  -504.0
 Etot   =     972.5497  EKtot   =    1339.0173  EPtot      =    -366.4676
 BOND   =     209.0431  ANGLE   =     678.0127  DIHED      =     128.0177
 1-4 NB =     170.4545  1-4 EEL =    2486.0823  VDWAALS    =    -771.6823
 EELEC  =   -3266.3957  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.6859  VIRIAL  =     323.1150  VOLUME     =   17224.0847
                                                Density    =       0.8798
 Ewald error estimate:   0.1852E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 432000 TIME(PS) =   432.000  TEMP(K) =   374.67  PRESS =  -299.7
 Etot   =     975.5140  EKtot   =    1348.3464  EPtot      =    -372.8324
 BOND   =     214.4487  ANGLE   =     696.1209  DIHED      =     137.3979
 1-4 NB =     168.1133  1-4 EEL =    2458.7993  VDWAALS    =    -771.4791
 EELEC  =   -3276.2333  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     154.1015  VIRIAL  =     265.2508  VOLUME     =   17174.6880
                                                Density    =       0.8824
 Ewald error estimate:   0.2454E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 433000 TIME(PS) =   433.000  TEMP(K) =   375.51  PRESS =  -165.4
 Etot   =     971.3686  EKtot   =    1351.3756  EPtot      =    -380.0070
 BOND   =     199.1187  ANGLE   =     689.1938  DIHED      =     122.0022
 1-4 NB =     161.6985  1-4 EEL =    2467.9374  VDWAALS    =    -763.3817
 EELEC  =   -3256.5759  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.1036  VIRIAL  =     197.8626  VOLUME     =   17294.3325
                                                Density    =       0.8763
 Ewald error estimate:   0.6146E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 434000 TIME(PS) =   434.000  TEMP(K) =   366.18  PRESS =  -211.9
 Etot   =     972.9432  EKtot   =    1317.8235  EPtot      =    -344.8803
 BOND   =     204.4391  ANGLE   =     677.9451  DIHED      =     143.6915
 1-4 NB =     164.9619  1-4 EEL =    2488.5589  VDWAALS    =    -740.3203
 EELEC  =   -3284.1565  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.7242  VIRIAL  =     218.6310  VOLUME     =   17463.4552
                                                Density    =       0.8678
 Ewald error estimate:   0.1023E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 435000 TIME(PS) =   435.000  TEMP(K) =   362.36  PRESS =  -299.5
 Etot   =     980.3838  EKtot   =    1304.0740  EPtot      =    -323.6902
 BOND   =     215.4888  ANGLE   =     690.9140  DIHED      =     148.6356
 1-4 NB =     169.6214  1-4 EEL =    2472.6415  VDWAALS    =    -752.4963
 EELEC  =   -3268.4953  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.2292  VIRIAL  =     241.6080  VOLUME     =   17381.1345
                                                Density    =       0.8719
 Ewald error estimate:   0.7856E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 436000 TIME(PS) =   436.000  TEMP(K) =   371.21  PRESS =    72.2
 Etot   =     971.4443  EKtot   =    1335.9231  EPtot      =    -364.4788
 BOND   =     211.9905  ANGLE   =     669.1852  DIHED      =     150.4783
 1-4 NB =     154.0781  1-4 EEL =    2472.1498  VDWAALS    =    -741.0958
 EELEC  =   -3281.2650  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.3130  VIRIAL  =     109.0922  VOLUME     =   17463.5129
                                                Density    =       0.8678
 Ewald error estimate:   0.2615E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 437000 TIME(PS) =   437.000  TEMP(K) =   366.84  PRESS =  -342.6
 Etot   =     964.9123  EKtot   =    1320.1801  EPtot      =    -355.2678
 BOND   =     201.1315  ANGLE   =     687.2797  DIHED      =     160.3119
 1-4 NB =     168.7683  1-4 EEL =    2471.2961  VDWAALS    =    -763.2010
 EELEC  =   -3280.8544  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.7168  VIRIAL  =     264.0620  VOLUME     =   17215.4143
                                                Density    =       0.8803
 Ewald error estimate:   0.1138E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 438000 TIME(PS) =   438.000  TEMP(K) =   368.57  PRESS =   466.9
 Etot   =     964.0350  EKtot   =    1326.4064  EPtot      =    -362.3714
 BOND   =     181.1704  ANGLE   =     724.5646  DIHED      =     145.5358
 1-4 NB =     167.8993  1-4 EEL =    2469.8359  VDWAALS    =    -754.5358
 EELEC  =   -3296.8416  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.5922  VIRIAL  =     -39.2232  VOLUME     =   17240.6848
                                                Density    =       0.8790
 Ewald error estimate:   0.7298E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 439000 TIME(PS) =   439.000  TEMP(K) =   363.39  PRESS =   168.7
 Etot   =     962.9013  EKtot   =    1307.7636  EPtot      =    -344.8623
 BOND   =     218.1072  ANGLE   =     705.3468  DIHED      =     133.8079
 1-4 NB =     160.5157  1-4 EEL =    2469.9224  VDWAALS    =    -740.5412
 EELEC  =   -3292.0211  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.9530  VIRIAL  =      77.0417  VOLUME     =   17267.2283
                                                Density    =       0.8776
 Ewald error estimate:   0.1466E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 440000 TIME(PS) =   440.000  TEMP(K) =   385.91  PRESS =  -272.8
 Etot   =     949.5940  EKtot   =    1388.8027  EPtot      =    -439.2087
 BOND   =     191.5398  ANGLE   =     681.8337  DIHED      =     132.6073
 1-4 NB =     162.9436  1-4 EEL =    2460.7498  VDWAALS    =    -778.7286
 EELEC  =   -3290.1543  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.0239  VIRIAL  =     244.1045  VOLUME     =   16988.7763
                                                Density    =       0.8920
 Ewald error estimate:   0.1540E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 441000 TIME(PS) =   441.000  TEMP(K) =   365.80  PRESS =   412.1
 Etot   =     954.0774  EKtot   =    1316.4377  EPtot      =    -362.3602
 BOND   =     206.7636  ANGLE   =     681.1932  DIHED      =     134.3790
 1-4 NB =     170.3051  1-4 EEL =    2484.8662  VDWAALS    =    -735.8774
 EELEC  =   -3303.9900  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.2207  VIRIAL  =     -26.6569  VOLUME     =   17296.0581
                                                Density    =       0.8762
 Ewald error estimate:   0.2206E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 442000 TIME(PS) =   442.000  TEMP(K) =   372.57  PRESS =  -666.1
 Etot   =     963.6274  EKtot   =    1340.8053  EPtot      =    -377.1780
 BOND   =     207.7483  ANGLE   =     713.6182  DIHED      =     146.4237
 1-4 NB =     161.6194  1-4 EEL =    2459.6790  VDWAALS    =    -774.7720
 EELEC  =   -3291.4945  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.1226  VIRIAL  =     389.0945  VOLUME     =   17242.2140
                                                Density    =       0.8789
 Ewald error estimate:   0.6902E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 443000 TIME(PS) =   443.000  TEMP(K) =   378.61  PRESS =  -139.8
 Etot   =     960.6976  EKtot   =    1362.5526  EPtot      =    -401.8550
 BOND   =     192.6031  ANGLE   =     679.6224  DIHED      =     149.8982
 1-4 NB =     157.3830  1-4 EEL =    2485.6899  VDWAALS    =    -780.5153
 EELEC  =   -3286.5364  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.2619  VIRIAL  =     174.4938  VOLUME     =   16978.6665
                                                Density    =       0.8926
 Ewald error estimate:   0.4676E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 444000 TIME(PS) =   444.000  TEMP(K) =   369.94  PRESS =  -417.6
 Etot   =     957.5062  EKtot   =    1331.3402  EPtot      =    -373.8340
 BOND   =     209.8280  ANGLE   =     700.9580  DIHED      =     128.9829
 1-4 NB =     161.9538  1-4 EEL =    2465.4946  VDWAALS    =    -786.4833
 EELEC  =   -3254.5680  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.3234  VIRIAL  =     288.2375  VOLUME     =   16957.6157
                                                Density    =       0.8937
 Ewald error estimate:   0.9557E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 445000 TIME(PS) =   445.000  TEMP(K) =   378.39  PRESS =    56.2
 Etot   =     947.8419  EKtot   =    1361.7546  EPtot      =    -413.9127
 BOND   =     179.8349  ANGLE   =     709.5472  DIHED      =     130.9119
 1-4 NB =     153.3644  1-4 EEL =    2470.5154  VDWAALS    =    -775.6694
 EELEC  =   -3282.4172  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.7818  VIRIAL  =     122.2045  VOLUME     =   16952.0118
                                                Density    =       0.8940
 Ewald error estimate:   0.6751E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 446000 TIME(PS) =   446.000  TEMP(K) =   375.88  PRESS =  -176.2
 Etot   =     951.0535  EKtot   =    1352.7103  EPtot      =    -401.6567
 BOND   =     204.6752  ANGLE   =     678.9474  DIHED      =     149.6802
 1-4 NB =     156.7279  1-4 EEL =    2445.3585  VDWAALS    =    -771.0647
 EELEC  =   -3265.9812  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     125.2972  VIRIAL  =     190.3066  VOLUME     =   17089.9786
                                                Density    =       0.8867
 Ewald error estimate:   0.1644E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 447000 TIME(PS) =   447.000  TEMP(K) =   362.47  PRESS =   -88.7
 Etot   =     963.4428  EKtot   =    1304.4648  EPtot      =    -341.0220
 BOND   =     219.9656  ANGLE   =     679.6429  DIHED      =     148.4222
 1-4 NB =     161.3255  1-4 EEL =    2467.2138  VDWAALS    =    -764.6459
 EELEC  =   -3252.9461  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.7922  VIRIAL  =     163.7190  VOLUME     =   17199.5284
                                                Density    =       0.8811
 Ewald error estimate:   0.1776E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 448000 TIME(PS) =   448.000  TEMP(K) =   382.48  PRESS =    40.4
 Etot   =     964.2459  EKtot   =    1376.4638  EPtot      =    -412.2179
 BOND   =     192.2875  ANGLE   =     652.8237  DIHED      =     149.0870
 1-4 NB =     167.0296  1-4 EEL =    2478.0851  VDWAALS    =    -766.9598
 EELEC  =   -3284.5710  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     153.6653  VIRIAL  =     138.7386  VOLUME     =   17096.9158
                                                Density    =       0.8864
 Ewald error estimate:   0.2853E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 449000 TIME(PS) =   449.000  TEMP(K) =   374.39  PRESS =   327.1
 Etot   =     966.4659  EKtot   =    1347.3493  EPtot      =    -380.8834
 BOND   =     183.0741  ANGLE   =     676.8507  DIHED      =     157.5237
 1-4 NB =     166.9110  1-4 EEL =    2473.9485  VDWAALS    =    -742.8658
 EELEC  =   -3296.3257  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.2118  VIRIAL  =      13.1469  VOLUME     =   17141.4925
                                                Density    =       0.8841
 Ewald error estimate:   0.5342E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 450000 TIME(PS) =   450.000  TEMP(K) =   376.76  PRESS =  -126.8
 Etot   =     962.1910  EKtot   =    1355.8814  EPtot      =    -393.6904
 BOND   =     199.4787  ANGLE   =     658.0928  DIHED      =     134.4660
 1-4 NB =     164.9335  1-4 EEL =    2488.9985  VDWAALS    =    -753.2601
 EELEC  =   -3286.3998  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.9436  VIRIAL  =     198.0084  VOLUME     =   17559.5728
                                                Density    =       0.8630
 Ewald error estimate:   0.1986E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 451000 TIME(PS) =   451.000  TEMP(K) =   379.07  PRESS =   -34.4
 Etot   =     965.8464  EKtot   =    1364.1957  EPtot      =    -398.3493
 BOND   =     187.5408  ANGLE   =     670.8428  DIHED      =     139.7350
 1-4 NB =     160.2157  1-4 EEL =    2471.8416  VDWAALS    =    -741.5605
 EELEC  =   -3286.9647  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.0306  VIRIAL  =     155.0416  VOLUME     =   17531.8194
                                                Density    =       0.8644
 Ewald error estimate:   0.8620E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 452000 TIME(PS) =   452.000  TEMP(K) =   376.03  PRESS =  -237.7
 Etot   =     963.1285  EKtot   =    1353.2637  EPtot      =    -390.1351
 BOND   =     191.2811  ANGLE   =     689.9937  DIHED      =     148.6186
 1-4 NB =     157.3084  1-4 EEL =    2462.7804  VDWAALS    =    -756.6190
 EELEC  =   -3283.4984  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.1539  VIRIAL  =     234.0184  VOLUME     =   17513.4703
                                                Density    =       0.8653
 Ewald error estimate:   0.5853E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 453000 TIME(PS) =   453.000  TEMP(K) =   380.69  PRESS =  -393.5
 Etot   =     963.9316  EKtot   =    1370.0254  EPtot      =    -406.0938
 BOND   =     195.9835  ANGLE   =     670.9262  DIHED      =     137.5197
 1-4 NB =     157.1932  1-4 EEL =    2462.1540  VDWAALS    =    -766.8116
 EELEC  =   -3263.0589  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     119.4381  VIRIAL  =     267.7058  VOLUME     =   17452.1108
                                                Density    =       0.8683
 Ewald error estimate:   0.1607E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 454000 TIME(PS) =   454.000  TEMP(K) =   374.68  PRESS =   163.4
 Etot   =     967.1838  EKtot   =    1348.3998  EPtot      =    -381.2160
 BOND   =     206.0245  ANGLE   =     672.2347  DIHED      =     136.3449
 1-4 NB =     162.5109  1-4 EEL =    2465.7335  VDWAALS    =    -739.1555
 EELEC  =   -3284.9089  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.6084  VIRIAL  =      82.6397  VOLUME     =   17568.2976
                                                Density    =       0.8626
 Ewald error estimate:   0.8449E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 455000 TIME(PS) =   455.000  TEMP(K) =   370.48  PRESS =  -147.6
 Etot   =     968.1770  EKtot   =    1333.2824  EPtot      =    -365.1054
 BOND   =     198.7448  ANGLE   =     703.8259  DIHED      =     126.4507
 1-4 NB =     160.4569  1-4 EEL =    2474.6670  VDWAALS    =    -729.4720
 EELEC  =   -3299.7787  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.5447  VIRIAL  =     198.8025  VOLUME     =   17651.3337
                                                Density    =       0.8585
 Ewald error estimate:   0.2082E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 456000 TIME(PS) =   456.000  TEMP(K) =   373.92  PRESS =   332.0
 Etot   =     973.5116  EKtot   =    1345.6769  EPtot      =    -372.1652
 BOND   =     201.7271  ANGLE   =     681.2703  DIHED      =     126.4873
 1-4 NB =     161.7585  1-4 EEL =    2469.9531  VDWAALS    =    -762.3020
 EELEC  =   -3251.0596  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.3335  VIRIAL  =      10.0722  VOLUME     =   17197.6641
                                                Density    =       0.8812
 Ewald error estimate:   0.1145E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 457000 TIME(PS) =   457.000  TEMP(K) =   372.86  PRESS =    -4.1
 Etot   =     974.8383  EKtot   =    1341.8610  EPtot      =    -367.0227
 BOND   =     236.4135  ANGLE   =     643.9901  DIHED      =     143.6185
 1-4 NB =     155.8896  1-4 EEL =    2467.4946  VDWAALS    =    -767.0694
 EELEC  =   -3247.3595  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.8180  VIRIAL  =     144.3521  VOLUME     =   17140.2811
                                                Density    =       0.8841
 Ewald error estimate:   0.2413E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 458000 TIME(PS) =   458.000  TEMP(K) =   371.50  PRESS =  -207.8
 Etot   =     972.6612  EKtot   =    1336.9502  EPtot      =    -364.2890
 BOND   =     214.7179  ANGLE   =     648.3222  DIHED      =     149.8542
 1-4 NB =     163.6673  1-4 EEL =    2486.2541  VDWAALS    =    -774.6137
 EELEC  =   -3252.4910  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.6647  VIRIAL  =     217.3400  VOLUME     =   17088.7628
                                                Density    =       0.8868
 Ewald error estimate:   0.4155E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 459000 TIME(PS) =   459.000  TEMP(K) =   373.75  PRESS =   -34.9
 Etot   =     967.5576  EKtot   =    1345.0624  EPtot      =    -377.5048
 BOND   =     206.7848  ANGLE   =     670.3870  DIHED      =     132.0670
 1-4 NB =     157.7743  1-4 EEL =    2478.9980  VDWAALS    =    -762.4900
 EELEC  =   -3261.0260  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.0894  VIRIAL  =     147.0946  VOLUME     =   17234.7541
                                                Density    =       0.8793
 Ewald error estimate:   0.3483E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 460000 TIME(PS) =   460.000  TEMP(K) =   377.56  PRESS =  -171.5
 Etot   =     961.0219  EKtot   =    1358.7807  EPtot      =    -397.7588
 BOND   =     211.6152  ANGLE   =     663.2083  DIHED      =     130.5161
 1-4 NB =     164.9150  1-4 EEL =    2461.4547  VDWAALS    =    -733.7298
 EELEC  =   -3295.7382  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.8085  VIRIAL  =     186.5849  VOLUME     =   17489.1840
                                                Density    =       0.8665
 Ewald error estimate:   0.3530E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 461000 TIME(PS) =   461.000  TEMP(K) =   369.12  PRESS =    58.5
 Etot   =     963.5159  EKtot   =    1328.3999  EPtot      =    -364.8840
 BOND   =     193.8768  ANGLE   =     681.9153  DIHED      =     148.7854
 1-4 NB =     157.6294  1-4 EEL =    2466.6039  VDWAALS    =    -727.2312
 EELEC  =   -3286.4636  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.0341  VIRIAL  =     104.5758  VOLUME     =   17768.2270
                                                Density    =       0.8529
 Ewald error estimate:   0.1041E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 462000 TIME(PS) =   462.000  TEMP(K) =   382.05  PRESS =  -490.5
 Etot   =     964.4588  EKtot   =    1374.9081  EPtot      =    -410.4493
 BOND   =     188.4411  ANGLE   =     667.1986  DIHED      =     144.4790
 1-4 NB =     157.0188  1-4 EEL =    2461.6595  VDWAALS    =    -770.2261
 EELEC  =   -3259.0202  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.1121  VIRIAL  =     321.3282  VOLUME     =   17298.6030
                                                Density    =       0.8760
 Ewald error estimate:   0.2341E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 463000 TIME(PS) =   463.000  TEMP(K) =   363.61  PRESS =  -266.3
 Etot   =     959.6330  EKtot   =    1308.5774  EPtot      =    -348.9444
 BOND   =     206.1509  ANGLE   =     708.2006  DIHED      =     156.8277
 1-4 NB =     163.6246  1-4 EEL =    2462.6578  VDWAALS    =    -772.4628
 EELEC  =   -3273.9431  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.4744  VIRIAL  =     232.0133  VOLUME     =   17136.4800
                                                Density    =       0.8843
 Ewald error estimate:   0.2364E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 464000 TIME(PS) =   464.000  TEMP(K) =   365.21  PRESS =  -160.2
 Etot   =     960.5847  EKtot   =    1314.3283  EPtot      =    -353.7436
 BOND   =     234.1407  ANGLE   =     631.6176  DIHED      =     154.6522
 1-4 NB =     162.9612  1-4 EEL =    2464.7171  VDWAALS    =    -765.5553
 EELEC  =   -3236.2772  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.1857  VIRIAL  =     194.9784  VOLUME     =   17291.0914
                                                Density    =       0.8764
 Ewald error estimate:   0.1623E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 465000 TIME(PS) =   465.000  TEMP(K) =   361.70  PRESS =   229.1
 Etot   =     957.3725  EKtot   =    1301.6714  EPtot      =    -344.2988
 BOND   =     218.8353  ANGLE   =     682.9881  DIHED      =     153.8643
 1-4 NB =     154.3891  1-4 EEL =    2459.0930  VDWAALS    =    -756.4316
 EELEC  =   -3257.0371  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.5661  VIRIAL  =      48.6262  VOLUME     =   17172.5128
                                                Density    =       0.8825
 Ewald error estimate:   0.4947E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 466000 TIME(PS) =   466.000  TEMP(K) =   375.25  PRESS =    90.5
 Etot   =     956.3764  EKtot   =    1350.4614  EPtot      =    -394.0851
 BOND   =     202.0198  ANGLE   =     680.7078  DIHED      =     129.2663
 1-4 NB =     157.8390  1-4 EEL =    2458.4907  VDWAALS    =    -759.0173
 EELEC  =   -3263.3913  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.3552  VIRIAL  =     100.7303  VOLUME     =   17205.8656
                                                Density    =       0.8808
 Ewald error estimate:   0.4501E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 467000 TIME(PS) =   467.000  TEMP(K) =   367.40  PRESS =   295.7
 Etot   =     957.1282  EKtot   =    1322.2165  EPtot      =    -365.0884
 BOND   =     214.7984  ANGLE   =     665.6640  DIHED      =     146.3854
 1-4 NB =     153.0252  1-4 EEL =    2469.7211  VDWAALS    =    -748.0365
 EELEC  =   -3266.6459  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     135.8491  VIRIAL  =      25.4658  VOLUME     =   17290.4981
                                                Density    =       0.8765
 Ewald error estimate:   0.1949E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 468000 TIME(PS) =   468.000  TEMP(K) =   371.14  PRESS =   192.2
 Etot   =     953.4563  EKtot   =    1335.6574  EPtot      =    -382.2011
 BOND   =     187.3388  ANGLE   =     700.2611  DIHED      =     143.5284
 1-4 NB =     155.2509  1-4 EEL =    2459.7712  VDWAALS    =    -739.4990
 EELEC  =   -3288.8524  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.1156  VIRIAL  =      70.7815  VOLUME     =   17187.9937
                                                Density    =       0.8817
 Ewald error estimate:   0.8511E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 469000 TIME(PS) =   469.000  TEMP(K) =   369.23  PRESS =    31.7
 Etot   =     947.2795  EKtot   =    1328.7760  EPtot      =    -381.4965
 BOND   =     191.4164  ANGLE   =     697.3734  DIHED      =     139.3939
 1-4 NB =     164.7271  1-4 EEL =    2476.0426  VDWAALS    =    -758.6898
 EELEC  =   -3291.7601  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.0353  VIRIAL  =     129.2980  VOLUME     =   17166.2365
                                                Density    =       0.8828
 Ewald error estimate:   0.7513E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 470000 TIME(PS) =   470.000  TEMP(K) =   361.82  PRESS =   137.3
 Etot   =     941.2691  EKtot   =    1302.1212  EPtot      =    -360.8521
 BOND   =     204.0720  ANGLE   =     721.3922  DIHED      =     138.4368
 1-4 NB =     159.6138  1-4 EEL =    2466.2292  VDWAALS    =    -750.4990
 EELEC  =   -3300.0971  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.8853  VIRIAL  =      90.5557  VOLUME     =   17319.2203
                                                Density    =       0.8750
 Ewald error estimate:   0.1278E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 471000 TIME(PS) =   471.000  TEMP(K) =   370.96  PRESS =  -105.7
 Etot   =     945.5309  EKtot   =    1335.0195  EPtot      =    -389.4886
 BOND   =     207.2361  ANGLE   =     673.5377  DIHED      =     141.8887
 1-4 NB =     162.7899  1-4 EEL =    2473.7199  VDWAALS    =    -756.3600
 EELEC  =   -3292.3009  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.9118  VIRIAL  =     177.5741  VOLUME     =   17379.4178
                                                Density    =       0.8720
 Ewald error estimate:   0.3605E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 472000 TIME(PS) =   472.000  TEMP(K) =   367.19  PRESS =   171.4
 Etot   =     947.0088  EKtot   =    1321.4310  EPtot      =    -374.4222
 BOND   =     179.7153  ANGLE   =     707.9860  DIHED      =     157.0248
 1-4 NB =     164.5160  1-4 EEL =    2470.9461  VDWAALS    =    -763.0976
 EELEC  =   -3291.5127  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.0454  VIRIAL  =      66.7353  VOLUME     =   17109.2746
                                                Density    =       0.8857
 Ewald error estimate:   0.3159E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 473000 TIME(PS) =   473.000  TEMP(K) =   368.63  PRESS =  -124.1
 Etot   =     953.5255  EKtot   =    1326.6358  EPtot      =    -373.1103
 BOND   =     192.3955  ANGLE   =     708.7696  DIHED      =     149.3255
 1-4 NB =     164.8473  1-4 EEL =    2471.3454  VDWAALS    =    -780.1982
 EELEC  =   -3279.5954  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.9329  VIRIAL  =     172.5061  VOLUME     =   17012.0018
                                                Density    =       0.8908
 Ewald error estimate:   0.8195E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 474000 TIME(PS) =   474.000  TEMP(K) =   364.87  PRESS =   159.7
 Etot   =     955.5795  EKtot   =    1313.0837  EPtot      =    -357.5043
 BOND   =     198.3194  ANGLE   =     728.7156  DIHED      =     128.0334
 1-4 NB =     158.6706  1-4 EEL =    2467.9972  VDWAALS    =    -754.7896
 EELEC  =   -3284.4508  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.4933  VIRIAL  =      73.9200  VOLUME     =   17274.4374
                                                Density    =       0.8773
 Ewald error estimate:   0.4382E-05
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 475000 TIME(PS) =   475.000  TEMP(K) =   371.02  PRESS =  -105.0
 Etot   =     954.6774  EKtot   =    1335.2416  EPtot      =    -380.5642
 BOND   =     200.2137  ANGLE   =     694.3999  DIHED      =     147.0179
 1-4 NB =     165.1140  1-4 EEL =    2459.9098  VDWAALS    =    -752.4702
 EELEC  =   -3294.7493  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.5032  VIRIAL  =     173.6791  VOLUME     =   17285.9164
                                                Density    =       0.8767
 Ewald error estimate:   0.1306E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 476000 TIME(PS) =   476.000  TEMP(K) =   367.04  PRESS =   100.4
 Etot   =     945.0893  EKtot   =    1320.9163  EPtot      =    -375.8270
 BOND   =     201.6786  ANGLE   =     698.5455  DIHED      =     153.5335
 1-4 NB =     154.3482  1-4 EEL =    2477.7297  VDWAALS    =    -781.3326
 EELEC  =   -3280.3300  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.6262  VIRIAL  =      94.1425  VOLUME     =   16832.2354
                                                Density    =       0.9003
 Ewald error estimate:   0.1710E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 477000 TIME(PS) =   477.000  TEMP(K) =   363.95  PRESS =    38.1
 Etot   =     944.6256  EKtot   =    1309.8012  EPtot      =    -365.1756
 BOND   =     207.0907  ANGLE   =     699.5445  DIHED      =     141.8271
 1-4 NB =     164.8318  1-4 EEL =    2471.8391  VDWAALS    =    -759.6084
 EELEC  =   -3290.7004  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.2168  VIRIAL  =     122.0945  VOLUME     =   17185.0752
                                                Density    =       0.8818
 Ewald error estimate:   0.3214E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 478000 TIME(PS) =   478.000  TEMP(K) =   370.38  PRESS =  -171.2
 Etot   =     939.2284  EKtot   =    1332.9129  EPtot      =    -393.6845
 BOND   =     186.1497  ANGLE   =     698.6343  DIHED      =     149.0931
 1-4 NB =     161.7011  1-4 EEL =    2469.9195  VDWAALS    =    -777.7317
 EELEC  =   -3281.4504  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.5690  VIRIAL  =     192.4741  VOLUME     =   17021.5583
                                                Density    =       0.8903
 Ewald error estimate:   0.6670E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 479000 TIME(PS) =   479.000  TEMP(K) =   367.17  PRESS =   -37.4
 Etot   =     946.9020  EKtot   =    1321.3869  EPtot      =    -374.4848
 BOND   =     191.9121  ANGLE   =     668.7163  DIHED      =     143.3908
 1-4 NB =     164.5568  1-4 EEL =    2473.7285  VDWAALS    =    -745.7994
 EELEC  =   -3270.9899  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     130.2552  VIRIAL  =     144.2931  VOLUME     =   17397.6754
                                                Density    =       0.8711
 Ewald error estimate:   0.4646E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 480000 TIME(PS) =   480.000  TEMP(K) =   364.78  PRESS =   162.5
 Etot   =     947.6088  EKtot   =    1312.7817  EPtot      =    -365.1728
 BOND   =     220.4014  ANGLE   =     689.4263  DIHED      =     135.0351
 1-4 NB =     161.2849  1-4 EEL =    2454.1449  VDWAALS    =    -740.0044
 EELEC  =   -3285.4611  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.4934  VIRIAL  =      87.6816  VOLUME     =   17617.0364
                                                Density    =       0.8602
 Ewald error estimate:   0.1557E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 481000 TIME(PS) =   481.000  TEMP(K) =   371.20  PRESS =   199.5
 Etot   =     959.4143  EKtot   =    1335.8780  EPtot      =    -376.4637
 BOND   =     197.8629  ANGLE   =     683.1385  DIHED      =     128.8297
 1-4 NB =     160.5168  1-4 EEL =    2479.5916  VDWAALS    =    -738.7295
 EELEC  =   -3287.6737  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     151.3774  VIRIAL  =      76.3820  VOLUME     =   17409.6430
                                                Density    =       0.8705
 Ewald error estimate:   0.2135E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 482000 TIME(PS) =   482.000  TEMP(K) =   371.87  PRESS =    50.0
 Etot   =     955.8826  EKtot   =    1338.2771  EPtot      =    -382.3945
 BOND   =     194.1420  ANGLE   =     655.7012  DIHED      =     148.1998
 1-4 NB =     168.6033  1-4 EEL =    2469.4124  VDWAALS    =    -727.7776
 EELEC  =   -3290.6756  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.8237  VIRIAL  =     120.8720  VOLUME     =   17554.6110
                                                Density    =       0.8633
 Ewald error estimate:   0.1301E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 483000 TIME(PS) =   483.000  TEMP(K) =   379.61  PRESS =   -66.7
 Etot   =     959.8995  EKtot   =    1366.1398  EPtot      =    -406.2403
 BOND   =     194.4784  ANGLE   =     641.4294  DIHED      =     142.7264
 1-4 NB =     160.4302  1-4 EEL =    2486.8855  VDWAALS    =    -732.1907
 EELEC  =   -3299.9995  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.0443  VIRIAL  =     163.5109  VOLUME     =   17675.7649
                                                Density    =       0.8574
 Ewald error estimate:   0.1762E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 484000 TIME(PS) =   484.000  TEMP(K) =   372.45  PRESS =  -298.5
 Etot   =     961.3843  EKtot   =    1340.3835  EPtot      =    -378.9992
 BOND   =     180.0820  ANGLE   =     683.9243  DIHED      =     149.7966
 1-4 NB =     161.0398  1-4 EEL =    2462.8602  VDWAALS    =    -745.6681
 EELEC  =   -3271.0339  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.1031  VIRIAL  =     242.6497  VOLUME     =   17615.2470
                                                Density    =       0.8603
 Ewald error estimate:   0.1535E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 485000 TIME(PS) =   485.000  TEMP(K) =   381.35  PRESS =    45.7
 Etot   =     965.7256  EKtot   =    1372.3916  EPtot      =    -406.6659
 BOND   =     201.9058  ANGLE   =     629.8662  DIHED      =     137.7859
 1-4 NB =     163.6396  1-4 EEL =    2472.5585  VDWAALS    =    -735.5505
 EELEC  =   -3276.8714  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.9171  VIRIAL  =     129.5306  VOLUME     =   17632.4890
                                                Density    =       0.8595
 Ewald error estimate:   0.3270E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 486000 TIME(PS) =   486.000  TEMP(K) =   372.34  PRESS =  -187.7
 Etot   =     966.0987  EKtot   =    1339.9883  EPtot      =    -373.8896
 BOND   =     196.1764  ANGLE   =     675.4788  DIHED      =     142.4573
 1-4 NB =     171.8162  1-4 EEL =    2483.1353  VDWAALS    =    -737.1178
 EELEC  =   -3305.8358  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.8394  VIRIAL  =     213.0327  VOLUME     =   17570.6907
                                                Density    =       0.8625
 Ewald error estimate:   0.1776E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 487000 TIME(PS) =   487.000  TEMP(K) =   366.45  PRESS =   302.0
 Etot   =     967.5597  EKtot   =    1318.7830  EPtot      =    -351.2232
 BOND   =     199.7371  ANGLE   =     677.7165  DIHED      =     148.7693
 1-4 NB =     162.0300  1-4 EEL =    2474.1523  VDWAALS    =    -739.8402
 EELEC  =   -3273.7882  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.4332  VIRIAL  =       6.9003  VOLUME     =   17565.4507
                                                Density    =       0.8627
 Ewald error estimate:   0.6517E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 488000 TIME(PS) =   488.000  TEMP(K) =   367.58  PRESS =  -462.7
 Etot   =     970.7492  EKtot   =    1322.8381  EPtot      =    -352.0888
 BOND   =     210.3574  ANGLE   =     668.4994  DIHED      =     150.9604
 1-4 NB =     164.1561  1-4 EEL =    2467.0297  VDWAALS    =    -754.8715
 EELEC  =   -3258.2204  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.4361  VIRIAL  =     308.8212  VOLUME     =   17554.6070
                                                Density    =       0.8633
 Ewald error estimate:   0.1186E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 489000 TIME(PS) =   489.000  TEMP(K) =   377.75  PRESS =   -41.2
 Etot   =     969.7065  EKtot   =    1359.4491  EPtot      =    -389.7426
 BOND   =     193.0608  ANGLE   =     675.6478  DIHED      =     143.5942
 1-4 NB =     159.8829  1-4 EEL =    2466.4968  VDWAALS    =    -754.2748
 EELEC  =   -3274.1504  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     158.6112  VIRIAL  =     174.0527  VOLUME     =   17364.1406
                                                Density    =       0.8727
 Ewald error estimate:   0.1486E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 490000 TIME(PS) =   490.000  TEMP(K) =   370.39  PRESS =    64.5
 Etot   =     970.9787  EKtot   =    1332.9549  EPtot      =    -361.9762
 BOND   =     203.2891  ANGLE   =     661.4481  DIHED      =     148.3470
 1-4 NB =     167.5222  1-4 EEL =    2476.1776  VDWAALS    =    -733.0571
 EELEC  =   -3285.7032  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     146.7849  VIRIAL  =     122.2188  VOLUME     =   17651.8159
                                                Density    =       0.8585
 Ewald error estimate:   0.6277E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 491000 TIME(PS) =   491.000  TEMP(K) =   380.14  PRESS =  -212.9
 Etot   =     979.8333  EKtot   =    1368.0387  EPtot      =    -388.2055
 BOND   =     188.1259  ANGLE   =     680.9070  DIHED      =     134.3436
 1-4 NB =     155.6506  1-4 EEL =    2451.1361  VDWAALS    =    -738.3101
 EELEC  =   -3260.0585  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     124.3177  VIRIAL  =     205.7880  VOLUME     =   17719.8668
                                                Density    =       0.8552
 Ewald error estimate:   0.7124E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 492000 TIME(PS) =   492.000  TEMP(K) =   356.28  PRESS =   -40.9
 Etot   =     978.8359  EKtot   =    1282.1926  EPtot      =    -303.3567
 BOND   =     212.1606  ANGLE   =     683.7764  DIHED      =     150.3166
 1-4 NB =     162.3177  1-4 EEL =    2480.5732  VDWAALS    =    -729.8907
 EELEC  =   -3262.6105  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.3275  VIRIAL  =     151.8652  VOLUME     =   17601.3661
                                                Density    =       0.8610
 Ewald error estimate:   0.2940E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 493000 TIME(PS) =   493.000  TEMP(K) =   370.14  PRESS =  -271.1
 Etot   =     989.8298  EKtot   =    1332.0482  EPtot      =    -342.2185
 BOND   =     201.5910  ANGLE   =     682.4655  DIHED      =     136.5102
 1-4 NB =     160.5703  1-4 EEL =    2465.4169  VDWAALS    =    -729.5986
 EELEC  =   -3259.1738  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.6050  VIRIAL  =     248.3722  VOLUME     =   17727.9271
                                                Density    =       0.8548
 Ewald error estimate:   0.1389E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 494000 TIME(PS) =   494.000  TEMP(K) =   383.46  PRESS =   192.2
 Etot   =     989.8159  EKtot   =    1380.0019  EPtot      =    -390.1860
 BOND   =     190.0088  ANGLE   =     656.7075  DIHED      =     130.5389
 1-4 NB =     165.2368  1-4 EEL =    2470.4048  VDWAALS    =    -738.8569
 EELEC  =   -3264.2260  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.5591  VIRIAL  =      59.9645  VOLUME     =   17496.3084
                                                Density    =       0.8661
 Ewald error estimate:   0.2708E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 495000 TIME(PS) =   495.000  TEMP(K) =   365.08  PRESS =  -425.1
 Etot   =     993.5952  EKtot   =    1313.8564  EPtot      =    -320.2612
 BOND   =     198.2252  ANGLE   =     708.1490  DIHED      =     136.4138
 1-4 NB =     162.4209  1-4 EEL =    2473.4183  VDWAALS    =    -750.5157
 EELEC  =   -3248.3727  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.0423  VIRIAL  =     292.3912  VOLUME     =   17577.0785
                                                Density    =       0.8622
 Ewald error estimate:   0.2972E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 496000 TIME(PS) =   496.000  TEMP(K) =   362.95  PRESS =   283.8
 Etot   =     987.7357  EKtot   =    1306.1781  EPtot      =    -318.4424
 BOND   =     193.4677  ANGLE   =     718.6831  DIHED      =     148.5740
 1-4 NB =     160.3561  1-4 EEL =    2451.6512  VDWAALS    =    -723.2425
 EELEC  =   -3267.9319  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.1178  VIRIAL  =      36.9027  VOLUME     =   17657.9111
                                                Density    =       0.8582
 Ewald error estimate:   0.7982E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 497000 TIME(PS) =   497.000  TEMP(K) =   377.98  PRESS =   179.2
 Etot   =     984.1652  EKtot   =    1360.2924  EPtot      =    -376.1271
 BOND   =     201.0001  ANGLE   =     633.3123  DIHED      =     136.9933
 1-4 NB =     161.8502  1-4 EEL =    2475.8469  VDWAALS    =    -723.7324
 EELEC  =   -3261.3976  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.0649  VIRIAL  =      70.4950  VOLUME     =   17724.1484
                                                Density    =       0.8550
 Ewald error estimate:   0.2284E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 498000 TIME(PS) =   498.000  TEMP(K) =   375.39  PRESS =   -66.4
 Etot   =     981.1257  EKtot   =    1350.9611  EPtot      =    -369.8354
 BOND   =     187.8762  ANGLE   =     645.6735  DIHED      =     140.8278
 1-4 NB =     174.8330  1-4 EEL =    2482.7741  VDWAALS    =    -740.6818
 EELEC  =   -3261.1382  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.1347  VIRIAL  =     158.1573  VOLUME     =   17450.3943
                                                Density    =       0.8684
 Ewald error estimate:   0.1009E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 499000 TIME(PS) =   499.000  TEMP(K) =   373.81  PRESS =  -251.9
 Etot   =     983.1626  EKtot   =    1345.2660  EPtot      =    -362.1034
 BOND   =     197.9714  ANGLE   =     659.7185  DIHED      =     151.3314
 1-4 NB =     169.9005  1-4 EEL =    2468.5446  VDWAALS    =    -725.6549
 EELEC  =   -3283.9149  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     133.2062  VIRIAL  =     229.3336  VOLUME     =   17674.6228
                                                Density    =       0.8574
 Ewald error estimate:   0.1538E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP = 500000 TIME(PS) =   500.000  TEMP(K) =   375.82  PRESS =  -187.6
 Etot   =     975.3293  EKtot   =    1352.5095  EPtot      =    -377.1802
 BOND   =     195.0333  ANGLE   =     648.9491  DIHED      =     133.6026
 1-4 NB =     166.5894  1-4 EEL =    2484.2021  VDWAALS    =    -754.7440
 EELEC  =   -3250.8128  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     145.9407  VIRIAL  =     216.7736  VOLUME     =   17491.3638
                                                Density    =       0.8664
 Ewald error estimate:   0.1705E-04
 ------------------------------------------------------------------------------


      A V E R A G E S   O V E R  500000 S T E P S


 NSTEP = 500000 TIME(PS) =   500.000  TEMP(K) =   370.47  PRESS =    -4.5
 Etot   =     969.8614  EKtot   =    1333.2520  EPtot      =    -363.3906
 BOND   =     195.3611  ANGLE   =     672.7515  DIHED      =     142.5562
 1-4 NB =     161.8346  1-4 EEL =    2470.9060  VDWAALS    =    -737.6741
 EELEC  =   -3269.1257  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.6132  VIRIAL  =     142.0996  VOLUME     =   17767.7378
                                                Density    =       0.8605
 Ewald error estimate:   0.1201E-03
 ------------------------------------------------------------------------------


      R M S  F L U C T U A T I O N S


 NSTEP = 500000 TIME(PS) =   500.000  TEMP(K) =    15.34  PRESS =   303.2
 Etot   =      94.1055  EKtot   =      55.2169  EPtot      =      70.2399
 BOND   =      19.7897  ANGLE   =      55.8747  DIHED      =      11.4055
 1-4 NB =       5.5198  1-4 EEL =       9.3913  VDWAALS    =      58.6275
 EELEC  =      52.8884  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      18.6422  VIRIAL  =     119.5632  VOLUME     =    2144.0158
                                                Density    =       0.0633
 Ewald error estimate:   0.8835E-04
 ------------------------------------------------------------------------------

|
|>>>>>>>>PROFILE of TIMES>>>>>>>>>>>>>>>>>  
|
|                Ewald setup time           0.12 ( 0.01% of List )
|                Check list validity       88.94 ( 7.06% of List )
|                Map frac coords            2.15 ( 0.17% of List )
|                Setup grids                0.08 ( 0.01% of List )
|                Grid unit cell             3.11 ( 0.25% of List )
|                Grid image cell            1.44 ( 0.11% of List )
|                Build the list          1157.61 (91.91% of List )
|                Other                      6.07 ( 0.48% of List )
|             List time               1259.52 ( 2.85% of Nonbo)
|                Direct Ewald time      24334.13 (56.61% of Ewald)
|                Adjust Ewald time        916.47 ( 2.13% of Ewald)
|                Self Ewald time            6.40 ( 0.01% of Ewald)
|                Finish NB virial          58.35 ( 0.14% of Ewald)
|                   Fill Bspline coeffs      268.06 ( 1.54% of Recip)
|                   Fill charge grid        4966.23 (28.55% of Recip)
|                   Scalar sum              3969.87 (22.83% of Recip)
|                   Grad sum                4810.98 (27.66% of Recip)
|                   FFT time                3369.45 (19.37% of Recip)
|                   Other                      7.53 ( 0.04% of Recip)
|                Recip Ewald time       17392.12 (40.46% of Ewald)
|                Other                    280.01 ( 0.65% of Ewald)
|             Ewald time             42987.48 (97.14% of Nonbo)
|             Other                      5.84 ( 0.01% of Nonbo)
|          Nonbond force          44252.85 (96.51% of Force)
|          Bond energy               36.08 ( 0.08% of Force)
|          Angle energy             438.91 ( 0.96% of Force)
|          Dihedral energy         1008.28 ( 2.20% of Force)
|          Noe calc time              2.86 ( 0.01% of Force)
|          Other                    116.04 ( 0.25% of Force)
|       Force time             45855.02 (98.61% of Runmd)
|       Shake time               247.04 ( 0.53% of Runmd)
|       Verlet update time       151.61 ( 0.33% of Runmd)
|       Ekcmr time               192.87 ( 0.41% of Runmd)
|       Other                     55.03 ( 0.12% of Runmd)
|    Runmd Time             46501.55 (100.0% of Total)
| Total time             46501.70 (100.0% of ALL  )

| Highest rstack allocated:     117886
| Highest istack allocated:      73750

|     Setup wallclock           4 seconds
|     Nonsetup wallclock    46909 seconds
