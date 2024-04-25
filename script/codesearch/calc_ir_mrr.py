import json

def cal_mrr_and_hit(db_path):
    with open(db_path, "r") as f:
        db = json.load(f)

    K = [1, 2, 3, 5, 10, 15, 50, 100]
    mrr_k = {_k: 0 for _k in K}
    hit_k = {_k: 0 for _k in K}

    for data in db:
        for rank, preds in enumerate(data["query_res"],1):
            if preds[0] == data['correct_id']:
                for k in K:
                    if rank <= k:
                        mrr_k[k] += 1/rank
                        hit_k[k] += 1
    mrr = dict()
    for k, value in mrr_k.items():
        mrr[k] = value / len(db)

    hit = dict()
    for k, value in hit_k.items():
        hit[k] = value / len(db)
    print("MRR :{}, HIT:{}".format(mrr, hit))

# test
# db = [{"correct_id":2,"query_res":[[1,0.12],[2,0.12],[3,0.10]]}]
# cal_mrr_and_hit(db)


print("original_code=>")
res_file = "data/database/codesearch/IR_NEW/search_code_new.json"
cal_mrr_and_hit(res_file)
print()

print("original_code+generated_doc=>")
res_file = "data/database/codesearch/IR_NEW/search_code_doc_new.json"
cal_mrr_and_hit(res_file)
print()

print("enriched_code=>")
res_file = "data/database/codesearch/IR_NEW/search_enriched_code_new.json"
cal_mrr_and_hit(res_file)
print()

print("generated_doc+enriched_code=>")
res_file = "data/database/codesearch/IR_NEW/search_doc_enriched_code_new.json"
cal_mrr_and_hit(res_file)
print()