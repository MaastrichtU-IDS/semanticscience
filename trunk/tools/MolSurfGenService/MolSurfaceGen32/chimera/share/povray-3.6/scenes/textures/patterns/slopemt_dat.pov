// Persistence Of Vision raytracer version 3.5 sample file.
// File: slopemt_dat.pov
// Date: August 30 2001
// Auth: Rune S. Johansen
// Desc: Render this file and then render SLOPEMT.POV.
// 
// +w400 +h400

global_settings {noise_generator 1 hf_gray_16}

camera {
   location 22*y
   up y
   right x
   look_at 0
}

light_source {y, color 1}

plane {
   y, 0
   texture {
      pigment {
         wrinkles
         scale 0.8
         color_map {
            [0.0, color rgb 0.3]
            [1.0, color rgb 1.6]
         }
      }
      finish {ambient 0 diffuse 1}
   }
   texture {
      pigment {
         spherical translate -0.2*x
         color_map {
            [0.0, color rgb 1 transmit 1.0]
            [0.3, color rgb 1 transmit 0.3]
            [1.0, color rgb 1 transmit 0.0]
         }
      }
      finish {ambient 0 diffuse 1}
   }
}
