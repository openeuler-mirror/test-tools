/*一个结构体中同时有两个结构体指针被压缩*/
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
    node_p pred;
};

struct arc
{
    arc_p tail;
};

struct network
{
    char arr[7];
    arc_p sorted_arcs;
    node_p nodes;
};

network_t net;
node_p node;
arc_p sorted_arc;

int main ()
{
    sorted_arc = (arc_p) calloc (MAX, sizeof (arc_t));
    node = (node_p) calloc (MAX, sizeof (node_t));
    net.nodes = node;
    net.sorted_arcs = sorted_arc;
    for (unsigned i = 0; i < MAX; i++){
	node->pred = node;
	node = node + 1;
    }

    for (unsigned i = 0; i < MAX; i++){
        sorted_arc->tail = sorted_arc;
        sorted_arc = sorted_arc + 1;
    }

    node = net.nodes;
    for (unsigned i = 0; i < MAX; i++){
        if (node->pred != node)
            abort ();
        node = node + 1;
    }

    sorted_arc = net.sorted_arcs;
    for (unsigned i = 0; i < MAX; i++){
        if (sorted_arc->tail != sorted_arc)
            abort ();
        sorted_arc = sorted_arc + 1;
    }
    
    return 0;
}

/* { dg-final { scan-ipa-dump "Number of structures to transform in pointer compression is 2" "struct_reorg" } } */
