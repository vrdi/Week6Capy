# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:21:28 2019

@author: Brian
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import scipy
import math

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



# =================== Functions to run ensembles on population distributions and calculate clustering scores  ===================

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
    pop_tol (float, default 0.05) -- tolerance for deviation from perfectly balanced populations between districts
    min_win_thresh (float, default 0.5) -- percent of minority population needed in a district for it to be considered a minority win. If the minority percentage in a district is greater than or equal to min_win_thresh then that district is considered a minority win.
    
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


# =================== Functions to randomly populate graphs  ===================


def randomly_populate_grid_fraction_one_per_node(m, n, min_pop_col, maj_pop_col, minority_fraction, tot_pop_col = None):
    """Populates an m-by-n grid with members of a minority group and a majority group by randomly assigning members to nodes, placing exactly one person/population unit on each node. Returns a grid graph with majority and minority populations as node attributes. This function takes a fraction of the total population that will be the minority population.
    
    Parameters:
    m (int) -- the number of rows in the grid
    n (int) -- the number of columns in the grid
    min_pop_col (string) -- the name for the minority population attribute to be given to the nodes
    maj_pop_col (string) -- the name for the majority population attribute to be given to the nodes
    minority_fraction (float) -- the proportion of the total population to be assigned that belongs to the minority group. The exact number of minority group members assigned will be math.floor(minority_fraction*m*n); the remainder will be majority group members.
    tot_pop_col (string or None, default None) -- if a string, the name for the total population attribute to be given to the nodes, which will be the sum of the majority and minority populations. If None, then a total population attribute will not be added (the default behavior). Note that other functions in this file may request a total population column.
    
    Returns:
    output_graph (networkx.Graph) -- an m-by-n grid graph with a single randomly assigned majority or minority group member on each node, with node populations accessible as attributes with the keys min_pop_col and maj_pop_col
    """
    return randomly_populate_grid_fraction(m, n, min_pop_col, maj_pop_col, minority_fraction, m*n, tot_pop_col)

def randomly_populate_grid_fraction(m, n, min_pop_col, maj_pop_col, minority_fraction, total_pop, tot_pop_col = None, no_empty_nodes = True):
    """Populates an m-by-n grid with members of a minority group and a majority group by randomly assigning members to nodes. Returns a grid graph with majority and minority populations as node attributes. This version of the function takes a total population to assign to nodes in the graph and a fraction of the total that will be the minority population.
    
    Parameters:
    m (int) -- the number of rows in the grid
    n (int) -- the number of columns in the grid
    min_pop_col (string) -- the name for the minority population attribute to be given to the nodes
    maj_pop_col (string) -- the name for the majority population attribute to be given to the nodes
    minority_fraction (float) -- the proportion of the total population to be assigned that belongs to the minority group. The exact number of minority group members assigned will be math.floor(minority_fraction*total_pop); the remainder will be majority group members.
    total_pop (int) -- the total number of majority and minority group members to assign to nodes in the graph.
    tot_pop_col (string or None, default None) -- if a string, the name for the total population attribute to be given to the nodes, which will be the sum of the majority and minority populations. If None, then a total population attribute will not be added (the default behavior). Note that other functions in this file may request a total population column.
    no_empty_nodes (bool, default True) -- if True, all of the nodes will be given a nonzero population (the default behavior). If True, num_minority + num_majority must be at least the number of nodes in the graph (i.e. m*n), otherwise an exception will be thrown. If False, empty nodes will be allowed.
    
    Returns:
    output_graph (networkx.Graph) -- an m-by-n grid graph with randomly assigned majority and minority populations on each node, accessible as attributes with the keys min_pop_col and maj_pop_col
    """
    graph = nx.grid_graph([m,n])
    return randomly_populate_graph_fraction(graph, min_pop_col, maj_pop_col, minority_fraction, total_pop, tot_pop_col, no_empty_nodes)

def randomly_populate_grid(m, n, min_pop_col, maj_pop_col, num_minority, num_majority, tot_pop_col = None, no_empty_nodes = True):
    """Populates an m-by-n grid with members of a minority group and a majority group by randomly assigning members to nodes. Returns a grid graph with majority and minority populations as node attributes. This version of the function takes total numbers of majority and minority group members to assign to nodes in the graph.
    
    Parameters:
    m (int) -- the number of rows in the grid
    n (int) -- the number of columns in the grid
    min_pop_col (string) -- the name for the minority population attribute to be given to the nodes
    maj_pop_col (string) -- the name for the majority population attribute to be given to the nodes
    num_minority (int) -- the number of minority members to put into the graph
    num_majority (int) -- the number of majority members to put into the graph
    tot_pop_col (string or None, default None) -- if a string, the name for the total population attribute to be given to the nodes, which will be the sum of the majority and minority populations. If None, then a total population attribute will not be added (the default behavior). Note that other functions in this file may request a total population column.
    no_empty_nodes (bool, default True) -- if True, all of the nodes will be given a nonzero population (the default behavior). If True, num_minority + num_majority must be at least the number of nodes in the graph (i.e. m*n), otherwise an exception will be thrown. If False, empty nodes will be allowed.
    
    Returns:
    output_graph (networkx.Graph) -- an m-by-n grid graph with randomly assigned majority and minority populations on each node, accessible as attributes with the keys min_pop_col and maj_pop_col
    """
    graph = nx.grid_graph([m,n])
    return randomly_populate_graph(graph, min_pop_col, maj_pop_col, num_minority, num_majority, tot_pop_col, no_empty_nodes)

def randomly_populate_graph_fraction(graph, min_pop_col, maj_pop_col, minority_fraction, total_pop, tot_pop_col = None, no_empty_nodes = True):
    """Populates a graph with members of a minority group and a majority group by randomly assigning members to nodes. Returns a copy of the input graph with majority and minority populations added as node attributes. This version of the function takes a total population to assign to nodes in the graph and a fraction of the total that will be the minority population.
    The copy is a shallow copy, meaning that the original graph's nodes' attributes will not be changed, but if any of those attributes are themselves containers/references, then modifying the values in those containers/references in the output graph will modify the values in the original graph.
    
    Parameters:
    graph (networkx.Graph) -- a NetworkX graph object to populate with majority and minority populations
    min_pop_col (string) -- the name for the minority population attribute to be given to the nodes. If this name is the same as the key for any of the existing attributes, the old data will be overwritten.
    maj_pop_col (string) -- the name for the majority population attribute to be given to the nodes. If this name is the same as the key for any of the existing attributes, the old data will be overwritten.
    minority_fraction (float) -- the proportion of the total population to be assigned that belongs to the minority group. The exact number of minority group members assigned will be math.floor(minority_fraction*total_pop); the remainder will be majority group members.
    total_pop (int) -- the total number of majority and minority group members to assign to nodes in the graph.
    tot_pop_col (string or None, default None) -- if a string, the name for the total population attribute to be given to the nodes, which will be the sum of the majority and minority populations. If this name is the same as the key for any of the existing attributes, the old data will be overwritten. If None, then a total population attribute will not be added (the default behavior). Note that other functions in this file may request a total population column.
    no_empty_nodes (bool, default True) -- if True, all of the nodes will be given a nonzero population (the default behavior). If True, num_minority + num_majority must be at least the number of nodes in the graph, otherwise an exception will be thrown. If False, empty nodes will be allowed.
    
    Returns:
    output_graph (networkx.Graph) -- a shallow copy of the input graph with randomly assigned majority and minority populations on each node, accessible as attributes with the keys min_pop_col and maj_pop_col
    """
    num_minority = math.floor(minority_fraction*total_pop)
    num_majority = math.ceil((1-minority_fraction)*total_pop)
    return randomly_populate_graph(graph, min_pop_col, maj_pop_col, num_minority, num_majority, tot_pop_col, no_empty_nodes)
    
def randomly_populate_graph(graph, min_pop_col, maj_pop_col, num_minority, num_majority, tot_pop_col = None, no_empty_nodes = True):
    """Populates a graph with members of a minority group and a majority group by randomly assigning members to nodes. Returns a copy of the input graph with majority and minority populations added as node attributes. This version of the function takes total numbers of majority and minority group members to assign to nodes in the graph.
    The copy is a shallow copy, meaning that the original graph's nodes' attributes will not be changed, but if any of those attributes are themselves containers/references, then modifying the values in those containers/references in the output graph will modify the values in the original graph.
    
    Parameters:
    graph (networkx.Graph) -- a NetworkX graph object to populate with majority and minority populations
    min_pop_col (string) -- the name for the minority population attribute to be given to the nodes. If this name is the same as the key for any of the existing attributes, the old data will be overwritten.
    maj_pop_col (string) -- the name for the majority population attribute to be given to the nodes. If this name is the same as the key for any of the existing attributes, the old data will be overwritten.
    num_minority (int) -- the number of minority members to put into the graph
    num_majority (int) -- the number of majority members to put into the graph
    tot_pop_col (string or None, default None) -- if a string, the name for the total population attribute to be given to the nodes, which will be the sum of the majority and minority populations. If this name is the same as the key for any of the existing attributes, the old data will be overwritten. If None, then a total population attribute will not be added (the default behavior). Note that other functions in this file may request a total population column.
    no_empty_nodes (bool, default True) -- if True, all of the nodes will be given a nonzero population (the default behavior). If True, num_minority + num_majority must be at least the number of nodes in the graph, otherwise an exception will be thrown. If False, empty nodes will be allowed.
    
    Returns:
    output_graph (networkx.Graph) -- a shallow copy of the input graph with randomly assigned majority and minority populations on each node, accessible as attributes with the keys min_pop_col and maj_pop_col
    """
    total_pop = num_minority+num_majority
    num_nodes = len(graph)
    if no_empty_nodes and total_pop<num_nodes:
        raise Exception("Combined majority and minority population too small to fill entire graph and no_empty_nodes was set to True")
    
    output_graph = graph.copy() #only a shallow copy, which should be sufficient for our purposes
    pop_assignment_list = random.sample(num_majority*[0]+num_minority*[1],total_pop)
    node_list = list(output_graph.nodes)
    
    for node in output_graph.nodes:
        output_graph.nodes[node][min_pop_col] = 0
        output_graph.nodes[node][maj_pop_col] = 0
        
    if no_empty_nodes:
        shuffled_node_list = random.sample(node_list,num_nodes)
        for node in shuffled_node_list:
            if pop_assignment_list.pop() == 0:
                output_graph.nodes[node][maj_pop_col] += 1
            else:
                output_graph.nodes[node][min_pop_col] += 1
    
    for person in pop_assignment_list:
        node = random.choice(node_list)
        if person == 0:
            output_graph.nodes[node][maj_pop_col] += 1
        else:
            output_graph.nodes[node][min_pop_col] += 1
    
    if tot_pop_col is not None:
        for node in output_graph.nodes:
            output_graph.nodes[node][tot_pop_col] = output_graph.nodes[node][min_pop_col] + output_graph.nodes[node][maj_pop_col]
    
    return output_graph