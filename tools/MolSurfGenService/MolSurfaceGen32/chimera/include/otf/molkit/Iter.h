// Copyright 1993, U.C.S.F. Computer Graphics Laboratory
// $Id: Iter.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef Iter_h
#define	Iter_h

// This header file provides a template class for iterators.

// A CIter is an iterator that doesn't support addition or deletion
// to the container being iterated over.

template <class T>
class CIter {
public:
	typedef void (*cb_func)(CIter *i);
private:
	T	*cur_element;
	bool	okay_;
	void	*state_info;
	cb_func	advance, dup_state, cleanup;
	unsigned int	(*count)(const CIter *i);
public:
	// the following functions are for users of iterators
		CIter(): cur_element(0), okay_(0), state_info(0),
				advance(0), dup_state(0), cleanup(0) {}
	bool	ok() const { return okay_; }
	void	next() { advance(this); }
	unsigned int	numRemaining() const { return count(this); }
	T	&operator*() const { return *cur_element; }
	T	*operator->() const { return cur_element; }
		operator T *() { return cur_element; }
	CIter	&operator=(const CIter &i);
		CIter(const CIter &i);
	virtual	~CIter() { if (cleanup) cleanup(this); }

	// the following functions are for creators of iterators
	CIter(cb_func adv, T *first, int valid, cb_func destruct,
					unsigned int (*cnt)(const CIter *)):
			cur_element(first), okay_(valid), state_info(0),
			advance(adv), dup_state(0), cleanup(destruct),
			count(cnt)
		{}
	CIter(cb_func adv, T *first, int valid, cb_func destruct,
		unsigned int (*cnt)(const CIter *), void *data,
		cb_func dup_data):
			cur_element(first), okay_(valid), state_info(data),
			advance(adv), dup_state(dup_data), cleanup(destruct),
			count(cnt)
		{}
	T	*element() const { return cur_element; }
	void	element(T *t, int valid) { cur_element = t; okay_ = valid; }
	void	*state() const { return state_info; }
	void	state(void *data) { state_info = data; }
};

// A Iter is an iterator that supports addition or deletion to the
// container being iterated over.

template <class T>
class Iter: public CIter<T> {
public:
	Iter	&operator=(const Iter &i) {
			*((CIter<T> *) this) = i;
			return *this;
		}
		Iter(const Iter &i): CIter<T>(i) {}
};

template <class T> inline CIter<T> &
CIter<T>::operator=(const CIter &i)
{
	if (&i == this)
		return *this;
	if (cleanup)
		cleanup(this);
	cleanup = i.cleanup;
	advance = i.advance;
	count = i.count;
	cur_element = i.cur_element;
	okay_ = i.okay_;
	dup_state = i.dup_state;
	state_info = i.state_info;
	if (dup_state)
		dup_state(this);
	return *this;
}

template <class T> inline
CIter<T>::CIter(const CIter &i)
{
	cleanup = i.cleanup;
	advance = i.advance;
	count = i.count;
	cur_element = i.cur_element;
	okay_ = i.okay_;
	dup_state = i.dup_state;
	state_info = i.state_info;
	if (dup_state)
		dup_state(this);
}

#endif
