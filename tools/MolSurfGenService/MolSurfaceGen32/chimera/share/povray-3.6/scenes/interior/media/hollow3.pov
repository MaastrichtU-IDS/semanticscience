//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: hollow3.pov
//	Author: Dieter Bayer
//	Description:
// This scene shows a hollow, checkered sphere filled with fire.
//
// -w320 -h240
// -w800 -h600 +a0.3
//
//*******************************************

global_settings {
  max_trace_level 5
}

#include "colors.inc"

camera {
	location <-1.5, 30, -150>
	look_at <0, 25, 35>
	angle 35
}

background { color rgb <0.2, 0.4, 0.8> }

light_source { <100, 100, -200> color White }

plane { y, 0
	pigment { NeonBlue }
	finish {reflection 0.15}
	hollow
}

sphere {< 0, 0, 0>, 1
	pigment {
		checker YellowGreen, rgbt<1, 1, 1, 0.7>
		scale <0.4, 0.5, 0.2>
		rotate <90, 0, -90>
	}
	finish {
		brilliance 8
		phong 1
		phong_size 100
	}
	interior {
		media {
			emission 0.05
			intervals 1
			samples 5
			method 3
			density {
				spherical
				ramp_wave
				turbulence 1
				color_map {
					[0.0 color rgb <0, 0, 0>]
					[0.1 color rgb <1, 0, 0>]
					[1.0 color rgb <1, 1, 0>]
				}
			}
		}
	}
	scale 25
	translate 25*y
	hollow
}

