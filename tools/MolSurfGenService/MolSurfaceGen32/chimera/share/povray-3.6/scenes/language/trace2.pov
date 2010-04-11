//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: trace2.pov
//	Last updated: 8/25/01
//	Author: Chris Huff
//	Description: pins on a height field...animated.
//
// -w320 -h240
// -w800 -h600 +a0.3
//
//*******************************************

#declare GridXRes = 16;
#declare GridZRes = 16;
// Total # of pins will be GridXRes*GridZRes...be careful
//not to use too high of a number.
#declare PinHeight = 0.25;

#version 3.5;

#include "functions.inc"
#include "math.inc"
#include "consts.inc"
#include "colors.inc"

//-------------------------------------------
global_settings {
	assumed_gamma 1
}

#default {finish {ambient 0 diffuse 1}}

#declare CamLoc = < 3, 4,-5>;

camera {
	location CamLoc
	look_at < 0, 0, 0>
	angle 24
}

light_source {CamLoc color White*0.35}
light_source {<-50, 150,-75> color White}
//-------------------------------------------

#declare Land =
isosurface {
	function {y + f_noise3d(x, y+clock*2, z)}
	threshold 0
	max_gradient 1.75
	contained_by {box {<-1.1,-1,-1.1>, < 1.1, 1, 1.1>}}
	translate y*0.75
}

union {
	#declare J = 0;
	#while(J < GridXRes)
		#declare K = 0;
		#while(K < GridZRes)
			#declare stPt = <2*J/(GridXRes-1) - 1, 10, 2*K/(GridZRes-1) - 1>;
			#declare iNorm = y;
			#declare iPt = trace(Land, stPt, -y, iNorm);
			#if(!VZero(iNorm))
				cylinder {iPt, iPt + iNorm*PinHeight, 0.01}
			#end
			#declare K = K + 1;
		#end
		#declare J = J + 1;
	#end
	texture {
		pigment {color Green}
		finish {
			specular 1
		}
	}
}

object {Land
	texture {
		pigment {color White}
		finish {
			specular 1
		}
	}
}
//*******************************************

