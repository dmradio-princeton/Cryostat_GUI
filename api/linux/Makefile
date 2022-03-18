# Build API for Sensoray 2600 as a static library
CC = gcc
CFLAGS = -m64 -fPIC -Wall -O3 -c

all: lib2600.a

lib2600.a: s26core.o s26mod.o
	ar rcs lib2600.a s26core.o s26mod.o

s26core.o: 
	$(CC) $(CFLAGS) -D OSTYPE_LINUX -D ENDIAN_LITTLE -I ../linux -I ../common -o s26core.o ../common/s26core.c

s26mod.o:
	$(CC) $(CFLAGS) -I ../common -o s26mod.o s26mod.c
	
clean:
	rm *.a *.o || echo "s2600 Directory already clean"
