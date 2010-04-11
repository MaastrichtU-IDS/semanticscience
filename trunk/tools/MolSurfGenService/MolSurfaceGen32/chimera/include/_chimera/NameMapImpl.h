#ifndef Chimera_NameMapImpl_h
# define Chimera_NameMapImpl_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include <otf/Symbol.h>
# include "NameMap.h"

namespace chimera {

template <class klass> typename Name<klass>::NameMap Name<klass>::all;
template <class klass> typename Name<klass>::BackMap Name<klass>::back;

template <class klass> klass*
Name<klass>::lookup(otf::Symbol name)
{
	if (name.empty())
		return NULL;
	typename NameMap::iterator i = all.find(name);
	if (i == all.end())
		return NULL;
	return dynamic_cast<klass*>(i->second);
}

template <class klass> void
Name<klass>::remove(otf::Symbol name) throw ()
{
	typename NameMap::iterator i = all.find(name);
	if (i == all.end())
		return;
	typename BackMap::iterator j = back.find(i->second);
	all.erase(i);
	back.erase(j);
}

template <class klass> typename Name<klass>::NameMapRange
Name<klass>::list() throw ()
{
	return std::make_pair(all.begin(), all.end());
}

template <class klass>
Name<klass>::~Name()
{
	remove();
}

template <class klass> void
Name<klass>::save(otf::Symbol name) throw (std::logic_error)
{
	if (name.empty())
		throw std::invalid_argument("empty name");
	typename NameMap::iterator i = all.find(name);
	if (i != all.end())
		throw std::invalid_argument("name already defined");
	all[name] = this;
	back[this] = name;
}

template <class klass> otf::Symbol
Name<klass>::name() const throw ()
{
	Name<klass>* k = const_cast<Name<klass>*>(this);
	typename BackMap::const_iterator i = back.find(k);
	if (i == back.end())
		return otf::Symbol();
	return i->second;
}

template <class klass> void
Name<klass>::remove() throw ()
{
	typename BackMap::iterator i = back.find(this);
	if (i == back.end())
		return;
	typename NameMap::iterator j = all.find(i->second);
	back.erase(i);
	all.erase(j);
}

} // namespace chimera

# endif /* WrapPy */

#endif
