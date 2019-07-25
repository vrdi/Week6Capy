import networkx as nx
import itertools
import numpy as np
def crapy(gr, minority_attribute, majority_attribute, r = 1/2, weight_limit = None):
    node_scores_min = []
    node_scores_maj = []
    diam = nx.diameter(gr)
    numerator = 1 - r**(diam + 1)
    frac = numerator/(1-r) - 1
    a = 1/frac    
    for node in gr.nodes:
        node_info = gr.node[node][minority_attribute]
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
        sum_weight = 0
        for key in dictionary_levels.keys():
            values = dictionary_levels[key]
            num_same = 0
            for test_node in values:
                if gr.node[test_node][minority_attribute] == node_info:
                    num_same += 1
            ratio = num_same / len(values)
            sum_weight += a*r**key*ratio
            if node_info == 1:
                node_scores_min.append(sum_weight)
            else:
                node_scores_maj.append(sum_weight)
    minority_score = np.average(node_scores_min)
    majority_score = np.average(node_scores_maj)
    #print("Minority Average: {0}".format(minority_score))
    #print("Majority Average: {0}".format(majority_score))
    return minority_score, majority_score
    
