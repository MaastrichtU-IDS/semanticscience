// Persistence Of Vision raytracer version 3.5 sample file.
//
//Demonstration of the "parallel" light modifier
//
// -w320 -h240
// -w800 -h600 +a0.3

#include "colors.inc"

camera {location <100,60,0> direction z*1 look_at <0,20,0>}

#declare I=-20;
#while (I < 20)
  box {<0,50,0+I>,<40,50.5,3+I> pigment {Red}}
  #declare I=I+8;
#end

plane {y,0 pigment {White}}
plane {x,0 pigment {White}}

light_source {<20,70,0> White*1.5 parallel point_at <10,0,20>}
light_source {<20,70,0> SteelBlue*.8}
