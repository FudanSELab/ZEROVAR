'''
    将自动筛选后的数据送入微调模型预测，并计算bleu
'''

import json
import logging
import traceback
import time

from tqdm import tqdm
from var_exp.pseudo_param.hybird import HybirdVarExplainer


def write_json(records, output_file):
    with open(output_file, "a") as f:
        json.dump(records, f, indent=4)

if __name__ == "__main__":
    timestamp = time.strftime("%m%d-%H%M", time.localtime())
    log_file = f"data/ExtractVarComment/hybird_generated_comment.log"
    logging.basicConfig(filename=log_file, level=logging.INFO)

    checkpoint = f"data/param_exp_tuning/csn_multi_param_in_place-epoch2-1020-0135.bin"
    explainer = HybirdVarExplainer(device="cuda", explain_checkpoint=checkpoint)

    DATA_PATH = "data/ExtractVarComment/work-auto_filtered_csn_var_comment.json"
    OUTPUT_PATH = "data/ExtractVarComment/hybird_generated_comment.json"


    with open(DATA_PATH, "r") as f:
        db = json.load(f)

    records = list()
    batch_size = 8
    ranges = list(zip(range(0, len(db), batch_size), range(batch_size, len(db)+batch_size, batch_size)))
    for beg, end in tqdm(ranges, ascii=True):
        batch = db[beg:end]
        methods = [example["code"] for example in batch]
        vars_list = [[example["var"]] for example in batch]
        idx_list = [example["id"] for example in batch]
        true_exp_list = [example["exp"] for example in batch]

        try:
            prompt_templates_list, explanations_list = explainer.explain(methods, vars_list, prompt_num=1, cand_num=3)
        except Exception:
            logging.error(f"[Error] - Batch {beg} - {end}\n{traceback.format_exc()}")
            continue

        for idx, method, vars, true_exp, explanations in zip(idx_list, methods, vars_list, true_exp_list, explanations_list):
            record = dict()
            record["id"] = idx
            record["var"] = vars[0]
            record["truth"] = true_exp
            record["predictions"] = list(explanations[0].values())[0]
            record["method"] = method
            records.append(record)

        if len(records) >= 1000 or end >= len(db):
            write_json(records, OUTPUT_PATH)
            records.clear()
        logging.info(f"[INFO] - Batch {beg} - {end}")

