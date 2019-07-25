# to plot clustering edge scores and % expected minority seats
# Muniba & Kristen, 7/23/19

# Import and Setup Block
import networkx as nx
from networkx.readwrite import json_graph
from gerrychain import Graph
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

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
    calculate_clustering_scores,
    randomly_populate_grid_fraction_one_per_node,
    randomly_populate_grid_fraction,
    randomly_populate_grid,
    randomly_populate_graph_fraction,
    randomly_populate_graph
)

import csv
import pickle

fileObject1 = open("10x10_PA_nodepop1_20percmin_expweight", 'rb')
fileObject2 = open("10x10_PA_nodepop1_20percmin_multweight", 'rb')
dual_graph_list = pickle.load(fileObject1) + pickle.load(fileObject2)
print("Dual graph list generated.")

edge_score_list = []
half_edge_score_list = []
expected_min_seats_list = []

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

    """
    # Draws dual graph coloring nodes by their vote preference (minority/majority)
    cdict = {20: "pink", 100: "purple", 0: "hotpink", 70: "blue", 25: "green", 40: "black"}
    plt.figure()
    nx.draw(
        dg
        pos={x: x for x in dg.nodes()},
        node_color=[cdict[dg.node[x]["MINPOP"]] for x in dg.nodes()],
        node_size=50,
        node_shape="s",
    )
    plt.show()
    """

    # set parameters for ensemble
    num_districts = 10
    num_steps = 10000
    tot_pop_col = 'population'
    min_pop_col = 'purple'
    maj_pop_col = 'pink'
    cddict = recursive_tree_part(dg, range(num_districts), 10, tot_pop_col, 0.001, 1)
    initial_plan = Partition(dg, cddict)
    print("Parameters set.")
    
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
        is_mixed = input('Is the appropriate mixing time met? (y/n) ')
        if(is_mixed == 'y'):
            print("Mixing time verified.")
            break

        elif(is_mixed == 'n'):
            num_steps = int(input('Reset number of steps for chain: '))
    
    """
    # plot number of minority seats in each step of chain
    plt.figure()
    plt.hist(min_seats_list, bins=20)
    plt.xlabel("# of minority seats")
    plt.ylabel("frequency")
    plt.show()
    plt.close()
    """

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
    half_edge_score_list.append(half_edge_score)
    expected_min_seats_list.append(expected_min_seats)
    print("Edge scores and min seats saved.")
    print()

#  plot edge score and expected minority seats
slope1, intercept1, r_value1, p_value1, std_err1 = scipy.stats.linregress(edge_score_list, expected_min_seats_list)

min1 = min(edge_score_list)
max1 = max(edge_score_list)

x1 = np.linspace(min1,max1,100)
y1 = slope1 * x1 + intercept1

print("edge score R^2:", r_value1**2)

plt.figure()
plt.scatter(edge_score_list, expected_min_seats_list)
plt.plot(x1, y1, ':r')
plt.xlabel("clustering edge score")
plt.ylabel("percent expected minority seats")
plt.savefig("./edge_score_plot.png")
plt.close()

#  plot half edge score and expected minority seats
slope2, intercept2, r_value2, p_value2, std_err2 = scipy.stats.linregress(half_edge_score_list, expected_min_seats_list)

min2 = min(half_edge_score_list)
max2 = max(half_edge_score_list)

x2 = np.linspace(min2,max2,100)
y2 = slope2 * x2 + intercept2

print("Half edge score R^2:", r_value2**2)

plt.figure()
plt.scatter(half_edge_score_list, expected_min_seats_list)
plt.plot(x2, y2, ':r')
plt.xlabel("clustering half edge score")
plt.ylabel("percent expected minority seats")
plt.savefig("./half_edge_score_plot.png")
plt.close()

statistics = pd.DataFrame({
    "EDGE_SCORES": edge_score_list,
    "HALF_EDGE_SCORES": half_edge_score_list,
    "EXPECTED_MIN_SEATS": expected_min_seats_list
})

statistics.to_csv("clustering_statistics.csv", index=False)