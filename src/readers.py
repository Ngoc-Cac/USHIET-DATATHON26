import os.path as osp, glob
import pandas as pd

_EXCLUDE = ["sample_submission.csv"]

def load_csv(data_dir):
    return {
        osp.split(csv)[-1][:-4]: pd.read_csv(csv)
        for csv in glob.glob(f"{data_dir}/*.csv")
        if osp.split(csv)[-1] not in _EXCLUDE
    }
