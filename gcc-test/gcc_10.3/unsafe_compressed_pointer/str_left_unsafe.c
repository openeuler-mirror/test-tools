/* 结构体指针偏移 */
/* { dg-do compile } */
/* { dg-do run } */
#include <stdio.h>
#include <stdlib.h>

typedef struct str_t1 str_t;
struct str_t1 {
    int a;
    float b;
};

#ifdef STACK_SIZE
#if STACK_SIZE > 16000
#define N 1000
#else
#define N (STACK_SIZE/16)
#endif
#else
#define N 1000
#endif

int num;
str_t *p3;

int main ()
{
    int i, r;

    r = rand ();
    num = r > N ? N : r; 
    str_t *p1 = calloc(num, sizeof(str_t));
    if (p1 == NULL) {
	return 0;
    }
    for (i = 0; i < num; i++) {
	p1[i].a = 1;
    }
    for (i = 0; i < num; i++) {
	p1[i].b = 2;
    }
    for (i = 0; i < num; i++) {
	if (p1[i].a != 1) {
	    abort ();
	}
    }    
    for (i = 0; i < num; i++) {
	if (abs(p1[i].b - 2) > 0.0001) {
	    abort ();
	}
    }
    p3 = (str_t *)(&p1 + 1);
    if (p3 == p1) {
	abort ();
    }

    return 0;
}

/*--------------------------------------------------------------------------*/
/* { dg-final { scan-ipa-dump "Number of structures to transform in pointer compression is 1" "struct_reorg" } } */
