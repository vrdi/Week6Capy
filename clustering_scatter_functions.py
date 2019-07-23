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
    """Runs a Recom chain on a given graph with a given minority/majority population distribution and returns lists of cut edges, minority seat wins, and tuples of minority percentage by district for each step of the chain.
    
    Parameters:
    graph (networkx.Graph) -- a NetworkX graph object representing the dual graph on which to run the chain. The nodes should have attributes for majority population, minority population, and total population.
    min_pop_col (string) -- the key/column name for the minority population attribute in graph
    maj_pop_col (string) -- the key/column name for the majority population attribute in graph
    tot_pop_col (string) -- the key/column name for the total population attribute in graph
    num_districts (int) -- number of districts to run for the chain
    initial_plan (gerrychain.Partition) -- an initial partition for the chain (which does not need updaters since the function will supply its own updaters)
    num_steps (int) -- the number of steps for which to run the chain
    pop_tol (float) -- tolerance for deviation from perfectly balanced populations between districts (default 0.05)
    min_win_thresh -- percent of minority population needed in a district for it to be considered a minority win. If the minority percentage in a district is greater than or equal to min_win_thresh then that district is considered a minority win. (default 0.5)
    
    Returns:
    [cut_edges_list,min_seats_list,min_percents_list] (list)
        WHERE
        cut_edges_list (list) -- list where cut_edges_list[i] is the number of cut edges in the partition at step i of the Markov chain
        min_seats_list -- list where min_seats_list[i] is the number of districts won by the minority (according to min_win_thresh) at step i of the chain
        min_percents_list -- list where min_percents_list[i] is a tuple, with min_percents_list[i][j] being the minority percentage in district j at step i of the chain
    """
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
    """Returns a dictionary of various clustering scores for given graph with a given minority/majority population distribution
    
    Parameters:
    graph (networkx.Graph) -- a NetworkX graph object representing the dual graph on which to run the chain. The nodes should have attributes for majority population, minority population, and total population.
    min_pop_col (string) -- the key/column name for the minority population attribute in graph
    maj_pop_col (string) -- the key/column name for the majority population attribute in graph
    tot_pop_col (string) -- the key/column name for the total population attribute in graph
    
    Returns:
    output (dict) -- dictionary where the keys are the names of clustering scores as strings (currently the options are "edge" and "half_edge") and the value for a key is the evaluation of the specified clustering score on the graph and its population distribution
    """
    adj_mat = nx.to_numpy_array(graph, weight=None)
    min_vect = np.array(graph.node(data=min_pop_col))[:,1]  #pull out the minority populations and convert them to a vector
    maj_vect = np.array(graph.node(data=maj_pop_col))[:,1]  #pull out the majority populations and convert them to a vector
    edge_score = capy.edge(min_vect, maj_vect, adj_mat)
    half_edge_score = capy.half_edge(min_vect, maj_vect, adj_mat)
    
    output = {}
    output["edge"] = edge_score
    output["half_edge"] = half_edge_score
    
    return output