import hashlib
import json
import config
import os
import pandas as pd

def get_dict_uuid(d):
    # Sort the dictionary by keys to ensure consistent order
    sorted_dict = json.dumps(d, sort_keys=True).encode('utf-8')
    # Generate a SHA-256 hash of the sorted dictionary
    hash_object = hashlib.sha256(sorted_dict)
    # Return the first 8 characters of the hash as the UUID
    return hash_object.hexdigest()[:8]

def is_cached(data_uid):
    return os.path.exists(os.path.join(config.cached_folder, data_uid + '.csv'))

def dump_data(dataframe, data_uid):
    """
    Dump data to csv file
    :Parameters:
        dataframe : pandas dataframe
        data_uid: the uid of the data
    """
    cached_folder = config.cached_folder
    cached_file = os.path.join(cached_folder, data_uid + '.csv')
    dtype_file = os.path.join(cached_folder, data_uid + '.dtype')
    dataframe.to_csv(cached_file)
    # Save the dtypes of the dataframe
    dtype_dict = dataframe.dtypes.apply(str).to_dict()
    with open(dtype_file, 'w') as f:
        json.dump(dtype_dict, f)
def load_data(data_uid,parse_dates):
    cached_folder = config.cached_folder
    cached_file = os.path.join(cached_folder, data_uid + '.csv')
    dtype_file = os.path.join(cached_folder, data_uid + '.dtype')
    # Load the dtypes of the dataframe
    with open(dtype_file, 'r') as f:
        dtypes = json.load(f)
    # Load the dataframe
    dataframe = pd.read_csv(cached_file, dtype=dtypes, index_col=0,parse_dates=parse_dates)
    return dataframe

prompt_token = 0
completion_token = 0
messages = []