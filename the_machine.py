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
import cv2

def hist_intersect(hist1, hist2, bins):
    bins = np.diff(bins)
    intersect = 0
    whole = 0
    for i in range (len(bins)):
        intersect += min(bins[i]*hist1[i], bins[i]*hist2[i])
        whole += max(bins[i]*hist1[i], bins[i]*hist2[i])
    return intersect/whole

fileObject1 = open("10x10_PA_nodepop100_20percmin_expweight_10dgs", 'rb')
fileObject2 = open("10x10_PA_nodepop100_20percmin_multweight_10dgs", 'rb')
dual_graph_list = pickle.load(fileObject2)
print("Dual graph list generated.")

intersect_list = []
num_steps_list = []
edge_score_list = []
half_edge_score_list = []
morans_I_min_list = []
morans_I_maj_list =[]
crapy_min_list = []
crapy_maj_list = []
expected_min_seats_list = []

outdir = "./test_outputs/"
try:
    # Create target Directory
    os.mkdir(outdir)
    print("Directory " , outdir ,  " created ") 
except FileExistsError:
    print("Directory " , outdir ,  " already exists")
print()

default = input("Do you want to go with default values for r, zero neighbor, and weight limit? (y/n): ")
if default == 'y':
    r = 0.5
    zero_neighbors = 0
    weight_limit = None
elif default == 'n':
    r = float(input("Set decay parameter for weights (default 1/2): "))
    zero_neighbors = float(input("Set zero neighbor ratio (default 0): "))
    weight_limit = input("Set integer weight limit (radius of neighbors to check for each node), or none (default none): ")
    if weight_limit != "none":
        weight_limit = int(weight_limit)
    else:
        weight_limit = None

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
    graph_num = str(dual_graph_list.index(dg))
    print("Processing graph " + graph_num + ".")

    # set initial parameters for ensemble
    num_districts = 10
    num_steps = 5000
    tot_pop_col = 'population'
    min_pop_col = 'minority'
    maj_pop_col = 'majority'
    cddict = {x: int(x[0])  for x in dg.nodes()}
    initial_plan = Partition(dg, cddict)
    print("Parameters set.")
    
    while True:
        
        print('Running ensemble at', num_steps, 'steps.')

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

        hist1, bins1, patches1 = plt.hist(cut_edges_list, bins, alpha=0.5, label='all steps in chain')
        hist2, bins2, patches2 = plt.hist(half_of_cut_edges, bins, alpha=0.5, label='first 1/2 of steps')

        intersect = hist_intersect(hist1, hist2, bins)
        print('Intersection:', intersect)

        if(intersect >= 0.95):
            print("Mixing time verified.")

            plt.xlabel("# of cut edges")
            plt.ylabel("frequency")
            plt.legend(loc='upper right')
            plt.savefig(outdir + "mix_hist_" + graph_num + ".png")
            plt.close()

            intersect_list.append(intersect)
            num_steps_list.append(num_steps)

            print("Intersection score, number of steps, and cut-edge histogram saved.")

            break

        else:
            plt.close()
            num_steps = num_steps * 2
            print("Mixing time insufficient, rerunning at", num_steps, "steps.")
 
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
    scores = calculate_clustering_scores(dg, min_pop_col, maj_pop_col, tot_pop_col, r, zero_neighbors, weight_limit)
    edge_score = scores["edge"]
    half_edge_score = scores["half_edge"]
    morans_I_min_score = scores["morans_I_min"]
    morans_I_maj_score = scores["morans_I_maj"]
    crapy_min_score = scores["crapy_min"]
    crapy_maj_score = scores["crapy_maj"]
    print('Edge score:', edge_score)
    print('Half edge score:', half_edge_score)
    print('Morans I minority:', morans_I_min_score)
    print('Morans I majority:', morans_I_maj_score)
    print('Crapy minority:', crapy_min_score)
    print('Crapy majority:', crapy_maj_score)

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
    morans_I_min_list.append(morans_I_min_score)
    morans_I_maj_list.append(morans_I_maj_score)
    crapy_min_list.append(crapy_min_score)
    crapy_maj_list.append(crapy_maj_score)
    print("Clustering scores and min seats saved.")
    print()

#  plot edge score and expected minority seats
slope1, intercept1, r_value1, p_value1, std_err1 = scipy.stats.linregress(edge_score_list, expected_min_seats_list)

min1 = min(edge_score_list)
max1 = max(edge_score_list)

x1 = np.linspace(min1,max1,100)
y1 = slope1 * x1 + intercept1

print("edge score R^2:", r_value1**2)
label1 = 'R^2=' + str(r_value1**2)

plt.figure()
plt.scatter(edge_score_list, expected_min_seats_list)
plt.plot(x1, y1, ':r', label=label1)
plt.xlabel("clustering edge score")
plt.ylabel("percent expected minority seats")
plt.legend(loc='upper left')
plt.savefig(outdir + "edge_score_plot.png")
plt.close()

#  plot half edge score and expected minority seats
slope2, intercept2, r_value2, p_value2, std_err2 = scipy.stats.linregress(half_edge_score_list, expected_min_seats_list)

min2 = min(half_edge_score_list)
max2 = max(half_edge_score_list)

x2 = np.linspace(min2,max2,100)
y2 = slope2 * x2 + intercept2

print("Half edge score R^2:", r_value2**2)
label2 = 'R^2=' + str(r_value2**2)

plt.figure()
plt.scatter(half_edge_score_list, expected_min_seats_list)
plt.plot(x2, y2, ':r', label=label2)
plt.xlabel("clustering half edge score") 
plt.ylabel("percent expected minority seats")
plt.legend(loc='upper left')
plt.savefig(outdir + "half_edge_score_plot.png")
plt.close()

# plot morans I minority and expected minority seats
slope3, intercept3, r_value3, p_value3, std_err3 = scipy.stats.linregress(morans_I_min_list, expected_min_seats_list)

min3 = min(morans_I_min_list)
max3 = max(morans_I_min_list)

x3 = np.linspace(min3,max3,100)
y3 = slope3 * x3 + intercept3

print("Morans I minority score R^2:", r_value3**2)
label3 = 'R^2=' + str(r_value3**2)

plt.figure()
plt.scatter(morans_I_min_list, expected_min_seats_list)
plt.plot(x3, y3, ':r', label=label3)
plt.xlabel("morans I minority score")
plt.ylabel("percent expected minority seats")
plt.legend(loc='upper left')
plt.savefig(outdir + "morans_I_min_score_plot.png")
plt.close()

# plot crapy minority and expected minority seats

slope4, intercept4, r_value4, p_value4, std_err4 = scipy.stats.linregress(crapy_min_list, expected_min_seats_list)

min4 = min(crapy_min_list)
max4 = max(crapy_min_list)

x4 = np.linspace(min4,max4,100)
y4 = slope4 * x4 + intercept4

print("Crapy minority score R^2:", r_value4**2)
label4 = 'R^2=' + str(r_value4**2)

plt.figure()
plt.scatter(crapy_min_list, expected_min_seats_list)
plt.plot(x4, y4, ':r', label=label4)
plt.xlabel("crapy minority score")
plt.ylabel("percent expected minority seats")
plt.legend(loc='upper left')
plt.savefig(outdir + "crapy_min_score_plot.png")
plt.close()

statistics = pd.DataFrame({
    "INTERSECTIONS": intersect_list,
    "NUM_STEPS": num_steps_list,
    "EDGE_SCORES": edge_score_list,
    "HALF_EDGE_SCORES": half_edge_score_list,
    "EXPECTED_MIN_SEATS": expected_min_seats_list,
    "MORANS_I_MIN": morans_I_min_list,
    "MORANS_I_MAJ": morans_I_maj_list,
    "CRAPY_MIN_SCORES": crapy_min_list,
    "CRAPY_MAJ_SCORES": crapy_maj_list
})

statistics.to_csv(outdir + "clustering_statistics.csv", index=False)