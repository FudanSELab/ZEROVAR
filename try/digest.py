import json
from datasets import load_dataset
from tqdm import tqdm
import hashlib

from common.config import CSN_DATA_DIR
train_data = load_dataset(CSN_DATA_DIR + "train")
valid_data = load_dataset(CSN_DATA_DIR + "valid")
test_data = load_dataset(CSN_DATA_DIR + "test")
mds = dict()

for d  in tqdm(train_data["train"]):
    md5 = hashlib.md5()
    encoded_code = d["code"].encode()
    md5.update(encoded_code)
    mds[md5.hexdigest()] = d

for d in tqdm(test_data["test"]):
    md5 = hashlib.md5()
    encoded_code = d["code"].encode()
    md5.update(encoded_code)
    mds[md5.hexdigest()] = d

for d in tqdm(valid_data["validation"]):
    md5 = hashlib.md5()
    encoded_code = d["code"].encode()
    md5.update(encoded_code)
    mds[md5.hexdigest()] = d

with open("data/map_code_to_dataset.json", "w+") as f:
    json.dump(mds, f)