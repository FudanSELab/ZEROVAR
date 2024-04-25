import jsonlines
import logging
from tqdm import tqdm
import traceback

from common.database import Database

def write(records, output_file):
    with jsonlines.open(output_file, "a") as writer:
        for record in records:
            writer.write(record)

def predict(explainer, src_file, output_file, log_file):
    logging.basicConfig(filename=log_file)
    db: Database = Database.load(src_file)
    records = list()
    for idx, example in enumerate(tqdm(db)):
        try:
            record = dict()
            # 因引入codesearchnet，id信息冲突，暂时去除
            record["so_id"] = example.so_id
            record["code"] = example.method
            record["origin_explanation"] = example.explanation
            record["predictions"] = explainer.explain(example)
            records.append(record)

            if len(records) == 1:
                write(records, output_file)
                records.clear()
        except:
            logging.error(f"[Error] - Method index {idx}\n{traceback.format_exc()}")
    write(records, output_file)