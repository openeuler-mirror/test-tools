/* 包含结构体指针的不安全指针压缩 */
/* { dg-do compile } */
/* { dg-do run } */

#include <stdlib.h>

typedef struct str_t1 str_t;
typedef struct u_n u_t;
struct u_n {
    float b;
};

struct str_t1 {
    int a;
    u_t *u;
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
int num;

int main ()
{
    int i, r;

    r = rand ();
    num = r > N ? N : r; 
    p1 = calloc(num, sizeof(str_t));
    if (p1 == NULL) {
	return 0;
    }
    for (i = 0; i < num; i++) {
	p1[i].a = 1;
    }
    for (i = 0; i < num; i++){
	p1[i].u = malloc(1 * sizeof (u_t));
	(p1[i].u)->b = 2;
    }
    
    for (i = 0; i < num; i++) {
	if (p1[i].a != 1) {
	    abort ();
	}
    }
    
    return 0;
}

/*--------------------------------------------------------------------------*/
/* { dg-final { scan-ipa-dump "Number of structures to transform in pointer compression is 1" "struct_reorg" } } */
