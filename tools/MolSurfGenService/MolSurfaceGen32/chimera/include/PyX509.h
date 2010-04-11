// --- UCSF Chimera Copyright ---
// Copyright (c) 2000 Regents of the University of California.
// All rights reserved.  This software provided pursuant to a
// license agreement containing restrictions on its disclosure,
// duplication and use.  This notice must be embedded in or
// attached to all copies, including partial copies, of the
// software or any revisions or derivations thereof.
// --- UCSF Chimera Copyright ---

#ifndef	VERIFYCERT_INCLUDE
# define VERIFYCERT_INCLUDE

# include <string>
# include <utility>
# include <vector>
# include <stdexcept>

# include <otf/WrapPy2.h>

# ifndef WrapPy
#  include <openssl/x509.h>
# endif

# ifndef X509_DLL
#  define X509_IMEX
# elif defined(X509_EXPORT)
#  define X509_IMEX __declspec(dllexport)
# else
#  define X509_IMEX __declspec(dllimport)
# endif

namespace PyX509 {

# ifndef WrapPy
extern const std::string empty;
# endif

typedef std::vector<int> ASNString;

class X509_IMEX CAStore : public otf::WrapPyObj
{
	X509_STORE		*store;
public:
				CAStore(const std::string &CAFile = empty)
					throw (std::invalid_argument,
						std::runtime_error);
				~CAStore();
# ifndef WrapPy
	X509_STORE		*caStore() const { return store; }
	virtual PyObject*	wpyNew() const;
# endif
};

class X509_IMEX Certificate : public otf::WrapPyObj
{
	X509			*cert;
public:
				Certificate(const std::string &certFile)
					throw (std::runtime_error);
				Certificate(const std::string &certData,
						int start, int length)
					throw (std::runtime_error);
				~Certificate();
	bool			verify(const CAStore *store) const
					throw (std::runtime_error);
	std::string		name() const;
	int			version() const;
	ASNString		serialNumber() const;
	std::string		issuer() const;
	std::string		subject() const;
	std::string		validNotBefore() const;
	std::string		validNotAfter() const;
	void			writePEM(const std::string &certFile)
					throw (std::runtime_error);
# ifndef WrapPy
				Certificate(X509 *x509);
	X509			*certificate() const { return cert; }
	virtual PyObject*	wpyNew() const;
# endif
};

class X509_IMEX PrivateKey : public otf::WrapPyObj
{
	EVP_PKEY		*pkey;
public:
				PrivateKey(const std::string &keyFile,
						const std::string &password)
					throw (std::runtime_error);
				PrivateKey(const std::string &type,
						const std::string &keyData,
						int start, int length)
					throw (std::runtime_error);
				~PrivateKey();
	int			type() const;
	void			writePEM(const std::string &pkcs8File,
					const std::string &password,
					const std::string &randomFile = empty)
					throw (std::runtime_error);
# ifndef WrapPy
	EVP_PKEY		*key() const { return pkey; }
	virtual PyObject*	wpyNew() const;
# endif
};

class X509_IMEX SMIME : public otf::WrapPyObj
{
	CAStore			*store;
public:
				SMIME(CAStore *s);
				~SMIME();
	std::pair<std::string, std::vector<Certificate *> >
				verifyFile(const std::string &msgFile) const
					throw (std::runtime_error);
	std::pair<std::string, std::vector<Certificate *> >
				verifyString(const std::string &data,
						int start, int length) const
					throw (std::runtime_error);
	std::string		signFile(const std::string &msgFile,
					const Certificate *signer,
					/* NULL_OK */const Certificate *other,
					const PrivateKey *key,
					const std::string &randomFile = empty)
						const
					throw (std::runtime_error);
	std::string		signString(const std::string &data,
					int start, int length,
					const Certificate *signer,
					/* NULL_OK */const Certificate *other,
					const PrivateKey *key,
					const std::string &randomFile = empty)
						const
					throw (std::runtime_error);
private:
	std::pair<std::string, std::vector<Certificate *> >
				verifyBIO(BIO *in) const
					throw (std::runtime_error);
	std::string		signBIO(BIO *in,
					const Certificate *signer,
					const Certificate *other,
					const PrivateKey *key,
					const std::string &randomFile = empty)
						const
					throw (std::runtime_error);
# ifndef WrapPy
	virtual PyObject*	wpyNew() const;
# endif
};

# ifndef WrapPy
extern bool	initAlgorithms;
extern bool	initRandom;
# endif

extern void	initializeAlgorithms();
extern void	initializeRandom(const std::string &randomFile);

extern std::string	SHA1(const std::string &s, int start, int length);
extern std::string	MD5(const std::string &s, int start, int length);
extern std::string	RC4(const std::string &key, const std::string &s,
				int start, int length);

# ifndef WrapPy
extern X509	*CACertificate()
			throw (std::runtime_error);
# endif

} // namespace PyX509

#endif
