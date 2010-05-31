/* call to the C function realloc is necessary as memory is adjusted at
   run time 			S. Sridharan. Sep 95 */
#include <stdlib.h> 

#ifdef IRIX
#define memalloc memalloc_
#elif defined (LINUX)
#define memalloc memalloc_
#elif defined (CRAY)
#define memalloc MEMALLOC
#elif defined (PC)
#define memalloc (_stdcall MEMALLOC)
#endif
void *memalloc( void **ptr, int *new_size )
{	void *newptr;   
	if(!*new_size) 
        {
	  if(*ptr) free(*ptr);
	  return NULL;
	}
	if(!*ptr) 
        {
          if((*new_size)<0){newptr=calloc(-(*new_size),1);}
		  else
          {
	    /*newptr=malloc(*new_size);*/
            newptr=calloc((*new_size)/4,4);
          }
	} else 
        {if(*new_size<0) { newptr=realloc(*ptr, -(*new_size));
		}else{             newptr=realloc(*ptr, *new_size);	}
	}
	if (newptr == 0 && *new_size != 0) 
        {
#ifdef PC
          perror("memalloc");
#else
          perror("memalloc", 8L);
#endif
	  exit(EXIT_FAILURE);
	}

	return newptr;
}
