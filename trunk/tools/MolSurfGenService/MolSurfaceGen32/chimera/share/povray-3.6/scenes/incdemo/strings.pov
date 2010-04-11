//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: strings.pov
//	Author: Chris Huff
//	Description: A demo of the string macros in strings.inc.
//	This file will not render an image, check the debug messages
//	for the results.
//
// -f
//
//*******************************************

#include "strings.inc"
#version 3.5;


#debug concat("\n",CRGBFTStr(color rgbft <0.2, 0.3, 0.4, 0.5, 0.6>, 5, 5),"\n")
#debug concat(CRGBStr(color rgb <0.2, 0.3, 0.4>, 5, 5),"\n")

#debug concat(Triangle_Str(<0, 0, 0>, <1, 0, 0>, <0.5, 1, 0>),"\n")
#debug concat(Smooth_Triangle_Str(<0, 0, 0>, <-0.2,-0.1,-1>, <1, 0, 0>, <0.2,-0.1,-1>, <0.5, 1, 0>, <0, 0.2,-1>),"\n\n")

//*******************************************

