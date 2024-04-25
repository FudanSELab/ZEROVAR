'''
    对CSN数据中的方法参数进行预测
'''
import jsonlines
import logging
import time
from tqdm import tqdm
import traceback

from common.config import DATABASE_PATH, DATABASE_TYPES
from common.database import Database
from var_exp.pseudo_param.codet5 import CodeT5VarExplainer

def write(records, output_file):
    with jsonlines.open(output_file, "a") as writer:
        for record in records:
            writer.write(record)

if __name__ == "__main__":
    # 通过指定database_type和checkpoint来自定义预测

    # 原始模型
    # database_type = "csn_single_param"
    # checkpoint = None

    # csn single param
    # database_type = "csn_single_param"
    # 尝试预测atend格式的数据
    # database_type = "csn_multi_param_at_end"
    # checkpoint = "data/param_exp_tuning/model-epoch1-0922-2355.bin"

    # csn multi-param in-place
    # database_type = "csn_multi_param_in_place"
    # checkpoint = f"data/param_exp_tuning/{database_type}-epoch2-1020-0135.bin"

    # csn multi-param at end
    # database_type = "csn_multi_param_at_end"
    # 尝试预测atend格式的数据
    # database_type = "csn_multi_param_at_end"
    # checkpoint = "data/param_exp_tuning/model-epoch2-1009-0731.bin"

    # 用方法中的参数做生成测试
    database_type = "vars_in_method"
    # checkpoint = "data/param_exp_tuning/csn_multi_param_at_end-epoch2-1020-0147.bin"
    checkpoint = f"data/param_exp_tuning/csn_multi_param_in_place-epoch2-1020-0135.bin"

    timestamp = time.strftime("%m%d-%H%M", time.localtime())
    log_file = f"log/var_exp/pseudo_param/{database_type}_{timestamp}.log"
    logging.basicConfig(filename=log_file)

    data_file = DATABASE_PATH[database_type]["test"]
    output_file = f"data/output/var_exp/pseudo_param/{database_type}_{timestamp}.jsonl"

    explainer = CodeT5VarExplainer(device="cuda", checkpoint=checkpoint)
    db: Database = Database.load(data_file)
    records = list()
    for idx, example in enumerate(tqdm(db)):
        try:
            record = dict()
            record["code"] = example.method
            record["prompt"] = example.docstring
            record["var"] = example.var
            record["original_explanation"] = example.explanation
            explanations = explainer.explain_with_doc(example.method, example.docstring)
            for key,value in explanations.items():
                record["predictions"] = value
            records.append(record)

            if len(records) == 50:
                write(records, output_file)
                records.clear()
        except:
            logging.error(f"[Error] - Method index {idx}\n{traceback.format_exc()}")
            # 报错时添加一个空记录
            records.append({})
    write(records, output_file)