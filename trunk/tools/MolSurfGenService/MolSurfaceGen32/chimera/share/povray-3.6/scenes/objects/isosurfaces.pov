//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: isosurfaces.pov
//	Last updated: 8/5/01
//	Author: Chris Huff
//	Description: Various isosurfaces.
//	From left to right, top to bottom:
//	1: simple plane
//	2: simple sphere
//	3: simple cylinder
//	4: parabolic (like a headlight reflector)

//	5: parallel ripples on a plane
//	6: radial ridges on a sphere
//	7: a bumpy cylinder
//	8: a potato chip

//	9: radial ripples on a plane
//	10: dog chew toy
//	11: simple cone (cylinder with varying radius)
//		This can be made single-ended, replace abs(y) with max(y, 0).
//	12: a kind of spindle shape
//
// -w320 -h240
// -w800 -h600 +a0.3
//
//*******************************************

#version 3.5;

#include "colors.inc"
#include "functions.inc"

//-------------------------------------------
global_settings {
	assumed_gamma 1
}

#declare CamLoc = < 0, 0,-10>;

camera {
	location CamLoc
	look_at < 0, 0, 0>
	angle 45
}

light_source {CamLoc color White*0.35}
light_source {<-50, 150,-75> color White}

box {<-4,-3, 1>, < 4, 3, 2>
	texture {
		pigment {checker color rgb < 0.05, 0, 0.35>, color White}
		finish {ambient 0 diffuse 1}
	}
}
//-------------------------------------------

#declare IsoFinish =
finish {
	ambient 0 diffuse 1
	specular 1 roughness 0.02
	brilliance 2
}

isosurface {
	function {y}
	threshold 0
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	open
	texture {
		pigment {color Red}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate <-3, 2, 0>
}
isosurface {
	function {sqrt(x*x + y*y + z*z) - 1}
	threshold 0
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	texture {
		pigment {color Red}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate <-1, 2, 0>
}
isosurface {
	function {sqrt(x*x + z*z) - 1}
	threshold 0
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	texture {
		pigment {color Red}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate < 1, 2, 0>
}


isosurface {
	function {y - sin(x*4*pi)*0.1}
	threshold 0
	max_gradient 1.4
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	open
	texture {
		pigment {color Green}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate <-3, 0, 0>
}
//atan(x, z) = angle around y axis in radians
isosurface {
	function {
		sqrt(x*x + y*y + z*z) - 0.9
		+ sin(12*atan2(x, z))*0.1
	}
	threshold 0
	max_gradient 150
	contained_by {sphere {< 0, 0, 0>, 1}}
	texture {
		pigment {color Green}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate <-1, 0, 0>
}
isosurface {
	function {
		sqrt(x*x + z*z) - 1
		+ f_noise3d(x*3, y*3, z*3)*0.25
	}
	threshold 0
	max_gradient 2
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	texture {
		pigment {color Green}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate < 1, 0, 0>
}



isosurface {
	function {y - cos(sqrt(x*x + z*z)*4*pi)*0.1}
	threshold 0
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	max_gradient 2
	open
	texture {
		pigment {color Blue}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate <-3,-2, 0>
}

//atan(x, z) = angle around y axis in radians
isosurface {
	function {
		sqrt(x*x + y*y + z*z) - 0.9
		+ sin(12*atan2(x, z))*sin(8*atan2(y, sqrt(x*x + z*z)))*0.1
	}
	threshold 0
	max_gradient 8.5
	contained_by {sphere {< 0, 0, 0>, 1}}
	texture {
		pigment {color Blue}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate <-1,-2, 0>
}
isosurface {
	function {sqrt(x*x + z*z) - abs(y)}
	threshold 0
	max_gradient 1.4
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	texture {
		pigment {color Blue}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate < 36,-24, 0>
	translate < 1,-2, 0>
}

isosurface {
	function {y - (x*x + z*z)*0.5}
	threshold 0
	max_gradient 1.5
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	open
	texture {
		pigment {color Yellow}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36, 24, 0>
	translate < 3, 2, 0>
}

isosurface {
	function {y - x*x + z*z}
	threshold 0
	max_gradient 2.3
	contained_by {sphere {< 0, 0, 0>, 1}}
	open
	texture {
		pigment {color Yellow}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate <-36,-24, 0>
	translate < 3, 0, 0>
}

isosurface {
	function {x*x + z*z - y*y - 0.25}
	threshold 0
	max_gradient 3.5
	contained_by {box {<-1,-1,-1>, < 1, 1, 1>}}
	texture {
		pigment {color Yellow}
		finish {IsoFinish}
	}
	scale 1/vlength(1)
	rotate < 36,-24, 0>
	translate < 3,-2, 0>
} 

//*******************************************

