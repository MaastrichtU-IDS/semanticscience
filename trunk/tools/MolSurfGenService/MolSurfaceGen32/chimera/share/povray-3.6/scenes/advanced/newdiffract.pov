//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: newdiffract.pov
//	Author: Modified by Chris Huff, original author unknown
//	Description: A collection of glass objects, using photons
//and dispersion.
//
// -w320 -h240
// -w800 -h600 +a0.3
//
//*******************************************

#include "colors.inc"
#include "woods.inc"

#declare Photons = on;

#declare Interior =
interior {
	fade_distance 2
	fade_power 3
	ior 1.45
	dispersion 0.1//far outside the usual range, but produces interesting results
	dispersion_samples 12
}
#macro PhotonBlock()
	#if(Photons)
		photons {
			target
			collect off
			reflection off
			refraction on
		}
	#end
#end

#declare Intensity = 20;
#declare L_Fade_Distance = 20;
#declare L_Fade_Power = 2;

#declare Area_Light=off;
#declare ALL = 8;//area light height (width?)
#declare ALW = 8;//area light width
#declare ALR = 6;//area light resolution


global_settings {
	assumed_gamma 1
	max_trace_level 5
	#if(Photons)
		photons {spacing 0.02}
	#end
}

#default {finish {ambient 0}}

camera {
	angle 45
	location  < 5,-18, 6>
	direction < 0, 0, 1.6542>
	sky       z  // Use right handed-system!
	up        z  // Where Z is up
	right     x*image_width/image_height
	look_at   < 0, 0,-2.75>
}

light_source {<-50, 100, 65>, color White*Intensity
	#if(Area_Light)
		area_light x*ALL, z*ALW, ALR, ALR
		adaptive 1
		jitter
	#end
	fade_distance L_Fade_Distance
	fade_power L_Fade_Power
	#if(Photons)
		photons {refraction on reflection off}
	#end
}

sky_sphere {
	pigment {
		gradient y
		color_map {
			[0.0 color Gray10]
			[1.0 color Gray30]
		}
	}
}

#declare GlassTex =
texture {
	pigment {color rgbf <1, 1, 1, 1>}
	finish {
		reflection 0.05
		specular 1
		roughness 0.001
		metallic on
//		irid {0.65             // contribution to overall color
//			thickness 0.8    // affects frequency, or "busy-ness"
//			turbulence 0.1   // Variance in film thickness
//		}
	}
}

union {
	cylinder {<-3,0,0>, <3,0,0>, 0.3}
	torus {1, 0.25 rotate z*90}
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
	translate < 0,-5,-0.75>
}

cylinder {<-0.5,0,0>, < 0.5,0,0>, 0.3 translate < 2,-5,-1.7>
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
}

torus {1.25, 0.25 rotate x*90 translate < 5,-6.5,-1.75>
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
}

box { <-1, -1, -1>, <1, 1, 1>
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()

	scale <3.0, 0.5, 0.5>
	translate  -1.75*z
	rotate x*45
	translate  -1.5*y
}

sphere { <0,0,0>,1
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
	translate < 5, 3,-1>
}
sphere { <0,0,0>,1
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
	translate  <0,3.0, -0.5>
}
sphere { <0,0,0>,1
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
	translate  <-3.0, 3.0, -1>
}
cone { 0, 1, -2*z, 0
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
	translate  <-4.0, 0.3, 0>
}
cone { 0, 1, -2*z, 0
	texture {GlassTex}
	interior {Interior}
	PhotonBlock()
	translate  <4.0, 0.3, 0>
}

plane {z, -2
	pigment {color Gray60}
}
