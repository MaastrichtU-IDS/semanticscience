#include <otf/Symbol.h>

namespace otf {

class TmplAtom;

// functor to convert the two types of atom assignment methods
class assigner : public std::binary_function<TmplAtom *, const char *, void> {
	void (TmplAtom::*aFunc)(const char *);
	void (*func)(TmplAtom *, const char *);
public:
	assigner(void (TmplAtom::*assignFunc)(const char *)) :
						aFunc(assignFunc), func(NULL) {}
	assigner(void (*assignFunc)(TmplAtom *, const char *)) :
						aFunc(NULL), func(assignFunc) {}
	void operator()(TmplAtom *a, otf::Symbol val) {
		if (aFunc)
			(a->*aFunc)(val.c_str());
		else
			(*func)(a, val.c_str());
	}
};

}

