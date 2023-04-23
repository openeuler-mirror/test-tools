/*被压缩指针指向结构体中包含enum类型成员，优化触发*/
/* { dg-do compile } */
/* { dg-do run } */

#include <stdio.h>
#include <stdlib.h>
typedef struct node node_t;
typedef struct node *node_p;
typedef struct arc arc_t;
typedef struct arc *arc_p;
typedef struct network network_t;
const unsigned MAX = 100;
struct node
{
    enum E{
          B,
          C,
    } e;
    node_p pred;
};

struct arc
{
    node_p tail;
};

struct network
{
    arc_p arcs;
    arc_p sorted_arcs;
    node_p nodes;
};

network_t net;
node_p node;

int main ()
{
    net.arcs = (arc_p) calloc (MAX, sizeof (arc_t));
    net.sorted_arcs = (arc_p) calloc (MAX, sizeof (arc_t));
    node = (node_p) calloc (MAX,sizeof (node_t));
    net.nodes = node;
    for (unsigned i = 0; i < MAX; i++){
        node->pred = node;
        node = node + 1;
    }
    node = net.nodes;
    for (unsigned i = 0; i < MAX; i++){
        if (node->pred != node)
            abort ();
            node = node + 1;
    }
    node = net.nodes;
    for (unsigned i = 0; i < MAX; i++){
	node->e = C;
	node = node + 1;
    }
    node = net.nodes;
    for (unsigned i = 0; i < MAX; i++){
	if (node->e != C)
	    abort ();
    }
    return 0;
}

/* { dg-final { scan-ipa-dump "Number of structures to transform in pointer compression is 1" "struct_reorg" } } */
