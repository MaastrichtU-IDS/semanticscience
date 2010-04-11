// Persistence Of Vision raytracer version 3.5 sample file.
//
//Demonstration of the area_light "orient" keyword
//
// -w320 -h240
// -w800 -h600 +a0.3

#include "colors.inc"

camera {location <50,42,0> direction z*1 look_at <0,2,0>}

//lights
light_source {<0,15,8+3> White*1.5
              area_light x*1.5,z*1.5,4,4 jitter adaptive 2 
              circular
              orient //that's here !
              }

light_source {<0,15,8-30> White*1.5
              area_light x*1.5,z*1.5,4,4 jitter adaptive 2
              }

//objects
#declare With =
union {
 text {ttf "cyrvetic","orient",.05,0}
 text {ttf "cyrvetic","with",.05,0 translate y*1}
 pigment {SteelBlue*2}
 rotate <90,-90,0>
 scale 5
 }

#declare Without =
union {
 text {ttf "cyrvetic","orient",.05,0}
 text {ttf "cyrvetic","without",.05,0 translate y*1}
 pigment {SteelBlue*2}
 rotate <90,-90,0>
 scale 5
 }

#declare Object_4 =
union {
 #declare I=0;
 #while (I < 15)
  box {<0,0,0>,<1,.1,10> translate <-4,I,0>}
 #declare I=I+2;
 #end
rotate y*-20
pigment {OrangeRed}
}

object {With translate <10,8.5,5+3>}
object {Without translate <10,8.5,5-30>}
object {Object_4 translate <0,5,8-30>}
object {Object_4 translate <0,5,8+3>}

//markers to show where the light_sources are
sphere {<0,15,8+3>,.4 pigment {Green*2} finish {diffuse 0 ambient 1} no_shadow}
sphere {<0,15,8-30>,.4 pigment {Green*2} finish {diffuse 0 ambient 1} no_shadow}

//fill light
light_source {<100,150,10> White*.5 shadowless}

//context
fog {distance 200 Wheat*.5}
plane {y,0 pigment {rgb <.9,.9,1>*1.2}}
plane {x,-10 pigment {rgb <.9,.9,1>*1.2}}
box {<45,0,-.1>,<-150,40,.1> pigment {SteelBlue}}
