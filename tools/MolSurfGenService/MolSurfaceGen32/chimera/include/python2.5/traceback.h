
#ifndef Py_TRACEBACK_H
#define Py_TRACEBACK_H
#ifdef __cplusplus
extern "C" {
#endif

struct _frame;

/* Traceback interface */

typedef struct _traceback {
	PyObject_HEAD
	struct _traceback *tb_next;
	struct _frame *tb_frame;
	int tb_lasti;
	int tb_lineno;
} PyTracebackObject;

PyAPI_FUNC(int) PyTraceBack_Here(struct _frame *);
PyAPI_FUNC(int) PyTraceBack_Print(PyObject *, PyObject *);

/* Reveal traceback type so we can typecheck traceback objects */
PyAPI_DATA(PyTypeObject) PyTraceBack_Type;
#define PyTraceBack_Check(v) ((v)->ob_type == &PyTraceBack_Type)

#ifdef __cplusplus
}
#endif
#endif /* !Py_TRACEBACK_H */
