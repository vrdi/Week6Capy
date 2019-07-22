# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:21:28 2019

@author: Brian
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import scipy

import random

import matplotlib.pyplot as plt
from functools import partial
import networkx as nx

from gerrychain import MarkovChain
from gerrychain.constraints import (
    Validator,
    single_flip_contiguous,
    within_percent_of_ideal_population,
)
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain.updaters import Election, Tally, cut_edges
from gerrychain.partition import Partition
from gerrychain.proposals import recom
from gerrychain.metrics import mean_median, efficiency_gap

import csv
import os
from functools import partial
import json

import matplotlib.pyplot as plt

from gerrychain import (
    Election,
    Graph,
    MarkovChain,
    Partition,
    accept,
    constraints,
    updaters,
)

from gerrychain.tree import recursive_tree_part

import capy




def run_ensemble_on_distro(graph, min_pop_col, maj_pop_col, tot_pop_col, num_districts, initial_plan, num_steps, pop_tol = 0.05, min_win_thresh = 0.5):
    my_updaters = {
        "population": Tally(tot_pop_col, alias = "population"),
        "cut_edges": cut_edges,
        "maj-min": Election("maj-min", {"maj": maj_pop_col, "min": min_pop_col}),
    }
    
    initial_partition = Partition(graph = initial_plan.graph, assignment = initial_plan.assignment, updaters = my_updaters)
    
    # ADD CONSTRAINTS
    popbound = within_percent_of_ideal_population(initial_partition, 0.1)
    
    # ########Setup Proposal
    ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)
    
    tree_proposal = partial(
        recom,
        pop_col=tot_pop_col,
        pop_target=ideal_population,
        epsilon=pop_tol,
        node_repeats=1,
    )
    
    # ######BUILD MARKOV CHAINS
    
    recom_chain = MarkovChain(
        tree_proposal,
        Validator([popbound]),
        accept=always_accept,
        initial_state=initial_partition,
        total_steps=num_steps,
    )
    
    cut_edges_list = []
    min_seats_list = []
    min_percents_list = []
    
    for part in recom_chain:
        cut_edges_list.append(len(part["cut_edges"]))
        min_percents_list.append(part["maj-min"].percents("min"))
        min_seats = (np.array(part["maj-min"].percents("min")) >= min_win_thresh).sum()
        min_seats_list.append(min_seats)
    
    return [cut_edges_list,min_seats_list,min_percents_list]
    


def calculate_clustering_scores(graph, min_pop_col, maj_pop_col, tot_pop_col):
    adj_mat = nx.to_numpy_array(graph)
    min_vect = np.array(graph.node(data=min_pop_col))[:,1]  #pull out the minority populations and convert them to a vector
    maj_vect = np.array(graph.node(data=maj_pop_col))[:,1]  #pull out the majority populations and convert them to a vector
    edge_score = capy.edge(min_vect, maj_vect, adj_mat)
    half_edge_score = capy.half_edge(min_vect, maj_vect, adj_mat)
    
    output = {}
    output["edge"] = edge_score
    output["half_edge"] = half_edge_score
    
    return output


graph = nx.grid_graph([10,10])


for vertex in graph.nodes():
    graph.node[vertex]["population"] = 1
    graph.node[vertex]["pink"] = 0
    graph.node[vertex]["purple"] = 1

    
for i in rnd.choice(range(len(graph.nodes)),size=40,replace=False):
    vertex = list(graph.nodes)[i]
    graph.node[vertex]["purple"] = 0
    graph.node[vertex]["pink"] = 1
    
cdict = {1: "pink", 0: "purple"}

plt.figure()
nx.draw(
    graph,
    pos={x: x for x in graph.nodes()},
    node_color=[cdict[graph.node[x]["pink"]] for x in graph.nodes()],
    node_size=ns,
    node_shape="s",
)
plt.show()