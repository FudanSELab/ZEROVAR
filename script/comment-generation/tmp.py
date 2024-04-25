import json
import random

hybird_data_path = "data/ExtractVarComment/hybird_generated_comment.json"
codet5_data_path = "data/ExtractVarComment/artifial_filtered_codet5_generated_csn_var_comment.json"
store_data_path = "data/ExtractVarComment/tmp.json"

if __name__ == "__main__": 
    # 混合两种数据
    with open(hybird_data_path, "r") as f:
        hybird_data = json.load(f)
    with open(codet5_data_path, "r") as f:
        codet5_data = json.load(f)    
    
    for idx, d in enumerate(hybird_data):
        d["codet5_predictions"] = codet5_data[idx]["predictions"]

    with open(store_data_path, "w+") as f:
        json.dump(hybird_data, f, indent=4)


    # 抽取样本
    store_data_path = "data/ExtractVarComment/samples.json"
    tmp_data_path = "data/ExtractVarComment/tmp.json"

    with open(store_data_path, "r") as f:
        data = json.load(f)
    with open(tmp_data_path, "r") as f:
        src_data = json.load(f)

    for d in data:
        for d2 in src_data:
            if d2["id"] == d["id"]:
                d["codet5_predictions"] = d2["codet5_predictions"]
                break

    with open(store_data_path, "w+") as f:
        json.dump(data, f, indent=4)
