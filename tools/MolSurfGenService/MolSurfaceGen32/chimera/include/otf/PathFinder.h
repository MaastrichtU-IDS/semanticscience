#ifndef otf_PathFinder_h
# define otf_PathFinder_h

# include "config.h"
# include <string>
# include <vector>
# include <fstream>

namespace otf {

class PathFinder;

class OTF_IMEX PathFactory {
	// singleton class
	static PathFactory *pathFactory_;
	PathFactory();
public:
	static PathFactory *pathFactory();
	PathFinder	*makePathFinder(const std::string &dataRoot,
				const std::string &package,
				const std::string &env,
				bool hideData = true,
				bool useDotDefault = true,
				bool useHomeDefault = true) const;
	static char	pathSeparator();
};

class OTF_IMEX PathFinder {
	void operator=(const PathFinder &p);	// disable
public:
	PathFinder(const PathFinder &p);

	// in all the below functions, 'app' can be an empty string, in which
	// case no 'app' subdirectory is assumed

	typedef std::vector<std::string> StrList;
	// The paths that will be checked, in the order they are checked
	void		pathList(/*OUT*/ StrList *paths, const std::string &app,
				const std::string &file, bool usePackageData,
				bool useDot, bool useHome) const;
	void		pathList(/*OUT*/ StrList *paths, const std::string &app,
				const std::string &file) const;
	void		pathList(/*OUT*/ StrList *paths, const std::string &app,
				const std::string &file,
				bool usePackageData) const;

	// first path that has the named file/directory
	// order checked is:
	//      . (if 'useDot' is true)
	//      ./package/app (again, if 'useDot' is true)
	//      ~/package/app (if 'useHome' is true)
	//      <data root>/app (presumably, 'data root' contains package's
	//				name in some form)
	std::string	firstExistingFile(const std::string &app,
				const std::string &file, bool usePackageData,
				bool useDot, bool useHome) const;
	std::string	firstExistingFile(const std::string &app,
				const std::string &file, bool useDot,
				bool useHome) const;
	std::string	firstExistingFile(const std::string &app,
				const std::string &file) const;
	std::string	firstExistingDir(const std::string &app,
				const std::string &file, bool usePackageData,
				bool useDot, bool useHome) const;
	std::string	firstExistingDir(const std::string &app,
				const std::string &file, bool useDot,
				bool useHome) const;
	std::string	firstExistingDir(const std::string &app,
				const std::string &file) const;

	// all paths that have the named file
	void		allExistingFiles(/*OUT*/ StrList *paths,
				const std::string &app, const std::string &file,
				bool usePackageData, bool useDot, bool useHome
			) const;
	void		allExistingFiles(/*OUT*/ StrList *paths,
				const std::string &app, const std::string &file,
				bool useDot, bool useHome) const;
	void		allExistingFiles(/*OUT*/ StrList *paths,
				const std::string &app, const std::string &file
			) const;
	void		allExistingDirs(/*OUT*/ StrList *paths,
				const std::string &app, const std::string &file,
				bool usePackageData, bool useDot, bool useHome
			) const;
	void		allExistingDirs(/*OUT*/ StrList *paths,
				const std::string &app, const std::string &file,
				bool useDot, bool useHome) const;
	void		allExistingDirs(/*OUT*/ StrList *paths,
				const std::string &app, const std::string &file
			) const;
	
	// configuration information
	const std::string &
			dataRoot() const;
	bool		hideData() const;
	bool		packageDotDefault() const;
	bool		packageHomeDefault() const;
private:
	std::string	firstExisting(const std::string &app,
				const std::string &file, bool useDot,
				bool useHome, bool asFile, bool usePackageData = true) const; void		allExisting(/*OUT*/ StrList *validPaths, const std::string &app,
				const std::string &file, bool useDot,
				bool useHome, bool asFile,
				bool usePackageData = true) const;
	friend class PathFactory;
	PathFinder(const std::string &dataRoot, const std::string &package,
				const std::string &env, bool hideData,
				bool useDotDefault, bool useHomeDefault);

	std::string	dataRoot_;
	std::string	package_;
	const bool	hideData_;
	const bool	useDotDefault_;
	const bool	useHomeDefault_;
};

class OTF_IMEX InputFile {
	InputFile(const InputFile&);		// disable
	InputFile& operator=(const InputFile&);	// disable
public:
	// a wrapper around ifstream that guarantees that the file closes
	// when the scope is closed
	std::ifstream &ifstream() const;

	// check ifstream() for success in opening file
	InputFile(const std::string &path);
	~InputFile();
private:
	std::ifstream *ifs_;
};

class OTF_IMEX OutputFile {
	OutputFile(const OutputFile&);			// disable
	OutputFile& operator=(const OutputFile&);	// disable
public:
	// a wrapper around ofstream that guarantees that the file closes
	// when the scope is closed
	std::ofstream &ofstream() const;

	// check ofstream() for success in opening file
	OutputFile(const std::string &path);
	~OutputFile();
private:
	std::ofstream *ofs_;
};

} // namespace otf

#endif
