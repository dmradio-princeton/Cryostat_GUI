#include<stdio.h>

// Fundamental types.
typedef unsigned char	u8;						// 8-bit unsigned.
typedef unsigned short	u16;						// 16-bit unsigned.
typedef unsigned long	u32;						// 32-bit unsigned.
typedef signed short	s16;						// 16-bit signed.
typedef signed long	s32;						// 32-bit signed.
typedef double		DOUBLE;						// Floating point, double precision.
typedef int		BOOL;						// Boolean.

typedef unsigned int lucas_u32;
typedef signed int lucas_s32;

int main(int argc, char** argv)
{
	printf("u8 size: %d\n", (int)sizeof(u8));
	printf("u16 size: %d\n", (int)sizeof(u16));
	printf("u32 size: %d\n", (int)sizeof(u32));
	printf("s16 size: %d\n", (int)sizeof(s16));
	printf("s32 size: %d\n", (int)sizeof(s32));
	printf("DOUBLE size: %d\n", (int)sizeof(DOUBLE));
	printf("BOOL size: %d\n", (int)sizeof(BOOL));

	printf("lucas_u32 size: %d\n", (int)sizeof(lucas_u32));
	printf("lucas_s32 size: %d\n", (int)sizeof(lucas_s32));

	return 0;
}

