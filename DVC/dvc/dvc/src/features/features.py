import pandas as pd
import logging
import os

logging_str="[% (asctime)s: %(levelname)s: %(module)s] %(module)s"
log_dir="logs"
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"running_logs.log",level=logging.INFO,format=logging_str))



def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract features.

    Args:
        df {pandas.DataFrame}: dataset

    Returns:
        pandas.DataFrame: updated dataset with new features
    """
    logging.info("Let extract the features:")
    dataset = df.copy()
    dataset['sepal_length_to_sepal_width'] = dataset['sepal_length'] / dataset['sepal_width']
    dataset['petal_length_to_petal_width'] = dataset['petal_length'] / dataset['petal_width']


    dataset = dataset[[
        'sepal_length', 'sepal_width', 'petal_length', 'petal_width',
        'sepal_length_to_sepal_width', 'petal_length_to_petal_width',

        'target'
    ]]

    return dataset
