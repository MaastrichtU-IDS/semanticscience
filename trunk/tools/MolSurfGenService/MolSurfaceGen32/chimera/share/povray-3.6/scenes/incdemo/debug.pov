//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: debug.pov
//	Last updated: 2001.4.26
//	Author: Chris J. Huff
//	Description:
//
// -w320 -h240
// -w800 -h600 +a0.3
//
//*******************************************

#include "colors.inc"
#include "debug.inc"
#version 3.5;
//-------------------------------------------
global_settings {
	assumed_gamma 1
}

#declare CamPos = < 2, 3.5,-8>;

camera {
	location CamPos
	up y*image_height/image_width  right x
	angle 35
	look_at < 0, 1, 0>
}

light_source {CamPos color Gray25}
light_source {<-50, 150,-100>, color White}

box {<-100,-1,-100>, < 100, 0, 100>
	texture {
		pigment {checker color Gray50, color White}
	}
}
//*******************************************
Set_Debug(on)
Debug_Message("\n starting debug.inc test")

sphere {< 0, 1, 0>, 1
	texture {
		pigment {checker color Blue, color Green scale 0.5}
	}
}

Debug_Message("debug.inc test finished \n")
//*******************************************

