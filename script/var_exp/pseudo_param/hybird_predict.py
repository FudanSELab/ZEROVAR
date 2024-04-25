'''
    对从方法中挖掘到的参数进行预测
'''

import functools
import jsonlines
import logging
import time
from tqdm import tqdm
import traceback

from common.config import DATABASE_PATH, DATABASE_TYPES, PLACEHOLDER
from common.database import Database
from var_exp.pseudo_param.hybird import HybirdVarExplainer

def add_exp_to_code(method: str, exp_dicts: list) -> str:
    '''
        将生成的方法注释以行间注释的形式加入到源代码中，并返回生成的代码
    '''
    split_method = method.split("\n")
    commented_method = []
    for idx, line in enumerate(split_method,1):
        for exp_dict in exp_dicts:
            if exp_dict["line"] == idx and len(exp_dict['exp'])>0:
                commented_method.append(f"// {exp_dict['var']}: {exp_dict['exp'][0]}\n")
        commented_method.append(line+"\n")
    return "".join(commented_method)


def write(records, output_file):
    with jsonlines.open(output_file, "a") as writer:
        for record in records:
            writer.write(record)

if __name__ == "__main__":
    # 给方法中的参数做参数预测
    database_type = "vars_in_method"
    model_type = "in_place"
    # checkpoint = "data/param_exp_tuning/csn_multi_param_at_end-epoch2-1020-0147.bin"
    checkpoint = f"data/param_exp_tuning/csn_multi_param_in_place-epoch2-1020-0135.bin"

    timestamp = time.strftime("%m%d-%H%M", time.localtime())
    log_file = f"log/var_exp/pseudo_param/{database_type}_{model_type}_{timestamp}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO)

    #origin op
    # data_file = DATABASE_PATH[database_type]["test"]

    # tmp op
    data_file = "data/database/csn_all_filtered_data.pkl"
    output_file = f"data/output/var_exp/pseudo_param/{database_type}_{model_type}_{timestamp}.jsonl"

    explainer = HybirdVarExplainer(device="cuda", explain_checkpoint=checkpoint)
    db: Database = Database.load(data_file)
    records = list()

    batch_size = 128
    ranges = list(zip(range(0, len(db), batch_size), range(batch_size, len(db)+batch_size, batch_size)))
    for beg, end in tqdm(ranges, ascii=True):
        batch = db[beg:end]
        batch = [example for example in batch if example.vars is not None]
        methods = [example.method for example in batch]
        vars_list = [[var for var, _ in example.vars.items()] for example in batch]
        lines_list = [[line for _, line in example.vars.items()] for example in batch]
        docstrings = [example.docstring for example in batch]
        try:
            prompt_templates_list, explanations_list = explainer.explain(methods, vars_list, prompt_num=1, cand_num=3)
        except Exception:
            logging.error(f"[Error] - Batch {beg} - {end}\n{traceback.format_exc()}")
            continue

        for method, vars, lines, docstring, prompt_templates, explanations in zip(
                    methods, vars_list, lines_list, docstrings, prompt_templates_list, explanations_list):
            record = dict()
            record["original_code"] = method
            record["original_docstring"] = docstring
            # 生成新注释
            record["generated_docstring"] = prompt_templates[0]
            record["exp_dicts"] = [dict(var=var, line=line, exp=list(temp_dict.values())[0]) for var, line, temp_dict in zip(vars, lines, explanations)]
            record["enriched_code"] = add_exp_to_code(method, record["exp_dicts"])
            records.append(record)
        if len(records) >= 1000 or end >= len(db):
            write(records, output_file)
            records.clear()
        logging.info(f"[INFO] - Batch {beg} - {end}")