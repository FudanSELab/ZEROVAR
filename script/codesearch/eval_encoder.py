from config_class import Config
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
import json
from dataset import EncoderDataset
from model import BiEncoder
from utils import cos_similarity, get_priliminary
import logging
import time
import tqdm


def eval_encoder(dataloader, encoder, config, test = False, ret = False):
    if config.use_cuda:
        encoder = encoder.cuda()

    encoder.eval()
    code_vecs_list = []
    nl_vecs_list = []

    for batch in tqdm.tqdm(dataloader, desc="Eval-Encoding", ascii=True, total=len(dataloader.dataset) // dataloader.batch_size):
        nl_ids, pl_ids, ty_ids = batch

        if config.use_cuda:
            pl_ids = pl_ids.cuda()
            nl_ids = nl_ids.cuda()
            ty_ids = ty_ids.cuda()

        with torch.no_grad():
            nl_vecs, code_vecs = encoder(nl_ids, pl_ids, ty_ids)
            # scores = cos_similarity(nl_vec, code_vec)
            code_vecs_list.append(code_vecs.cpu().numpy())
            nl_vecs_list.append(nl_vecs.cpu().numpy())

    code_vecs = np.concatenate(code_vecs_list, 0)
    code_vecs = code_vecs / np.linalg.norm(code_vecs, axis=1, keepdims=True)
    code_vecs = torch.tensor(code_vecs.T)
    if config.use_cuda:
        code_vecs = code_vecs.cuda()
    nl_vecs = np.concatenate(nl_vecs_list, 0)
    nl_vecs = nl_vecs / np.linalg.norm(nl_vecs, axis=1, keepdims=True)

    K = [1, 2, 3, 5, 10, 15, 50, 100]
    # 计算mrr值
    rank_k = {_k: 0 for _k in K}
    # 存储answered_k值
    ans_k = {_k: 0 for _k in K}
    
    scores = []
    batch_size = 256
    batch_ranges = list(zip(range(0, len(nl_vecs), batch_size), range(batch_size, len(nl_vecs)+batch_size, batch_size)))
    for beg, end in tqdm.tqdm(batch_ranges, desc="Eval-Similarity", ascii=True):
        batch = torch.tensor(nl_vecs[beg:end])
        if config.use_cuda:
            batch = batch.cuda()
        sims = torch.matmul(batch, code_vecs)
        ranked_idxs = torch.argsort(sims, dim=-1, descending=True)[:,:config.filter_K]
        ranked_idxs = ranked_idxs.cpu().numpy().tolist()
        scores.append(sims[:, ranked_idxs].cpu().numpy())
        for i, idxs in enumerate(ranked_idxs):
            target = beg + i
            if target not in idxs:
                continue
            loc = idxs.index(target) + 1
            for k in K:
                if loc <= k:
                    ans_k[k] += 1
                    rank_k[k] += 1/loc

    mrr = dict()
    for k, value in rank_k.items():
        mrr[k] = value / len(dataloader.dataset)
    
    hit = dict()
    for k, value in ans_k.items():
        hit[k] = value / len(dataloader.dataset)

    logging.info("Evaluation --- MRR :{}, HIT:{}".format(mrr, hit))
    if ret:
        return mrr, hit
    if test:
        return np.concatenate(scores, axis=0)

#用测试集对encoder进行测试，并且对NL查询按相似度排序返回结果
def test_encoder(dataloader, encoder, dataset, config, log = False, ret = False):
        test_result_path = config.data_path + "java_test_0.jsonl"
        if (ret == True and log == True):
                scores = eval_encoder(dataloader, encoder, config=config, test=True)
                results, _ = get_priliminary(scores, dataset, config.filter_K)
                if log:
                        nl_no = 1
                log = open(test_result_path,'w')
                for result in results:
                        js = {}
                        js['nl_idx'] = nl_no
                        js['answers'] = []
                        for res in result:
                                pl_no = res.ids
                                js['answers'].append(pl_no)
                                log.write(json.dumps(js)+"\n")
                log.close()
                return results

        elif (ret == False and log == True):
                scores = eval_encoder(dataloader, encoder, True)
                results, _ = get_priliminary(scores, dataset, config.filter_K)
                nl_no = 1
                log = open(test_result_path,'w')
                for result in results:
                        js = {}
                        js['nl_idx'] = nl_no
                        js['answers'] = []
                        for res in result:
                                pl_no = res.ids
                                js['answers'].append(pl_no)
                        log.write(json.dumps(js)+"\n")
                        log.close()
        else:
                eval_encoder(dataloader, encoder)

if __name__ == '__main__':
    res_type = "original_code"
#     res_type = "enriched_code"
#     res_type = "docstring_original_code"
#     res_type = "docstring_enriched_code"

    timestamp = time.strftime("%m%d-%H%M", time.localtime())
    log_file = f"log/codesearch-new/predict/{res_type}-{timestamp}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, filemode="w")

    config = Config()
    encoder = BiEncoder()
    encoder.load_state_dict(torch.load(config.saved_path+"/"+f"{res_type}-encoder.pt"))

    logging.info("Loading dataset...")
    dataset = EncoderDataset(config, res_type,'test')
    dataloader = DataLoader(dataset, config.eval_batch_size, collate_fn=dataset.collate_fn)

    logging.info("Start testing...")
    eval_encoder(dataloader, encoder, config, test=False, ret=False)