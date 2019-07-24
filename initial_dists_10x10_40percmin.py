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
    graph.node[vertex]["TOTPOP"] = 100
 
dual_graph_list = []

#four rows of minority at the bottom
for vertex in graph.nodes():
    if vertex[1] < rho*n:
        graph.node[vertex]["MINPOP"] = 100
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 100

dual_graph_list.append(graph)

# four rows of mostly minrity at the bottom
for vertex in graph.nodes():
    if vertex[1] < rho*n:
        graph.node[vertex]["MINPOP"] = 70
        graph.node[vertex]["MAJPOP"] = 30
    else:
        graph.node[vertex]["MINPOP"] = 20
        graph.node[vertex]["MAJPOP"] = 80

dual_graph_list.append(graph)
 
 
# The voter configuration called Henry :total
for vertex in graph.nodes():
    # For 10 x 10 grid
    Henry = [[1,1,0,0,0,0,0,0,1,1],[1,1,1,1,1,1,1,1,1,0],[0,1,0,0,0,1,1,1,0,0],[1,0,0,1,1,0,0,0,1,1],[0,0,1,1,1,1,1,0,1,0],[0,1,1,1,0,1,1,1,1,0],[0,1,0,0,0,1,0,1,1,1],[0,1,0,1,1,1,1,1,1,0],[0,1,1,1,0,0,1,1,1,0],[1,1,1,0,1,1,1,1,0,0]]
    if Henry[9-vertex[1]][vertex[0]] == 0:
        graph.node[vertex]["MINPOP"] = 100
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 100  
dual_graph_list.append(graph)  

# The voter configuration called Henry: mostly minority
for vertex in graph.nodes():
    # For 10 x 10 grid
    Henry = [[1,1,0,0,0,0,0,0,1,1],[1,1,1,1,1,1,1,1,1,0],[0,1,0,0,0,1,1,1,0,0],[1,0,0,1,1,0,0,0,1,1],[0,0,1,1,1,1,1,0,1,0],[0,1,1,1,0,1,1,1,1,0],[0,1,0,0,0,1,0,1,1,1],[0,1,0,1,1,1,1,1,1,0],[0,1,1,1,0,0,1,1,1,0],[1,1,1,0,1,1,1,1,0,0]]
    if Henry[9-vertex[1]][vertex[0]] == 0:
        graph.node[vertex]["MINPOP"] = 70
        graph.node[vertex]["MAJPOP"] = 30
    else:
        graph.node[vertex]["MINPOP"] = 20
        graph.node[vertex]["MAJPOP"] = 80
dual_graph_list.append(graph) 

#Random totally minority vertices        
minorityvtxs = random.sample(graph.nodes(),40)        
for vertex in graph.nodes():
    if vertex in minorityvtxs:
        graph.node[vertex]["MINPOP"] = 100
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 100
dual_graph_list.append(graph) 

#random totally minority vertices
minorityvtxs = random.sample(graph.nodes(),40)        
for vertex in graph.nodes():
    if vertex in minorityvtxs:
        graph.node[vertex]["MINPOP"] = 100
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 100
dual_graph_list.append(graph) 

#random mostly minority vertices
minorityvtxs = random.sample(graph.nodes(),40)        
for vertex in graph.nodes():
    if vertex in minorityvtxs:
        graph.node[vertex]["MINPOP"] = 100
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 100
dual_graph_list.append(graph) 

#random moatly minority vertices
minorityvtxs = random.sample(graph.nodes(),40)        
for vertex in graph.nodes():
    if vertex in minorityvtxs:
        graph.node[vertex]["MINPOP"] = 70
        graph.node[vertex]["MAJPOP"] = 30
    else:
        graph.node[vertex]["MINPOP"] = 20
        graph.node[vertex]["MAJPOP"] = 80
dual_graph_list.append(graph) 

#Center blob, from Natasha's code, modified so that there are 4000 minority voters
for vertex in graph.nodes():
    # For 10 x 10 grid
    Henry = [[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],
             [0,0,0,1,0,0,0,0,0,0],[0,0,1,1,1,0,0,0,0,0],[0,0,1,1,1,1,1,0,0,0], 
             [0,0,1,1,1,1,1,1,1,0],[0,0,0,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]
    if Henry[9-vertex[1]][vertex[0]] == 0:
        graph.node[vertex]["MINPOP"] = 25
        graph.node[vertex]["MAJPOP"] = 75
    else:
        graph.node[vertex]["MINPOP"] = 100
        graph.node[vertex]["MAJPOP"] = 0 
dual_graph_list.append(graph) 
 

# The voter configuration called Henry: mostly minority
for vertex in graph.nodes():
    # For 10 x 10 grid
    Henry = [[1,1,0,0,0,0,0,0,1,1],[1,1,1,1,1,1,1,1,1,0],[0,1,0,0,0,1,1,1,0,0],[1,0,0,1,1,0,0,0,1,1],[0,0,1,1,1,1,1,0,1,0],[0,1,1,1,0,1,1,1,1,0],[0,1,0,0,0,1,0,1,1,1],[0,1,0,1,1,1,1,1,1,0],[0,1,1,1,0,0,1,1,1,0],[1,1,1,0,1,1,1,1,0,0]]
    if Henry[9-vertex[1]][vertex[0]] == 0:
        graph.node[vertex]["MINPOP"] = 70
        graph.node[vertex]["MAJPOP"] = 30
    else:
        graph.node[vertex]["MINPOP"] = 20
        graph.node[vertex]["MAJPOP"] = 80
dual_graph_list.append(graph) 

print(len(dual_graph_list))
#pickle dual graph list
# Save initial spatial distribution of voters
file_Name = "10x10_100pernode_40percmin"
# open the file for writing
fileObject = open(file_Name,'wb') 
pickle.dump(dual_graph_list,fileObject)
fileObject.close()

fileObject = open(file_Name,'rb') # Open for reading
dgl = pickle.load(fileObject)

print(len(dgl))

#unpickle to check it 




