'''
给codesearchnet里的数据编号，并将编号保存在数据条目中
'''

import jsonlines
import json
import pickle

# code_db：只含原代码
# code_doc_db：原代码 + 方法注释
# code_comment_db：原代码 + 行间注释
# code_doc_comment_db：原代码 + 方法注释 + 行间注释
code_db = dict()
code_output_file = "data/database/codesearch/IR/code_db_test.pkl"
code_doc_db = dict()
code_doc_output_file = "data/database/codesearch/IR/code_doc_db_test.pkl"
code_comment_db = dict()
code_comment_output_file = "data/database/codesearch/IR/code_comment_db_test.pkl"
code_doc_comment_db = dict()
code_doc_comment_output_file = "data/database/codesearch/IR/code_doc_comment_db_test.pkl"

id = 0
db_file = "data/database/codesearch/test.json"
with open(db_file, "r") as f:
    db = json.load(f)

for line in db:
    code_db[id] = f"class Foo{{\n{line['original_code']}\n}}"
    code_doc_db[id] = f"class Foo {{\n/**\n{line['generated_docstring']}\n*/\n{line['original_code']}}}"
    code_comment_db[id] = f"class Foo{{\n/**\n{line['var_comments']}\n*/\n{line['original_code']}}}"
    code_doc_comment_db[id] = f"class Foo{{\n/**\n{line['generated_docstring']}\n{line['var_comments']}\n*/\n{line['original_code']}}}"
    line["id"] = id
    id += 1

# print(code_db[0])
# print("-------------------------------------")
# print(code_doc_db[0])
# print("-------------------------------------")
# print(code_comment_db[0])
# print("-------------------------------------")
# print(code_doc_comment_db[0])
# print("-------------------------------------")

with open(code_output_file, "wb") as f:
    pickle.dump(code_db, f)
with open(code_doc_output_file, "wb") as f:
    pickle.dump(code_doc_db, f)
with open(code_comment_output_file, "wb") as f:
    pickle.dump(code_comment_db, f)
with open(code_doc_comment_output_file, "wb") as f:
    pickle.dump(code_doc_comment_db, f)

with open(db_file, "w") as f:
    json.dump(db, f, indent=4)
