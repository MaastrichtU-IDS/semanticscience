
          -------------------------------------------------------
          Amber 7  SANDER                   Scripps/UCSF 2000
          -------------------------------------------------------

|      Tue Jan  1 16:25:25 2002

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
 
 molecular dynamics, polarizable solute                                        
 $cntrl                                                                        
  irest  = 0, ntx    = 1,                                                      
  ntb    = 2, ntp    = 1,                                                      
  nstlim = 50000,                                                              
  dt     = 0.002,                                                              
  ntpr   = 1000,                                                               
  nsnb   = 5,                                                                  
  temp0  = 300.,                                                               
  cut    =  7.0,                                                               
  scee   = 1.2,                                                                
  ntf    = 2,                                                                  
  ntc    = 2,                                                                  
 $end                                                                          
                                                                               
-------------------------------------------------------------------------------

 molecular dynamics, polarizable solute                                         

| Flags:                                                                        


   1.  RESOURCE   USE: 

 getting new box info from bottom of inpcrd
| peek_ewald_inpcrd: Box info found

   EWALD SPECIFIC INPUT:

     Largest sphere to fit in unit cell has radius =     9.867
     Calculating ew_coeff from dsum_tol,cutoff
     Box X =   20.146   Box Y =   19.733   Box Z =   20.297
     Alpha =   90.000   Beta =   90.000   Gamma =   90.000
     NFFT1 =   20       NFFT2 =   20       NFFT3 =   20
     Cutoff=    7.000   Tol   =0.100E-04
     Ewald Coefficient =  0.40167

     Interpolation order =    4
| New format PARM file being parsed.
| Version =    1.000 Date = 12/30/01 Time = 08:25:33
 NATOM  =     864 NTYPES =       2 NBONH =     648 MBONA  =     216
 NTHETH =       0 MTHETA =       0 NPHIH =       0 MPHIA  =       0
 NHPARM =       0 NPARM  =       0 NNB   =    1512 NRES   =     216
 NBONA  =     216 NTHETA =       0 NPHIA =       0 NUMBND =       3
 NUMANG =       0 NPTRA  =       0 NATYP =       3 NPHB   =       1
 IFBOX  =       1 NMXRS  =       4 IFCAP =       0 NEXTRA =     216


   EWALD MEMORY USE:

|    Total heap storage needed        =        345
|    Adjacent nonbond minimum mask    =       3024
|    Max number of pointers           =         25
|    List build maxmask               =       6048
|    Maximage  =       1267

   EWALD LOCMEM POINTER OFFSETS
|      Real memory needed by PME        =        345
|      Size of EEDTABLE                 =      21087
|      Real memory needed by EEDTABLE   =      84348
|      Integer memory needed by ADJ     =       6048
|      Integer memory used by local nonb=      37447
|      Real memory used by local nonb   =      14169

|    MAX NONBOND PAIRS =    5000000

|     Memory Use     Allocated         Used
|     Real             2000000       141727
|     Hollerith         500000         5402
|     Integer          3500000        69055

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

     NTB   =    2       BOXX  =   20.146
     BOXY  =   19.733   BOXZ  =   20.297

     NTT   =    0       TEMP0 =  300.000
     DTEMP =    0.000   TAUTP =    1.000
     VLIMIT=   20.000

     NTP   =    1       PRES0 =    1.000   COMP  =   44.600
     TAUP  =    0.200   NPSCAL=    1

     NSCM  =    1000

     NSTLIM=  50000     NTU   =    1
     T     =    0.000   DT    =   0.00200

     NTC   =    2       TOL   =   0.00001  JFASTW =    0

     NTF   =    2       NSNB  =    5

     CUT   =    7.000   SCNB  =    2.000
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

     NATOM =     864  NRES =    216

     Water definition for fast triangulated model:
     Resname = WAT ; Oxygen_name = O   ; Hyd1_name = H1  ; Hyd2_name = H2  
| EXTRA_PTS: numextra =    216
| EXTRA PTS fill_bonded: num11-14 =    216  1080     0     0
| EXTRA_PTS, build_14: num of 14 terms =      0
| EXTRA_PTS, trim_bonds: num bonds BEFORE trim =   648   648
| EXTRA_PTS, trim_bonds: num bonds AFTER trim =   648   648
| EXTRA_PTS, trim_bonds: num bonds BEFORE trim =   216   216
| EXTRA_PTS, trim_bonds: num bonds AFTER trim =     0     0
| EXTRA_PTS, trim_theta: num angles BEFORE trim =     0     0
| EXTRA_PTS, trim_theta: num angles AFTER trim =     0     0
| EXTRA_PTS, trim_theta: num angles BEFORE trim =     0     0
| EXTRA_PTS, trim_theta: num angles AFTER trim =     0     0
| EXTRA_PTS, trim_phi: num dihedrals BEFORE trim =     0     0
| EXTRA_PTS, trim_phi: num dihedrals AFTER trim =     0     0
| EXTRA_PTS, trim_phi: num dihedrals BEFORE trim =     0     0
| EXTRA_PTS, trim_phi: num dihedrals AFTER trim =     0     0

   3.  ATOMIC COORDINATES AND VELOCITIES

                                                                                
 begin time read from input coords =     0.000 ps

 Number of triangulated 3-point waters found:      216

     Sum of charges from parm topology file =   0.00000000
     Forcing neutrality...
 ---------------------------------------------------
 APPROXIMATING switch and d/dx switch using CUBIC SPLINE INTERPOLATION
 using   5000.0 points per unit in tabled values
 TESTING RELATIVE ERROR over r ranging from 0.0 to cutoff
| CHECK switch(x): max rel err =   0.1990E-14   at   2.461500
| CHECK d/dx switch(x): max rel err =   0.7670E-11   at   2.772760
 ---------------------------------------------------
     Total number of mask terms =       1296
     Total number of mask terms =       2592
| Local SIZE OF NONBOND LIST =     140205
| TOTAL SIZE OF NONBOND LIST =     140205

 NSTEP =      0 TIME(PS) =     0.000  TEMP(K) =     0.00  PRESS = -8067.0
 Etot   =   -1869.9700  EKtot   =       0.0000  EPtot      =   -1869.9700
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     108.9038
 EELEC  =   -1978.8738  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =       0.0000  VIRIAL  =    1405.4087  VOLUME     =    8068.8900
                                                Density    =       0.8009
 Ewald error estimate:   0.6070E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   1000 TIME(PS) =     2.000  TEMP(K) =   243.48  PRESS =   -97.1
 Etot   =   -1985.2638  EKtot   =     312.7981  EPtot      =   -2298.0619
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     430.5887
 EELEC  =   -2728.6506  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     159.4359  VIRIAL  =     172.4029  VOLUME     =    6183.3462
                                                Density    =       1.0451
 Ewald error estimate:   0.4601E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   2000 TIME(PS) =     4.000  TEMP(K) =   252.63  PRESS =  -149.5
 Etot   =   -1988.9111  EKtot   =     324.5619  EPtot      =   -2313.4730
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     448.6156
 EELEC  =   -2762.0885  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     166.7729  VIRIAL  =     187.3351  VOLUME     =    6368.7391
                                                Density    =       1.0146
 Ewald error estimate:   0.5407E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   3000 TIME(PS) =     6.000  TEMP(K) =   246.52  PRESS =  -157.6
 Etot   =   -1990.1077  EKtot   =     316.7035  EPtot      =   -2306.8113
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     460.8483
 EELEC  =   -2767.6596  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     161.4615  VIRIAL  =     183.9357  VOLUME     =    6604.8021
                                                Density    =       0.9784
 Ewald error estimate:   0.8582E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   4000 TIME(PS) =     8.000  TEMP(K) =   268.03  PRESS =   -99.7
 Etot   =   -1998.8949  EKtot   =     344.3496  EPtot      =   -2343.2445
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     475.7474
 EELEC  =   -2818.9919  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     188.5664  VIRIAL  =     202.5722  VOLUME     =    6504.5053
                                                Density    =       0.9935
 Ewald error estimate:   0.2880E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   5000 TIME(PS) =    10.000  TEMP(K) =   269.71  PRESS =  -675.5
 Etot   =   -2007.1635  EKtot   =     346.5058  EPtot      =   -2353.6694
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     452.4062
 EELEC  =   -2806.0755  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     171.4170  VIRIAL  =     264.6533  VOLUME     =    6393.0778
                                                Density    =       1.0108
 Ewald error estimate:   0.1741E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   6000 TIME(PS) =    12.000  TEMP(K) =   234.41  PRESS =   839.9
 Etot   =   -2014.3260  EKtot   =     301.1456  EPtot      =   -2315.4716
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     476.6337
 EELEC  =   -2792.1053  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     140.0498  VIRIAL  =      25.3436  VOLUME     =    6325.4493
                                                Density    =       1.0216
 Ewald error estimate:   0.1886E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   7000 TIME(PS) =    14.000  TEMP(K) =   241.10  PRESS =   134.2
 Etot   =   -2018.9757  EKtot   =     309.7477  EPtot      =   -2328.7234
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     478.5570
 EELEC  =   -2807.2804  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.4470  VIRIAL  =     129.9329  VOLUME     =    6388.5975
                                                Density    =       1.0115
 Ewald error estimate:   0.6514E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   8000 TIME(PS) =    16.000  TEMP(K) =   254.65  PRESS =  -363.4
 Etot   =   -2024.4149  EKtot   =     327.1594  EPtot      =   -2351.5743
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     455.8074
 EELEC  =   -2807.3818  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     162.8240  VIRIAL  =     212.6508  VOLUME     =    6350.6005
                                                Density    =       1.0175
 Ewald error estimate:   0.5383E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   9000 TIME(PS) =    18.000  TEMP(K) =   233.08  PRESS =   478.3
 Etot   =   -2029.6107  EKtot   =     299.4417  EPtot      =   -2329.0524
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     473.6023
 EELEC  =   -2802.6547  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     150.1159  VIRIAL  =      84.5742  VOLUME     =    6345.9602
                                                Density    =       1.0183
 Ewald error estimate:   0.7625E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  10000 TIME(PS) =    20.000  TEMP(K) =   230.01  PRESS =   771.3
 Etot   =   -2034.5328  EKtot   =     295.4988  EPtot      =   -2330.0316
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     485.2647
 EELEC  =   -2815.2963  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     149.7725  VIRIAL  =      43.6127  VOLUME     =    6374.5230
                                                Density    =       1.0137
 Ewald error estimate:   0.1349E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  11000 TIME(PS) =    22.000  TEMP(K) =   239.30  PRESS =  -118.4
 Etot   =   -2040.5575  EKtot   =     307.4390  EPtot      =   -2347.9965
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     471.7613
 EELEC  =   -2819.7578  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     158.8328  VIRIAL  =     175.1944  VOLUME     =    6400.7674
                                                Density    =       1.0096
 Ewald error estimate:   0.8712E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  12000 TIME(PS) =    24.000  TEMP(K) =   233.67  PRESS =   -55.2
 Etot   =   -2048.4570  EKtot   =     300.1985  EPtot      =   -2348.6556
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     464.2674
 EELEC  =   -2812.9230  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     161.6488  VIRIAL  =     169.1951  VOLUME     =    6330.5988
                                                Density    =       1.0208
 Ewald error estimate:   0.5444E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  13000 TIME(PS) =    26.000  TEMP(K) =   225.02  PRESS =  -445.9
 Etot   =   -2053.5016  EKtot   =     289.0842  EPtot      =   -2342.5858
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     452.9884
 EELEC  =   -2795.5742  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.3973  VIRIAL  =     197.0844  VOLUME     =    6304.0094
                                                Density    =       1.0251
 Ewald error estimate:   0.4108E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  14000 TIME(PS) =    28.000  TEMP(K) =   228.82  PRESS =   305.9
 Etot   =   -2057.0687  EKtot   =     293.9723  EPtot      =   -2351.0410
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     492.6877
 EELEC  =   -2843.7287  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.0930  VIRIAL  =      95.0659  VOLUME     =    6363.3865
                                                Density    =       1.0155
 Ewald error estimate:   0.7338E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  15000 TIME(PS) =    30.000  TEMP(K) =   231.94  PRESS =   405.4
 Etot   =   -2061.4622  EKtot   =     297.9781  EPtot      =   -2359.4404
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     496.4997
 EELEC  =   -2855.9401  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.7062  VIRIAL  =      83.7123  VOLUME     =    6397.4659
                                                Density    =       1.0101
 Ewald error estimate:   0.1279E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  16000 TIME(PS) =    32.000  TEMP(K) =   229.27  PRESS =  -481.8
 Etot   =   -2070.8000  EKtot   =     294.5531  EPtot      =   -2365.3531
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     461.0315
 EELEC  =   -2826.3847  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     154.7393  VIRIAL  =     220.0157  VOLUME     =    6274.6705
                                                Density    =       1.0299
 Ewald error estimate:   0.1090E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  17000 TIME(PS) =    34.000  TEMP(K) =   228.49  PRESS =  -283.9
 Etot   =   -2076.4340  EKtot   =     293.5427  EPtot      =   -2369.9767
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     478.4136
 EELEC  =   -2848.3902  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.8852  VIRIAL  =     188.6261  VOLUME     =    6483.3245
                                                Density    =       0.9967
 Ewald error estimate:   0.8664E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  18000 TIME(PS) =    36.000  TEMP(K) =   224.68  PRESS =  -359.9
 Etot   =   -2080.6364  EKtot   =     288.6487  EPtot      =   -2369.2851
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     487.2392
 EELEC  =   -2856.5243  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     141.8790  VIRIAL  =     192.5715  VOLUME     =    6523.8002
                                                Density    =       0.9905
 Ewald error estimate:   0.1182E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  19000 TIME(PS) =    38.000  TEMP(K) =   230.49  PRESS = -1091.7
 Etot   =   -2086.5872  EKtot   =     296.1165  EPtot      =   -2382.7037
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     463.3258
 EELEC  =   -2846.0295  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     150.6119  VIRIAL  =     304.0570  VOLUME     =    6509.7861
                                                Density    =       0.9927
 Ewald error estimate:   0.2713E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  20000 TIME(PS) =    40.000  TEMP(K) =   229.91  PRESS =     5.4
 Etot   =   -2092.7677  EKtot   =     295.3654  EPtot      =   -2388.1331
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     494.8071
 EELEC  =   -2882.9403  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     147.4933  VIRIAL  =     146.7395  VOLUME     =    6473.1605
                                                Density    =       0.9983
 Ewald error estimate:   0.1471E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  21000 TIME(PS) =    42.000  TEMP(K) =   216.20  PRESS =  1113.6
 Etot   =   -2100.0876  EKtot   =     277.7511  EPtot      =   -2377.8387
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     530.8232
 EELEC  =   -2908.6618  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     126.8994  VIRIAL  =     -28.3549  VOLUME     =    6457.0418
                                                Density    =       1.0008
 Ewald error estimate:   0.2522E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  22000 TIME(PS) =    44.000  TEMP(K) =   213.45  PRESS =    11.9
 Etot   =   -2106.5406  EKtot   =     274.2253  EPtot      =   -2380.7658
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     491.1593
 EELEC  =   -2871.9252  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.3321  VIRIAL  =     136.6894  VOLUME     =    6380.2198
                                                Density    =       1.0128
 Ewald error estimate:   0.5409E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  23000 TIME(PS) =    46.000  TEMP(K) =   214.96  PRESS =   504.8
 Etot   =   -2113.2447  EKtot   =     276.1697  EPtot      =   -2389.4144
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     507.5910
 EELEC  =   -2897.0054  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.0420  VIRIAL  =      73.7629  VOLUME     =    6355.8249
                                                Density    =       1.0167
 Ewald error estimate:   0.2667E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  24000 TIME(PS) =    48.000  TEMP(K) =   219.66  PRESS =   560.9
 Etot   =   -2120.2141  EKtot   =     282.2017  EPtot      =   -2402.4158
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     521.9750
 EELEC  =   -2924.3908  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.9094  VIRIAL  =      62.3016  VOLUME     =    6407.7929
                                                Density    =       1.0085
 Ewald error estimate:   0.3165E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  25000 TIME(PS) =    50.000  TEMP(K) =   224.64  PRESS =    59.8
 Etot   =   -2124.6195  EKtot   =     288.5952  EPtot      =   -2413.2147
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     515.7268
 EELEC  =   -2928.9415  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     143.7488  VIRIAL  =     135.4434  VOLUME     =    6427.4436
                                                Density    =       1.0054
 Ewald error estimate:   0.1105E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  26000 TIME(PS) =    52.000  TEMP(K) =   220.20  PRESS =  -237.2
 Etot   =   -2131.4346  EKtot   =     282.9002  EPtot      =   -2414.3349
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     498.3969
 EELEC  =   -2912.7317  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.9267  VIRIAL  =     169.3645  VOLUME     =    6334.5139
                                                Density    =       1.0201
 Ewald error estimate:   0.2041E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  27000 TIME(PS) =    54.000  TEMP(K) =   218.13  PRESS =  -187.7
 Etot   =   -2136.9588  EKtot   =     280.2315  EPtot      =   -2417.1902
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     500.4679
 EELEC  =   -2917.6581  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     136.1307  VIRIAL  =     162.0952  VOLUME     =    6406.7444
                                                Density    =       1.0086
 Ewald error estimate:   0.2690E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  28000 TIME(PS) =    56.000  TEMP(K) =   219.85  PRESS =  -518.6
 Etot   =   -2141.7379  EKtot   =     282.4513  EPtot      =   -2424.1893
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     484.9569
 EELEC  =   -2909.1462  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     148.0966  VIRIAL  =     219.2410  VOLUME     =    6354.0501
                                                Density    =       1.0170
 Ewald error estimate:   0.6039E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  29000 TIME(PS) =    58.000  TEMP(K) =   218.47  PRESS =  -753.2
 Etot   =   -2146.3940  EKtot   =     280.6704  EPtot      =   -2427.0643
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     482.7529
 EELEC  =   -2909.8172  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     142.9462  VIRIAL  =     246.1909  VOLUME     =    6348.8574
                                                Density    =       1.0178
 Ewald error estimate:   0.1603E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  30000 TIME(PS) =    60.000  TEMP(K) =   211.34  PRESS =  -299.1
 Etot   =   -2151.5159  EKtot   =     271.5077  EPtot      =   -2423.0236
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     502.2372
 EELEC  =   -2925.2608  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     138.5498  VIRIAL  =     179.6297  VOLUME     =    6362.0261
                                                Density    =       1.0157
 Ewald error estimate:   0.9255E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  31000 TIME(PS) =    62.000  TEMP(K) =   208.52  PRESS =  -281.7
 Etot   =   -2157.6295  EKtot   =     267.8891  EPtot      =   -2425.5186
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     500.8024
 EELEC  =   -2926.3211  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     134.2331  VIRIAL  =     172.6614  VOLUME     =    6319.1237
                                                Density    =       1.0226
 Ewald error estimate:   0.1231E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  32000 TIME(PS) =    64.000  TEMP(K) =   203.25  PRESS =   369.8
 Etot   =   -2161.8920  EKtot   =     261.1129  EPtot      =   -2423.0050
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     521.8862
 EELEC  =   -2944.8912  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     129.3436  VIRIAL  =      78.5881  VOLUME     =    6357.3063
                                                Density    =       1.0165
 Ewald error estimate:   0.3511E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  33000 TIME(PS) =    66.000  TEMP(K) =   202.45  PRESS =    57.7
 Etot   =   -2166.8131  EKtot   =     260.0971  EPtot      =   -2426.9102
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     516.6335
 EELEC  =   -2943.5437  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.5294  VIRIAL  =     124.6020  VOLUME     =    6358.5268
                                                Density    =       1.0163
 Ewald error estimate:   0.1023E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  34000 TIME(PS) =    68.000  TEMP(K) =   205.22  PRESS =   161.3
 Etot   =   -2173.2720  EKtot   =     263.6513  EPtot      =   -2436.9233
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     526.2160
 EELEC  =   -2963.1393  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     127.9205  VIRIAL  =     105.7349  VOLUME     =    6368.4361
                                                Density    =       1.0147
 Ewald error estimate:   0.8006E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  35000 TIME(PS) =    70.000  TEMP(K) =   201.91  PRESS =    71.6
 Etot   =   -2177.8796  EKtot   =     259.3957  EPtot      =   -2437.2753
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     520.1932
 EELEC  =   -2957.4685  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     144.9055  VIRIAL  =     135.0384  VOLUME     =    6380.0114
                                                Density    =       1.0129
 Ewald error estimate:   0.1732E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  36000 TIME(PS) =    72.000  TEMP(K) =   206.07  PRESS =   260.5
 Etot   =   -2180.8726  EKtot   =     264.7379  EPtot      =   -2445.6106
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     534.8515
 EELEC  =   -2980.4621  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     132.0656  VIRIAL  =      95.6667  VOLUME     =    6472.0119
                                                Density    =       0.9985
 Ewald error estimate:   0.1360E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  37000 TIME(PS) =    74.000  TEMP(K) =   202.65  PRESS =   172.5
 Etot   =   -2186.3130  EKtot   =     260.3540  EPtot      =   -2446.6670
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     534.2558
 EELEC  =   -2980.9228  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.5831  VIRIAL  =     107.5674  VOLUME     =    6449.2337
                                                Density    =       1.0020
 Ewald error estimate:   0.1625E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  38000 TIME(PS) =    76.000  TEMP(K) =   192.85  PRESS =    56.9
 Etot   =   -2190.2743  EKtot   =     247.7537  EPtot      =   -2438.0280
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     528.2016
 EELEC  =   -2966.2297  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     119.2398  VIRIAL  =     111.3353  VOLUME     =    6431.9418
                                                Density    =       1.0047
 Ewald error estimate:   0.1286E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  39000 TIME(PS) =    78.000  TEMP(K) =   197.87  PRESS =   564.5
 Etot   =   -2194.4170  EKtot   =     254.2059  EPtot      =   -2448.6229
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     547.3849
 EELEC  =   -2996.0078  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.4411  VIRIAL  =      42.5935  VOLUME     =    6469.4819
                                                Density    =       0.9988
 Ewald error estimate:   0.2168E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  40000 TIME(PS) =    80.000  TEMP(K) =   195.85  PRESS =   186.1
 Etot   =   -2201.2000  EKtot   =     251.6131  EPtot      =   -2452.8131
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     530.5543
 EELEC  =   -2983.3674  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.1619  VIRIAL  =      97.5241  VOLUME     =    6380.2134
                                                Density    =       1.0128
 Ewald error estimate:   0.6906E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  41000 TIME(PS) =    82.000  TEMP(K) =   190.23  PRESS =  -803.4
 Etot   =   -2208.1824  EKtot   =     244.3976  EPtot      =   -2452.5800
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     497.6902
 EELEC  =   -2950.2702  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.0991  VIRIAL  =     232.2750  VOLUME     =    6293.8700
                                                Density    =       1.0267
 Ewald error estimate:   0.3772E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  42000 TIME(PS) =    84.000  TEMP(K) =   199.90  PRESS =  -499.4
 Etot   =   -2211.3362  EKtot   =     256.8201  EPtot      =   -2468.1563
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     511.3469
 EELEC  =   -2979.5032  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.2889  VIRIAL  =     207.6488  VOLUME     =    6339.1987
                                                Density    =       1.0194
 Ewald error estimate:   0.5677E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  43000 TIME(PS) =    86.000  TEMP(K) =   192.88  PRESS =   323.7
 Etot   =   -2214.2430  EKtot   =     247.7924  EPtot      =   -2462.0354
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     541.9623
 EELEC  =   -3003.9977  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.2249  VIRIAL  =      76.3503  VOLUME     =    6420.0394
                                                Density    =       1.0065
 Ewald error estimate:   0.7957E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  44000 TIME(PS) =    88.000  TEMP(K) =   181.27  PRESS =   391.8
 Etot   =   -2218.4069  EKtot   =     232.8823  EPtot      =   -2451.2892
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     542.4143
 EELEC  =   -2993.7035  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     117.9490  VIRIAL  =      63.5848  VOLUME     =    6426.6400
                                                Density    =       1.0055
 Ewald error estimate:   0.1069E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  45000 TIME(PS) =    90.000  TEMP(K) =   191.09  PRESS =   -26.9
 Etot   =   -2222.3114  EKtot   =     245.4985  EPtot      =   -2467.8098
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     539.0312
 EELEC  =   -3006.8411  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     118.6368  VIRIAL  =     122.4086  VOLUME     =    6501.4497
                                                Density    =       0.9939
 Ewald error estimate:   0.6953E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  46000 TIME(PS) =    92.000  TEMP(K) =   187.54  PRESS =   162.2
 Etot   =   -2228.3562  EKtot   =     240.9346  EPtot      =   -2469.2908
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     539.5192
 EELEC  =   -3008.8099  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     121.8117  VIRIAL  =      99.2784  VOLUME     =    6435.3732
                                                Density    =       1.0041
 Ewald error estimate:   0.8434E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  47000 TIME(PS) =    94.000  TEMP(K) =   185.25  PRESS =  -153.0
 Etot   =   -2232.9977  EKtot   =     237.9895  EPtot      =   -2470.9872
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     527.3731
 EELEC  =   -2998.3603  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     123.3301  VIRIAL  =     144.6734  VOLUME     =    6459.7465
                                                Density    =       1.0004
 Ewald error estimate:   0.1131E-02
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  48000 TIME(PS) =    96.000  TEMP(K) =   201.27  PRESS =  -684.5
 Etot   =   -2235.3267  EKtot   =     258.5813  EPtot      =   -2493.9079
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     531.6977
 EELEC  =   -3025.6057  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     137.3613  VIRIAL  =     234.3874  VOLUME     =    6564.8667
                                                Density    =       0.9843
 Ewald error estimate:   0.5468E-04
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  49000 TIME(PS) =    98.000  TEMP(K) =   193.20  PRESS =  -403.2
 Etot   =   -2240.7019  EKtot   =     248.2034  EPtot      =   -2488.9052
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     537.5695
 EELEC  =   -3026.4748  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     131.1168  VIRIAL  =     187.7913  VOLUME     =    6510.2960
                                                Density    =       0.9926
 Ewald error estimate:   0.7112E-03
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  50000 TIME(PS) =   100.000  TEMP(K) =   178.49  PRESS =   403.2
 Etot   =   -2243.5871  EKtot   =     229.3033  EPtot      =   -2472.8904
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     561.4354
 EELEC  =   -3034.3258  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     117.6548  VIRIAL  =      60.8057  VOLUME     =    6529.7842
                                                Density    =       0.9896
 Ewald error estimate:   0.3099E-03
 ------------------------------------------------------------------------------


      A V E R A G E S   O V E R   50000 S T E P S


 NSTEP =  50000 TIME(PS) =   100.000  TEMP(K) =   217.52  PRESS =    -8.4
 Etot   =   -2118.7285  EKtot   =     279.4467  EPtot      =   -2398.1752
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     499.6583
 EELEC  =   -2897.8334  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     139.9170  VIRIAL  =     141.2678  VOLUME     =    6404.1336
                                                Density    =       1.0092
 Ewald error estimate:   0.7934E-03
 ------------------------------------------------------------------------------


      R M S  F L U C T U A T I O N S


 NSTEP =  50000 TIME(PS) =   100.000  TEMP(K) =    19.30  PRESS =   405.5
 Etot   =      79.2883  EKtot   =      24.7943  EPtot      =      58.1958
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =      32.5462
 EELEC  =      89.0639  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      13.4837  VIRIAL  =      60.3149  VOLUME     =      86.7510
                                                Density    =       0.0132
 Ewald error estimate:   0.4727E-03
 ------------------------------------------------------------------------------

| Zhou-Berne energy conservation: log10(DeltaE) = -0.86
|
|>>>>>>>>PROFILE of TIMES>>>>>>>>>>>>>>>>>  
|
|                Ewald setup time           0.10 ( 0.13% of List )
|                Check list validity        5.08 ( 6.60% of List )
|                Map frac coords            0.18 ( 0.24% of List )
|                Setup grids                0.03 ( 0.04% of List )
|                Grid unit cell             0.10 ( 0.13% of List )
|                Grid image cell            0.13 ( 0.17% of List )
|                Build the list            70.95 (92.16% of List )
|                Other                      0.40 ( 0.52% of List )
|             List time                 76.98 ( 3.19% of Nonbo)
|                Direct Ewald time       1528.62 (65.48% of Ewald)
|                Adjust Ewald time         21.03 ( 0.90% of Ewald)
|                Self Ewald time            0.53 ( 0.02% of Ewald)
|                Finish NB virial           2.87 ( 0.12% of Ewald)
|                   Fill Bspline coeffs       13.45 ( 1.76% of Recip)
|                   Fill charge grid         279.02 (36.51% of Recip)
|                   Scalar sum               101.65 (13.30% of Recip)
|                   Grad sum                 276.86 (36.23% of Recip)
|                   FFT time                  92.59 (12.12% of Recip)
|                   Other                      0.57 ( 0.07% of Recip)
|                Recip Ewald time         764.14 (32.73% of Ewald)
|                Other                     17.20 ( 0.74% of Ewald)
|             Ewald time              2334.38 (96.80% of Nonbo)
|             Other                      0.30 ( 0.01% of Nonbo)
|          Nonbond force           2411.67 (99.67% of Force)
|          Bond energy                0.40 ( 0.02% of Force)
|          Angle energy               0.35 ( 0.01% of Force)
|          Dihedral energy            0.55 ( 0.02% of Force)
|          Noe calc time              0.15 ( 0.01% of Force)
|          Other                      6.60 ( 0.27% of Force)
|       Force time              2419.72 (98.62% of Runmd)
|       Shake time                 9.65 ( 0.39% of Runmd)
|       Verlet update time         8.92 ( 0.36% of Runmd)
|       Ekcmr time                11.82 ( 0.48% of Runmd)
|       Other                      3.48 ( 0.14% of Runmd)
|    Runmd Time              2453.58 (100.0% of Total)
| Total time              2453.63 (100.0% of ALL  )

| Highest rstack allocated:      44098
| Highest istack allocated:      31536

|     Setup wallclock           0 seconds
|     Nonsetup wallclock     2473 seconds
