#ifndef otf_getLine_h
# define otf_getLine_h

# include <string>
# include <istream>

namespace otf {

//  otf::getLine(istream&, string&) acts like std::getline(istream&, string&)
//  except that it returns lines that end with '\r\n', '\n', or '\r'.

template <class _charT, class _traits, class _alloc>
std::basic_istream<_charT, _traits>&
getLine(std::basic_istream<_charT, _traits>& _is,
				std::basic_string<_charT, _traits, _alloc>& _s)
{
	typename std::basic_istream<_charT, _traits>::sentry _sentry(_is, true);
	if (!_sentry) {
		_is.setstate(std::ios_base::failbit);
		return _is;
	}

	typedef typename _alloc::size_type _size_type;
	const _size_type _max = _s.max_size();
	const _charT _nl = _is.widen('\n');
	const _charT _ret = _is.widen('\r');

	std::basic_streambuf<_charT, _traits>* _buf = _is.rdbuf();
	_s.clear();
	for (_size_type _count = 0; _count != _max; ++_count) {
		int _c1 = _buf->sbumpc();
		if (_traits::eq_int_type(_c1, _traits::eof())) {
			_is.setstate(std::ios_base::eofbit);
			if (_count == 0)
				_is.setstate(std::ios_base::failbit);
			break;
		}
		_charT _c = _traits::to_char_type(_c1);
		if (_traits::eq(_c, _nl))
			break;
		if (_traits::eq(_c, _ret)) {
			// also skip optional trailing '\n'
			_c1 = _buf->sgetc();
			if (!_traits::eq_int_type(_c1, _traits::eof())) {
				_c = _traits::to_char_type(_c1);
				if (_traits::eq(_c, _nl)) {
					_buf->sbumpc();
				}
			}
			break;
		}
		_s.push_back(_c);
	}
	return _is;
}

} // namespace otf

#endif
