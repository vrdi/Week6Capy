import pickle
from crapy import crapy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import clustering_scatter_functions

fileObject1 = open("10x10_PA_nodepop1_20percmin_expweight", 'rb')
fileObject2 = open("10x10_PA_nodepop1_20percmin_multweight", 'rb')
fileObject3 = open("10x10_PA_nodepop1_20percmin_unbaised_100graphs", 'rb')
dual_graph_1= pickle.load(fileObject1)
dual_graph_2 = pickle.load(fileObject2)
dual_graph_3 = pickle.load(fileObject3)
fileObject1.close()
fileObject2.close()
fileObject3.close()

#dual_graphs_40_percent_unbiased = [
#        clustering_scatter_functions.randomly_populate_grid_fraction_one_per_node(10,10, "purple", "pink", 0.4, "population") \
#        for i in range(100)]

num_graphs_per_min_frac = 100
dual_graphs_unbiased_variable_percent = {}
for key in np.linspace(0.05,0.5,10):
    dual_graphs_unbiased_variable_percent[key] = [
        clustering_scatter_functions.randomly_populate_grid_fraction_one_per_node(10,10, "purple", "pink", key, "population") \
        for i in range(num_graphs_per_min_frac)]


#cdict = {1: "pink", 0: "purple"}
#crapy_scores_min = []
#crapy_scores_maj = []
#for i in range(0, len(dual_graphs_40_percent_unbiased)):
#    graph = dual_graphs_40_percent_unbiased[i]
#    #plt.figure()
#    #nx.draw(graph, pos = {x:x for x in graph.nodes}, node_color=[cdict[graph.node[x]["pink"]] for x in graph.nodes()])
#    #plt.show()
#    values = crapy(graph, "purple", "pink")
#    crapy_scores_min.append(values[0])
#    crapy_scores_maj.append(values[1])
#print("Average minority score:", np.average(crapy_scores_min))
#print("Average majority score:", np.average(crapy_scores_maj))
#plt.hist(crapy_scores_min)
    

min_percent_list = []
crapy_min_list = []
crapy_maj_list = []

for key in dual_graphs_unbiased_variable_percent:
    min_percent_list.extend(num_graphs_per_min_frac*[key])
    graphs = dual_graphs_unbiased_variable_percent[key]
    scores = np.array([crapy(graph,"purple","pink") for graph in graphs])
    scores_min = scores[:,0]
    scores_maj = scores[:,1]
    crapy_min_list.extend(scores_min)
    crapy_maj_list.extend(scores_maj)
    
    plt.figure()
    plt.hist(scores_min)
    plt.title("Minority Crapy scores, {}% minority".format(int(100*key)))
    plt.show()
    
    plt.figure()
    plt.hist(scores_maj)
    plt.title("Majority Crapy scores, {}% minority".format(int(100*key)))
    plt.show()

plt.figure()
plt.scatter(min_percent_list, crapy_min_list)
plt.xlabel("Minority fraction")
plt.ylabel("Minority clustering score")
plt.title("Minority clustering score vs. minority fraction")
plt.savefig("crapy_r_50_percent_minority_clustering_vs_fraction")
plt.show()

plt.figure()
plt.scatter(min_percent_list, crapy_maj_list)
plt.xlabel("Minority fraction")
plt.ylabel("Majority clustering score")
plt.title("Majority clustering score vs. minority fraction")
plt.savefig("crapy_r_50_percent_majority_clustering_vs_fraction")
plt.show()

plt.figure()
plt.scatter(crapy_min_list, crapy_maj_list)
plt.xlabel("Minority clustering score")
plt.ylabel("Majority clustering score")
plt.title("Majority clustering score vs. Minority clustering score")
plt.savefig("crapy_r_50_percent_majority_clustering_vs_minority_clustering")
plt.show()