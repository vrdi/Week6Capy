# to plot clustering edge scores and % expected minority seats
# Muniba & Kristen, 7/23/19

# Import and Setup Block
import networkx as nx
from networkx.readwrite import json_graph
from gerrychain import Graph
import matplotlib.pyplot as plt

import geopandas as gpd
from random import randint, random
from random import choice, shuffle
import numpy as np
import scipy
from gerrychain import (
    Graph,
    Partition
)
from gerrychain.tree import recursive_tree_part

import itertools
from itertools import combinations
from shapely.geometry import (
    Polygon,
    Point
) 

from geopandas import GeoSeries
import pandas as pd
import os
import json
from clustering_scatter_functions import (
    run_ensemble_on_distro,
    calculate_clustering_scores
)

import csv
import pickle

fileObject = open("10x10_100pernode_40percmin", 'rb')

dual_graph_list = pickle.load(fileObject)

points = []
edge_score_list = []
expected_min_seats_list = []

num_states = 1
# iterate over states to be plotted
for dg in dual_graph_list:

    """
    # generate graph and dataframe from json
    graph_path = "./IA_counties/IA_counties.shp"
    graph = Graph.from_file(graph_path, reproject = False)
    graph.to_json("ia_json.json")
    jgraph = Graph.from_json("ia_json.json")
    df = gpd.read_file(graph_path)
    """
    cdict = {20: "pink", 100: "purple", 0: "hotpink", 70: "blue", 25: "green", 40: "black"}
    # Draws dual graph coloring nodes by their vote preference (minority/majority)
    plt.figure()
    nx.draw(
        dg,
        pos={x: x for x in dg.nodes()},
        node_color=[cdict[dg.node[x]["MINPOP"]] for x in dg.nodes()],
        node_size=50,
        node_shape="s",
    )
    plt.show()

    # set parameters for ensemble
    num_districts = 10
    num_steps = 1000
    tot_pop_col = 'TOTPOP'
    min_pop_col = 'MINPOP'
    maj_pop_col = 'MAJPOP'
    cddict = recursive_tree_part(dg, range(num_districts), 1000, tot_pop_col, 0.001, 1)
    initial_plan = Partition(dg, cddict)
    print("Set parameters.")
    
    while True:
        
        # run ensemble and store outputs
        output = run_ensemble_on_distro(dg, min_pop_col, maj_pop_col, tot_pop_col, num_districts, initial_plan, num_steps) 
        cut_edges_list = output[0]
        min_seats_list = output[1]
        min_percents_list = output[2] 

        print("Ran ensemble.")

        # verify appropriate mixing time
        half_of_cut_edges = []
        for i in range (int(len(cut_edges_list)/2)):
            half_of_cut_edges.append(cut_edges_list[i])
            half_of_cut_edges.append(cut_edges_list[i])

        minimum = min(cut_edges_list)
        maximum = max(cut_edges_list)

        bins = np.linspace(minimum, maximum, maximum - minimum + 1)
        plt.hist(cut_edges_list, bins, alpha=0.5, label='all steps in chain')
        plt.hist(half_of_cut_edges, bins, alpha=0.5, label='first 1/2 of steps')
        plt.xlabel("# of cut edges")
        plt.ylabel("frequency")
        plt.legend(loc='upper right')
        plt.show()

        print('You are running', num_steps, 'steps.')
        is_mixed = input('Is the appropriate mixing time met? (Y/N) ')

        if(is_mixed == 'Y'):
            print("Mixing time verified.")
            break

        elif(is_mixed == 'N'):
            num_steps = int(input('Reset number of steps for chain: '))
    
    # plot number of minority seats in each step of chain
    plt.figure()
    plt.hist(min_seats_list, bins=20)
    plt.xlabel("# of minority seats")
    plt.ylabel("frequency")
    plt.show()
    plt.savefig("./capy_hist.png")
    plt.close()

    # calculate clustering scores
    scores = calculate_clustering_scores(dg, min_pop_col, maj_pop_col, tot_pop_col)
    edge_score = scores["edge"]
    half_edge_score = scores["half_edge"]
    print('Edge score:', edge_score)
    print('Half edge score:', half_edge_score)

    # calculate % expected minority seats
    # (assumes 1 seat per district)
    total_min_seats = 0.0
    for i in range (len(min_seats_list)):
        total_min_seats += min_seats_list[i]
    expected_min_seats = (total_min_seats / len(min_seats_list)) / num_districts
    print("Percent expected minority seats:", expected_min_seats)

    # save edge scores and % expected minority seats
    edge_score_list.append(edge_score)
    expected_min_seats_list.append(expected_min_seats)
    print("Edge scores and min seats saved.")
    print()

#  plot edge score and expected minority seats
plt.figure()
plt.scatter(edge_score_list, expected_min_seats_list)
plt.xlabel("clustering edge score")
plt.ylabel("percent expected minority seats")
plt.show()
plt.savefig("./capy_scatter.png")
plt.close()