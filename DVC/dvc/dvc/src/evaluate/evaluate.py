import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import confusion_matrix, f1_score
from typing import Text,Tuple

import logging
import os

logging_str="[% (asctime)s: %(levelname)s: %(module)s] %(module)s"
log_dir="logs"
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"running_logs.log",level=logging.INFO,format=logging_str))


def evaluate(df: pd.DataFrame, target_column: Text, clf: BaseEstimator) -> Dict:
    """Evaluate classifier on a dataset

    Args:
        df {pandas.DataFrame}: dataset
        target_column {Text}: target column name
        clf {sklearn.base.BaseEstimator}: classifier (trained model)

    Returns:
        Dict: Dict of reported metrics
            'f1' - F1 score
            'cm' - Comnfusion Matrix
            'actual' - true values for test data
            'predicted' - predicted values for test data
    """
    logging.info("Let start the evaluation:")
    # Get X and Y
    y_test = df.loc[:, target_column].values.astype('int32')
    X_test = df.drop(target_column, axis=1).values.astype('float32')

    prediction = clf.predict(X_test)
    f1 = f1_score(y_true=y_test, y_pred=prediction, average='macro')
    cm = confusion_matrix(prediction, y_test)

    return{
        'f1': f1,
        'cm': cm,
        'actual': y_test,
        'predicted': prediction
        }
