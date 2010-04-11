// Persistence Of Vision raytracer version 3.5 sample file.
//
// -w320 -h240
// -w800 -h600 +a0.3

#include "colors.inc"

camera {location <2,3,-10> direction z*1 look_at <-2,2,0>}

plane {y,0 pigment {White} }
plane {z,0 pigment {SteelBlue} hollow on }

#declare Object1 =
union {
	torus {2 .1 rotate <100,10,0> translate z*1}
	text {ttf "cyrvetic.ttf","projected",.1,0}
	text {ttf "cyrvetic.ttf","through",.1,0 translate y*-1}
	scale .4 translate <-1,3,-7>
}

object {Object1 pigment {YellowGreen}}

light_source {<0,4,-10> White*2 projected_through {Object1}}

light_source {<0,3,-9> White*1 shadowless}
