import pickle
from crapy import crapy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

fileObject1 = open("10x10_PA_nodepop1_20percmin_expweight", 'rb')
fileObject2 = open("10x10_PA_nodepop1_20percmin_multweight", 'rb')
fileObject3 = open("10x10_PA_nodepop1_20percmin_unbaised_100graphs", 'rb')
dual_graph_1= pickle.load(fileObject1)
dual_graph_2 = pickle.load(fileObject2)
dual_graph_3 = pickle.load(fileObject3)
fileObject1.close()
fileObject2.close()
fileObject3.close()

cdict = {1: "pink", 0: "purple"}
crapy_scores_min = []
crapy_scores_maj = []
for i in range(0, len(dual_graph_3)):
    graph = dual_graph_3[i]
    plt.figure()
    #nx.draw(graph, pos = {x:x for x in graph.nodes}, node_color=[cdict[graph.node[x]["pink"]] for x in graph.nodes()])
    plt.show()
    values = crapy(graph, "purple", "pink")
    crapy_scores_min.append(values[0])
    crapy_scores_maj.append(values[1])
#print(np.average(crapy_scores_min))
#print(np.average(crapy_scores_maj))
plt.hist(crapy_scores_min)
    

