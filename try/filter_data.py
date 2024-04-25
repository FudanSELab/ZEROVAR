'''
用千成的方法对codesearchnet进行筛选
'''
import jsonlines
from common.config import CSN_DATA_DIR
src_path = CSN_DATA_DIR + "train"
config = [("train", 16), ("test", 1), ("valid", 1)]
data = []
for data_type, num in config:
    src_path = CSN_DATA_DIR + data_type
    for i in range(num):
        path = f"{src_path}/java_{data_type}_{i}.jsonl"
        with open(path, "r") as f:
            for line in jsonlines.Reader(f):
                data.append(line)

output_path = "data/database/csn_all_data.jsonl"
with jsonlines.open(output_path, "w") as w:
    for i in data:
        w.write(i)