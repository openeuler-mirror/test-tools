/* 结构体指针比较 */
/* { dg-do compile } */
/* { dg-do run } */

#include <stdlib.h>

typedef struct str_t str_t1;
struct str_t {
    int a;
    float b;
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

int num;
str_t1 *t1;
int main ()
{
    int i, r;
    r = rand ();
    num = r > N ? N : r; 
    str_t1 *p1 = calloc(num, sizeof(str_t1));
    t1 = &p1[0] - 1;
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
    for (i = 0; i < num-1; i++) {
	if(&p1[i] < t1) {
	    abort();
	}
    }
    free(p1);

    return 0;
}

/*--------------------------------------------------------------------------*/
/* { dg-final { scan-ipa-dump "Number of structures to transform in pointer compression is 1" "struct_reorg" } } */
