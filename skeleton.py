# to plot clustering edge scores and % expected minority seats
# Muniba & Kristen, 7/23/19

# Import and Setup Block
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

dual_graph_list = []
points = []
edge_score_list = []
expected_min_seats_list = []

num_states = 1

# iterate over states to be plotted
for state in range (num_states):

    # generate graph and dataframe from json
    graph_path = "./IA_counties/IA_counties.shp"
    graph = Graph.from_file(graph_path, reproject = False)
    graph.to_json("ia_json.json")
    jgraph = Graph.from_json("ia_json.json")
    df = gpd.read_file(graph_path)

    # set parameters for ensemble
    min_pop_col = 'PRES00R'
    maj_pop_col = 'PRES00D'
    tot_pop_col = 'TOTVOT00'
    num_districts = 4
    initial_plan = Partition(jgraph, "CD")
    num_steps = 100
    
    while True:
        
        # run ensemble and store outputs
        output = run_ensemble_on_distro(jgraph, min_pop_col, maj_pop_col, tot_pop_col, num_districts, initial_plan, num_steps) 
        cut_edges_list = output[0]
        min_seats_list = output[1]
        min_percents_list = output[2] 

        # verify appropriate mixing time
        half_of_cut_edges = []
        for i in range (int(len(cut_edges_list)/2)):
            half_of_cut_edges.append(cut_edges_list[i])
            half_of_cut_edges.append(cut_edges_list[i])

        plt.hist(cut_edges_list, bins=25, alpha=0.5, label='all steps in chain')
        plt.hist(half_of_cut_edges, bins=25, alpha=0.5, label='first 1/2 of steps')
        plt.xlabel("# of cut edges")
        plt.ylabel("frequency")
        plt.legend(loc='upper right')
        plt.show()

        is_mixed = input('Is the appropriate mixing time met? (Y/N) ')

        if(is_mixed == 'Y'):
            break

        elif(is_mixed == 'N'):
            num_steps = int(input('Reset number of steps for chain: '))

    dual_graph_list.append(jgraph)
    
    # plot number of minority seats in each step of chain
    plt.figure()
    plt.hist(min_seats_list, bins=20)
    plt.xlabel("# of minority seats")
    plt.ylabel("frequency")
    plt.show()
    plt.savefig("./capy_hist.png")
    plt.close()

    # calculate clustering scores
    scores = calculate_clustering_scores(jgraph, min_pop_col, maj_pop_col, tot_pop_col)
    print(scores["edge"])
    edge_score = scores["edge"]
    half_edge_score = scores["half_edge"]

    # calculate % expected minority seats
    # (assumes 1 seat per district)
    total_min_seats = 0.0
    for i in range (len(min_seats_list)):
        total_min_seats += min_seats_list[i]
    expected_min_seats = (total_min_seats / len(min_seats_list)) / num_districts

    # save edge scores and % expected minority seats
    edge_score_list.append(edge_score)
    expected_min_seats_list.append(expected_min_seats)

#  plot edge score and expected minority seats
plt.figure()
plt.scatter(edge_score_list, expected_min_seats_list)
plt.xlabel("clustering edge score")
plt.ylabel("percent expected minority seats")
plt.show()
plt.savefig("./capy_scatter.png")
plt.close()