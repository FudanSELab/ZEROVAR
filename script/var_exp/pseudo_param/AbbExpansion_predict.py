'''
    对AbbExpansion论文中的数据进行预测
'''
import json
import logging
import time
import traceback
from codetoolkit.javalang.parse import parse
from codetoolkit.javalang.tree import *
from tqdm import tqdm

from var_exp.pseudo_param.hybird import HybirdVarExplainer

def add_exps_to_method(explanations, method, insert_line):
    '''
        把生成的解释插入到方法中
    '''
    explanation = "// " +" ".join(explanations)
    lines = method.split("\n")
    enriched_method = ""
    for idx, line in enumerate(lines, 1):
        if insert_line == idx:
            enriched_method += "\n" + explanation +"\n"
        enriched_method += line + "\n"
    return enriched_method


def write_json(records, output_file):
    with open(output_file, "a") as f:
        json.dump(records, f, indent=4)

data_file = "data/AbbExpansion/abb_expansion.json"
# output_file = "data/AbbExpansion/pseudo_param_abb_expansion_abbr.json"
output_file = "data/AbbExpansion/pseudo_param_abb_expansion_abbr_with_line1.json"

# load db
with open(data_file, "r") as f:
    db = json.load(f)

model_type = "in_place"
checkpoint = f"data/database/param_exp_tuning/csn_multi_param_in_place-epoch2-1020-0135.bin"

timestamp = time.strftime("%m%d-%H%M", time.localtime())
log_file = f"log/var_exp/pseudo_param/abb_expansion_{model_type}_{timestamp}.log"
logging.basicConfig(filename=log_file, level=logging.INFO)

explainer = HybirdVarExplainer(device="cuda", explain_checkpoint=checkpoint)

records = list()
batch_size = 128
ranges = list(zip(range(0, len(db), batch_size), range(batch_size, len(db)+batch_size, batch_size)))
for beg, end in tqdm(ranges, ascii=True):
    batch = db[beg:end]
    batch = [example for example in batch if example["var"]]
    methods = [example["method"] for example in batch]
    vars_list = [[example["var"]] for example in batch]
    # 变量所处的行号
    line_list = [example["line"] for example in batch]
    lib_list = [example["lib"] for example in batch]
    type_list = [example["type"] for example in batch]
    abbr_list = [example["abbr"] for example in batch]
    path_list = [example["path"] for example in batch]
    expansion_list = [example["expansion"] for example in batch]
    # 用abbr跑
    vars_list = [[example["abbr"]] for example in batch]
    abbr_list = [example["var"] for example in batch]

    try:
        prompt_templates_list, explanations_list = explainer.explain(methods, vars_list, prompt_num=1, cand_num=3)
    except Exception:
        logging.error(f"[Error] - Batch {beg} - {end}\n{traceback.format_exc()}")
        continue

    for lib,type,vars, abbr, expansion,  explanations, method, path, prompt_templates,line in zip(
                lib_list, type_list, vars_list, abbr_list, expansion_list, explanations_list, methods, path_list, prompt_templates_list, line_list):
        record = dict()
        record["lib"] = lib
        record["type"] = type
        record["var"] = vars[0]
        record["name"] = abbr
        record["line"] = line
        record["expansion"] = expansion
        record["explanation"] = list(explanations[0].values())[0]
        record["method"] = method
        record["enriched_method"] = add_exps_to_method(list(explanations[0].values())[0], method, line)
        record["path"] = path
        record["generated_docstring"] = prompt_templates[0]
        records.append(record)
    if len(records) >= 1000 or end >= len(db):
        write_json(records, output_file)
        records.clear()
    logging.info(f"[INFO] - Batch {beg} - {end}")