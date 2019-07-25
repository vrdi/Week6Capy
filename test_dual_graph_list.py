# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 11:36:07 2019

@author: canno
"""

import pickle
import matplotlib.pyplot as plt
import networkx as nx

fileObject1 = open("10x10_PA_nodepop1_20percmin_expweight", 'rb')
fileObject2 = open("10x10_PA_nodepop1_20percmin_multweight", 'rb')
dual_graph_list = pickle.load(fileObject1) + pickle.load(fileObject2)
print("Dual graph list generated.")

cdict = {1: "pink",0: "purple"}

for graph in dual_graph_list:
    plt.figure()
    ns = 50
    nx.draw(
        graph,
        pos={x: x for x in graph.nodes()},
        node_color=[cdict[graph.node[x]["pink"]] for x in graph.nodes()],
        node_size=ns,
        node_shape="s",
    )
    plt.show()
    