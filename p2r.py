#!/bin/env python

# USAGE: ./p2r.py -d datasets/positions.csv -r rsu.csv -k5 > datasets/dataset5.csv

import math
from collections import deque
import pandas as pd
from geopy.distance import geodesic
import argparse

# Each RSU is identified by its coordinates (x, y) and its radius (reach radius?)
# 'id':'RSU1', 'x':1, 'y':2, 'radius':0.1 (radius in KMs)
# These RSUs are put in a CSV file of which lines are of this format:
# id1, x1, y1, radius1
# id2, x2, y2, radius2
# ...
# A line that starts with a # in this file will be ignored.


# For each profile record its last k rsus
LAST_K_RSUS = {}
MAX_HISTORY = 4

class POS:
    """ A class representing positions (coordinates) """
    def __init__(self, id, x, y):
        self.id, self.x, self.y = id, x, y

    def __str__(self):
        return f"POS({self.x}, {self.y})"

    def distance(self, other):
        """ Distance from another POS"""
        return geodesic((self.x, self.y), (other.x, other.y)).km


class RSU:
    """ A class representing RSUs """
    def __init__(self, id, x, y, radius):
        self.id, self.radius, self.center = id, radius, POS(id, x, y)

    def __str__(self):
        return f'RSU(ID: {self.id} at {self.center} Radius:{self.radius}'

    def contains(self, point):
        """ Is pos inside rsu's perimeter? """
        distance = self.center.distance(point)
        return (distance <= self.radius)


def convert_positions_to_ids(positions, rsus, verbose = False):
    """ 
    Take a list of positions and RSUs and print a list of RSU IDs, in O(n²).
    If none of the RSU contains the pos, print N/A.
    The RSUs are printed (fold-printed) each MAX_HISTORY on a line.
    """
    for pos in positions:
        if not pos.id in LAST_K_RSUS:
            LAST_K_RSUS[pos.id] = deque(maxlen=MAX_HISTORY)
        if verbose:
            print('>> Processing {}'.format(pos))
        pos_rsu = 'N/A'
        for rsu in rsus:
            if verbose:
                d = rsu.center.distance(pos)
                print(f':: {rsu.id} is {d} kms away from {pos}')
            if rsu.contains(pos):
                pos_rsu = rsu.id
                break
        LAST_K_RSUS[pos.id].append(pos_rsu)
        if len(LAST_K_RSUS[pos.id]) == MAX_HISTORY:
            print(int(pos.id), ', ', ', '.join(LAST_K_RSUS[pos.id]), sep='')


def generate_lists(dataset_file_name, rsu_file_name):
    """Generate two lists: one of POSs, and another of RSUs. """
    df = pd.read_csv(dataset_file_name, delimiter=',', comment='#', header=None)
    positions = (POS(*t) for t in df.values)
    rf = pd.read_csv(rsu_file_name, delimiter=',', comment='#', header=None)
    rsus = [RSU(*t) for t in rf.values]
    return {'positions': positions, 'rsus':rsus}


def do_it():
    """ 
    Convert a list of coordinates (x, y) to a list of RSUs ID in which
    they're contained.
    """
    global MAX_HISTORY

    ap = argparse.ArgumentParser(description="Coordinates to RSU IDs")
    ap.add_argument('-d', action="store", dest="dataset_file")
    ap.add_argument('-r', action="store", dest="rsu_file")
    ap.add_argument('-k', type=int, action="store", dest="history_size")
    ap.add_argument('-v', action="store_true", dest="verbose")

    args = ap.parse_args()
    data = generate_lists(args.dataset_file, args.rsu_file)
    MAX_HISTORY = args.history_size

    convert_positions_to_ids(data['positions'], data['rsus'], args.verbose)

if __name__ == "__main__":
    do_it()
