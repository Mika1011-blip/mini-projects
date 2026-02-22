"""
Read k-means-applied.ipynb to get more details
"""
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
from k_means import get_shortestDistancePairs, run_monteCarlo, get_lowest_inertia_centroids


# #### Analyze/predict real-world data
def get_model_SL(csv_file:str = None,k : int = 16, runs : int = 100,save_model : bool = False, model_title : str = "model_sl"):
    if not csv_file :
        raise ValueError("Require dataset filepath")
    #vopen file
    try :
        df = pd.read_csv(csv_file)
    except Exception :
        raise ValueError("Error converting file.csv to dataframe")
    
    try :
        #get useful cols
        cols = ['PRICE','TYPE','LOC','AREA','TERRAIN','DISPONIBL MAINTEN','NEUF',
            'CHAMBRE','PIECE','FLOOR','FLOORS']
        cat_cols = ['TYPE','LOC']
        num_cols = ['AREA','TERRAIN','DISPONIBL MAINTEN','NEUF',
            'CHAMBRE','PIECE','FLOOR','FLOORS']
        out = df.loc[:,cols]
        
        """
        How to decide number of ks ?
        maybe based on number of features,
        we have 2 categorical features, 8 numerical features,
        for each numerical feature, we divide each into 2 types, 1 good, 1 bad. (can try 1 good, 1 medium, 1 bad later)
        -> 8*2 = 16, k = 16.
        """
        for c in cat_cols :
            out[c] = out[c].astype(str)
        #get categorical data
        def get_value_list(df,mask,col):
            return df.loc[mask,col].tolist()
        typs = set(out["TYPE"].tolist())
        locs = set(out["LOC"].tolist())
        for loc in locs :
            for typ in typs :
                mask = (out["TYPE"].eq(typ)) & (out["LOC"].eq(loc))
                df_by_cat = out.loc[mask]
                if len(df_by_cat) >= k*2 :
                    out.loc[mask,"POINT"] = out.loc[mask,num_cols].agg(tuple,axis=1)
                    pts = out.loc[mask,"POINT"].tolist()
                    centroids = get_lowest_inertia_centroids(run_monteCarlo(k=k,nb_runs=runs,points=pts))
                    clusters = get_shortestDistancePairs(classified_pts=centroids,unclassified_pts=pts)
                    out.loc[mask,"CENTROID"] = out.loc[mask,"POINT"].apply(lambda x : clusters[x] if x else pd.NA)
                    out.loc[mask,"CENTROID W"] = len(df_by_cat)
                else : 
                    continue
        out["CENTROID"] = out["CENTROID"].apply(
            lambda v: tuple(v) if isinstance(v, (list, np.ndarray)) else v
        )
        centroids = set(out["CENTROID"].dropna().tolist())
        for c in centroids :
            prices = out.loc[out["CENTROID"].isin([c]), "PRICE"].tolist()
            avg = sum(prices) / len(prices)
            out.loc[out["CENTROID"].isin([c]), "PRED"] = avg
        out["CAT"] = out.loc[:,["TYPE","LOC"]].agg(tuple,axis=1)
        if save_model :
            #out.to_csv(f"{model_title}_{runs}.csv",index=False)
            save = out.copy(deep=True)
            save = save.dropna()
            for c in ("POINT", "CENTROID", "CAT"):
                if c in save.columns:
                    save[c] = save[c].astype("object").apply(lambda x : list(x) if x else pd.NA)
            save = save.dropna()
            save.to_parquet(f"{model_title}_{runs}.parquet",index=False)
    except Exception :
        raise ValueError("Incompatible dataset")
    return out.dropna()
    #return centroids,weight
def model_SL_predict(parquet_model : str = None, model : pd.core.frame.DataFrame = None ,data : dict = None ):
    """
    data : dict -> shape = {str:tuple,str:tuple} keys() = {"CAT","POINT"}
    out -> float
    """
    #safety check
    if model is None and not parquet_model :
        raise ValueError("No model provided")
    if not data :
        return None
    if parquet_model :
        try :
            model = pd.read_parquet(parquet_model)
            for c in set(model.columns) :       
                model[c] = model[c].apply(lambda x : tuple(x.tolist()) if isinstance(x,np.ndarray) else x)
                model[c] = model[c].apply(lambda x : tuple(x) if isinstance(x,list) else x)
        except Exception :
            raise ValueError("Error converting model_sl.csv to dataframe")
    model.dropna(inplace = True)
    #get model capability to predict (have predictable input category)
    if sorted(set(data.keys())) != sorted({"CAT","POINT"}):
        raise ValueError("Invalid data keys")
    predictable_cat = set(model["CAT"].tolist())
    if (data["CAT"] not in predictable_cat) or (len(data["CAT"]) != 2):
        raise ValueError("Incompatible category")
    if len(data["POINT"]) != 8 :
        raise ValueError("Incompatible point")
    mask = model["CAT"].apply(lambda x : sorted(x) == sorted(data["CAT"]) if x else False)
    centroids = set(model.loc[mask,"CENTROID"].tolist())
    pair = get_shortestDistancePairs(classified_pts=centroids,unclassified_pts=[data["POINT"]])
    key = tuple(map(float, data["POINT"]))
    nearest = pair[key]
    pred = set(model.loc[model["CENTROID"].isin([nearest]), "PRED"].tolist())
    return pred
            