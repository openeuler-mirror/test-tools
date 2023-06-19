/*结构体指针做减法，优化触发*/
/* { dg-do compile } */
/* { dg-do run } */

#include <stdlib.h>

typedef struct node node_t;
typedef struct node* node_p;

struct node {
    unsigned long a;
    unsigned long b;
};

int max;
int x;

node_p n;
node_p z;

int main ()
{
    x = 9;
    max = 100;
    n = (node_p)calloc(max, sizeof(node_t));
    z = (node_p)calloc(max, sizeof(node_t));
    node_p xp = &n[x];

    if (xp - z == 10) {
	abort ();
    }
    return 0;
}

/* { dg-final { scan-ipa-dump "Number of structures to transform in semi-relayout is 1" "struct_reorg" } } */
