# Template by Sarah Cannon
# Based on simple_chain.py by Darryl DeFord


import random 
import pickle

# import matplotlib
# matplotlib.use('Agg')

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import itertools


# BUILD GRAPH
n = 10 # side length of grid
pop = 100
m = 4000
rho = 0.4 # Minority Fraction

# Create  n x n Grid Graph
graph = nx.grid_graph([n,n])

# Initialization steps
for vertex in graph.nodes():
    # Set each vertex in the graph to have population 1
    graph.node[vertex]["TOTPOP"] = 1
 
dual_graph_list = []

for vertex in graph.nodes():
    if vertex[1] < rho*n:
        graph.node[vertex]["MINPOP"] = 1
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 1

dual_graph_list.append(graph)
 
# The voter configuration called Henry :total
for vertex in graph.nodes():
    # For 10 x 10 grid
    Henry = [[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0], [1,1,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0],[0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,1,0,0,0,0],[0,1,0,0,0,0,0,1,1,1],[0,0,0,0,0,0,1,1,1,1],[0,0,0,0,0,0,1,1,1,1]]
    if Henry[9-vertex[1]][vertex[0]] == 0:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 1
    else:
        graph.node[vertex]["MINPOP"] = 1
        graph.node[vertex]["MAJPOP"] = 0 

dual_graph_list.append(graph)  
         

cdict = {1: "gray", 0: "pink"}
nx.draw(graph, pos={x: x for x in graph.nodes()}, 
                    node_color=[cdict[graph.node[x]["MINPOP"]] for x in graph.nodes()],
                    node_size=80,
                    node_shape="o",)


gr = graph

print(nx.diameter(gr))

node_scores = []
r = 1/2
a = 1/(((1-(r)**nx.diameter(gr))/(1-r))-1)

for node in gr.nodes:
   if gr.node[node]["MINPOP"] == 1:
       dictionary_nodes = dict(nx.bfs_successors(gr,node))
       dictionary_levels = {}
       dictionary_levels[1] = dictionary_nodes[node]
       current_list = [dictionary_nodes[x] for x in dictionary_levels[1] if x in dictionary_nodes.keys()]
       i = 2
       while current_list:
           dictionary_levels[i] = list(itertools.chain.from_iterable(current_list))
           current_list = [dictionary_nodes[x] for x in dictionary_levels[i] if x in dictionary_nodes.keys()]
           i += 1
       sum = 0
       for key in dictionary_levels.keys():
           values = dictionary_levels[key]
           num_same = 0
           for test_node in values:
               if gr.node[test_node]["MINPOP"] == 1:
                   num_same += 1
           ratio = num_same / len(values)
           sum += a*r**key
       node_scores.append(sum)
print(np.average(node_scores))

print(a)
