# Template by Sarah Cannon
# Based on simple_chain.py by Darryl DeFord


import random 
import pickle

# import matplotlib
# matplotlib.use('Agg')

import matplotlib.pyplot as plt
import networkx as nx


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
    Henry = [[1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1]]
    if Henry[9-vertex[1]][vertex[0]] == 0:
        graph.node[vertex]["MINPOP"] = 1
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 1  

dual_graph_list.append(graph)  
         

cdict = {1: "gray", 0: "pink"}
nx.draw(graph, pos={x: x for x in graph.nodes()}, 
                    node_color=[cdict[graph.node[x]["MINPOP"]] for x in graph.nodes()],
                    node_size=80,
                    node_shape="o",)
