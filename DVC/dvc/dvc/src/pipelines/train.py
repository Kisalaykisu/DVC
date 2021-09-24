import argparse
import joblib
import os
import pandas as pd
from typing import Text
import yaml
import logging

from src.train import train



logging_str="[% (asctime)s: %(levelname)s: %(module)s] %(module)s"
log_dir="logs"
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"running_logs.log",level=logging.INFO,format=logging_str))


def train_model(config_path: Text) -> None:
    """Train model.
    Args:
        config_path {Text}: path to config
    """
    logging.info("Let start the creation of training pipeline:")
    config = yaml.safe_load(open(config_path))
    estimator_name = config['train']['estimator_name']
    param_grid = config['train']['estimators'][estimator_name]['param_grid']
    cv = config['train']['cv']
    target_column = config['featurize']['target_column']
    train_df = pd.read_csv(config['data_split']['train_path'])

    model = train(
        df=train_df,
        target_column=target_column,
        estimator_name=estimator_name,
        param_grid=param_grid,
        cv=cv
    )
    logging.info(model.best_score_)

    model_name = config['base']['model']['model_name']
    models_folder = config['base']['model']['models_folder']

    joblib.dump(
        model,
        os.path.join(models_folder, model_name)
    )


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    train_model(config_path=args.config)

