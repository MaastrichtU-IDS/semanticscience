# -----------------------------------------------------------------------------
# Vertex and fragment shaders code in OpenGL Shading Language (GLSL).
# Provides per-pixel lighting that matches Chimera's two light model.
# Provides angle dependent transparency so edge-on surfaces are more opaque.
#
vShader = \
'''
%s
varying vec3 N;
varying vec3 v;

void main(void)
{
  v = vec3(gl_ModelViewMatrix * gl_Vertex);
  N = normalize(gl_NormalMatrix * gl_Normal);

  gl_Position = ftransform();
  gl_FrontColor = gl_Color;

#ifdef USE_FOG
  gl_FogFragCoord = abs(v.z);
#endif

#ifdef USE_CLIP_VERTEX
  gl_ClipVertex = gl_ModelViewMatrix * gl_Vertex;
#endif
}
'''

# -----------------------------------------------------------------------------
# Fragment shader should have fogEnabled set to 0.0 or 1.0 by the code that
# installs the shader.
#
fShader = \
'''
%s
uniform float fogEnabled;
varying vec3 N;
varying vec3 v;

void main (void)
{
  const int kl = 1;  // Chimera key light is 1, fill light is 0.
  const int fl = 0;
  vec3 N1 = normalize(N);
  vec3 L = normalize(gl_LightSource[kl].position.xyz);  // Light at infinity.
  vec3 Lf = normalize(gl_LightSource[fl].position.xyz); // Light at infinity.
  vec3 E = normalize(-v);      // In eye coordinates eye position is (0,0,0).
  vec3 R = normalize(-reflect(L,N1)); 

  // ambient
  vec4 Iamb = gl_FrontLightProduct[kl].ambient;  // Chimera default ambient = 0

  // diffuse
  vec4 Idiff = gl_Color * (gl_LightSource[kl].diffuse * max(dot(N1,L),0.0)
                         + gl_LightSource[fl].diffuse * max(dot(N1,Lf),0.0));

  // specular
  vec4 Ispec = gl_FrontLightProduct[kl].specular 
                  * pow(max(dot(R,E),0.0),0.3*gl_FrontMaterial.shininess);

  // scene
  vec4 Iscene = gl_Color * gl_LightModel.ambient;

  // transparency
  float a = gl_Color.a;
#ifdef USE_ANGLE_DEPENDENT_TRANSPARENCY
  a = 1.0 - pow(max(1.0-a,0.0), 1.0/max(abs(N1.z),0.01));
#endif

  // total color
  vec3 Ifrag = Iscene.rgb + Iamb.rgb + Idiff.rgb + Ispec.rgb;

#ifdef USE_FOG
  // fog
  float fog = clamp((gl_FogFragCoord - gl_Fog.start) * gl_Fog.scale, 0.0, 1.0);
  Ifrag = mix(Ifrag, gl_Fog.color.rgb, fogEnabled * fog);
#endif

  // final color
  gl_FragColor = vec4(Ifrag, a);
}
'''

# -----------------------------------------------------------------------------
#
mode = {
  'USE_FOG': True,
  'USE_ANGLE_DEPENDENT_TRANSPARENCY': True,
  'USE_CLIP_VERTEX': True
  }
import chimera
if not chimera.nogui and chimera.opengl_vendor().startswith('ATI'):
  # On ATI drivers this slows the code about 10x by switching to software
  # rendering even when clip planes are not used.  This code is necesary
  # in GLSL for oblique clip planes but is not required on some ATI
  # systems (Mac Radeon 9800 pro works, iMac Radeon X1600 works (10.4.11),
  # MacBook Pro radeon X1600 does not work when zooming (10.5.6)).
  mode['USE_CLIP_VERTEX'] = False

defs = '\n'.join([('#define %s 1' % s) for s,u in mode.items() if u])
vShader = vShader % defs
fShader = fShader % defs
