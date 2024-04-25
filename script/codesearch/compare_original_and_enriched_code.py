'''
比较在IR搜索结果中，使用变量解释后的代码搜索效果和不加的区别
'''
import os
import json
import logging

def turn_index_to_code(data, index):
    if index == "code":
        return data["original_code"]
    elif index == "enriched_code":
        return data["enriched_code"]
    elif index == "code_doc":
        return data["generated_docstring"] + "\n" + data["original_code"]
    elif index == "doc_enriched_code":
        return data["generated_docstring"] + "\n" + data["enriched_code"]

def compare_index_a_and_index_b(db, index_a, index_b):
    logging.info(f"'{index_b}'比'{index_a}':")
    index_a_output=f"data/database/codesearch/IR_NEW/search_{index_a}_new.json"
    index_b_output=f"data/database/codesearch/IR_NEW/search_{index_b}_new.json"
    save_dir = f"data/database/codesearch/IR_NEW/{index_b}比{index_a}"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    better_ouput = f"{save_dir}/better.json"
    equal_output = f"{save_dir}/equal.json"
    worse_output = f"{save_dir}/worse.json"
    better = []
    equal = []
    worse = []

    with open(index_a_output, "r") as f:
        index_a_data = json.load(f)
    with open(index_b_output, "r") as f:
        index_b_data = json.load(f)


    for idx,index_a_entry in enumerate(index_a_data):
        index_a_rank = 1000
        index_b_rank = 1000
        index_b_entry = index_b_data[idx]

        # find rank in index_a res
        for rank, method_info in enumerate(index_a_entry["query_res"],1):
            method_id = method_info[0]
            if method_id == index_a_entry["correct_id"]:
                index_a_rank = rank
                break

        for rank, method_info in enumerate(index_b_entry["query_res"],1):
            method_id = method_info[0]
            if method_id == index_b_entry["correct_id"]:
                index_b_rank = rank
                break

        res = {}
        res["method_id"] = index_a_entry["correct_id"]
        res[f"{index_a}_rank"] = index_a_rank
        res[f"{index_b}_rank"] = index_b_rank
        res["query"] = index_a_entry["query"]
        res[f"{index_a}_method"] = turn_index_to_code(db[index_a_entry["correct_id"]], index_a)
        res[f"{index_b}_method"] = turn_index_to_code(db[index_a_entry["correct_id"]], index_b)

        # 效果变差
        if index_a_rank < index_b_rank:
            worse.append(res)
        elif index_b_rank < index_a_rank:
            better.append(res)
        else:
            equal.append(res)
    logging.info(f"Worse count: {len(worse)}/{len(db)}, Worse Rate: {len(worse)/len(db)}")
    logging.info(f"Better count: {len(better)}/{len(db)}, Better Rate: {len(better)/len(db)}")
    logging.info(f"Equal count: {len(equal)}/{len(db)}, Equal Rate: {len(equal)/len(db)}")
    logging.info("-------------------------------------------------------------------------------")

    with open(better_ouput, "w") as f:
        json.dump(better, f, indent=4)
    with open(worse_output, "w") as f:
        json.dump(worse, f, indent=4)
    with open(equal_output, "w") as f:
        json.dump(equal, f, indent=4)

if __name__ == "__main__":
    logging.basicConfig(filename="log/codesearch/compare_ir_indexs.log", level=logging.INFO, filemode="w")

    db_file = "data/database/codesearch/test.json"
    with open(db_file, "r") as f:
        db = json.load(f)

    # code, code_doc, enriched_code, doc_enriched_code
    combine = list()
    index_list = ["code", "code_doc", "enriched_code", "doc_enriched_code"]
    for idx, index_a in enumerate(index_list):
        for index_b in index_list[idx+1:]:
            combine.append((index_a, index_b))
    for index_a, index_b in combine:
        compare_index_a_and_index_b(db, index_a, index_b)