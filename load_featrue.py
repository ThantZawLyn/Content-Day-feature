
import pandas as pd                        
import pyidaungsu as pds
import pickle

def load_feature( data_file,feature_file, vectorizer_file):
    # Load data
    data = pd.read_csv(data_file)
    data = pd.DataFrame(data)
    # Load feature
    feature = pickle.load(open(feature_file, "rb"))
    # Load vectorizer
    vectorizer = pickle.load(open(vectorizer_file, "rb"))
    return data, feature, vectorizer

