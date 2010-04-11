// Persistence Of Vision raytracer version 3.5 sample file.
// File: glass2.pov
// Desc: glass material and photons sample
// Date: June-August 2001
// Auth: Christoph Hormann

// -w320 -h160
// -w512 -h256 +a0.3

#version 3.5;
#include "colors.inc"
#include "glass.inc"

global_settings {
  assumed_gamma 1
  max_trace_level 25

  photons {
    spacing 0.05
    autostop 0
    jitter 0
  }
}

camera {
  location    <20, 4.6, 10>
  right       2*x
  look_at     <0, 2.4, 0>
  angle       38
}

light_source {
  <-10, 7, 18>
  color rgb <1.3, 1.2, 1.1>
  fade_power 2
  fade_distance 45

  photons {
    reflection on
    refraction on
  }
}
#declare T_Wall=
  texture {
    pigment {
      color rgb <0.98, 0.96, 0.90>
    }
    finish {
      diffuse 0.7
      brilliance 0.6
    }
  }
  
cylinder {
  0*y, 9*y, 30

  texture { T_Wall }
  hollow on
}

#declare Height=2.4;

#declare ObjX=
intersection {
  merge {
    blob {
      threshold 0.25
      cylinder { -Height*y,  Height*y,  0.7, 1 }
      cylinder { <0, 2, 0.6>,  <0, 2, -0.6>,  0.25, 1 }
      cylinder { <0.5, 2.4, 0>,  <-0.5, 2.4, 0>,  0.4, -1 }

      sturm
    }

    box { <-1.5, 0, -0.3>, <1.5, 1.2, 0.3> }
    cylinder { <-1.5,   0, 0>,  <-1.5, 1.2, 0>,  0.3 }
    cylinder { < 1.5,   0, 0>,  < 1.5, 1.2, 0>,  0.3 }
    cylinder { <-1.5, 1.2, 0>,  < 1.5, 1.2, 0>,  0.3 }
    sphere { <-1.5, 1.2, 0>,  0.3 }
    sphere { < 1.5, 1.2, 0>,  0.3 }
    scale 2
  }
  plane { -y, 0.001 }
}

#declare Col=color rgb <0.35, 0.65, 0.85>;

object {
  ObjX
  material {
    texture {
      pigment { color Col_Glass_Clear }
      finish { F_Glass6 }
    }
    interior {
      I_Glass_Exp(2)
      fade_color Col
    }
  }
  photons {
    target
    reflection on
    refraction on
    collect off
  }
}

