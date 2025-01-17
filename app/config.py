import os

current_dir = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.dirname(current_dir)

DATA_LAKE_PATH = os.path.join(PROJECT_ROOT, "datalake")
DATA_MART_PATH = os.path.join(PROJECT_ROOT, "datamart")
