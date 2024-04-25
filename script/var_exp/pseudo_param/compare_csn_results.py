'''
    比较几种不同的方式预训练出的codet5模型生成的预测结果
'''
import jsonlines
import random

output_dir = "data/output/var_exp/pseudo_param"
origin_path = f"{output_dir}/original_codet5_1009-1543.jsonl"
single_param_path = f"{output_dir}/csn_single_param_1009-1921.jsonl"
multi_param_in_place_path = f"{output_dir}/csn_multi_param_in_place_1009-1536.jsonl"
multi_param_at_end_path = f"{output_dir}/csn_multi_param_at_end_1009-1512.jsonl"

origin = []
with open(origin_path, "r") as f:
    for i in jsonlines.Reader(f):
        origin.append(i)

single_param = []
with open(single_param_path, "r") as f:
    for i in jsonlines.Reader(f):
        single_param.append(i)

multi_param_in_place = []
with open(multi_param_in_place_path, "r") as f:
    for i in jsonlines.Reader(f):
        multi_param_in_place.append(i)

multi_param_at_end = []
with open(multi_param_at_end_path, "r") as f:
    for i in jsonlines.Reader(f):
        multi_param_at_end.append(i)

a = random.randint(0,len(origin))
print(f'example id: {a}')
print(f'method:')
print(origin[a]["code"])
print(f'var: {origin[a]["var"]}')
print(f'original_explanation: {origin[a]["original_explanation"]}')
print()
# print("origin=>")
# print(origin[a]["predictions"])
# print()
print("single_param=>")
print(single_param[a]["predictions"])
print()
print("multi_param_in_place=>")
print(multi_param_in_place[a]["predictions"])
print()
print("multi_param_at_end=>")
print(multi_param_at_end[a]["predictions"])