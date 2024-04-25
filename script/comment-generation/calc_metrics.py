'''
  计算模型预测的变量解释和groundtruth的bleu指标
'''

import json
from nltk.translate.meteor_score import meteor_score
from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize
from rouge import Rouge

def split_cands_and_refs(database_path):
    ref_db = []
    cand_db = []
    with open(database_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    for ex in db:
        try:
            cand_db.append(ex["predictions"][0]) # 生成文本只能要一句
            ref_db.append(ex["truth"])
        except:
            print("Error", ex["id"])
            continue
    return cand_db, ref_db


def calc_bleu(cand_list, ref_list):
    references =  [[word_tokenize(i)] for i in ref_list]
    candidates =  [word_tokenize(i) for i in cand_list]

    cc = SmoothingFunction()
    bleu_1 = corpus_bleu(references, candidates, weights=(1,0,0,0), smoothing_function=cc.method4)
    bleu_2 = corpus_bleu(references, candidates, weights=(0.5,0.5,0,0), smoothing_function=cc.method4)
    bleu_3 = corpus_bleu(references, candidates, weights=(0.33,0.33,0.33,0), smoothing_function=cc.method4)
    bleu_4 = corpus_bleu(references, candidates, weights=(0.25,0.25,0.25,0.25), smoothing_function=cc.method4)
    return (bleu_1, bleu_2, bleu_3, bleu_4)

def calc_meteor(cand_list, ref_list):
    reference = [[ref] for ref in ref_list]
    # 计算Meteor指标
    score = meteor_score(reference, cand_list)
    return score

def calc_rouge(cand_list, ref_list):
    # 创建Rouge对象
    rouge_calculator = Rouge()
    # 计算ROUGE-N和ROUGE-L
    scores = rouge_calculator.get_scores(cand_list, ref_list, avg=True)
    return scores

if __name__ == "__main__":
    hybird_data_path = "data/ExtractVarComment/hybird_generated_comment.json"
    codet5_data_path = "data/ExtractVarComment/artifial_filtered_codet5_generated_csn_var_comment.json"
    hybird_cand, hybird_ref  = split_cands_and_refs(hybird_data_path)
    codet5_cand, codet5_ref = split_cands_and_refs(codet5_data_path)

    # calc bleu
    hybird_bleu = {f"bleu-{i}" : round(v,4) for i, v in  enumerate(calc_bleu(hybird_cand, hybird_ref), 1)}
    codet5_bleu = {f"bleu-{i}" : round(v,4) for i, v in  enumerate(calc_bleu(codet5_cand, codet5_ref), 1)}
    metrics = ['bleu-1', 'bleu-2', 'bleu-3', 'bleu-4', 'rouge-1', 'rouge-2', 'meteor']
    # calc rouge
    hybird_rouge = {key: round(value["f"], 4) for key, value in calc_rouge(hybird_cand, hybird_ref).items()}
    codet5_rouge = {key: round(value["f"], 4) for key, value in calc_rouge(codet5_cand, codet5_ref).items()}

    # # calc meteor
    hybird_meteor = round(calc_meteor(hybird_cand, hybird_ref), 4)
    codet5_meteor = round(calc_meteor(codet5_cand, codet5_ref), 4)
    print(f"{'':^15}|{'bleu-1':^10}{'bleu-2':^10}{'bleu-3':^10}{'bleu-4':^10}|{'rouge-1':^10}{'rouge-2':^10}{'rouge-l':^10}|{'meteor':^10}")
    print(f"{'our model':^15}|{hybird_bleu['bleu-1']:^10}{hybird_bleu['bleu-2']:^10}{hybird_bleu['bleu-3']:^10}{hybird_bleu['bleu-4']:^10}|{hybird_rouge['rouge-1']:^10}{hybird_rouge['rouge-2']:^10}{hybird_rouge['rouge-l']:^10}|{hybird_meteor:^10}")
    print(f"{'codet5':^15}|{codet5_bleu['bleu-1']:^10}{codet5_bleu['bleu-2']:^10}{codet5_bleu['bleu-3']:^10}{codet5_bleu['bleu-4']:^10}|{codet5_rouge['rouge-1']:^10}{codet5_rouge['rouge-2']:^10}{codet5_rouge['rouge-l']:^10}|{codet5_meteor:^10}")
    