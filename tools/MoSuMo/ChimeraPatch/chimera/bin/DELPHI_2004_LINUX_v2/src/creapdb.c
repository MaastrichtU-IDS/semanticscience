#include <stdio.h>
#include <string.h>

#ifdef IRIX
#define creapdb creapdb_
#elif defined (LINUX)
#define creapdb creapdb_
#elif defined (CRAY)
#define creapdb CREAPDB 
#elif defined (PC)
#define creapdb (_stdcall CREAPDB)
#endif

int readline(FILE *fid,char *str);
void substring(char *str,char *str1,int st,int fin);

void  creapdb(float *prepsout, int *pnumbmol)
{
 FILE *fid,*fidout;
 int objecttype,distrtype,link,kind; 
 /* kind=0 dielectric; kind=1 metal; kind=2 pore,kind=3 fictious,end of pore */
 int ii,cont,cont1,mediacont=0,flag,tmp;
 float medeps[80],repsin,charge;

 char filename[10],line[160],str[7],ans,c='w',choice;
 for (ii=0;ii<159;ii++) line[ii]=' ';
 line[159]='\0';
 *pnumbmol=0;

 /* inizializzazione con mezzo esterno*/
 medeps[mediacont]=*prepsout;
 printf("External Dielectric Constant %8.3f\n",medeps[mediacont]);

 
 printf("\nDo you want to overwrite file fort.13, if present? [y/n]: ");
 scanf("%c",&c);
 if (c!='y') return;

 fidout=fopen("fort.13","w");
 if (fidout==NULL) printf("\n can't open objectfile\n");
 fprintf(fidout,"                                                                         \n");  
 cont=1;
 do                                     /* cycle on different objects */
    {
    flag=0; kind=0;
    /* write down the line: OBJECT #object #objecttype #media */
    fprintf(fidout,"OBJECT %3d ",cont); 

    printf("\nInput objecttype number : ");
    printf("\n  molecule from pdb file [0], ");
    printf("sphere [1], cylinder [2], cone [3], box [4] ");
    printf("\n");
    scanf("%d",&objecttype);
    fprintf(fidout,"%3d ",objecttype);
 
    tmp=-1;
    printf("\nInput internal dielectric constant : ");
    scanf("%f",&repsin);
    for (cont1=1;cont1<=mediacont;cont1++)
        if (repsin==medeps[cont1]) tmp=cont1;
    if (tmp==-1)
       {
       mediacont++;
       medeps[mediacont]=repsin;
       tmp=mediacont;     
       } 
    fprintf(fidout,"%3d ",tmp);                  /* write medianumber */
    fprintf(fidout,"%8.3f\n",repsin);              /* write epsilon */
    
    for (ii=0;ii<159;ii++) line[ii]=' ';
    line[159]='\0';

    switch(objecttype)
       {
       case 0: /* in case the object comes from a pdbfile, writes it down */
             {
             (*pnumbmol)++;
             printf("\ninsert filename of object %d : ",cont); 
             scanf("%s",filename);
             c=getchar();
             fid=fopen(filename,"r");
             if (fid==NULL) printf("\n can't open this file\n");
             while (flag!=EOF) /* writes only lines starting with ATOM or HETATM*/
                {
                flag=readline(fid,line);
                substring(line,str,0,5);
                if ((strcmp(str,"ATOM  ")==0)||(strcmp(str,"HETATM")==0))
                    fprintf(fidout,"%s\n",line);
                }
             fclose(fid);
             break;
             }
       default:
             {
/*           if(repsin==medeps[0])
               {
               printf("Epsilon equal to the solvent=>Assuming this is a pore\n");
               kind=2;
               }
             if(repsin==10000)
               {
               printf("Epsilon equal to 10000=>Assuming this is a metal\n");
               kind=1;
               }*/

             printf("\nInsert data of object %d (spaced by commas): ",cont);
             scanf("%s",line);
             c=getchar();

             fprintf(fidout,"DATA   %3d %3d %3d %s\n",objecttype,tmp,kind,line);
             if ((kind==2)&&(objecttype==2))
             /*aggiungo oggetto fittizio per poter generare vertici bene*/
                {
                cont++;
                fprintf(fidout,"OBJECT %3d %3d %3d %8.3f\n",cont,20,tmp,repsin);
                fprintf(fidout,"DATA   %3d %3d %3d %s\n",10,tmp,3,line);
                cont++;
                fprintf(fidout,"OBJECT %3d %3d %3d %8.3f\n",cont,20,tmp,repsin);
                fprintf(fidout,"DATA   %3d %3d %3d %s\n",10,tmp,3,line);
                }
             break;
             }
        }
    printf("\n Are you going to insert a new object?(y/n):");  
    ans=getchar();
    c=getchar();
    cont++;
    } while((ans=='y')||(ans=='Y'));

 printf("\n Are you going to insert charge distributions?(y/n):"); 
 ans=getchar();
 c=getchar();
 if ((ans=='y')||(ans=='Y'))
   { 
   cont=1;
   do                                            /* cycle on different distributions */
    {
    /* write down the line: CRGDST #distribution              */
    fprintf(fidout,"CRGDST %3d ",cont);

    printf("\nInput distrtype number : ");
    printf("\nShape: sphere [1], cylinder [2], cone [3], box [4], ");
    printf("\npoint charge [8], segment [9], disk [10], rectangular plate [11] ");
    printf("\n");
    scanf("%d",&distrtype);
    c=getchar();

    printf("\nIs it a volumic (v) or surfacial (s) charge? : ");
    choice=getchar();
    c=getchar();

    printf("\nInput objectnumber to which this distribution is linked (0 if is free) : ");
    scanf("%d",&link);

    printf("\nInput total charge in this distribution : ");
    scanf("%f",&charge);
   
    for (ii=0;ii<159;ii++) line[ii]=' ';
    line[159]='\0';

    printf("\nInsert data of distribution %d : ",cont);
    scanf("%s",line);
    c=getchar();
    /*printf("\n debug : line= %s :",line);*/
    fprintf(fidout,"\nDATA   %3d %c %3d %8.3f %s\n",distrtype,choice,link,charge,line);

    printf("\n Are you going to insert a new distribution?(y/n):"); 
    ans=getchar();
    c=getchar();
    cont++;
    } while((ans=='y')||(ans=='Y'));
   }

 rewind(fidout);
 fprintf(fidout,"MEDIA  %3d ",mediacont);  /* write number of different media at the beginning of file*/

 fclose(fidout);
 return;
} 

int readline(FILE *fid,char *str)
 
   {
   char c;
   int cont=0,flag=0;
   flag=fscanf(fid,"%c",&c);
/* while ((c!=EOF) && (c!= '\n')&& (flag!=EOF))*/
   while ((c!= '\n')&& (flag!=EOF))
    {
    str[cont]=c;
    flag=fscanf(fid,"%c",&c);
    cont++;
    }
    str[cont]='\0';
    return(flag); 
   }  

void substring(char *str,char *str1,int st,int fin)

   {
   int cont,cont1=0;
   for (cont=st;cont<=fin;cont++)
     {
     str1[cont1]=str[cont];
     cont1++;
     }
     str1[cont1]='\0';
     return;
   } 
