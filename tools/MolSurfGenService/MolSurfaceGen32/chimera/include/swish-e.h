#ifndef SEARCHSWISH_H
#define SEARCHSWISH_H 1

#include "time.h"  /* for time_t, which isn't really needed */

#ifdef __cplusplus
extern "C" {
#endif

typedef void * SW_HANDLE;
typedef void * SW_SEARCH;
typedef void * SW_RESULTS;
typedef void * SW_RESULT;
typedef void * SW_FUZZYWORD;  /* access to the swish-e stemmers */


/* These must match headers.h */

typedef enum {
    SWISH_NUMBER,
    SWISH_STRING,
    SWISH_LIST,
    SWISH_BOOL,
    SWISH_WORD_HASH,
    SWISH_OTHER_DATA,
    SWISH_HEADER_ERROR /* must check error in this case */
} SWISH_HEADER_TYPE;

typedef union
{
    const char           *string;
    const char          **string_list;
          unsigned long   number;
          int             boolean;
} SWISH_HEADER_VALUE;


const char **SwishHeaderNames( SW_HANDLE );  /* fetch the list of available header names */
const char **SwishIndexNames( SW_HANDLE );  /* fetch list of index files names associated */
SWISH_HEADER_VALUE SwishHeaderValue( SW_HANDLE, const char *index_name, const  char *cur_header, SWISH_HEADER_TYPE *type );
SWISH_HEADER_VALUE SwishResultIndexValue( SW_RESULT, const char *name, SWISH_HEADER_TYPE *type );

typedef const void * SW_META;
typedef SW_META * SWISH_META_LIST;

/* Meta and Property Values */

#define SW_META_TYPE_UNDEF 0
#define SW_META_TYPE_STRING 4
#define SW_META_TYPE_ULONG 8
#define SW_META_TYPE_DATE 16

SWISH_META_LIST SwishMetaList( SW_HANDLE, const char *index_name );
SWISH_META_LIST SwishPropertyList( SW_HANDLE, const char *index_name );
SWISH_META_LIST SwishResultMetaList( SW_RESULT );
SWISH_META_LIST SwishResultPropertyList( SW_RESULT );
const char *SwishMetaName( SW_META );
int SwishMetaType( SW_META );
int SwishMetaID( SW_META );

/* Limit searches by structure */

#define IN_FILE_BIT     0
#define IN_TITLE_BIT    1
#define IN_HEAD_BIT     2
#define IN_BODY_BIT     3
#define IN_COMMENTS_BIT 4
#define IN_HEADER_BIT   5
#define IN_EMPHASIZED_BIT   6
#define IN_META_BIT     7


#define IN_FILE         (1<<IN_FILE_BIT)
#define IN_TITLE        (1<<IN_TITLE_BIT)
#define IN_HEAD         (1<<IN_HEAD_BIT)
#define IN_BODY         (1<<IN_BODY_BIT)
#define IN_COMMENTS     (1<<IN_COMMENTS_BIT)
#define IN_HEADER       (1<<IN_HEADER_BIT)
#define IN_EMPHASIZED (1<<IN_EMPHASIZED_BIT)
#define IN_META         (1<<IN_META_BIT)
#define IN_ALL (IN_FILE|IN_TITLE|IN_HEAD|IN_BODY|IN_COMMENTS|IN_HEADER|IN_EMPHASIZED|IN_META)



SW_HANDLE  SwishInit(char *);

SW_RESULTS SwishQuery(SW_HANDLE, char *words );

SW_SEARCH New_Search_Object( SW_HANDLE, char *query );

void SwishRankScheme( SW_HANDLE sw, int scheme );
void SwishSetRefPtr( SW_HANDLE sw, void *address );
void *SwishGetRefPtr( SW_HANDLE sw );

void *SwishSearch_parent( SW_SEARCH srch );
void *SwishResults_parent( SW_RESULTS results );
void *SwishResult_parent( SW_RESULT result );
void ResultsSetRefPtr( SW_RESULTS results, void *address );

void SwishSetStructure( SW_SEARCH srch, int structure );
void SwishPhraseDelimiter( SW_SEARCH srch, char delimiter );
void SwishSetSort( SW_SEARCH srch, char *sort );
void SwishSetQuery( SW_SEARCH srch, char *query );

int SwishSetSearchLimit( SW_SEARCH srch, char *propertyname, char *low, char *hi);
void SwishResetSearchLimit( SW_SEARCH srch );

SW_RESULTS SwishExecute( SW_SEARCH, char *optional_query );

/* Headers specific to results */
int SwishHits( SW_RESULTS );
SWISH_HEADER_VALUE SwishParsedWords( SW_RESULTS, const char *index_name );
SWISH_HEADER_VALUE SwishRemovedStopwords( SW_RESULTS, const char *index_name );



int SwishSeekResult( SW_RESULTS, int position );
SW_RESULT SwishNextResult( SW_RESULTS );

char *SwishResultPropertyStr(SW_RESULT, char *propertyname);
unsigned long SwishResultPropertyULong(SW_RESULT, char *propertyname);
SW_HANDLE SW_ResultToSW_HANDLE( SW_RESULT );
SW_HANDLE SW_ResultsToSW_HANDLE( SW_RESULTS );

void Free_Search_Object( SW_SEARCH srch );
void Free_Results_Object( SW_RESULTS results );


void SwishClose( SW_HANDLE );


int  SwishError( SW_HANDLE );           /* test if error state - returns error number */
int  SwishCriticalError( SW_HANDLE );   /* true if show stopping error */
void SwishAbortLastError( SW_HANDLE );  /* format and abort the error message */

char *SwishErrorString( SW_HANDLE );    /* string for the error number */
char *SwishLastErrorMsg( SW_HANDLE );   /* more specific message about the error */

void set_error_handle( FILE *where );
void SwishErrorsToStderr( void );

/* Returns all words that begin with the specified char */
const char *SwishWordsByLetter(SW_HANDLE, char *filename, char c);


/* Stemming Interface */

char *SwishStemWord( SW_HANDLE, char *word );  /* Really this is depreciated */

SW_FUZZYWORD SwishFuzzyWord( SW_RESULT r, char *word );
SW_FUZZYWORD SwishFuzzy( SW_HANDLE sw, const char *index_name, char *word );
const char **SwishFuzzyWordList( SW_FUZZYWORD fw );
int SwishFuzzyWordCount( SW_FUZZYWORD fw );
int SwishFuzzyWordError( SW_FUZZYWORD fw );
void SwishFuzzyWordFree( SW_FUZZYWORD fw );
const char *SwishFuzzyMode( SW_RESULT r );

/* For low-level access to a property */

typedef enum
{                               /* Property Datatypes */
    PROP_UNDEFINED = -1,        /* a result does not have a value for that prop */
    PROP_UNKNOWN = 0,           /* invalid property requested (not really used anyplace) */
    PROP_STRING,
    PROP_INTEGER,
    PROP_FLOAT,
    PROP_DATE,
    PROP_ULONG
}
PropType;



typedef union
{                               /* storage of the PropertyValue */
    char   *v_str;              /* strings */
    int     v_int;              /* Integer */
    time_t  v_date;             /* Date    */
    double  v_float;            /* Double Float */
    unsigned long v_ulong;      /* Unsigned long */
}
u_PropValue1;
 
typedef struct
{                               /* Propvalue with type info */
    PropType datatype;
    u_PropValue1 value;
    int      destroy;           /* flag to destroy (free) any pointer type */
} 
PropValue;

PropValue *getResultPropValue (SW_RESULT result, char *name, int ID);
void    freeResultPropValue(PropValue *pv);

#ifdef __cplusplus
}
#endif /* __cplusplus */


#endif /* !SEARCHSWISH_H */




