import jsonlines
import random

from common.database import Database

at_end_output = []
with open("data/output/var_exp/pseudo_param/vars_in_method_1020-1840.jsonl") as f:
    for line in jsonlines.Reader(f):
        at_end_output.append(line)

in_place_output = []
with open("data/output/var_exp/pseudo_param/vars_in_method_1020-1903.jsonl") as f:
    for line in jsonlines.Reader(f):
        in_place_output.append(line)

idx = random.randint(0, min(len(at_end_output), len(in_place_output)))

print(at_end_output[idx]["prompt"])
print(at_end_output[idx]["code"])
print()
print(at_end_output[idx]["var"])
print()
print("at_end=>")
print(at_end_output[idx]["predictions"])
print()
print("in_place=>")
print(in_place_output[idx]["predictions"])