
          -------------------------------------------------------
          Amber 7  SANDER                   Scripps/UCSF 2000
          -------------------------------------------------------

|      Fri Jan  4 13:40:06 2002

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
  dt     = 0.001,                                                              
  ntt    = 1,                                                                  
  ipol   = 1,                                                                  
  ntpr   = 1000,                                                               
  nsnb   = 5,                                                                  
  temp0  = 300.0,                                                              
  cut    = 7.0,                                                                
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

     Largest sphere to fit in unit cell has radius =    10.000
     Calculating ew_coeff from dsum_tol,cutoff
     Box X =   20.000   Box Y =   20.000   Box Z =   20.000
     Alpha =   90.000   Beta =   90.000   Gamma =   90.000
     NFFT1 =   20       NFFT2 =   20       NFFT3 =   20
     Cutoff=    7.000   Tol   =0.100E-04
     Ewald Coefficient =  0.40167

     Interpolation order =    4
| New format PARM file being parsed.
| Version =    1.000 Date = 12/29/01 Time = 15:52:26
 NATOM  =     648 NTYPES =       2 NBONH =     648 MBONA  =       0
 NTHETH =       0 MTHETA =       0 NPHIH =       0 MPHIA  =       0
 NHPARM =       0 NPARM  =       0 NNB   =     864 NRES   =     216
 NBONA  =       0 NTHETA =       0 NPHIA =       0 NUMBND =       2
 NUMANG =       0 NPTRA  =       0 NATYP =       2 NPHB   =       1
 IFBOX  =       1 NMXRS  =       3 IFCAP =       0 NEXTRA =       0


   EWALD MEMORY USE:

|    Total heap storage needed        =        345
|    Adjacent nonbond minimum mask    =       1728
|    Max number of pointers           =         25
|    List build maxmask               =       3456
|    Maximage  =        950

   EWALD LOCMEM POINTER OFFSETS
|      Real memory needed by PME        =        345
|      Size of EEDTABLE                 =      21087
|      Real memory needed by EEDTABLE   =      84348
|      Integer memory needed by ADJ     =       3456
|      Integer memory used by local nonb=      31197
|      Real memory used by local nonb   =      10626

|    MAX NONBOND PAIRS =    5000000

|     Memory Use     Allocated         Used
|     Real             2000000       139480
|     Hollerith         500000        13826
|     Integer          3500000        54597

|     Max Nonbonded Pairs: 5000000
    0 pairs for pol 1-4.

| Duplicated    0 dihedrals
| Duplicated    0 dihedrals

     BOX TYPE: RECTILINEAR


   2.  CONTROL  DATA  FOR  THE  RUN

                                                                                

     TIMLIM=  999999.   IREST =    0       IBELLY=    0
     IMIN  =    0
     IPOL  =    1

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

     NATOM =     648  NRES =    216

     Water definition for fast triangulated model:
     Resname = WAT ; Oxygen_name = O   ; Hyd1_name = H1  ; Hyd2_name = H2  
| EXTRA_PTS: numextra =      0
| EXTRA PTS fill_bonded: num11-14 =      0   648     0     0
| EXTRA_PTS, build_14: num of 14 terms =      0

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
     Total number of mask terms =        648
     Total number of mask terms =       1296
| Local SIZE OF NONBOND LIST =      80171
| TOTAL SIZE OF NONBOND LIST =      80171

 NSTEP =      0 TIME(PS) =     0.000  TEMP(K) =     0.00  PRESS = -5523.0
 Etot   =   -1867.9666  EKtot   =       0.0000  EPtot      =   -1867.9666
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     353.1835
 EELEC  =   -1766.8118  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =       0.0000  VIRIAL  =     953.9876  VOLUME     =    8000.0000
 EPOLZ  =    -454.3383  E3BODY  =       0.0000
 Dipole convergence: rms =  0.875E-04 temperature =   0.00
                                                Density    =       0.8078
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   1000 TIME(PS) =     1.000  TEMP(K) =   272.02  PRESS =   366.7
 Etot   =   -1888.3423  EKtot   =     349.4743  EPtot      =   -2237.8166
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     729.0549
 EELEC  =   -2283.3201  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     196.5283  VIRIAL  =     145.1890  VOLUME     =    6483.8566
 EPOLZ  =    -683.5514  E3BODY  =       0.0000
 Dipole convergence: rms =  0.874E-03 temperature =   0.08
                                                Density    =       0.9966
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   2000 TIME(PS) =     2.000  TEMP(K) =   292.78  PRESS =   -85.1
 Etot   =   -1856.5639  EKtot   =     376.1420  EPtot      =   -2232.7059
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     693.4576
 EELEC  =   -2253.7662  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     196.9473  VIRIAL  =     208.6256  VOLUME     =    6357.9578
 EPOLZ  =    -672.3973  E3BODY  =       0.0000
 Dipole convergence: rms =  0.951E-03 temperature =   0.10
                                                Density    =       1.0164
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   3000 TIME(PS) =     3.000  TEMP(K) =   289.55  PRESS =   297.8
 Etot   =   -1832.2330  EKtot   =     371.9965  EPtot      =   -2204.2295
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     706.2237
 EELEC  =   -2243.1036  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     185.8996  VIRIAL  =     144.5323  VOLUME     =    6433.3506
 EPOLZ  =    -667.3495  E3BODY  =       0.0000
 Dipole convergence: rms =  0.114E-02 temperature =   0.11
                                                Density    =       1.0045
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   4000 TIME(PS) =     4.000  TEMP(K) =   287.04  PRESS =  -523.0
 Etot   =   -1811.2681  EKtot   =     368.7659  EPtot      =   -2180.0341
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     662.1985
 EELEC  =   -2194.2308  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     179.7066  VIRIAL  =     252.5250  VOLUME     =    6448.4851
 EPOLZ  =    -648.0018  E3BODY  =       0.0000
 Dipole convergence: rms =  0.121E-02 temperature =   0.10
                                                Density    =       1.0021
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   5000 TIME(PS) =     5.000  TEMP(K) =   288.89  PRESS =   506.5
 Etot   =   -1801.2513  EKtot   =     371.1408  EPtot      =   -2172.3921
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     671.0594
 EELEC  =   -2198.4142  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     185.4832  VIRIAL  =     115.9132  VOLUME     =    6361.6763
 EPOLZ  =    -645.0373  E3BODY  =       0.0000
 Dipole convergence: rms =  0.138E-02 temperature =   0.12
                                                Density    =       1.0158
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   6000 TIME(PS) =     6.000  TEMP(K) =   290.11  PRESS =   -49.2
 Etot   =   -1784.5497  EKtot   =     372.7113  EPtot      =   -2157.2610
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     670.2767
 EELEC  =   -2184.4287  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     190.8513  VIRIAL  =     197.8381  VOLUME     =    6574.6064
 EPOLZ  =    -643.1089  E3BODY  =       0.0000
 Dipole convergence: rms =  0.155E-02 temperature =   0.10
                                                Density    =       0.9829
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   7000 TIME(PS) =     7.000  TEMP(K) =   300.43  PRESS =   133.2
 Etot   =   -1780.4511  EKtot   =     385.9677  EPtot      =   -2166.4188
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     683.4580
 EELEC  =   -2206.1865  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     175.4738  VIRIAL  =     156.5338  VOLUME     =    6583.6155
 EPOLZ  =    -643.6903  E3BODY  =       0.0000
 Dipole convergence: rms =  0.159E-02 temperature =   0.12
                                                Density    =       0.9815
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   8000 TIME(PS) =     8.000  TEMP(K) =   286.62  PRESS =   -81.7
 Etot   =   -1773.9235  EKtot   =     368.2267  EPtot      =   -2142.1502
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     647.8820
 EELEC  =   -2160.7641  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     187.1207  VIRIAL  =     198.4779  VOLUME     =    6438.4045
 EPOLZ  =    -629.2682  E3BODY  =       0.0000
 Dipole convergence: rms =  0.170E-02 temperature =   0.11
                                                Density    =       1.0037
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =   9000 TIME(PS) =     9.000  TEMP(K) =   299.06  PRESS =  -144.4
 Etot   =   -1768.8685  EKtot   =     384.2055  EPtot      =   -2153.0741
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     649.4671
 EELEC  =   -2166.3694  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     198.5965  VIRIAL  =     218.6029  VOLUME     =    6417.3863
 EPOLZ  =    -636.1717  E3BODY  =       0.0000
 Dipole convergence: rms =  0.179E-02 temperature =   0.11
                                                Density    =       1.0070
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  10000 TIME(PS) =    10.000  TEMP(K) =   287.85  PRESS =   229.9
 Etot   =   -1768.0981  EKtot   =     369.8089  EPtot      =   -2137.9070
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     656.4243
 EELEC  =   -2167.2908  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     184.8971  VIRIAL  =     152.7772  VOLUME     =    6469.8760
 EPOLZ  =    -627.0404  E3BODY  =       0.0000
 Dipole convergence: rms =  0.188E-02 temperature =   0.12
                                                Density    =       0.9988
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  11000 TIME(PS) =    11.000  TEMP(K) =   283.18  PRESS =   166.1
 Etot   =   -1762.7615  EKtot   =     363.8109  EPtot      =   -2126.5724
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     634.8316
 EELEC  =   -2142.7327  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     185.1765  VIRIAL  =     162.3486  VOLUME     =    6365.6936
 EPOLZ  =    -618.6714  E3BODY  =       0.0000
 Dipole convergence: rms =  0.197E-02 temperature =   0.12
                                                Density    =       1.0151
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  12000 TIME(PS) =    12.000  TEMP(K) =   308.99  PRESS =   170.0
 Etot   =   -1759.1393  EKtot   =     396.9700  EPtot      =   -2156.1093
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     662.4769
 EELEC  =   -2174.5586  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     191.3187  VIRIAL  =     167.6972  VOLUME     =    6436.6396
 EPOLZ  =    -644.0276  E3BODY  =       0.0000
 Dipole convergence: rms =  0.209E-02 temperature =   0.13
                                                Density    =       1.0039
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  13000 TIME(PS) =    13.000  TEMP(K) =   288.20  PRESS =   597.7
 Etot   =   -1758.3364  EKtot   =     370.2587  EPtot      =   -2128.5952
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     649.1582
 EELEC  =   -2150.8231  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     195.4520  VIRIAL  =     112.3399  VOLUME     =    6440.4326
 EPOLZ  =    -626.9303  E3BODY  =       0.0000
 Dipole convergence: rms =  0.211E-02 temperature =   0.12
                                                Density    =       1.0034
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  14000 TIME(PS) =    14.000  TEMP(K) =   306.12  PRESS =  -639.7
 Etot   =   -1751.1836  EKtot   =     393.2790  EPtot      =   -2144.4626
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     609.4246
 EELEC  =   -2136.1200  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     202.2892  VIRIAL  =     290.8631  VOLUME     =    6413.0079
 EPOLZ  =    -617.7671  E3BODY  =       0.0000
 Dipole convergence: rms =  0.221E-02 temperature =   0.12
                                                Density    =       1.0076
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  15000 TIME(PS) =    15.000  TEMP(K) =   299.97  PRESS =   134.7
 Etot   =   -1748.2055  EKtot   =     385.3758  EPtot      =   -2133.5813
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     664.9774
 EELEC  =   -2161.1677  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     177.2393  VIRIAL  =     158.3052  VOLUME     =    6507.9753
 EPOLZ  =    -637.3910  E3BODY  =       0.0000
 Dipole convergence: rms =  0.232E-02 temperature =   0.13
                                                Density    =       0.9929
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  16000 TIME(PS) =    16.000  TEMP(K) =   298.67  PRESS =   -64.0
 Etot   =   -1750.4842  EKtot   =     383.7090  EPtot      =   -2134.1932
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     632.7987
 EELEC  =   -2146.9057  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     187.4777  VIRIAL  =     196.4965  VOLUME     =    6524.4587
 EPOLZ  =    -620.0862  E3BODY  =       0.0000
 Dipole convergence: rms =  0.238E-02 temperature =   0.13
                                                Density    =       0.9904
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  17000 TIME(PS) =    17.000  TEMP(K) =   276.86  PRESS =   709.6
 Etot   =   -1754.2342  EKtot   =     355.6848  EPtot      =   -2109.9190
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     640.5137
 EELEC  =   -2132.1386  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     185.4757  VIRIAL  =      87.9575  VOLUME     =    6364.6249
 EPOLZ  =    -618.2941  E3BODY  =       0.0000
 Dipole convergence: rms =  0.240E-02 temperature =   0.12
                                                Density    =       1.0153
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  18000 TIME(PS) =    18.000  TEMP(K) =   306.87  PRESS =  -318.3
 Etot   =   -1749.5530  EKtot   =     394.2456  EPtot      =   -2143.7985
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     638.0863
 EELEC  =   -2158.9838  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     194.6354  VIRIAL  =     239.2829  VOLUME     =    6495.9306
 EPOLZ  =    -622.9010  E3BODY  =       0.0000
 Dipole convergence: rms =  0.249E-02 temperature =   0.13
                                                Density    =       0.9948
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  19000 TIME(PS) =    19.000  TEMP(K) =   292.49  PRESS =  -423.5
 Etot   =   -1750.6139  EKtot   =     375.7664  EPtot      =   -2126.3803
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     615.8315
 EELEC  =   -2122.3095  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     186.8229  VIRIAL  =     246.1879  VOLUME     =    6492.8161
 EPOLZ  =    -619.9023  E3BODY  =       0.0000
 Dipole convergence: rms =  0.254E-02 temperature =   0.13
                                                Density    =       0.9953
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  20000 TIME(PS) =    20.000  TEMP(K) =   295.26  PRESS =   845.4
 Etot   =   -1750.6955  EKtot   =     379.3240  EPtot      =   -2130.0195
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     675.8523
 EELEC  =   -2166.2741  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     193.8645  VIRIAL  =      74.5327  VOLUME     =    6537.7284
 EPOLZ  =    -639.5976  E3BODY  =       0.0000
 Dipole convergence: rms =  0.260E-02 temperature =   0.14
                                                Density    =       0.9884
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  21000 TIME(PS) =    21.000  TEMP(K) =   283.38  PRESS =   178.8
 Etot   =   -1750.5127  EKtot   =     364.0615  EPtot      =   -2114.5742
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     638.4884
 EELEC  =   -2135.5662  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     188.0717  VIRIAL  =     163.2128  VOLUME     =    6439.8270
 EPOLZ  =    -617.4964  E3BODY  =       0.0000
 Dipole convergence: rms =  0.272E-02 temperature =   0.14
                                                Density    =       1.0034
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  22000 TIME(PS) =    22.000  TEMP(K) =   289.70  PRESS =    43.2
 Etot   =   -1747.6095  EKtot   =     372.1865  EPtot      =   -2119.7960
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     654.5242
 EELEC  =   -2144.0109  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     188.5513  VIRIAL  =     182.3751  VOLUME     =    6622.6486
 EPOLZ  =    -630.3093  E3BODY  =       0.0000
 Dipole convergence: rms =  0.276E-02 temperature =   0.14
                                                Density    =       0.9757
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  23000 TIME(PS) =    23.000  TEMP(K) =   317.39  PRESS =  -457.1
 Etot   =   -1750.0938  EKtot   =     407.7544  EPtot      =   -2157.8483
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     624.7005
 EELEC  =   -2162.1223  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     209.9048  VIRIAL  =     273.2589  VOLUME     =    6419.2265
 EPOLZ  =    -620.4265  E3BODY  =       0.0000
 Dipole convergence: rms =  0.289E-02 temperature =   0.15
                                                Density    =       1.0067
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  24000 TIME(PS) =    24.000  TEMP(K) =   302.18  PRESS =  1078.7
 Etot   =   -1755.4169  EKtot   =     388.2125  EPtot      =   -2143.6294
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     698.5202
 EELEC  =   -2194.3497  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     191.3035  VIRIAL  =      39.7817  VOLUME     =    6505.4384
 EPOLZ  =    -647.7998  E3BODY  =       0.0000
 Dipole convergence: rms =  0.293E-02 temperature =   0.14
                                                Density    =       0.9933
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  25000 TIME(PS) =    25.000  TEMP(K) =   292.66  PRESS =   -95.0
 Etot   =   -1760.4183  EKtot   =     375.9801  EPtot      =   -2136.3984
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     632.9856
 EELEC  =   -2151.5042  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     177.4709  VIRIAL  =     190.5240  VOLUME     =    6366.2936
 EPOLZ  =    -617.8799  E3BODY  =       0.0000
 Dipole convergence: rms =  0.301E-02 temperature =   0.16
                                                Density    =       1.0150
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  26000 TIME(PS) =    26.000  TEMP(K) =   299.36  PRESS =   598.4
 Etot   =   -1757.1228  EKtot   =     384.5987  EPtot      =   -2141.7214
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     670.1455
 EELEC  =   -2182.3732  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     195.3905  VIRIAL  =     112.2404  VOLUME     =    6435.3120
 EPOLZ  =    -629.4938  E3BODY  =       0.0000
 Dipole convergence: rms =  0.298E-02 temperature =   0.15
                                                Density    =       1.0042
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  27000 TIME(PS) =    27.000  TEMP(K) =   301.87  PRESS =  -101.1
 Etot   =   -1760.1502  EKtot   =     387.8135  EPtot      =   -2147.9637
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     620.9682
 EELEC  =   -2146.3696  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     201.6983  VIRIAL  =     215.5115  VOLUME     =    6329.1684
 EPOLZ  =    -622.5623  E3BODY  =       0.0000
 Dipole convergence: rms =  0.302E-02 temperature =   0.15
                                                Density    =       1.0210
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  28000 TIME(PS) =    28.000  TEMP(K) =   300.21  PRESS =   313.7
 Etot   =   -1758.8849  EKtot   =     385.6832  EPtot      =   -2144.5681
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     641.7130
 EELEC  =   -2163.4079  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     191.9923  VIRIAL  =     149.2856  VOLUME     =    6305.1659
 EPOLZ  =    -622.8732  E3BODY  =       0.0000
 Dipole convergence: rms =  0.314E-02 temperature =   0.16
                                                Density    =       1.0249
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  29000 TIME(PS) =    29.000  TEMP(K) =   305.98  PRESS =  -105.5
 Etot   =   -1759.8909  EKtot   =     393.0967  EPtot      =   -2152.9876
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     664.9453
 EELEC  =   -2170.7860  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     200.3483  VIRIAL  =     215.0674  VOLUME     =    6463.4626
 EPOLZ  =    -647.1469  E3BODY  =       0.0000
 Dipole convergence: rms =  0.322E-02 temperature =   0.17
                                                Density    =       0.9998
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  30000 TIME(PS) =    30.000  TEMP(K) =   288.64  PRESS =   519.9
 Etot   =   -1755.1884  EKtot   =     370.8240  EPtot      =   -2126.0124
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     666.7933
 EELEC  =   -2162.2300  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     182.9773  VIRIAL  =     109.0961  VOLUME     =    6581.7392
 EPOLZ  =    -630.5757  E3BODY  =       0.0000
 Dipole convergence: rms =  0.312E-02 temperature =   0.16
                                                Density    =       0.9818
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  31000 TIME(PS) =    31.000  TEMP(K) =   298.92  PRESS =    76.3
 Etot   =   -1759.1129  EKtot   =     384.0305  EPtot      =   -2143.1434
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     647.9863
 EELEC  =   -2158.6315  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     173.3958  VIRIAL  =     162.7200  VOLUME     =    6480.8624
 EPOLZ  =    -632.4983  E3BODY  =       0.0000
 Dipole convergence: rms =  0.319E-02 temperature =   0.16
                                                Density    =       0.9971
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  32000 TIME(PS) =    32.000  TEMP(K) =   294.68  PRESS =   561.8
 Etot   =   -1754.4136  EKtot   =     378.5776  EPtot      =   -2132.9912
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     657.2584
 EELEC  =   -2155.7149  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     189.0244  VIRIAL  =     111.0153  VOLUME     =    6431.4146
 EPOLZ  =    -634.5347  E3BODY  =       0.0000
 Dipole convergence: rms =  0.334E-02 temperature =   0.16
                                                Density    =       1.0048
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  33000 TIME(PS) =    33.000  TEMP(K) =   292.15  PRESS =   131.5
 Etot   =   -1753.6535  EKtot   =     375.3244  EPtot      =   -2128.9779
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     651.2626
 EELEC  =   -2154.0645  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     187.9047  VIRIAL  =     169.4442  VOLUME     =    6503.4987
 EPOLZ  =    -626.1759  E3BODY  =       0.0000
 Dipole convergence: rms =  0.337E-02 temperature =   0.16
                                                Density    =       0.9936
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  34000 TIME(PS) =    34.000  TEMP(K) =   301.00  PRESS =   137.6
 Etot   =   -1756.0671  EKtot   =     386.6968  EPtot      =   -2142.7639
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     645.2867
 EELEC  =   -2161.8916  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     194.0024  VIRIAL  =     175.0993  VOLUME     =    6363.9261
 EPOLZ  =    -626.1591  E3BODY  =       0.0000
 Dipole convergence: rms =  0.348E-02 temperature =   0.17
                                                Density    =       1.0154
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  35000 TIME(PS) =    35.000  TEMP(K) =   318.65  PRESS =  -658.0
 Etot   =   -1753.5093  EKtot   =     409.3784  EPtot      =   -2162.8878
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     631.0106
 EELEC  =   -2169.0428  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     205.4874  VIRIAL  =     297.7448  VOLUME     =    6494.2418
 EPOLZ  =    -624.8556  E3BODY  =       0.0000
 Dipole convergence: rms =  0.334E-02 temperature =   0.19
                                                Density    =       0.9950
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  36000 TIME(PS) =    36.000  TEMP(K) =   310.54  PRESS =   392.4
 Etot   =   -1759.2027  EKtot   =     398.9617  EPtot      =   -2158.1644
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     669.9186
 EELEC  =   -2185.6611  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     189.9526  VIRIAL  =     135.9016  VOLUME     =    6379.2592
 EPOLZ  =    -642.4219  E3BODY  =       0.0000
 Dipole convergence: rms =  0.348E-02 temperature =   0.19
                                                Density    =       1.0130
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  37000 TIME(PS) =    37.000  TEMP(K) =   299.27  PRESS =  -183.9
 Etot   =   -1764.3177  EKtot   =     384.4812  EPtot      =   -2148.7989
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     644.4009
 EELEC  =   -2158.0147  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     189.4902  VIRIAL  =     214.9014  VOLUME     =    6400.6871
 EPOLZ  =    -635.1852  E3BODY  =       0.0000
 Dipole convergence: rms =  0.368E-02 temperature =   0.19
                                                Density    =       1.0096
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  38000 TIME(PS) =    38.000  TEMP(K) =   290.47  PRESS =  -278.3
 Etot   =   -1760.3249  EKtot   =     373.1761  EPtot      =   -2133.5010
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     635.4903
 EELEC  =   -2147.8961  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     197.0595  VIRIAL  =     236.3816  VOLUME     =    6545.0700
 EPOLZ  =    -621.0953  E3BODY  =       0.0000
 Dipole convergence: rms =  0.351E-02 temperature =   0.18
                                                Density    =       0.9873
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  39000 TIME(PS) =    39.000  TEMP(K) =   299.88  PRESS =  -719.4
 Etot   =   -1755.7375  EKtot   =     385.2666  EPtot      =   -2141.0040
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     612.6880
 EELEC  =   -2138.2560  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     205.8882  VIRIAL  =     305.8926  VOLUME     =    6438.2379
 EPOLZ  =    -615.4360  E3BODY  =       0.0000
 Dipole convergence: rms =  0.353E-02 temperature =   0.18
                                                Density    =       1.0037
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  40000 TIME(PS) =    40.000  TEMP(K) =   289.27  PRESS =   160.8
 Etot   =   -1754.7917  EKtot   =     371.6365  EPtot      =   -2126.4282
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     644.2033
 EELEC  =   -2146.7290  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     182.1965  VIRIAL  =     159.5675  VOLUME     =    6518.2860
 EPOLZ  =    -623.9025  E3BODY  =       0.0000
 Dipole convergence: rms =  0.371E-02 temperature =   0.18
                                                Density    =       0.9914
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  41000 TIME(PS) =    41.000  TEMP(K) =   292.00  PRESS =    41.9
 Etot   =   -1759.0875  EKtot   =     375.1408  EPtot      =   -2134.2282
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     640.9300
 EELEC  =   -2149.2493  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     173.3302  VIRIAL  =     167.5281  VOLUME     =    6419.2210
 EPOLZ  =    -625.9090  E3BODY  =       0.0000
 Dipole convergence: rms =  0.366E-02 temperature =   0.18
                                                Density    =       1.0067
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  42000 TIME(PS) =    42.000  TEMP(K) =   295.77  PRESS =   129.5
 Etot   =   -1749.3705  EKtot   =     379.9769  EPtot      =   -2129.3475
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     642.1263
 EELEC  =   -2153.0925  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     174.3520  VIRIAL  =     156.3026  VOLUME     =    6456.1305
 EPOLZ  =    -618.3813  E3BODY  =       0.0000
 Dipole convergence: rms =  0.376E-02 temperature =   0.18
                                                Density    =       1.0009
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  43000 TIME(PS) =    43.000  TEMP(K) =   292.61  PRESS =  -579.8
 Etot   =   -1748.3278  EKtot   =     375.9256  EPtot      =   -2124.2535
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     617.1533
 EELEC  =   -2127.8895  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     180.1458  VIRIAL  =     260.4895  VOLUME     =    6417.4969
 EPOLZ  =    -613.5172  E3BODY  =       0.0000
 Dipole convergence: rms =  0.377E-02 temperature =   0.19
                                                Density    =       1.0069
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  44000 TIME(PS) =    44.000  TEMP(K) =   293.53  PRESS =   132.6
 Etot   =   -1745.0738  EKtot   =     377.1052  EPtot      =   -2122.1791
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     641.8097
 EELEC  =   -2137.8839  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     185.6149  VIRIAL  =     166.8595  VOLUME     =    6552.1914
 EPOLZ  =    -626.1048  E3BODY  =       0.0000
 Dipole convergence: rms =  0.381E-02 temperature =   0.19
                                                Density    =       0.9862
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  45000 TIME(PS) =    45.000  TEMP(K) =   303.40  PRESS =   552.2
 Etot   =   -1742.2774  EKtot   =     389.7796  EPtot      =   -2132.0570
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     659.7053
 EELEC  =   -2159.3031  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     195.5231  VIRIAL  =     118.5567  VOLUME     =    6455.7117
 EPOLZ  =    -632.4591  E3BODY  =       0.0000
 Dipole convergence: rms =  0.392E-02 temperature =   0.20
                                                Density    =       1.0010
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  46000 TIME(PS) =    46.000  TEMP(K) =   307.67  PRESS =   -52.3
 Etot   =   -1740.9536  EKtot   =     395.2710  EPtot      =   -2136.2246
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     632.2724
 EELEC  =   -2148.9163  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     195.7280  VIRIAL  =     202.9557  VOLUME     =    6399.3599
 EPOLZ  =    -619.5808  E3BODY  =       0.0000
 Dipole convergence: rms =  0.394E-02 temperature =   0.20
                                                Density    =       1.0098
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  47000 TIME(PS) =    47.000  TEMP(K) =   307.92  PRESS =    58.4
 Etot   =   -1739.8377  EKtot   =     395.5860  EPtot      =   -2135.4237
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     634.5937
 EELEC  =   -2142.1566  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     210.3196  VIRIAL  =     202.3047  VOLUME     =    6351.3610
 EPOLZ  =    -627.8607  E3BODY  =       0.0000
 Dipole convergence: rms =  0.401E-02 temperature =   0.20
                                                Density    =       1.0174
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  48000 TIME(PS) =    48.000  TEMP(K) =   288.88  PRESS =   413.7
 Etot   =   -1739.3310  EKtot   =     371.1269  EPtot      =   -2110.4580
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     638.8293
 EELEC  =   -2134.8139  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     185.2403  VIRIAL  =     127.1844  VOLUME     =    6500.0695
 EPOLZ  =    -614.4734  E3BODY  =       0.0000
 Dipole convergence: rms =  0.387E-02 temperature =   0.20
                                                Density    =       0.9941
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  49000 TIME(PS) =    49.000  TEMP(K) =   288.66  PRESS =  -260.3
 Etot   =   -1747.4508  EKtot   =     370.8427  EPtot      =   -2118.2935
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     596.8348
 EELEC  =   -2112.8463  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     181.0928  VIRIAL  =     216.3859  VOLUME     =    6280.7189
 EPOLZ  =    -602.2820  E3BODY  =       0.0000
 Dipole convergence: rms =  0.389E-02 temperature =   0.20
                                                Density    =       1.0289
 ------------------------------------------------------------------------------

check COM velocity, temp:        0.000000     0.00(Removed)

 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =   312.80  PRESS =  -406.0
 Etot   =   -1742.0177  EKtot   =     401.8630  EPtot      =   -2143.8807
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     630.5212
 EELEC  =   -2156.9575  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     193.1637  VIRIAL  =     250.0884  VOLUME     =    6493.3231
 EPOLZ  =    -617.4444  E3BODY  =       0.0000
 Dipole convergence: rms =  0.403E-02 temperature =   0.22
                                                Density    =       0.9952
 ------------------------------------------------------------------------------


      A V E R A G E S   O V E R   50000 S T E P S


 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =   293.34  PRESS =   -17.7
 Etot   =   -1765.2343  EKtot   =     376.8651  EPtot      =   -2142.0994
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =     643.9010
 EELEC  =   -2158.5528  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =     188.2216  VIRIAL  =     191.0011  VOLUME     =    6450.7368
 EPOLZ  =    -627.4475  E3BODY  =       0.0000
 Dipole convergence: rms =  0.277E-02 temperature =   0.15
                                                Density    =       1.0019
 ------------------------------------------------------------------------------


      R M S  F L U C T U A T I O N S


 NSTEP =  50000 TIME(PS) =    50.000  TEMP(K) =    13.58  PRESS =   510.5
 Etot   =      31.5575  EKtot   =      17.4472  EPtot      =      25.7380
 BOND   =       0.0000  ANGLE   =       0.0000  DIHED      =       0.0000
 1-4 NB =       0.0000  1-4 EEL =       0.0000  VDWAALS    =      25.1906
 EELEC  =      30.7842  EHBOND  =       0.0000  CONSTRAINT =       0.0000
 EKCMT  =      10.7746  VIRIAL  =      73.7156  VOLUME     =      92.5026
 EPOLZ  =      15.3265  E3BODY  =       0.0000
 Dipole convergence: rms =  0.908E-03 temperature =   0.03
                                                Density    =       0.0136
 ------------------------------------------------------------------------------

|
|>>>>>>>>PROFILE of TIMES>>>>>>>>>>>>>>>>>  
|
|                Ewald setup time           0.10 ( 0.22% of List )
|                Check list validity        4.18 ( 9.25% of List )
|                Map frac coords            0.13 ( 0.29% of List )
|                Grid unit cell             0.08 ( 0.18% of List )
|                Grid image cell            0.08 ( 0.18% of List )
|                Build the list            40.22 (88.91% of List )
|                Other                      0.43 ( 0.96% of List )
|             List time                 45.23 ( 2.85% of Nonbo)
|                Direct Ewald time       1067.28 (69.14% of Ewald)
|                Adjust Ewald time         13.90 ( 0.90% of Ewald)
|                Self Ewald time            0.47 ( 0.03% of Ewald)
|                Finish NB virial           2.43 ( 0.16% of Ewald)
|                   Fill Bspline coeffs       11.73 ( 2.60% of Recip)
|                   Fill charge grid          52.43 (11.60% of Recip)
|                   Scalar sum               100.38 (22.22% of Recip)
|                   Grad sum                 197.38 (43.68% of Recip)
|                   FFT time                  87.39 (19.34% of Recip)
|                   Other                      2.55 ( 0.56% of Recip)
|                Recip Ewald time         451.87 (29.27% of Ewald)
|                Other                      7.60 ( 0.49% of Ewald)
|             Ewald time              1543.55 (97.13% of Nonbo)
|             Other                      0.37 ( 0.02% of Nonbo)
|          Nonbond force           1589.15 (99.48% of Force)
|          Bond energy                0.55 ( 0.03% of Force)
|          Angle energy               0.43 ( 0.03% of Force)
|          Dihedral energy            0.35 ( 0.02% of Force)
|          Noe calc time              0.15 ( 0.01% of Force)
|          Other                      6.87 ( 0.43% of Force)
|       Force time              1597.50 (97.86% of Runmd)
|       Shake time                 8.47 ( 0.52% of Runmd)
|       Verlet update time         9.77 ( 0.60% of Runmd)
|       Dipole update time         7.00 ( 0.43% of Runmd)
|       Ekcmr time                 9.62 ( 0.59% of Runmd)
|    Runmd Time              1632.35 (100.0% of Total)
| Total time              1629.43 (100.0% of ALL  )

| Highest rstack allocated:      46042
| Highest istack allocated:      23328

|     Setup wallclock           3 seconds
|     Nonsetup wallclock     1666 seconds
