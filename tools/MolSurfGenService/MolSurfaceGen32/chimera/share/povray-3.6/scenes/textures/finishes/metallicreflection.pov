// Persistence Of Vision raytracer version 3.5 sample file.
// This file demonstrates the effect of metallic reflection,
// formerly controlled by the "reflect_metallic" keyword
//
// -w320 -h240
// -w800 -h600 +a0.3

global_settings { 
  max_trace_level 5
}

#include "colors.inc"

camera {
	location <15,8,1>
	direction z*1.2
	look_at <0,2,0>
}

fog {Blue+Gray70 distance 200}

plane {y, 0
	pigment {crackle
		color_map {
			[0 Black]
			[1 Gray80]
		}
	}
}

sphere {<-2,3,-6>,3 pigment {OrangeRed} finish {reflection {0.0}}}
sphere {<0,3,0>,3   pigment {OrangeRed} finish {reflection {0.5}}}
sphere {<-2,3,6>,3  pigment {OrangeRed} finish {reflection {0.5 metallic}}}

text {ttf "cyrvetic.ttf","refl. 0.0 | refl. 0.5 | refl. 0.5",.1,0
	rotate <0,-90,90>
	translate <4,.05,-6>
	pigment {White}
}
text {ttf "cyrvetic.ttf","+ reflect_metallic",.1,0
	scale .6
	rotate <0,-90,90>
	translate <5,.03,2>
	pigment {White}
}

light_source {<400,500,300> White*2}
