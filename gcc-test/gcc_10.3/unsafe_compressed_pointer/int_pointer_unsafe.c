/* 不安全指针压缩，p1被压缩 */
/* { dg-do compile } */
/* { dg-do run } */

#include <stdlib.h>

typedef struct str_t str_t1;
struct str_t {
    int a;
    int *b;
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

str_t1 *p1;
int num;

int main ()
{
    int i, r;

    r = rand ();
    num = r > N ? N : r; 
    p1 = calloc(num, sizeof(str_t1));
    if (p1 == NULL) {
	return 0;
    }
    for (i = 0; i < num; i++) {
	p1[i].a = 1;
    }
    for (i = 0; i < num; i++) {
	p1[i].b = &r;
    }
    for (i = 0; i < num; i++) {
	if (p1[i].a != 1) {
	    abort ();
	}
    }
    
    return 0;
}

/*--------------------------------------------------------------------------*/
/* { dg-final { scan-ipa-dump "Number of structures to transform is 1" "struct_reorg" } } */
