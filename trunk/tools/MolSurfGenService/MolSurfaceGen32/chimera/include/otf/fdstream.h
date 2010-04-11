/* The following code declares classes to read from and write to
 * file descriptore or file handles.
 *
 * See
 *      http://www.josuttis.com/cppcode
 * for details and the latest version.
 *
 * - open:
 *      - integrating BUFSIZ on some systems?
 *      - optimized reading of multiple characters
 *      - stream for reading AND writing
 *      - i18n
 *
 * (C) Copyright Nicolai M. Josuttis 2001.
 * Permission to copy, use, modify, sell and distribute this software
 * is granted provided this copyright notice appears in all copies.
 * This software is provided "as is" without express or implied
 * warranty, and with no claim as to its suitability for any purpose.
 *
 * Version: Jul 28, 2002
 * History:
 *  Mar 23, 2006: convert to otf coding conventions
 *  Jul 28, 2002: bugfix memcpy() => memmove()
 *                fdinbuf::underflow(): cast for return statements
 *  Aug 05, 2001: first public version
 */
#ifndef OTF_FDSTREAM_H
#define OTF_FDSTREAM_H

#include <istream>
#include <ostream>
#include <streambuf>
// for memmove():
#include <string.h>


// low-level read and write functions
#ifdef _MSC_VER
# include <io.h>
#else
# include <unistd.h>
//extern "C" {
//    int write(int fd, const char* buf, int num);
//    int read(int fd, char* buf, int num);
//}
#endif


// BEGIN namespace OTF
namespace otf {


/************************************************************
 * fdostream
 * - a stream that writes on a file descriptor
 ************************************************************/


template <class charT, class traits = std::char_traits<charT> >
class basic_fdoutbuf: public std::basic_streambuf<charT, traits> {
protected:
	int fd;    // file descriptor
public:
	typedef charT char_type;
	typedef typename traits::int_type int_type;
	typedef typename traits::off_type off_type;
	typedef typename traits::pos_type pos_type;
	typedef traits traits_type;

	// constructor
	explicit basic_fdoutbuf(int _fd): fd(_fd) {
	}
protected:
	// write one character
	virtual int_type overflow(int_type c) {
		if (c != traits_type::eof()) {
			char_type z = c;
			if (::write(fd, &z, sizeof (char_type)) != sizeof (char_type)) {
				return traits_type::eof();
			}
		}
		return c;
	}
	// write multiple characters
	virtual std::streamsize xsputn(const char_type* s, std::streamsize num) {
		return ::write(fd, s, num * sizeof (char_type));
	}
};

template <class charT, class traits = std::char_traits<charT> >
class basic_fdostream: public std::basic_ostream<charT, traits> {
protected:
	basic_fdoutbuf<charT, traits> buf;
public:
	explicit basic_fdostream(int fd):
				std::basic_ostream<charT, traits>(0), buf(fd) {
		this->rdbuf(&buf);
	}
};

typedef basic_fdostream<char> fdostream;


/************************************************************
 * fdistream
 * - a stream that reads on a file descriptor
 ************************************************************/

template <class charT, class traits = std::char_traits<charT> >
class basic_fdinbuf: public std::basic_streambuf<charT, traits> {
protected:
	int fd;    // file descriptor
protected:
	/* data buffer:
	 * - at most, pbSize characters in putback area plus
	 * - at most, bufSize characters in ordinary read buffer
	 */
	static const int pbSize = 4;        // size of putback area
	static const int bufSize = 1024;    // size of the data buffer
	char buffer[bufSize + pbSize];        // data buffer
	typedef std::basic_streambuf<charT, traits> streambuf;
	using streambuf::eback;
	using streambuf::egptr;
	using streambuf::gptr;
	using streambuf::setg;

public:
	typedef charT char_type;
	typedef typename traits::int_type int_type;
	typedef typename traits::off_type off_type;
	typedef typename traits::pos_type pos_type;
	typedef traits traits_type;

	/* constructor
	 * - initialize file descriptor
	 * - initialize empty data buffer
	 * - no putback area
	 * => force underflow()
	 */
	explicit basic_fdinbuf(int _fd): fd(_fd) {
		setg(buffer + pbSize,     // beginning of putback area
				buffer + pbSize,     // read position
				buffer + pbSize);    // end position
	}

protected:
	// insert new characters into the buffer
	virtual int_type underflow() {
		// is read position before end of buffer?
		if (gptr() < egptr()) {
			return traits_type::to_int_type(*gptr());
		}

		/* process size of putback area
		 * - use number of characters read
		 * - but at most size of putback area
		 */
		int numPutback;
		numPutback = gptr() - eback();
		if (numPutback > pbSize) {
			numPutback = pbSize;
		}

		/* copy up to pbSize characters previously read into
		 * the putback area
		 */
		memmove(buffer + (pbSize - numPutback), gptr() - numPutback,
				numPutback);

		// read at most bufSize new characters
		int num;
		num = read(fd, buffer + pbSize, bufSize);
		if (num <= 0) {
			// ERROR or EOF
			return traits_type::eof();
		}

		// reset buffer pointers
		setg(buffer + (pbSize - numPutback),// beginning of putback area
				buffer + pbSize,         // read position
				buffer + pbSize + num);  // end of buffer

			// return next character
			return traits_type::to_int_type(*gptr());
	}
};

template <class charT, class traits = std::char_traits<charT> >
class basic_fdistream: public std::basic_istream<charT, traits> {
protected:
	basic_fdinbuf<charT, traits> buf;
public:
	explicit basic_fdistream(int fd):
				std::basic_istream<charT, traits>(0), buf(fd) {
		this->rdbuf(&buf);
	}
};

typedef basic_fdistream<char> fdistream;

} // END namespace otf

#endif /*OTF_FDSTREAM_H*/
