// Persistence Of Vision raytracer version 3.5 sample file.
// Demo scene for the "double_illuminate" object modifier
//
// -w320 -h240
// -w800 -h600 +a0.3

#include "colors.inc"
#include "thingy.inc"

camera {location <100,100,100> direction z*1 look_at <0,0,0>}

object {Thingy
        scale .4 translate <-60,0,-10> pigment {rgb <1,1,.5>}
        no_reflection
        }

box {<0,0,1>,<.1,60,60> pigment {White filter .7} double_illuminate}
box {<0,0,-1>,<.1,60,-60> pigment {White filter .7}}

plane {y,0 pigment {SteelBlue}}

text {ttf "cyrvetic","double_illuminate",.05,0 scale 10 rotate <90,-180,0> translate <80,.1,20> pigment {rgb <1,1,.5>} finish {ambient 1 diffuse 0}}
text {ttf "cyrvetic","(default)",.05,0 scale 10 rotate <90,-180,0> translate <45,.1,-20> pigment {rgb <1,1,.5>} finish {ambient 1 diffuse 0}}


light_source {<-200,30,0> White*1.5}
light_source {<400,500,300> White shadowless}
