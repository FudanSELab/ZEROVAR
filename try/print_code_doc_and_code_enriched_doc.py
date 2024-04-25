import json

worse_file = "data/database/codesearch/IR_NEW/doc_enriched_code比code_doc/worse.json"

with open(worse_file, "r") as f:
    db = json.load(f)
print(f"总数据量:{len(db)}")

res = []
count = [0,0,0,0,0,0,0,0,0,0]
# 记录每个数据的下降位数
drop = []
drop_map = {i:list() for i in range(0, 100, 10)}
for rand_data in db:
    a_rank = rand_data["code_doc_rank"]
    b_rank = rand_data["doc_enriched_code_rank"]
    a_rank = 100 if a_rank == 1000 else a_rank
    b_rank = 100 if b_rank == 1000 else b_rank
    diff = b_rank - a_rank
    for key,list in drop_map.items():
        if diff >= key and diff < key+10:
            drop_map[key].append(rand_data)
            a=False
print()
print("*******************************************")
print(f"范围\t数量\t比例")
for key, value in drop_map.items():
    print(f"{key}~{key+10}\t{len(value)}\t{len(value)/len(db)}")
print("*******************************************")
print()

# 获取下降范围大于min_diff的数据并输出
min_diff = 50
search_res = []
for key, value in drop_map.items():
    if key >= min_diff:
        search_res += value

print(f"number of drop>{min_diff}: {len(search_res)}")
output= "log/compare_doc_code_and_doc_enriched_code.txt"
with open(output, "w+") as f:
    f.write(f"drop > {min_diff}\n")
    for res in search_res:
        f.write("************************************************\n")
        f.write(f"method_id: {res['method_id']}\n")
        f.write(f"doc_code_rank: {res['code_doc_rank']}\n")
        f.write(f"doc_enriched_code_rank: {res['doc_enriched_code_rank']}\n")
        f.write(f"query: {res['query']} ")
        f.write("\n")
        f.write(f"doc_code_method=>\n {res['code_doc_method']}\n")
        f.write("\n")
        f.write(f"doc_enriched_code_method=>\n {res['doc_enriched_code_method']}\n")
        f.write("************************************************\n")



