import pandas as pd
from sklearn.datasets import load_iris
from typing import List
import logging
import os



logging_str="[% (asctime)s: %(levelname)s: %(module)s] %(module)s"
log_dir="logs"
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"running_logs.log",level=logging.INFO,format=logging_str))


def get_dataset() -> pd.DataFrame:
    """Read dataset into pandas.DataFrame

    Returns:
        pandas.DataFrame
    """
    logging.info("Let start the process:")
    data = load_iris(as_frame=True)

    dataset = data.frame
    dataset.columns = [colname.strip(' (cm)').replace(' ', '_') for colname in dataset.columns.tolist()]

    return dataset


def get_target_names() -> List:
    return load_iris(as_frame=True).target_names.tolist()
