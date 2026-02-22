python --version : python 3.13

libs (imports) :
-numpy
-pandas
-matplotlib
-scikit-learn
-nltk
-fastparquet
-re
-math
-unicodedata
-numbers
-tkinter

files :
3 notebooks :
	+ "k-algorithms.ipynb" -> k-means algo.
	+ "vectorize_dataset_seloger.ipynb" -> clean,vectorize seloger.com dataset + fill missing some values with linear regression models.
	+ "k-means-applied.ipynb" -> apply k-means algo to predict resdential properties prices from scraped seloger.com vectorized dataset.

4 executable files :
	+ 3 files provide functions from 3 notebooks mentioned (model.py,k_means.py,sl_vectorization.py)
	+ 1 file "app.py" execute a terminal interface allow user to get predicted price of a property.
		+ [video display how to use this app.py]
		+ #1) to execute, you first need to activate virtual env, in bash terminal type : "source .venv/Scripts/activate"
		+ #2) make sure all imports are satisfied.
		+ #3) tu run app file, in bash terminal type : "python app.py"
		+ #4) you will be asked to enter model path, models are in folder "models", i only provide 1 model (model_sl_10.parquet), so in terminal, type "models/model_sl_10" 
		(* 10 in "model_sl_10" represent number of randomized k-means run on vectorized dataset to obtain accurate centroids positions)
		+ #5) the terminal will the show you list of available types of residential property to predict (i limit the number due to small size dataset, roughly 1000 useable properties)
		+ #6) after picking a type (in this current model, we only have 1 option), the program will display list of locations (in codepostals) to select.
		+ #7) after selecting a location, you will be asked to enter numerical values in a format [area-terrain-dispo-neuf-chambre-piece-floor-floors], please enter exactly in this format, example : "21.5-0-0-1-2-3-5-6" -> area = 21.5 , surface (terrain) = 0, O not immediately available (dispo mtn), 1 is new (neuf), 2 chambre (bedrooms), 3 pieces, location floor =5, building has 6 floors.

3 dataset files :
	+ 2 (v_seloger_ds.csv) vectorized datasets (cleaned, vectorized, fillna)
	+ 1 (data_sample_1584.csv)raw dataset scraped from seloger.com (contains approximately 1600 properties) - this one was used to train model.
	+ 1 (data_sample_4743.csv)raw dataset scraped from seloger.com (contains approcimately 4800 properties , previous 1500 weren't included) - this one we did not test.

1 model file : 
	+ .parquet to preserve some datatypes when saving from pandas.DataFrame