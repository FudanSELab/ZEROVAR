'''
    计算预测结果与原结果之间的loss和bleu指标
'''

import jsonlines
from nltk.translate.bleu_score import corpus_bleu
from nltk.tokenize import word_tokenize

from common.database import Database
from common.config import DATABASE_PATH
from finetuning.codet5_tuning import CodeT5Tuning
from finetuning.config import CodeT5Config

def calc_loss(checkpoint, database_type):
    config = CodeT5Config(
        save_dir="data/param_exp_tuning/",
        train_batch_size=5,
        valid_batch_size=5
    )
    model = CodeT5Tuning(config)
    model.init_model(checkpoint)

    database = Database.load(DATABASE_PATH[database_type]["test"])
    loss = model.evaluate(database)
    return loss

def calc_bleu(database_path):
    ref_db = []
    cand_db = []
    with open(database_path, "r", encoding="utf-8") as f:
        for idx,ex in enumerate(jsonlines.Reader(f)):
            try:
                cand_db.append(ex["predictions"][0])
                ref_db.append(ex["original_explanation"])
            except:
                # print(idx)
                pass
    # 10个候选项，每个都算一下，最后取最大值
    references =  [[word_tokenize(i)] for i in ref_db]
    candidates =  [word_tokenize(i) for i in cand_db]

    bleu_1 = corpus_bleu(references, candidates, weights=(1,0,0,0))
    bleu_2 = corpus_bleu(references, candidates, weights=(0.5,0.5,0,0))
    bleu_3 = corpus_bleu(references, candidates, weights=(0.33,0.33,0.33,0))
    bleu_4 = corpus_bleu(references, candidates, weights=(0.25,0.25,0.25,0.25))
    return (bleu_1, bleu_2, bleu_3, bleu_4)

if __name__ == "__main__":
    # csn single param
    database_type = "csn_single_param"
    checkpoint = "data/param_exp_tuning/model-epoch1-0922-2355.bin"
    print(database_type)
    # loss = calc_loss(checkpoint, database_type)
    # print(f"mean loss: {loss}")
    bleu = calc_bleu("data/output/var_exp/pseudo_param/csn_single_param_1009-1921.jsonl")
    print(f"bleu: {bleu}")

    # csn multi-param in-place
    database_type = "csn_multi_param_in_place"
    checkpoint = "data/param_exp_tuning/model-epoch2-0930-0628.bin"
    print(database_type)
    # loss = calc_loss(checkpoint, database_type)
    # print(f"mean loss: {loss}")
    bleu = calc_bleu("data/output/var_exp/pseudo_param/csn_multi_param_in_place_1009-1536.jsonl")
    print(f"bleu: {bleu}")


    # # csn multi-param at end
    database_type = "csn_multi_param_at_end"
    checkpoint = "data/param_exp_tuning/model-epoch2-1009-0731.bin"
    print(database_type)
    # loss = calc_loss(checkpoint, database_type)
    # print(f"mean loss: {loss}")
    bleu = calc_bleu("data/output/var_exp/pseudo_param/csn_multi_param_at_end_1009-1512.jsonl")
    print(f"bleu: {bleu}")