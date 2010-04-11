
#ifndef Py_COMPILE_H
#define Py_COMPILE_H

#include "code.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Public interface */
struct _node; /* Declare the existence of this type */
PyAPI_FUNC(PyCodeObject *) PyNode_Compile(struct _node *, const char *);

/* Future feature support */

typedef struct {
    int ff_features;      /* flags set by future statements */
    int ff_lineno;        /* line number of last future statement */
} PyFutureFeatures;

#define FUTURE_NESTED_SCOPES "nested_scopes"
#define FUTURE_GENERATORS "generators"
#define FUTURE_DIVISION "division"
#define FUTURE_ABSOLUTE_IMPORT "absolute_import"
#define FUTURE_WITH_STATEMENT "with_statement"

struct _mod; /* Declare the existence of this type */
PyAPI_FUNC(PyCodeObject *) PyAST_Compile(struct _mod *, const char *,
					PyCompilerFlags *, PyArena *);
PyAPI_FUNC(PyFutureFeatures *) PyFuture_FromAST(struct _mod *, const char *);

#define ERR_LATE_FUTURE \
"from __future__ imports must occur at the beginning of the file"

#ifdef __cplusplus
}
#endif
#endif /* !Py_COMPILE_H */
