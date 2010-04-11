#ifndef Chimera_Shader_h
# define Chimera_Shader_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Array.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include <GfxInfo.h>
# include <string>
# include "_chimera_config.h"
# include "ColorGroup.h"
# include "NameMap.h"

# ifdef Bool
#  undef Bool
typedef int Bool;	// workaround <X11/Xlib.h>'s global name pollution
# endif

namespace chimera {

class Texture;
class Shader;

class CHIMERA_IMEX ShaderVariable: public NotifierList, public otf::WrapPyObj
{
	// Used to describe program uniform variables (for Shaders)
	// and vertex attribute variables (for Colors).
public:
	// Every variable should have a name, type, metatype, and a
	// description.  The metatype may be used to pick an appropriate
	// GUI element to interactively control a variable, such as:
	// color, point (or position), direction (or unit vector),
	// vector, etc.
	//
	enum Type {
		Float, Vec2, Vec3, Vec4,
		Int, IVec2, IVec3, IVec4,
		Bool, BVec2, BVec3, BVec4,
		Mat2, Mat3, Mat4,
		Sampler1D, Sampler2D, Sampler3D, SamplerCube, 
		Sampler1DShadow, Sampler2DShadow,
		Unknown
	};
	// ATTRIBUTE: name
	otf::Symbol	name() const;
	// ATTRIBUTE: type
	Type		type() const;
	// ATTRIBUTE: metatype
	const std::string&
			metatype() const;
	// ATTRIBUTE: description
	const std::string&
			description() const;
	int		location() const;
	void		setLocation(int location);

	Type		basetype() const;
#ifndef WrapPy
	unsigned	count() const;		// number of basetype elements
#else
	int		count() const;
#endif

	enum SubValue { CURRENT, MIN, MAX };
#ifndef WrapPy
	static unsigned const NUM_SUBVALUES = MAX + 1;
#else
	static int const NUM_SUBVALUES = MAX + 1;
#endif
#ifndef WrapPy
	float		getFloat(SubValue v = CURRENT) const;
	void		setFloat(float f, SubValue v = CURRENT);
	void		getFloatv(/*OUT*/ float* fv, SubValue v = CURRENT) const;
	
	void		setFloatv(float* fv, SubValue v = CURRENT);
	int		getInt(SubValue v = CURRENT) const;
	void		setInt(int i, SubValue v = CURRENT);
	void		getIntv(/*OUT*/ int* iv, SubValue v = CURRENT) const;
	void		setIntv(int* iv, SubValue v = CURRENT);
	bool		getBool(SubValue v = CURRENT) const;
	void		setBool(bool b, SubValue v = CURRENT);
	void		getBoolv(/*OUT*/ bool* bv, SubValue v = CURRENT) const;
	void		setBoolv(bool* bv, SubValue v = CURRENT);
	Texture*	texture(SubValue v = CURRENT) const;
	void		setTexture(Texture* t, SubValue v = CURRENT);

	virtual PyObject* wpyNew() const;
#endif
	bool		hasValue(SubValue v = CURRENT) const;
	PyObject*	value(SubValue v = CURRENT) const;
	void		setValue(PyObject* obj, SubValue v = CURRENT);
private:
	friend class Shader;
	ShaderVariable(otf::Symbol n, Type t, const std::string& metatype,
						const std::string& description);

	int		slot;
	otf::Symbol	name_;
	Type		type_;
	std::string	metatype_;
	std::string	description_;
	int		location_;
	bool		hasValue_[NUM_SUBVALUES];
	union Data {
		GLfloat	f;		// Float
		GLfloat	vec2[2];	// Vec2
		GLfloat	vec3[3];	// Vec3
		GLfloat	vec4[4];	// Vec4
		GLint	i;		// Int
		GLint	ivec2[2];	// IVec2
		GLint	ivec3[3];	// IVec3
		GLint	ivec4[4];	// IVec4
		GLint	b;		// Bool
		GLint	bvec2[2];	// BVec2
		GLint	bvec3[3];	// BVec3
		GLint	bvec4[4];	// BVec4
		GLfloat	mat2[2][2];	// Mat2
		GLfloat	mat3[3][3];	// Mat3
		GLfloat	mat4[4][4];	// Mat4
		Texture* tex;		// Sampler*
	};
	Data	data[NUM_SUBVALUES];
	void	drawUniform() const;
};

inline bool
ShaderVariable::hasValue(SubValue v) const
{
	return hasValue_[v];
}

inline otf::Symbol
ShaderVariable::name() const
{
	return name_;
}

inline ShaderVariable::Type
ShaderVariable::type() const
{
	return type_;
}

inline const std::string&
ShaderVariable::metatype() const
{
	return metatype_;
}

inline const std::string&
ShaderVariable::description() const
{
	return description_;
}

inline int
ShaderVariable::location() const
{
	return location_;
}

class CHIMERA_IMEX Shader: public ColorGroup, public Name<Shader>
{
public:
	Shader(otf::Symbol name, const std::string& dirname);
	virtual	~Shader();

# ifndef WrapPy
	// We use materials, so we can use glColor instead of glMaterial
	// to switch colors.
	virtual void	draw(bool lit) const throw ();
	virtual void	undraw() const throw ();
	void		baseDraw() const throw ();	// for Texture
# endif
# if 0
	virtual bool	operator<(const ColorGroup& o) const;
	virtual bool	operator==(const ColorGroup& o) const;
# endif
# ifndef WrapPy
	virtual bool	isTranslucent() const throw ();
# endif

	typedef std::vector<ShaderVariable*>	Parameters;
	// ATTRIBUTE: parameters
	const Parameters&	parameters();
	ShaderVariable*	parameter(otf::Symbol name,
						bool exceptions = false) const;

# ifndef WrapPy
	virtual void	notify(const NotifierReason& reason) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
# endif
#if defined(WrapPy)
	// wrappy can't handle Name<Shader> yet
	// Note: C++ still sees NameMap as map<Symbol, Name<Shader> >.
	typedef std::map<otf::Symbol, Shader*> NameMap;
	typedef std::pair<NameMap::const_iterator, NameMap::const_iterator> NameMapRange;
	static Shader* lookup(otf::Symbol name);
	//static void remove(otf::Symbol name) throw ();
	static NameMapRange list() throw ();
	void save(otf::Symbol name) throw (std::logic_error);
	void remove() throw ();
	otf::Symbol name() const throw ();
# endif
private:
	friend class Name<Shader>;
	static bool	foundShaders;
	static void	findAllShaders();
	typedef ShaderVariable Var;

	void		updateVar(Var* var, const NotifierReason&);
	class CHIMERA_IMEX VarNotifier: public Notifier {
	public:
		void update(const void* tag, void* param,
					const NotifierReason& reason) const {
			Shader* s = static_cast<Shader*>
						(const_cast<void*>(tag));
			Var* var = static_cast<Var*>(param);
			s->updateVar(var, reason);
}
	};
	friend class VarNotifier;
	VarNotifier	varNotifier;
	Parameters	parameters_;
	GLuint		programObj;		// OpenGL display list(s)
	void		recompileODL();
	static TrackChanges::Changes* const
			changes;
	bool		readShaderFile(const std::string& dirname, GLuint program);
	typedef std::pair<GLuint, std::string> ShaderId;
	typedef std::vector<ShaderId> Shaders;
	Shaders shaders;
};

inline const Shader::Parameters&
Shader::parameters()
{
	return parameters_;
}

# ifndef WrapPy
// specialize lookup and list so we can check the filesystem
template <> CHIMERA_IMEX Shader* Name<Shader>::lookup(otf::Symbol name);
template <> CHIMERA_IMEX Name<Shader>::NameMapRange Name<Shader>::list() throw ();
#endif

} // namespace chimera

#endif
