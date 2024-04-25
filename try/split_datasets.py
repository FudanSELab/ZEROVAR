'''
利用摘要算法将codesearchnet的train,test,valid分离出来
'''

import json
import jsonlines
import hashlib

# 加载映射
md_file = "data/map_code_to_dataset.json"
md5_map = dict()
with open(md_file, "r", encoding="utf-8") as f:
    md5_map = json.load(f)

train_data = []
valid_data = []
test_data = []
with open("data/output/var_exp/pseudo_param/vars_in_method_in_place_1027-1000.jsonl", "r", encoding="utf8") as f:
    for idx,data in enumerate(jsonlines.Reader(f)):
        md5 = hashlib.md5()
        encoded_code = data["original_code"].encode()
        md5.update(encoded_code)
        hex = md5.hexdigest()
        if not hex in md5_map:
            print(f"{idx}: {data} \nnot in md5_map")
        else:
            original_data = md5_map[hex]
            data["original_docstring_tokens"] = original_data["docstring_tokens"]
            data["partition"] = original_data["partition"]
            if original_data["partition"] == "train":
                train_data.append(data)
            elif original_data["partition"] == "test":
                test_data.append(data)
            elif original_data["partition"] == "valid":
                valid_data.append(data)
            else:
                print(f"{idx}: {data}\nnot belong to any dataset")

train_data_path = "data/database/codesearch/train.jsonl"
test_data_path = "data/database/codesearch/test.jsonl"
valid_data_path = "data/database/codesearch/valid.jsonl"

with jsonlines.open(train_data_path, "w") as writer:
    for record in train_data:
        writer.write(record)

with jsonlines.open(test_data_path, "w") as writer:
    for record in test_data:
        writer.write(record)

with jsonlines.open(valid_data_path, "w") as writer:
    for record in valid_data:
        writer.write(record)

