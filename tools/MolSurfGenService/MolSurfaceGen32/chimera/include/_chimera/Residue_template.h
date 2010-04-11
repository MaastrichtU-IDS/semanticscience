#include <otf/Symbol.h>

namespace chimera {

class Atom;

// functor to convert the two types of atom assignment methods
class assigner : public std::binary_function<Atom *, const char *, void> {
	void (Atom::*aFunc)(const char *);
	void (*func)(Atom *, const char *);
public:
	assigner(void (Atom::*assignFunc)(const char *)) :
						aFunc(assignFunc), func(NULL) {}
	assigner(void (*assignFunc)(Atom *, const char *)) :
						aFunc(NULL), func(assignFunc) {}
	void operator()(Atom *a, otf::Symbol val) {
		if (aFunc)
			(a->*aFunc)(val.c_str());
		else
			(*func)(a, val.c_str());
	}
};

}

