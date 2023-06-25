/*包含逃逸类型结构体指针，优化触发*/
/* { dg-do compile } */
/* { dg-do run } */

#include <stdlib.h>

typedef struct {
    int a;
    float b;
}__attribute__((aligned(1))) str_t2;

typedef struct {
   int a;
   str_t2 *t;
}str_t1;

#ifdef STACK_SIZE
#if STACK_SIZE > 16000
#define N 1000
#else
#define N (STACK_SIZE / 16)
#endif
#else
#define N 1000
#endif

int num;

int main ()
{
    int i, r;

    r = rand ();
    num = r > N ? N : r; 
    num = 100;
    str_t1 *p1 = calloc(num, sizeof(str_t1));
    str_t1 *p3 = calloc(num, sizeof(str_t1));
    str_t2 *p2 = malloc(num * sizeof(str_t2));
    if (p1 == NULL) {
	return 0;
    }
    for (i = 0; i < num; i++) {
	p1[i].a = 1;
    }
    for (i = 0; i < num; i++) {
	if (p1[i].a != 1) {
	    abort ();
	}
    }
    if (p3 == NULL) {
	return 0;
    }
    for (i = 0; i < num; i++) {
	p3[i].a = 1;
    }
    for (i = 0; i < num; i++) {
	if (p3[i].a != 1) {
	    abort ();
	}
    }
    free(p1);
    free(p2);
    free(p3);

    return 0;
}

/*--------------------------------------------------------------------------*/
/* { dg-final { scan-ipa-dump "Number of structures to transform in semi-relayout is 1" "struct_reorg" } } */
