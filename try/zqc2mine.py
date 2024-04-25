'''
11月17日 按学长要求，用千成新筛选的数据进行查询
'''

import hashlib
import json
from tqdm import tqdm

md52query = dict()
# 计算新code的md5，并保存
new_file = "data/database/codesearch/IR_NEW/csn_test_db.json"
with open(new_file, "r") as f:
    new_test = json.load(f)
for data in tqdm(new_test):
    md5 = hashlib.md5()
    encoded_code = data["code"].encode()
    md5.update(encoded_code)
    md52query[md5.hexdigest()] = data["docstring"]

# 计算原有数据code的md5，匹配后加入对应的
my_file =  "data/database/codesearch/test.json"
with open(my_file, "r") as f:
    my_test = json.load(f)
for data in my_test:
    md5 = hashlib.md5()
    encoded_code = data["original_code"].encode()
    md5.update(encoded_code)
    hex = md5.hexdigest()
    if hex in md52query:
        data["query"] = md52query[hex]
    else:
        data["query"] = " ".join(data["original_docstring_tokens"])

with open(my_file, "w") as f:
    json.dump(my_test, f, indent=4)