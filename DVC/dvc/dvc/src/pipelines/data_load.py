import argparse
from typing import Text
import yaml
import logging
import os
from src.data.dataset import get_dataset


logging_str="[% (asctime)s: %(levelname)s: %(module)s] %(module)s"
log_dir="logs"
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"running_logs.log",level=logging.INFO,format=logging_str))

def data_load(config_path: Text) -> None:
    """ Load raw data.
    Args:
        config_path{Text}:path to config
        base_config_path{Text}:path to base config
    """
    logging.info("Let start the creation of data load pipeline:")
    config = yaml.safe_load(open(config_path))
    dataset = get_dataset()
    dataset.to_csv(config['data_load']['dataset_csv'], index=False)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    data_load(config_path= args.config)
