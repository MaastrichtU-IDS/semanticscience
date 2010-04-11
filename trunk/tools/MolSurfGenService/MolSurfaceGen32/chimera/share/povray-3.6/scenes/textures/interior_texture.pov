// Persistence Of Vision raytracer version 3.5 sample file.
// This file demonstrates the "interior_texture" feature
//
// -w320 -h240
// -w800 -h600 +a0.3

#include "colors.inc"

camera {location <100,50,50> direction z*1.2 look_at <0,25,0>}

plane {y,0 pigment {White}}

//--------------declaring two "peel" textures
#declare Texture_1 =
texture {
  pigment {
   spiral1 1
   color_map {
    [0.0 White]
    [0.2 Wheat]
    [0.4 Orange]
    [0.4 Clear]
    [1.0 Clear]
   }
   scale 5
   }
  normal {bumps .3 scale .2}
  }
#declare Texture_2 =
texture {
  pigment {
   spiral1 1
   color_map {
    [0.0 Blue]
    [0.2 Red]
    [0.6 YellowGreen]
    [0.6 Clear]
    [1.0 Clear]
   }
   scale 5
   }
  normal {bumps .3 scale .2}
  }

//--------making spheres with different inside/outside textures

sphere {<0,25,-30>,25
        texture {Texture_1}
        interior_texture {Texture_2}
        }

sphere {<0,25,30>,25
        texture {pigment {rgb <1,0,.5>}}
        interior_texture {pigment {rgb <.4,.7,.2>}}
        clipped_by {box {<-50,20,-50>,<50,35,50> inverse}}
        }

light_source {<40,500,300> White*2}
fog {White distance 600}
