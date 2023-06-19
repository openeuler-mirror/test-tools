/*结构体指针存在三次calloc分配，优化触发*/
/* { dg-do compile } */
/* { dg-do run } */

#include <stdlib.h>

typedef struct str_t1 str_t;
struct str_t1 {
    short a;
    double b;
};

#ifdef STACK_SIZE
#if STACK_SIZE > 16000
#define N 1000
#else
#define N (STACK_SIZE / 16)
#endif
#else
#define N 1000
#endif

str_t *p1;
str_t *p2;
str_t *p3;
int num;

int main ()
{
    int i, r;

    r = rand ();
    num = r > N ? N : r;
    p1 = calloc(num, sizeof(str_t));
    p2 = calloc(num, sizeof(str_t));
    p3 = calloc(num, sizeof(str_t));
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
    for (i = 0; i < num; i++) {
	p2[i].a = 1;
    }
    for (i = 0; i < num; i++) {
	if (p2[i].a != 1) {
	    abort ();
	}
    }
    for (i = 0; i < num; i++) {
	p3[i].a = 1;
    }
    for (i = 0; i < num; i++) {
	if (p3[i].a != 1) {
	    abort ();
	}
    }

    return 0;
}

/* { dg-final { scan-ipa-dump "Number of structures to transform in semi-relayout is 1" "struct_reorg" } } */
