'''
把abbExp的数据转换成varsinExample的，并以数据库的格式保存
'''
import json
import pickle

from common.database import Database
from common.example import MethodVariableExample

db = Database()
id = 0
with open("data/AbbExpansion/all_abb_expansion_examples.json", "r") as f:
    data = json.load(f)
for example in data:
    for method in example["methods"]:
        db.examples.append(MethodVariableExample(id, method=method, docstring=None, vars={example["var"]:0}))

output_file = "data/AbbExpansion/abb_expansion.pkl"
with open(output_file, "wb+") as f:
    pickle.dump(db,f)

# test
with open(output_file, "rb") as f:
    d = pickle.load(f)[0]
    print(d)
    print(d.docstring == None)
