#ifndef Chimera_GfxInfo_h
# define Chimera_GfxInfo_h

# ifdef _WIN32
// alway include windows.h on Microsoft Windows
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
# else
#  define APIENTRY
# endif
# ifdef GFXINFO_AGL
// want our glext.h because it is newer
#  define GL_GLEXT_LEGACY
# endif
# include <GL/gl.h>
// want prototype typedefs from our glext.h
# undef __glext_h_
# undef GL_VERSION_1_2
# undef GL_VERSION_1_3
# undef GL_VERSION_1_4
# undef GL_VERSION_1_5
# undef GL_VERSION_2_0
# undef GL_VERSION_2_1
# undef GL_VERSION_3_0
# undef GL_VERSION_3_1
# undef GL_VERSION_3_2
# include <GL/glext.h>

# ifdef GFXINFO_WGL
#  include <GL/wglext.h>
# endif

# ifdef GFXINFO_X11
#  include <GL/glx.h>
// TODO: include <GL/glxext.h> when GLXFBConfig is defined
#  undef Always
#  ifndef GLX_VERSION_1_3
typedef struct __GLXFBConfigRec* GLXFBConfig;
#  endif
# endif

# ifdef GFXINFO_AGL
//extern double scalb(double x, long n);
// agl.h includes QuickDraw.h which defines a ColorTable structure
#  define ColorTable QDColorTable
#  include <AGL/agl.h>
// agl.h eventually includes AssertMacros.h, which defines the
// "check" macro.  This interferes with a number of _chimera
// source files, so we undefine "check" here.
#  ifdef check
#   undef check
#  endif
#  undef ColorTable
# endif

# ifdef GFXINFO_OSMESA
#  include <GL/osmesa.h>
# endif

# include <string>

# ifndef GFXINFO_DLL
#  define GFXINFO_IMEX
# elif defined(GFXINFO_EXPORT)
#  define GFXINFO_IMEX __declspec(dllexport)
# else
#  define GFXINFO_IMEX __declspec(dllimport)
# endif

// GfxInfo contains information about optional OpenGL graphics extensions,
// OpenGL bugs we have workarounds for, and windowing/stereo support.
//
// The two most important functions are: makeWSCurrent() and makeCurrent().
// They initialize the window system dependent and opengl context dependent
// functions.
//
// getProcAddr() is set to glxGetProcAddress, wglGetProcAddress, or some
// other platform-specific function.  It should be used to query for OpenGL
// functions (you can assume that is it never NULL).

namespace GfxInfo {

// Return information about graphics driver/card and operating system
GFXINFO_IMEX extern std::string getVendor();
GFXINFO_IMEX extern std::string getRenderer();
GFXINFO_IMEX extern std::string getVersion();
GFXINFO_IMEX extern std::string	getOS();

# ifndef WrapPy

extern "C" {
#ifdef _WIN32
typedef int (WINAPI* funcPtr)();
typedef funcPtr (WINAPI* GetProcAddrType)(const CHAR*);
#else
typedef void (*funcPtr)(...);
typedef funcPtr (*GetProcAddrType)(const char*);
#endif
extern GetProcAddrType GFXINFO_IMEX getProcAddr;
}
# endif /* WrapPy */

enum	Has	{ Not = 0x0, Extension = 0x01, Native = 0x02, Disabled = 0x4 };

// _reset resets the gfxinfo library.  In general, it should not be used.
// And if it is used, it should only be called if there are no OpenGL
// contexts open anywhere in the program.
GFXINFO_IMEX extern void	_reset();

//
// Context dependent functions
//

// From Microsoft docs:
//	The extension function addresses are unique for each pixel
//	format.  All rendering contexts of a given pixel format
//	share the same extension function addresses.
// From Linux ABI docs:
//	glXGetProcAddressARB "is functionally identical to the
//	wglGetProcAddress query defined by the Windows OpenGL library,
//	except that the function pointers returned are context independent,
//	unlike the WGL query."
//
//	Consequently, consider all extension use (anything after OpenGL 1.1)
//	to be rendering context dependent, and call makeCurrent() if you
//	change contexts.

GFXINFO_IMEX extern void	makeCurrent();

// computed information
GFXINFO_IMEX extern double	version();		// OpenGL version

// OpenGL extensions that we want to be aware of
// Note: internal FeatureNames array needs to match exactly

enum Features {
	// assume most OpenGL 1.1 features
	VertexArray,

	// standard OpenGL 1.2 features
	TextureEdgeClamp,
	Texture3D,
	SeparateSpecularColor,
	DrawRangeElements,

	// standard OpenGL 1.3 features
	Multisample,
	Multitexture,
	CubeMap,

	// standard OpenGL 1.4 features
	PointParameters,
	BlendEquation,
	BlendFuncSeparate,
	WindowPos,
	Shadows,

	// standard OpenGL 1.5 features
	VertexBufferObject,

	// standard OpenGL 2.0 features
	Shading,

	// standard OpenGL 3.0 features
	FramebufferObject,
	FramebufferMultisample,
	PackedDepthStencil,

	// Other extensions we're interested in
	CompiledVertexArray,
	CullVertex,
	ColorTable,
	TextureColorTable,
	PalettedTexture,

	// Windowing system features
	ChoosePixelFormat,	// Windows
	FBConfig,		// X11

	// Features that avoid workarounds
	TrustNormals,
	AntialiasLines,
	AntialiasPoints,
	TrustColorLogicBlend,
	CompileAndExecute,
	StereoRubberBanding,
	StereoMultisample,
	FastMultisampling,

	// must be last
	NumFeatures
};

GFXINFO_IMEX extern bool	has(Features f);
GFXINFO_IMEX extern int		hasInfo(Features f);

# ifndef WrapPy

// backwards compatibility

// standard OpenGL 1.2 features
inline bool hasTextureEdgeClamp() { return has(TextureEdgeClamp); }
inline bool hasTexture3D() { return has(Texture3D); }
inline bool hasSeparateSpecularColor() { return has(SeparateSpecularColor); }
inline bool hasDrawRangeElements() { return has(DrawRangeElements); }

// standard OpenGL 1.3 features
inline bool hasMultisample() { return has(Multisample); }
inline bool hasMultitexture() { return has(Multitexture); }
inline bool hasCubeMap() { return has(CubeMap); }

// standard OpenGL 1.4 features
inline bool hasPointParameters() { return has(PointParameters); }
inline bool hasBlendEquation() { return has(BlendEquation); }
inline bool hasBlendFuncSeparate() { return has(BlendFuncSeparate); }
inline bool hasWindowPos() { return has(WindowPos); }
inline bool hasShadows() { return has(Shadows); }

// standard OpenGL 1.5 features
inline bool hasVertexBufferObject() { return has(VertexBufferObject); }

// standard OpenGL 2.0 features
inline bool hasShading() { return has(Shading); }

// standard OpenGL 3.0 features
inline bool hasFramebufferObject() { return has(FramebufferObject); }
inline bool hasFramebufferMultisample() { return has(FramebufferMultisample); }
inline bool hasPackedDepthStencil() { return has(PackedDepthStencil); }

// Other extensions we're interested in
inline bool hasCompiledVertexArray() { return has(CompiledVertexArray); }
inline bool hasCullVertex() { return has(CullVertex); }
inline bool hasColorTable() { return has(ColorTable); }
inline bool hasTextureColorTable() { return has(TextureColorTable); }
inline bool hasPalettedTexture() { return has(PalettedTexture); }

// OpenGL implementation "features" that we have workarounds for
inline bool	badScale() { return !has(TrustNormals); }
GFXINFO_IMEX extern float	pedanticAALines();
inline bool	slowAALines() { return !has(AntialiasLines); }
inline bool	slowAAPoints() { return !has(AntialiasPoints); }
inline bool	badColorLogicBlend() { return !has(TrustColorLogicBlend); }
inline bool	badCompileAndExecute() { return !has(CompileAndExecute); }
GFXINFO_IMEX extern bool	badStereoBoolean();
inline bool	badDrawElements() { return !has(VertexArray); }
inline bool	badStereoFrontBuffer() { return !has(StereoRubberBanding); }
inline bool	badStereoMultisample() { return !has(StereoMultisample); }
inline bool	slowMultisampling() { return !has(FastMultisampling); }
# endif /* WrapPy */

//
// Window System dependent functions
//

GFXINFO_IMEX extern void	makeWSCurrent();

# ifndef WrapPy

# ifdef GFXINFO_WGL
inline bool hasChoosePixelFormat() { return has(ChoosePixelFormat); }
# endif

# ifdef GFXINFO_X11
inline bool hasFBConfig() { return has(FBConfig); }
GFXINFO_IMEX extern bool	badGLXMultisampleConstants();
# endif

extern "C" {

	// all of the OpenGL entry points are C functions
struct GFXINFO_IMEX CurrentFuncs
{
	// Texture3D
	PFNGLTEXIMAGE3DPROC		texImage3D;
	PFNGLTEXSUBIMAGE3DPROC		texSubImage3D;

	// ColorTable
	PFNGLCOLORTABLEPROC		colorTable;

	// PointParameters
	PFNGLPOINTPARAMETERFPROC	pointParameterf;
	PFNGLPOINTPARAMETERFVPROC	pointParameterfv;

	// Multitexture
	PFNGLACTIVETEXTUREPROC		activeTexture;
	PFNGLCLIENTACTIVETEXTUREPROC	clientActiveTexture;
	PFNGLMULTITEXCOORD1DPROC	multiTexCoord1d;
	PFNGLMULTITEXCOORD2DVPROC	multiTexCoord2dv;
	PFNGLMULTITEXCOORD3DVPROC	multiTexCoord3dv;
	PFNGLMULTITEXCOORD4DVPROC	multiTexCoord4dv;

	// BlendEquation
	PFNGLBLENDEQUATIONPROC		blendEquation;

	// CompiledVertexArray
	PFNGLLOCKARRAYSEXTPROC		lockArray;
	PFNGLUNLOCKARRAYSEXTPROC	unlockArray;

	// DrawRangeElements
	PFNGLDRAWRANGEELEMENTSPROC	drawRangeElements;

	// VertexBufferObject
	PFNGLBINDBUFFERPROC		bindBuffer;
	PFNGLDELETEBUFFERSPROC		deleteBuffers;
	PFNGLGENBUFFERSPROC		genBuffers;
	PFNGLISBUFFERPROC		isBuffer;
	PFNGLBUFFERDATAPROC		bufferData;
	PFNGLBUFFERSUBDATAPROC		bufferSubData;
	PFNGLGETBUFFERSUBDATAPROC	getBufferSubData;
	PFNGLMAPBUFFERPROC		mapBuffer;
	PFNGLUNMAPBUFFERPROC		unmapBuffer;
	PFNGLGETBUFFERPARAMETERIVPROC	getBufferParameteriv;
	PFNGLGETBUFFERPOINTERVPROC	getBufferPointerv;

	// Shading
	PFNGLATTACHSHADERPROC		attachShader;
	PFNGLCOMPILESHADERPROC		compileShader;
	PFNGLCREATESHADERPROC		createShader;
	PFNGLCREATEPROGRAMPROC		createProgram;
	PFNGLDELETEPROGRAMPROC		deleteProgram;
	PFNGLDELETESHADERPROC		deleteShader;
	PFNGLDETACHSHADERPROC		detachShader;
	PFNGLLINKPROGRAMPROC		linkProgram;
	PFNGLGETACTIVEATTRIBPROC	getActiveAttrib;
	PFNGLGETACTIVEUNIFORMPROC	getActiveUniform;
	PFNGLGETATTRIBLOCATIONPROC	getAttribLocation;
	PFNGLGETPROGRAMINFOLOGPROC	getProgramInfoLog;
	PFNGLGETSHADERINFOLOGPROC	getShaderInfoLog;
	PFNGLGETPROGRAMIVPROC		getProgramiv;
	PFNGLGETSHADERIVPROC		getShaderiv; PFNGLGETUNIFORMLOCATIONPROC	getUniformLocation; PFNGLSHADERSOURCEPROC		shaderSource; PFNGLUSEPROGRAMPROC		useProgram;
	PFNGLUNIFORM1FVPROC		uniform1fv;
	PFNGLUNIFORM2FVPROC		uniform2fv;
	PFNGLUNIFORM3FVPROC		uniform3fv;
	PFNGLUNIFORM4FVPROC		uniform4fv;
	PFNGLUNIFORM1IVPROC		uniform1iv;
	PFNGLUNIFORM2IVPROC		uniform2iv;
	PFNGLUNIFORM3IVPROC		uniform3iv;
	PFNGLUNIFORM4IVPROC		uniform4iv;
	PFNGLUNIFORMMATRIX2FVPROC	uniformMatrix2fv;
	PFNGLUNIFORMMATRIX3FVPROC	uniformMatrix3fv;
	PFNGLUNIFORMMATRIX4FVPROC	uniformMatrix4fv;

	// BlendFuncSeparate
	PFNGLBLENDFUNCSEPARATEPROC	blendFuncSeparate;

	// FramebufferObject
	PFNGLBINDRENDERBUFFERPROC	bindRenderbuffer;
	PFNGLDELETERENDERBUFFERSPROC	deleteRenderbuffers;
	PFNGLGENRENDERBUFFERSPROC	genRenderbuffers;
	PFNGLRENDERBUFFERSTORAGEPROC	renderbufferStorage;
	PFNGLBINDFRAMEBUFFERPROC	bindFramebuffer;
	PFNGLDELETEFRAMEBUFFERSPROC	deleteFramebuffers;
	PFNGLGENFRAMEBUFFERSPROC	genFramebuffers;
	PFNGLCHECKFRAMEBUFFERSTATUSPROC	checkFramebufferStatus;
	PFNGLFRAMEBUFFERRENDERBUFFERPROC framebufferRenderbuffer;

	// FramebufferMultisample
	PFNGLRENDERBUFFERSTORAGEMULTISAMPLEPROC renderbufferStorageMultisample;
};

} // extern "C"

GFXINFO_IMEX extern CurrentFuncs* conFuncs;

struct GFXINFO_IMEX WSFuncs
{
# if defined(GFXINFO_WGL)
	// Standard Windows extensions
	// ChoosePixelFormat
	PFNWGLCHOOSEPIXELFORMATARBPROC choosePixelFormat;
	PFNWGLGETPIXELFORMATATTRIBIVARBPROC getPixelFormatAttribiv;
# elif defined(GFXINFO_X11)
	// Assuming OpenGL 1.1, we have access to all of the GLX 1.2 functions.
	// GLX 1.3 functions we're interested in (that existed as extensions!)
	// FBConfig
	typedef GLXFBConfig* (*PFchooseFBConfig)(Display* dpy, int screen,
						int* attribList, int* nitems);
	PFchooseFBConfig	chooseFBConfig;
	typedef int (*PFgetFBConfigAttrib)(Display* dpy, GLXFBConfig config,
						int attribute, int* value);
	PFgetFBConfigAttrib	getFBConfigAttrib;
	typedef XVisualInfo* (*PFgetVisualFromFBConfig)(Display* dpy, GLXFBConfig config);
	PFgetVisualFromFBConfig	getVisualFromFBConfig;
# elif defined(GFXINFO_AGL)
	// agl has no extensions yet
# elif defined(GFXINFO_OSMESA)
	// osmesa has no extensions yet
# endif
};

GFXINFO_IMEX extern WSFuncs* wsFuncs;

// convenience functions

// Texture3D
inline void
texImage3D(GLenum target, GLint level, GLenum internalformat, GLsizei width,
		GLsizei height, GLsizei depth, GLint border, GLenum format,
		GLenum type, const GLvoid* pixels)
{ conFuncs->texImage3D(target, level, internalformat, width, height, depth, border, format, type, pixels); }

inline void
texSubImage3D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
		GLint zoffset, GLsizei width, GLsizei height, GLsizei depth,
		GLenum format, GLenum type, const GLvoid* pixels)
{ conFuncs->texSubImage3D(target, level, xoffset, yoffset, zoffset, width, height, depth, format, type, pixels); }

// ColorTable
inline void
colorTable(GLenum target, GLenum internalformat, GLsizei width, GLenum format,
		GLenum type, const GLvoid* table)
{ conFuncs->colorTable(target, internalformat, width, format, type, table); }

// DrawRangeElements
inline void
drawRangeElements(GLenum mode, GLuint start, GLuint end, GLsizei count,
		GLenum type, const GLvoid* indices)
{ conFuncs->drawRangeElements(mode, start, end, count, type, indices); }

// PointParameters
inline void
pointParameterf(GLenum pname, GLfloat param)
{ conFuncs->pointParameterf(pname, param); }

inline void
pointParameterfv(GLenum pname, const GLfloat* params)
{ conFuncs->pointParameterfv(pname, params); }

// Multitexture
inline void
activeTexture(GLenum target) { conFuncs->activeTexture(target); }
inline void
clientActiveTexture(GLenum target) { conFuncs->clientActiveTexture(target); }
inline void
multiTexCoord1d(GLenum target, GLdouble s)
{ conFuncs->multiTexCoord1d(target, s); }
inline void
multiTexCoord2dv(GLenum target, const GLdouble* v)
{ conFuncs->multiTexCoord2dv(target, v); }
inline void
multiTexCoord3dv(GLenum target, const GLdouble* v)
{ conFuncs->multiTexCoord3dv(target, v); }
inline void
multiTexCoord4dv(GLenum target, const GLdouble* v)
{ conFuncs->multiTexCoord4dv(target, v); }

// BlendEquation
inline void
blendEquation(GLenum mode) { conFuncs->blendEquation(mode); }

// CompiledVertexArray
inline void
lockArray(GLint first, GLint count) { conFuncs->lockArray(first, count); }
inline void
unlockArray() { conFuncs->unlockArray(); }

// VertexBufferObject
inline void
bindBuffer(GLenum target, GLuint buffer)
{ conFuncs->bindBuffer(target, buffer); }
inline void
deleteBuffers(GLsizei n, const GLuint *buffers)
{ conFuncs->deleteBuffers(n, buffers); }
inline void
genBuffers(GLsizei n, GLuint *buffers)
{ conFuncs->genBuffers(n, buffers); }
inline GLboolean
isBuffer(GLuint buffer)
{ return conFuncs->isBuffer(buffer); }
inline void
bufferData(GLenum target, GLsizeiptrARB size, const GLvoid *data, GLenum usage)
{ conFuncs->bufferData(target, size, data, usage); }
inline void
bufferSubData(GLenum target, GLintptrARB offset, GLsizeiptrARB size, const GLvoid *data)
{ conFuncs->bufferSubData(target, offset, size, data); }
inline void
getBufferSubData(GLenum target, GLintptrARB offset, GLsizeiptrARB size, GLvoid *data)
{ conFuncs->getBufferSubData(target, offset, size, data); }
inline GLvoid*
mapBuffer(GLenum target, GLenum access)
{ return conFuncs->mapBuffer(target, access); }
inline GLboolean
unmapBuffer(GLenum target)
{ return conFuncs->unmapBuffer(target); }
inline void
getBufferParameteriv(GLenum target, GLenum pname, GLint *params)
{ conFuncs->getBufferParameteriv(target, pname, params); }
inline void
getBufferPointerv(GLenum target, GLenum pname, GLvoid* *params)
{ conFuncs->getBufferPointerv(target, pname, params); }

// Shading
inline void
attachShader(GLuint program, GLuint shader)
{ conFuncs->attachShader(program, shader); }
inline void
compileShader(GLuint shader)
{ conFuncs->compileShader(shader); }
inline GLuint
createShader(GLenum shaderType)
{ return conFuncs->createShader(shaderType); }
inline GLuint
createProgram(void)
{ return conFuncs->createProgram(); }
inline void
deleteProgram(GLuint program)
{ conFuncs->deleteProgram(program); }
inline void
deleteShader(GLuint shader)
{ conFuncs->deleteShader(shader); }
inline void
detachShader(GLuint program, GLuint shader)
{ conFuncs->detachShader(program, shader); }
inline void
linkProgram(GLuint program)
{ conFuncs->linkProgram(program); }
inline void
getActiveAttrib(GLuint program, GLuint index, GLsizei maxLength, GLsizei *length, GLint *size, GLenum *type, GLchar *name)
{ conFuncs->getActiveAttrib(program, index, maxLength, length, size, type, name); }
inline void
getActiveUniform(GLuint program, GLuint index, GLsizei maxLength, GLsizei *length, GLint *size, GLenum *type, GLchar *name)
{ conFuncs->getActiveUniform(program, index, maxLength, length, size, type, name); }
inline GLint
getAttribLocation(GLuint program, const GLchar *name)
{ return conFuncs->getAttribLocation(program, name); }
inline void
getProgramInfoLog(GLuint program, GLsizei maxLength, GLsizei* length, GLchar* infoLog)
{ conFuncs->getProgramInfoLog(program, maxLength, length, infoLog); }
inline void
getShaderInfoLog(GLuint shader, GLsizei maxLength, GLsizei* length, GLchar* infoLog)
{ conFuncs->getShaderInfoLog(shader, maxLength, length, infoLog); }
inline void
getProgramiv(GLuint program, GLenum pname, GLint* params)
{ conFuncs->getProgramiv(program, pname, params); }
inline void
getShaderiv(GLuint shader, GLenum pname, GLint* params)
{ conFuncs->getShaderiv(shader, pname, params); }
inline GLint
getUniformLocation(GLuint program, const GLchar* name)
{ return conFuncs->getUniformLocation(program, name); }
inline void
shaderSource(GLuint shader, GLsizei nstrings, const GLchar* *strings, const GLint *lengths)
{ conFuncs->shaderSource(shader, nstrings, strings, lengths); }
inline void
useProgram(GLuint program)
{ conFuncs->useProgram(program); }
inline void
uniform1fv(GLint location, GLuint count, const GLfloat* v)
{ conFuncs->uniform1fv(location, count, v); }
inline void
uniform2fv(GLint location, GLuint count, const GLfloat* v)
{ conFuncs->uniform2fv(location, count, v); }
inline void
uniform3fv(GLint location, GLuint count, const GLfloat* v)
{ conFuncs->uniform3fv(location, count, v); }
inline void
uniform4fv(GLint location, GLuint count, const GLfloat* v)
{ conFuncs->uniform4fv(location, count, v); }
inline void
uniform1iv(GLint location, GLuint count, const GLint* v)
{ conFuncs->uniform1iv(location, count, v); }
inline void
uniform2iv(GLint location, GLuint count, const GLint* v)
{ conFuncs->uniform2iv(location, count, v); }
inline void
uniform3iv(GLint location, GLuint count, const GLint* v)
{ conFuncs->uniform3iv(location, count, v); }
inline void
uniform4iv(GLint location, GLuint count, const GLint* v)
{ conFuncs->uniform4iv(location, count, v); }
inline void
uniformMatrix2fv(GLint location, GLuint count, GLboolean transpose, const GLfloat* v)
{ conFuncs->uniformMatrix2fv(location, count, transpose, v); }
inline void
uniformMatrix3fv(GLint location, GLuint count, GLboolean transpose, const GLfloat* v)
{ conFuncs->uniformMatrix3fv(location, count, transpose, v); }
inline void
uniformMatrix4fv(GLint location, GLuint count, GLboolean transpose, const GLfloat* v)
{ conFuncs->uniformMatrix4fv(location, count, transpose, v); }

// BlendFuncSeparate
inline void
blendFuncSeparate(GLenum srcRGB, GLenum dstRGB, GLenum srcAlpha, GLenum dstAlpha)
{ conFuncs->blendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha); }

// FramebufferObject
inline void
bindRenderbuffer(GLenum target, GLuint renderbuffer)
{ conFuncs->bindRenderbuffer(target, renderbuffer); }
inline void
deleteRenderbuffers(GLsizei n, const GLuint *renderbuffers)
{ conFuncs->deleteRenderbuffers(n, renderbuffers); }
inline void
genRenderbuffers(GLsizei n, GLuint *renderbuffers)
{ conFuncs->genRenderbuffers(n, renderbuffers); }
inline void
renderbufferStorage(GLenum target, GLenum internalformat, GLsizei width, GLsizei height)
{ conFuncs->renderbufferStorage(target, internalformat, width, height); }
inline void
bindFramebuffer(GLenum target, GLuint framebuffer)
{ conFuncs->bindFramebuffer(target, framebuffer); }
inline void
deleteFramebuffers(GLsizei n, const GLuint *framebuffers)
{ conFuncs->deleteFramebuffers(n, framebuffers); }
inline void
genFramebuffers(GLsizei n, GLuint *framebuffers)
{ conFuncs->genFramebuffers(n, framebuffers); }
inline GLenum
checkFramebufferStatus(GLenum target)
{ return conFuncs->checkFramebufferStatus(target); }
inline void
framebufferRenderbuffer(GLenum target, GLenum attachment, GLenum renderbuffertarget, GLuint renderbuffer)
{ conFuncs->framebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer); }

// FramebufferMultisample
inline void
renderbufferStorageMultisample(GLenum target, GLsizei samples, GLenum internalformat, GLsizei width, GLsizei height)
{ conFuncs->renderbufferStorageMultisample(target, samples, internalformat, width, height); }

# ifdef GFXINFO_WGL
inline BOOL
choosePixelFormat(HDC hdc, const int* piAttribIList,
		const FLOAT* pfAttribFList, UINT nMaxFormats, int* piFormats,
		UINT* nNumFormats)
{ return wsFuncs->choosePixelFormat(hdc, piAttribIList, pfAttribFList, nMaxFormats, piFormats, nNumFormats); }

inline BOOL
getPixelFormatAttribiv(HDC hdc, int iPixelFormat, int iLayerPlane,
		UINT nAttributes, const int* piAttributes, int* piValues)
{ return wsFuncs->getPixelFormatAttribiv(hdc, iPixelFormat, iLayerPlane, nAttributes, piAttributes, piValues); }
# endif /* GFXINFO_WGL */

# ifdef GFXINFO_X11
inline GLXFBConfig*
chooseFBConfig(Display* dpy, int screen, int* attribList, int* nitems)
{ return wsFuncs->chooseFBConfig(dpy, screen, attribList, nitems); }

inline int
getFBConfigAttrib(Display* dpy, GLXFBConfig config, int attribute, int* value)
{ return wsFuncs->getFBConfigAttrib(dpy, config, attribute, value); }

inline XVisualInfo*
getVisualFromFBConfig(Display* dpy, GLXFBConfig config)
{ return wsFuncs->getVisualFromFBConfig(dpy, config); }

# endif /* GFXINFO_X11 */

} // namespace GfxInfo

// Define OpenGL enumerants that might be missing or wrong
// for supported extensions.

# ifdef GFXINFO_X11

// GLX 1.3, EXT_visual_rating
#  ifndef GLX_VERSION_1_3
#   define GLX_CONFIG_CAVEAT			0x20
#   define GLX_NONE				0x8000
#   define GLX_SLOW_CONFIG			0x8001
#   define GLX_NON_CONFORMANT_CONFIG		0x800D
#  endif

// ARB_multisample
#  ifdef GLX_SGIS_multisample
// SGI has GLX_SAMPLE_BUFFERS and GLX_SAMPLES constants exchanged.
// Make sure we default to ARB values (will workaround in code).
#   undef GLX_SAMPLE_BUFFERS_ARB
#   undef GLX_SAMPLES_ARB
#  endif
#  ifndef GLX_SAMPLE_BUFFERS_ARB
#   define GLX_SAMPLE_BUFFERS_ARB		100000
#  endif
#  ifndef GLX_SAMPLES_ARB
#   define GLX_SAMPLES_ARB			100001
#  endif

# endif /* GFXINFO_X11 */

# endif /* WrapPy */

#endif
