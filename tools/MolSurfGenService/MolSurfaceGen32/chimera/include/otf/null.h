#ifndef null_h
# define null_h

// Written by Greg Couch, UCSF Computer Graphics Lab, Sept. 1999

// null is a type-safe version version of the NULL macro.
//
// null is in the global/unnamed namespace, because we want null
// to appear as if it were a keyword (hoping that it will be someday).
//
// The scenario:  we are given a function that is overloaded
// with 2 versions, one that takes an integer argument and one
// that takes a pointer argument.  If that function is invoked
// with a NULL argument, some compilers will invoke the integer
// version and others will invoke the pointer version (is NULL
// 0 or (void *)0?, and besides if a programmer wrote NULL, the
// pointer version was intended).  By using null instead of NULL,
// the pointer version will always be invoked.  If the function
// has a third overload with another pointer type, the compiler
// will complain that it is ambiguous, as it should.
//
// Caveat: many compilers do not evaluate the inline cast as a
// compile-time constant and will generate extra code.  This
// is a problem with global pointer initialization, as the
// initialization is done at a random time relative to other
// global initializers.  Consequently, those other initializers
// can not depend on the null pointer being initialized.

class null_t {
	void *null;	// for functions with a variable number of arguments
public:
	null_t(): null(0) {}
	template <typename _t>
	operator _t *() const
	{
		return 0;
	}
};

template <typename _t>
inline bool operator==(_t *t, null_t)
{
	return t == 0;
}

template <typename _t>
inline bool operator==(null_t, _t *t)
{
	return 0 == t;
}

template <typename _t>
inline bool operator!=(_t *t, null_t)
{
	return t != 0;
}

template <typename _t>
inline bool operator!=(null_t, _t *t)
{
	return 0 != t;
}

namespace {
const null_t null;
}

#endif
