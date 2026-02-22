from model import model_SL_predict, get_model_SL
import pandas as pd
import numpy as np
def run_app():
    fname = input("input model(.parquet) filepath without '.parquet'  : ")
    fname+=".parquet"
    model = pd.read_parquet(fname)
    for c in set(model.columns) :       
        model[c] = model[c].apply(lambda x : tuple(x.tolist()) if isinstance(x,np.ndarray) else x)
        model[c] = model[c].apply(lambda x : tuple(x) if isinstance(x,list) else x)
    tps = model["TYPE"].unique()
    for i,t in enumerate(tps):
        print(f"{i} - [{t}]")
    choice_t : int = None
    while(choice_t == None):
        choice_t = input("Pick one : ")
        choice_t = int(choice_t)
        if choice_t < 0 or choice_t >= len(tps):
            print("wrong pick again.")
            choice_t = None
    picked_t = tps[choice_t]
    print("you pick choice : ",picked_t)
    locs = model["LOC"].loc[model["TYPE"] == tps[choice_t]].unique()
    choice_l : int = None
    for i,t in enumerate(locs):
        print(f"{i} - [{t}]")
    while(choice_l == None):
        choice_l = input("Pick one : ")
        choice_l = int(choice_l)
        if choice_l <= 0 or choice_l >= len(locs):
            print("wrong pick again.")
            choice_l = None
    picked_l = locs[choice_l]
    print("you pick choice : ",picked_l)
    loop = True
    while(loop):
        print("Format : [area-terrain-dispo-neuf-chambre-piece-floor-floors]")
        input_point = input("Input : ")
        try :
            dataPt = tuple(map(float, input_point.split("-")))
            #dataPt = tuple(map(float, input_point.split("-")))
            cat = tuple([str(picked_t),str(picked_l)])
            data = {
                "CAT" : cat,
                "POINT" : dataPt
            }
            predicted_price = model_SL_predict(model = model, data=data )
            if predicted_price :
                predicted_price = next(iter(predicted_price))
            print(f"Predicted price : {int(predicted_price)} EUR")
            loop = False
        except Exception :
            print(f"[ERROR] received {input_point}")
run_app()
