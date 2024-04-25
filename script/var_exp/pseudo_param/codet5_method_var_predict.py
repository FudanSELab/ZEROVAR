'''
    对从方法中挖掘到的参数进行预测
'''

import jsonlines
import logging
import time
from tqdm import tqdm
import traceback

from common.config import DATABASE_PATH, DATABASE_TYPES, PLACEHOLDER
from common.database import Database
from var_exp.pseudo_param.codet5 import CodeT5VarExplainer

def filter_predictions(var_name: str, predictions: list[dict]):
    res = []
    for pre in predictions:
        flag = True
        # 1. 以@开头的不要
        if pre.startswith("@"):
            flag = False
        # 2. 冠词加变量名的不要
        articles = ["the", "The", "a", "A", "an"]
        for arc in articles:
            if pre == f"{arc} {var_name}":
                flag = False
                break
        # 3. 变量名本身不要
        if pre == var_name:
            flag = False

        if flag:
            res.append(pre)
    return res



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
    logging.basicConfig(filename=log_file)

    # original op
    # data_file = DATABASE_PATH[database_type]["test"]

    # tmp op
    data_file = "data/database/csn_all_filtered_data.pkl"
    output_file = f"data/output/var_exp/pseudo_param/{database_type}_{model_type}_{timestamp}.jsonl"

    explainer = CodeT5VarExplainer(device="cuda", checkpoint=checkpoint)
    db: Database = Database.load(data_file)
    records = list()
    for idx, example in enumerate(tqdm(db)):
        try:
            record = dict()
            record["original_code"] = example.method
            record["original_docstring"] = example.docstring
            # 生成新注释
            record["codet5_generated_docstring"] = \
                explainer.generate_prompt_templates(example.method)
            predictions = []
            if example.vars == None:
                # 记录一下解析出错的情况
                record["error"] = "No vars extracted, caused by parse error"
            else:
                for var_name, line in example.vars.items():
                    prompt = example.docstring + f"\n@param {var_name} {PLACEHOLDER}"
                    explanations = explainer.explain_with_doc(example.method, prompt)
                    for key, value in explanations.items():
                        prediction = filter_predictions(var_name, value)
                        # 记录一下筛除后没有predictions的错误
                        if len(prediction) == 0:
                            record["error"] = f"No predictions for var: {key}"
                    predictions.append(dict(name=var_name, line=line, exp=prediction))
            record["predictions"] = predictions
            record["commented_code"] = explainer.add_exp_to_code(example.method, predictions)
            records.append(record)

            if len(records) == 50:
                write(records, output_file)
                records.clear()
        except:
            logging.error(f"[Error] - Method index {idx}\n{traceback.format_exc()}")
            # 报错时添加一个空记录
            records.append({})
    write(records, output_file)