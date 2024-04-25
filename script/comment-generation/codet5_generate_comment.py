'''
    将自动筛选后的数据送入codet5进行预测
'''
import json
import logging
import time
import traceback

from tqdm import tqdm
from transformers import T5ForConditionalGeneration, RobertaTokenizer

DATA_PATH = "data/ExtractVarComment/work-auto_filtered_csn_var_comment.json"
OUTPUT_FILE =  "data/ExtractVarComment/artifial_filtered_codet5_generated_csn_var_comment.json"

if __name__ == "__main__":
    timestamp = time.strftime("%m%d-%H%M", time.localtime())
    log_file = f"data/ExtractVarComment/codet5_generate.log"
    logging.basicConfig(filename=log_file)

    # load data
    with open(DATA_PATH, "r") as f:
        db = json.load(f)

    # generate prompt
    for d in db:
        lines = d["code"].split("\n")
        insert_line = d["comment_line"]
        lines[insert_line] = lines[insert_line].replace(d["exp"], "<extra_id_0>")
        d["masked_code"] = "\n".join(lines)

    # load model
    database_type = "vars_in_method"
    checkpoint = f"data/param_exp_tuning/csn_multi_param_in_place-epoch2-1020-0135.bin"
    model = T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base').to("cuda")
    tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')

    for idx, d in enumerate(tqdm(db)):
        try:
            input_ids = tokenizer(d["masked_code"], return_tensors="pt").input_ids.to("cuda")
            generated_ids = model.generate(
                input_ids,
                max_new_tokens=8,
                num_beams=3,
                num_return_sequences=3
                )
            d["predictions"] = [tokenizer.decode(id, skip_special_tokens=True) for id in generated_ids]
            d["truth"] = d["exp"]
        except:
            logging.error(f"[Error] - Method index {idx}\n{traceback.format_exc()}")

    with open(OUTPUT_FILE, "w+") as f:
        json.dump(db,f, indent=4)

