# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 10:38:18 2019

@author: canno
"""
import matplotlib.pyplot as plt
import networkx as nx
from clustering_scatter_functions import randomly_populate_grid_fraction
import pickle

#color dictionary for plotting
cdict = {}


#start dual graph list
dual_graph_list = []

#Generate a random voter config on 10x10 grid 
for i in range(100):
    graph = randomly_populate_grid_fraction(10,10, "MINPOP", "MAJPOP", 0.4, 10000, "TOTPOP", )
    dual_graph_list.append(graph)
    
    '''
    for n in graph.nodes():
        if graph.node[n]["MINPOP"] > 80:
            cdict.update({graph.node[n]["MINPOP"]: "red"})
        elif graph.node[n]["MINPOP"] > 60:
            cdict.update({graph.node[n]["MINPOP"]: "orange"})
        elif graph.node[n]["MINPOP"] > 40:
            cdict.update({graph.node[n]["MINPOP"]: "yellow"})
        elif graph.node[n]["MINPOP"] > 20:
            cdict.update({graph.node[n]["MINPOP"]: "green"})
        elif graph.node[n]["MINPOP"] > 0:
            cdict.update({graph.node[n]["MINPOP"]: "blue"})
        else:
            cdict.update({graph.node[n]["MINPOP"]: "black"})
    plt.figure()
    ns = 50
    nx.draw(
        graph,
        pos={x: x for x in graph.nodes()},
        node_color=[cdict[graph.node[x]["MINPOP"]] for x in graph.nodes()],
        node_size=ns,
        node_shape="s",
    )
    plt.show()'''
    
print(len(dual_graph_list))
file_Name = '10x10_random_10000totalpop_40percmin'
fileObject = open(file_Name, 'wb')
pickle.dump(dual_graph_list, fileObject)
fileObject.close()