import pickle
from crapy import crapy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import clustering_scatter_functions
import random



num_graphs_per_min_frac = 100
min_percents = np.linspace(0.05,0.5,10)
r_values = np.linspace(0.05,0.95,19)
dual_graphs_unbiased_variable_percent = {}
print("about to generate dual graphs")
for key in min_percents:
    dual_graphs_unbiased_variable_percent[key] = [
        clustering_scatter_functions.randomly_populate_grid_fraction_one_per_node(10,10, "minority", "majority", key, "population") \
        for i in range(num_graphs_per_min_frac)]
print("generated dual graphs")

crapy_scores = []

for min_frac in min_percents:
    graphs = dual_graphs_unbiased_variable_percent[min_frac]
    scores = [[crapy(graph,"minority","majority", r) for r in r_values] for graph in graphs]
    crapy_scores.append(scores)
    print("completed stage min_frac = {:.2f}".format(min_frac))

crapy_scores_array = np.array(crapy_scores) #indexing looks like [min_frac, graph, r, {0:majority score, 1:minority score}]

writer = open("10x10_unbiased_crapy_scores_array_with_variable_r_and_minority_fraction.pickle","wb")
pickle.dump(crapy_scores_array,writer)
writer.close()


for i in range(20):
    idx0 = random.randrange(len(min_percents))
    idx2 = random.randrange(len(r_values))
    
    
    plt.figure()
    plt.subplot(1,2,1)
    plt.hist(crapy_scores_array[idx0, :, idx2, 0])
    plt.title("Minority Crapy scores,\n {0}% minority, r-value {1:.2f}".format(int(100*min_percents[idx0]),r_values[idx2]))
    plt.subplot(1,2,2)
    plt.hist(crapy_scores_array[idx0, :, idx2, 1])
    plt.title("Majority Crapy scores,\n {0}% minority, r-value {1:.2f}".format(int(100*min_percents[idx0]),r_values[idx2]))
    plt.show()



# Plotting

crapy_min_vect = crapy_scores_array[:,:,:,0].flatten()
crapy_maj_vect = crapy_scores_array[:,:,:,1].flatten()
indices = np.unravel_index(range(len(crapy_min_vect)),crapy_scores_array[:,:,:,0].shape)
min_percent_vect = min_percents[indices[0]]
r_value_vect = r_values[indices[2]]



plt.figure()
plt.scatter(min_percent_vect, crapy_min_vect, c=r_value_vect, cmap="magma")
plt.xlabel("Minority fraction")
plt.ylabel("Minority clustering score")
plt.title("Minority clustering score vs. minority fraction,\ncolored by r value, 10x10 grid with one person per node")
plt.savefig("crapy_10x10_pop_1_variable_r_minority_clustering_vs_fraction", dpi=300)
plt.show()

plt.figure()
plt.scatter(min_percent_vect, crapy_maj_vect, c=r_value_vect, cmap="magma")
plt.xlabel("Minority fraction")
plt.ylabel("Majority clustering score")
plt.title("Majority clustering score vs. minority fraction,\ncolored by r value, 10x10 grid with one person per node")
plt.savefig("crapy_10x10_pop_1variable_r_majority_clustering_vs_fraction", dpi=300)
plt.show()

plt.figure()
plt.scatter(crapy_min_vect, crapy_maj_vect, c=r_value_vect, cmap="magma")
plt.xlabel("Minority clustering score")
plt.ylabel("Majority clustering score")
plt.title("Majority clustering score vs. minority clustering score,\ncolored by r value, 10x10 grid with one person per node")
plt.savefig("crapy_10x10_pop_1variable_r_majority_clustering_vs_minority_clustering", dpi=300)
plt.show()