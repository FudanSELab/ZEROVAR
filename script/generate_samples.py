'''
    SO任务中，抽取1000条数据做测试
'''

import pickle
import random

from common.database import Database

DATA_FILE = "data/var_exp/database2.pkl"
OUTPUT_FILE = "data/var_exp/database_samples.pkl"
IDX_FILE = "data/var_exp/samples_idx.pkl"
N_SAMPLES = 1000

if __name__ == "__main__":
	db: Database = Database.load(DATA_FILE)

	samples_idx = random.sample(range(len(db)), N_SAMPLES)
	with open(IDX_FILE, "wb+") as f:
		pickle.dump(samples_idx, f)

	samples = [db[i] for i in samples_idx]
	with open(OUTPUT_FILE, "wb+") as f:
		pickle.dump(samples, f)