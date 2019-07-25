import networkx as nx
import itertools
import numpy as np

def crapy_pop(gr, minority_attribute, majority_attribute, r = 1/2, weight_limit = None):
    node_scores_min = []
    node_scores_maj = []
    diam = nx.diameter(gr)
    numerator = 1 - r**(diam + 1)
    frac = numerator/(1-r) - 1
    a = 1/frac  
    tot_min_pop = 0
    tot_maj_pop = 0
    for node in gr.nodes:
        min_val = gr.node[node][minority_attribute]
        tot_min_pop += min_val
        maj_val = gr.node[node][majority_attribute]
        tot_maj_pop += maj_val
        dictionary_nodes = dict(nx.bfs_successors(gr,node))
        dictionary_levels = {}
        current_list = [dictionary_nodes[node]]
        for i in range(1, diam + 1):
            if (not current_list):
                break
            if weight_limit != None and i > weight_limit:
                break
            dictionary_levels[i] = list(itertools.chain.from_iterable(current_list))
            current_list = [dictionary_nodes[x] for x in dictionary_levels[i] if x in dictionary_nodes.keys()]
        min_sum_weight = 0
        maj_sum_weight = 0
        for key in dictionary_levels.keys():
            values = dictionary_levels[key]
            num_min = 0
            num_maj = 0
            num_tot = 0
            for test_node in values:
                num_min += gr.node[test_node][minority_attribute]
                num_maj += gr.node[test_node][majority_attribute]
                num_tot += gr.node[test_node][minority_attribute] + gr.node[test_node][majority_attribute]
            min_ratio = num_min/num_tot
            min_sum_weight += min_val*a*r**key*min_ratio
            maj_ratio = num_maj/num_tot
            maj_sum_weight += maj_val*a*r**key*maj_ratio
        node_scores_min.append(min_sum_weight)
        node_scores_maj.append(maj_sum_weight)
    minority_score = np.sum(node_scores_min)/tot_min_pop
    majority_score = np.sum(node_scores_maj)/tot_maj_pop
    #print("Minority Average: {0}".format(minority_score))
    #print("Majority Average: {0}".format(majority_score))
    return minority_score, majority_score