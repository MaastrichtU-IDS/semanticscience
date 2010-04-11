// Demo scene for povray 3.5
// Features Gaussian distribution and use of trace function
// Composed by Greg M. Johnson 2001
// Uses a macro by Rico Reusser.
//
// -w320 -h240
// -w800 -h600 +a0.3

#declare UseRadiosity = no;
#declare S = seed(20173);
#declare CompRadius=0.05;//radius of blob components;
#declare CompNum=7500;//number of blob components

#include "colors.inc"
#if(UseRadiosity)
	global_settings {
		radiosity {
			pretrace_start 0.04
			pretrace_end 2/300
			count 400
			recursion_limit 2
			nearest_count 1
			error_bound 0.2
		}
	}

	#default {finish { ambient 0}}
#else
	light_source {<0, 200, -100> colour rgb 1.5}
#end


//This macro created by Rico Reusser <reu1000@chorus.net>
#declare e = 2.718281828459;
#macro Gauss(RSR)
	sqrt(-2*log(rand(RSR))/log(e))*cos(2*pi*rand(RSR))
#end


plane {y,-0.9105  pigment {White}}


#declare Norm=<0,0,0>;//This variable is used to hold the normal vector obtained
//using trace(). This vector is then used to determine whether an intersection was found.
#declare Posy=array[CompNum]
#declare Posy[0]=<Gauss(S),0,Gauss(S)>;
#declare Ally=sphere {Posy[0], CompRadius}//This variable will hold a collection of spheres,
//one for each blob component. The algorithm checks against this object to decide
//if a component is "on top of" another.

#declare N=1;
#while(N<CompNum)
	#declare Test=<Gauss(S),0,Gauss(S)>;
	#declare Tracey=trace(Ally,Test+100*y,-y,Norm);

	#if (Norm.x = 0 & Norm.y = 0 & Norm.z = 0)
		#declare Posy[N]=Test;
		//put the new component at y=0
	#else
		#declare Posy[N]=Tracey+Norm*CompRadius;
		//put the new component at a point "above" the one it hit
		//The algorithm actually uses the normal to compute the position
	#end

	//Add new sphere to union
	#declare Ally=
	union {object {Ally}
		sphere {Posy[N], CompRadius}
	}

	#if(mod(N,1000) = 0)
		#debug concat(str(N,4,0), "\n")
	#end

	#declare N=N+1;
#end

blob {
	threshold 0.5

	#declare N=0;
	#while(N<CompNum)
		sphere {Posy[N], CompRadius*2.85, 1}
		#declare N=N+1;
	#end
	pigment {rgb <0.2,1,0.1>}
}


background {White}

sphere {<0.5,0,0>, 0.5
	inverse
	pigment {
		gradient x
		pigment_map {
			[0.0   rgb 0]
			[0.995   rgb 0.04]
			[1.0   rgb 2]
		}
	}
	finish {ambient 20}
	translate <-0.5,0,0>
	scale 500
}

camera {
	location <0,3,-15>
	look_at <0,0,0>
	angle 20
}

