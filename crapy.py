import networkx as nx
import itertools
import numpy as np

def crapy_one(gr, minority_attribute, majority_attribute, r = 1/2, weight_limit = None):
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

def crapy_zero_neighbors(gr, minority_attribute, majority_attribute, r = 1/2, zero_neighbor_ratio = 0, weight_limit = None):
    node_scores_min = []
    node_scores_maj = []
    diam = nx.diameter(gr)
    numerator = 1 - r**(diam + 1)
    frac = numerator/(1-r) - 1
    a = 1/frac  
    w1 = a*r
    k = 1/(1+ zero_neighbor_ratio*w1)
    w0 = zero_neighbor_ratio*k*w1
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
        if (w0 != 0):
            if (min_val==0):
                 node_scores_min.append(0)
            else:
                if (min_val==1 and maj_val==0):
                    node_scores_min.append(0)
                else:
                    min_ratio = w0*(min_val - 1)/(min_val + maj_val - 1)*min_val
                    node_scores_min.append(min_ratio)
            if (maj_val == 0):
                node_scores_maj.append(0)
            else:
                if (maj_val == 1 and min_val==0):
                    node_scores_maj.append(0)
                else:
                    maj_ratio = w0*(maj_val - 1)/(min_val + maj_val - 1)*maj_val
                    node_scores_maj.append(maj_ratio)
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
            maj_ratio = num_maj/num_tot
            min_sum_weight += min_val*k*a*r**key*min_ratio
            maj_sum_weight += maj_val*k*a*r**key*maj_ratio
        node_scores_min.append(min_sum_weight)
        node_scores_maj.append(maj_sum_weight)
    minority_score = np.sum(node_scores_min)/tot_min_pop
    majority_score = np.sum(node_scores_maj)/tot_maj_pop
    #print("Minority Average: {0}".format(minority_score))
    #print("Majority Average: {0}".format(majority_score))
    return minority_score, majority_score