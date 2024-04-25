'''
    测试数据结果里有没有<extra_id_1>
'''
import jsonlines
import logging
import time
from tqdm import tqdm
import traceback

from common.config import DATABASE_PATH, DATABASE_TYPES
from common.database import Database
from var_exp.pseudo_param.codet5 import CodeT5VarExplainer

if __name__ == "__main__":
    # 用方法中的参数做生成测试
    database_type = "vars_in_method"
    # checkpoint = "data/param_exp_tuning/csn_multi_param_at_end-epoch2-1020-0147.bin"
    checkpoint = f"data/param_exp_tuning/csn_multi_param_in_place-epoch2-1020-0135.bin"
    explainer = CodeT5VarExplainer(device="cuda", checkpoint=checkpoint)
    data_file = DATABASE_PATH[database_type]["test"]
    db: Database = Database.load(data_file)
    for idx, example in enumerate(tqdm(db)):
        try:
            explanations = explainer.explain_with_doc(example)
        except:
            logging.error(f"[Error] - Method index {idx}\n{traceback.format_exc()}")
            # 报错时添加一个空记录