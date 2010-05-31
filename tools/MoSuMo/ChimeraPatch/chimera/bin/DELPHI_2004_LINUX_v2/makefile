VPATH=src

FC=/razor/0/common/pgi7.1/linux86/7.1/bin/pgf77
CC=/razor/0/common/pgi7.1/linux86/7.1/bin/pgcc

#RECFLAGS = -g -Kieee -Mrecursive -DLINUX
#FLAGS = -g -Kieee  -DLINUX
#CFLAGS = -g -Kieee -DLINUX
#LFLAGS = -g -Kieee

RECFLAGS = -O3 -Kieee  -Mrecursive -DLINUX
#FLAGS = -O3   -Kieee -DLINUX -byteswapio
FLAGS = -O3   -Kieee -DLINUX
CFLAGS = -O3  -Kieee -DLINUX
#CFLAGS = -O3  -Kieee -DLINUX -byteswapio
#LFLAGS = -O3  #dynamic
LFLAGS = -O3 -Bstatic -L/razor/0/common/pgi7.0/share_objects/lib/libpgc.so #static


include $(VPATH)/genericLinux.mk

