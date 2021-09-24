import pandas as pd
from pkg_resources.py2_warn import msg
from sklearn.linear_model import LogisticRegression
from typing import Text,Dict

from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

import logging
import os


logging_str="[% (asctime)s: %(levelname)s: %(module)s] %(module)s"
log_dir="logs"
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"running_logs.log",level=logging.INFO,format=logging_str))

class UnsupportedClassifier(Exception):
    def __init__(self,estimator_name):
        self.msg=f'Unsupported estimator{estimator_name}'
        super().__init__(self,msg)


def get_supported_estimator()-> Dict:
    """
    Returns:
        Dict: supported classifiers
    """
    logging.info("Let Create the supported estimator:")
    return{
        'logreg':LogisticRegression,
        'svm':SVC,
        'knn':KNeighborsClassifier
    }

def train(df:pd.DataFrame,target_column:Text,
          estimator_name:Text,param_grid:Dict,cv:int):
    """ Train model.'''

    Args:
        df{pandas.DataFrame}:dataset
        target_column{Text}:target column name
        estimator_name{Text}:estimator_name
        param_grid{Dict}:grid parameters
        CV{int}:cross_validation value

    Returns:
        trained model
    """
    logging.info("Let start the process:")
    estimators = get_supported_estimator()

    if estimator_name not in estimators.keys():
        raise UnsupportedClassifier(estimator_name)

    estimator = estimators[estimator_name]()
    f1_scorer= make_scorer(f1_score,average='weighted')
    clf = GridSearchCV(estimator=estimator,
                       param_grid=param_grid,
                       cv=cv,
                       verbose=1,
                       scoring=f1_scorer)

    #Get X and Y


    y_train=df.loc[: ,target_column].values.astype("int32")
    X_train=df.drop(target_column,axis=1).values.astype('float32')

    clf.train(X_train,y_train)

    return clf





def train_lr(df: pd.DataFrame, target_column: Text) -> LogisticRegression:
    
    
    
    logging.info("Let start the process:")

    # Get X and Y
    y_train = df.loc[:, target_column].values.astype('int32')
    X_train = df.drop(target_column, axis=1).values.astype('float32')

    # Create an instance of Logistic Regression Classifier CV and fit the data

    logreg = LogisticRegression(C=0.001, solver='lbfgs', multi_class='multinomial', max_iter=100)
    logreg.fit(X_train, y_train)

    return logreg
