#If you want to get detailed explanation, please check the notebook (k-algorithms.ipynb)
import numpy as np
import matplotlib.pyplot as plt
import math
from numbers import Real
def get_difference(pair):
    if not isinstance(pair, (list, tuple)) or len(pair) != 2:
        raise ValueError("Pass a list/tuple with exactly two numbers.")
    a, b = pair
    if not isinstance(a, Real) or not isinstance(b, Real):
        raise TypeError("Both values must be real numbers.")
    return abs(a - b)
def calculate_distance(ptA,ptB):
    if not isinstance(ptA,(list,tuple)) or not isinstance(ptB,(list,tuple)):
        raise ValueError("Expect input with points in tuple or list")
    if len(ptA) == len(ptB): 
        zipped = [ptA,ptB]
        squared_sum = 0.0
        for coords in zip(*zipped):
            squared_sum += math.pow(get_difference(coords),2)
        return math.sqrt(squared_sum)
    else :
        raise ValueError("Size missmatched.")
def get_shortestDistancePairs(classified_pts : list = None ,unclassified_pts : list = None ,classify_classified : bool = False):
    pairs = {}
    for uc_pt in unclassified_pts :
        shortest_distance = 0.0
        nearest_neighbour = None
        for i,c_pt in enumerate(classified_pts) :
            distance = calculate_distance(uc_pt,c_pt)
            if distance < shortest_distance  or shortest_distance == 0 :
                shortest_distance = distance
                nearest_neighbour = c_pt
            elif math.isclose(distance,shortest_distance) :
                min_lexi_pt = min([c_pt,classified_pts[i-1]])
                nearest_neighbour = min_lexi_pt
        pairs[uc_pt] = nearest_neighbour
    if classify_classified : 
        for c_pt in classified_pts :
            pairs[c_pt] = c_pt       
    return pairs
def get_centroid(points : list = None):
    if not points :
        return None
    else :
        generalized_num_dims = len(points[0])
        if any(len(point) != generalized_num_dims for point in points):
            raise ValueError("points inconsitent dimensions")
    return tuple(sum(coords)/len(points) for coords in zip(*points))
def get_centroids(k : int = 3 ,points : list = None, centroids : list = None, 
                  float_precision : int = None,max_recursion_depth : int = 999,recursion_iter : int = 0):
    if not points or not k:
        return None
    elif recursion_iter == max_recursion_depth :
        if centroids :
            return centroids
        else :
            return None
    else :
        if centroids == None :
            centroids = []
            while(len(centroids)<k):
                rand = np.random.randint(0,len(points))
                if points[rand] not in centroids :
                    centroids.append(points[rand])
        pairs = get_shortestDistancePairs(centroids,points)
        new_centroids = []
        for centroid in centroids :
            cluster = []
            for key,value in pairs.items():
                if value == centroid :
                    cluster.append(key)
            if len(cluster) > 0 :
                new_centroids.append(get_centroid(cluster))
            else :
                new_centroids.append(centroid)
        if float_precision :
            centroids = [tuple(round(v, float_precision) for v in c) for c in centroids]
            new_centroids= [tuple(round(v, float_precision) for v in c) for c in new_centroids]
        if (sorted(centroids) == sorted(new_centroids)) or (
            get_inertia(centroids = centroids,points=points) < get_inertia(centroids = new_centroids,points=points)): 
            return centroids
        else :
            return get_centroids(k=k,points=points,centroids=new_centroids,
                                 float_precision=float_precision,max_recursion_depth=max_recursion_depth,
                                recursion_iter=recursion_iter+1)
def get_inertia(centroids : list = None, points : list = None):
    if not points or not centroids:
        raise ValueError("No centroids or points given")
    inertia = 0.0
    try :
        for point in points :
            distances = [math.pow(calculate_distance(centroid,point),2) for centroid in centroids]
            inertia += min(distances)
        return inertia
    except Exception as e :
        raise ValueError("Make sure centroids,points have numerical coordination values")
def run_monteCarlo(k : int = None ,points : list = None,
                  float_precision : int = None,
                  nb_runs : int = 10,
                  max_recursion_depth : int = 999,centroids : tuple = None):
    list_centroids = []
    list_centroids2inertia = []
    for run in range(nb_runs):
        centroids = sorted(get_centroids(k = k,points = points,float_precision = float_precision,
                                         max_recursion_depth = max_recursion_depth,centroids=centroids))
        inertia = get_inertia(centroids = centroids,points=points)
        if inertia :
            if len(list_centroids) == 0:
                list_centroids2inertia.append([centroids,inertia])
                list_centroids.append(centroids)
            elif centroids not in list_centroids :
                list_centroids2inertia.append([centroids,inertia])
                list_centroids.append(centroids)
    return list_centroids2inertia
def get_lowest_inertia_centroids(list_centroids2inertia : list = None):
    if list_centroids2inertia :
        lowest_inertia_centroids = None
        lowest_inertia = None
        for i,pair in enumerate(list_centroids2inertia) :
            centroids,inertia = pair
            if lowest_inertia == None or lowest_inertia > inertia:
                lowest_inertia_centroids = centroids
                lowest_inertia = inertia
        return lowest_inertia_centroids
    else :
        return None