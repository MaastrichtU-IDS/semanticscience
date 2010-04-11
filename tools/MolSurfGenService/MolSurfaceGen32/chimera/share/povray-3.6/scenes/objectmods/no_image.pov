// Persistence Of Vision raytracer version 3.5 sample file.
// Demo scene for the "no_image" object modifier
//
// -w320 -h240
// -w800 -h600 +a0.3

#include "colors.inc"
#include "thingy.inc"

camera {location <100,100,100> direction z*1 look_at <0,0,0>}

plane {y,0 pigment {SteelBlue}}

object {Thingy
        scale .4 translate <-40,0,30> pigment {rgb <1,1,.5>}
        no_image
        }

object {Thingy
        scale .4 translate <40,0,30> pigment {rgb <1,.5,.5>}
        }

plane {z,0 pigment {SteelBlue} finish {reflection {.5}} normal {bumps .02 scale 5}}

text {ttf "cyrvetic","no_image !",.05,0 scale 15 rotate <90,-90,0> translate <-30,.1,20> pigment {rgb <1,1,.5>} finish {ambient 1 diffuse 0}}


light_source {<400,500,130> White*2}
