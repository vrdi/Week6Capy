# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 09:50:26 2019

@author: canno
"""

import random 
import pickle

import matplotlib.pyplot as plt
import networkx as nx

# BUILD GRAPH
n = 10 # side length of grid; because some configurations are hard-coded, bust be 10
pop = 100 #population per node
m = 4000 #number of minority voters: hard-coded for now
rho = 0.4 #Minority Fraction: hard-coded for now

# Create  n x n Grid Graph
graph = nx.grid_graph([n,n])

# Initialization steps
for vertex in graph.nodes():
    # Set each vertex in the graph to have population 100
    graph.node[vertex]["TOTPOP"] = 100
 
dual_graph_list = []

#four rows of totally minority voters
for vertex in graph.nodes():
    if vertex[1] < rho*n:
        graph.node[vertex]["MINPOP"] = 100
        graph.node[vertex]["MAJPOP"] = 0
    else:
        graph.node[vertex]["MINPOP"] = 0
        graph.node[vertex]["MAJPOP"] = 100

dual_graph_list.append(graph)


# four rows of mostly minority voters
for vertex in graph.nodes():
    if vertex[1] < rho*n:
        graph.node[vertex]["MINPOP"] = 70
        graph.node[vertex]["MAJPOP"] = 30
    else:
        graph.node[vertex]["MINPOP"] = 20
        graph.node[vertex]["MAJPOP"] = 80

dual_graph_list.append(graph)
 
 
# The voter configuration called Henry :totally minority
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

#another random totally minority vertices
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

#another random moatly minority vertices
minorityvtxs = random.sample(graph.nodes(),40)        
for vertex in graph.nodes():
    if vertex in minorityvtxs:
        graph.node[vertex]["MINPOP"] = 70
        graph.node[vertex]["MAJPOP"] = 30
    else:
        graph.node[vertex]["MINPOP"] = 20
        graph.node[vertex]["MAJPOP"] = 80
dual_graph_list.append(graph) 

#Center blob: from Natasha's code, modified so that there are 4000 minority voters
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
 

# uniformly distributed minorities
for vertex in graph.nodes():
    graph.node[vertex]["MINPOP"] = 40
    graph.node[vertex]["MAJPOP"] = 60
dual_graph_list.append(graph) 

print(len(dual_graph_list)) #check everything ahs been added

#pickle dual graph list
# Save initial spatial distribution of voters
file_Name = "10x10_100pernode_40percmin"
# open the file for writing
fileObject = open(file_Name,'wb') 
pickle.dump(dual_graph_list,fileObject)
fileObject.close()

#check that pickle worked successfully: unpickle it
fileObject = open(file_Name,'rb') # Open for reading
dgl = pickle.load(fileObject)

print(len(dgl))





