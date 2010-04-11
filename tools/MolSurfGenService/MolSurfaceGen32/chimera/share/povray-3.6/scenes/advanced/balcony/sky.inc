// Persistence Of Vision Ray Tracer Include File
// File: sky.inc
// Vers: 3.5
// Desc: sky for 'balcony.pov' demonstration scene
// Date: July/August 2001
// Auth: Christoph Hormann

/*%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*/

#version 3.5;

#local P_Clouds=
pigment {
   gradient z
   pigment_map {
     [ 0.0 color rgbt 1]
     [ 0.1
       bozo
       color_map {
         [0.0 color rgbt < 0.85, 0.88, 0.94, 0.0>]
         [0.15 color rgbt < 0.91, 0.96, 0.99, 0.0>]
         [0.35 color rgbt < 0.91, 0.96, 0.99, 1.0>]
       }
       turbulence 0.75
       lambda 2.4
       omega 0.6
       octaves 8
       scale <0.4,0.4,0.15>
     ]
     [ 0.4
       bozo
       color_map {
         [0.0 color rgbt < 0.85, 0.88, 0.94, 0.0>]
         [0.15 color rgbt < 0.91, 0.96, 0.99, 0.0>]
         [0.35 color rgbt < 0.91, 0.96, 0.99, 1.0>]
       }
       turbulence 0.75
       lambda 2.4
       omega 0.6
       octaves 8
       scale <0.4,0.4,0.15>
     ]
     [ 0.65 color rgbt 1]

   }
   rotate 10*z
}


#local Tex_Sky =
texture {
   pigment {
     function { abs(z) }
     color_map {
       [0.0 color rgb < 0.640, 0.685, 0.800 >]
       [0.3 color rgb < 0.400, 0.550, 0.900 >]
     }
     turbulence 0.05
   }

   finish {
     diffuse 0
     ambient 1
   }
}
texture {
   pigment { P_Clouds }
   finish {
     diffuse 0
     ambient 1
   }
}


sphere {
  <0, 0, 0>, 1
  texture { Tex_Sky }
  scale<1000000, 1000000, 300000>
  no_shadow
  hollow on
  photons{ collect off }
}

/*%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*/
