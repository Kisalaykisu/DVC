import pandas as pd
from typing import Text
import yaml
import logging
import os



logging_str="[% (asctime)s: %(levelname)s: %(module)s] %(module)s"
log_dir="logs"
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"running_logs.log",level=logging.INFO,format=logging_str))


def data_split(config_path: Text) -> None:
    """Split dataset into train and test
    Args:
       config_path {Text}: path to config
    """
    logging.info("Let start the creation of data-split-pipeline:")
    config = yaml.safe_load(open(config_path))
    dataset = pd.read_csv(config['featurize']['features_path'])

    train_dataset,test_dataset=train_test_split(
        dataset,
        test_size = config['data_split']['test_size'],
        random_state=config['base']['random_state']
    )

    train_csv_path =config['data_split']['train_path']
    test_csv_path =config['data_split']['test_path']
    train_dataset.to_csv(train_csv_path,index=False)
    test_dataset.to_csv(test_csv_path,index=False)




if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    data_split(config_path=args.config)
