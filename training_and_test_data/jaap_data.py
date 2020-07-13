from os import listdir
from os.path import isfile, join
import pandas as pd

def read_and_prep_jaap_data(relevant_vars, min_obs_per_municipality = 15):
    csv_files = [f for f in listdir("Data/Jaap/") if isfile(join("Data/Jaap/", f)) and f.endswith('.csv') ]

def tmp_read_jaap_data():
    return pd.read_csv("Data/Jaap/housing_data.csv", encoding='ISO-8859-1', sep=";")