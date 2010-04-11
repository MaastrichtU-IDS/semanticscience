// required file for genclass'd file from GNU libg++ library
// $Id: StrPtrdefs.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef StringPtr_defs_h
#define StringPtr_defs_h

#include <String.h>
#include <builtin.h>

typedef String	*StringPtr;

#define StringPtrEQ(a, b)  (*(a) == *(b))

#define StringPtrLE(a, b)  (*(a) <= *(b))

#define StringPtrCMP(a, b) ( (*(a) <= *(b))? ((*(a) == *(b))? 0 : -1) : 1 )

#define	StringPtrHASH(x)	hashpjw((const char *) *x)

#define DEFAULT_INITIAL_CAPACITY 100

#define HASHTABLE_TOO_CROWDED(COUNT, SIZE) ((SIZE) - ((SIZE) >> 3) <= (COUNT))

#endif
