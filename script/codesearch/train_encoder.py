# 对快速编码器进行训练
import json
import logging
import random
import time
from tqdm import tqdm

from config_class import Config
from transformers import get_linear_schedule_with_warmup
import torch
import torch.nn as nn
import os
from eval_encoder import eval_encoder
from dataset import EncoderDataset
from torch.utils.data import DataLoader
from model import BiEncoder


def train_encoder(train_dataloader, eval_dataloader, encoder, config, type):
    max_mrr = 0
    if not os.path.exists(config.saved_path):
        os.makedirs(config.saved_path)

    if config.use_cuda:
        encoder = encoder.cuda()

    encoder.zero_grad()
    optimizer = torch.optim.AdamW(encoder.parameters(), lr=1e-5)
    num_training_steps = len(train_dataloader)*config.encoder_epoches
    logging.info(f"Total step: {num_training_steps}")
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)
    
    loss_func = torch.nn.TripletMarginWithDistanceLoss(distance_function=lambda x1, x2: 1 - torch.cosine_similarity(x1, x2), margin=config.margin)

#     if os.path.exists(config.saved_path+f"/{type}-encoder.pt"):
#         encoder.load_state_dict(torch.load(config.saved_path+f"/{type}-encoder.pt"))
#     if os.path.exists(config.saved_path+f"/{type}-optimizer.pt"):
#         optimizer.load_state_dict(torch.load(config.saved_path+f"/{type}-optimizer.pt"))
#     if os.path.exists(config.saved_path+f"/{type}-scheduler.pt"):
#         scheduler.load_state_dict(torch.load(config.saved_path+f"/{type}-scheduler.pt"))
    progress_bar = tqdm(desc="Training", total=num_training_steps, ascii=True)
    step = 0
    for epoch in range(1, config.encoder_epoches + 1):
        total_loss = 0
        tr_num = 0
        encoder.train()
        for batch_num, batch in enumerate(train_dataloader, 1):
            step += 1
            nl_ids, pl_ids, ty_ids = batch

            if config.use_cuda:
                nl_ids = nl_ids.cuda()
                pl_ids = pl_ids.cuda()
                ty_ids = ty_ids.cuda()
            nl_vecs, code_vecs = encoder(nl_ids, pl_ids, ty_ids)
            #scores = cos_similarity(nl_vecs, code_vecs)
        #     scores=(nl_vecs[:, None,:]*code_vecs[None,:,:]).sum(-1)
        #     # print(scores)
        #     labels = torch.arange(code_vecs.shape[0])
        #     # print(labels)
        #     if config.use_cuda:
        #         labels = labels.cuda()
        #     loss = loss_func(scores, labels)
            idxs = set(range(nl_ids.shape[0]))
            neg_idxs = [random.choice(list(idxs - {i})) for i in range(nl_ids.shape[0])]

            neg_code_vecs = code_vecs[neg_idxs,]
            loss = loss_func(nl_vecs, code_vecs, neg_code_vecs)
            # print(loss)
            
            # torch.nn.utils.clip_grad_norm(encoder.parameters(), 1.0)
            total_loss += loss.item()
            current_loss = loss.item()
            tr_num += 1

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            scheduler.step()

            progress_bar.update()
            if step % 500 == 0 or step == num_training_steps:
                logging.info("Epoch:{}, Batch:{}, Average Loss:{}, Current Loss:{}".format(epoch, batch_num, total_loss/tr_num, current_loss))
            if step % 20000 == 0 or step == num_training_steps:
                mrr, hit = eval_encoder(eval_dataloader, encoder=encoder, config=config, ret=True, test=False)
                logging.info("Evaluation --- Max MRR:{}, Current MRR:{}, Current HIT:{}".format(max_mrr, mrr, hit))
                if mrr[10] > max_mrr:
                    max_mrr = mrr[10]
                    torch.save(encoder.state_dict(), config.saved_path+f"/{type}-encoder.pt")
                    torch.save(optimizer.state_dict(), config.saved_path+f"/{type}-optimizer.pt")
                    torch.save(scheduler.state_dict(), config.saved_path+f"/{type}-scheduler.pt")
                # logging.info("evaluation---avg_loss:{}, mrr:{}, ans_k:{}".format(mrr, ans_k)+"\n")



if __name__ == '__main__':
    # code_keys = ["original_code"]
    # code_keys = ["enriched_code"]
    code_keys = ["enriched_code_outer"]
    # code_keys = ["generated_docstring", "original_code"]
    # code_keys = ["generated_docstring", "enriched_code"]
    # code_keys = ["generated_docstring", "enriched_code_outer"]

    setting_name = "+".join(code_keys)

    timestamp = time.strftime("%m%d-%H%M%S", time.localtime())
    log_file = f"log/codesearch-new/{setting_name}-{timestamp}.log"
    format = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(filename=log_file, level=logging.INFO, format=format)


    config = Config()

    logging.info(f"Setting: {code_keys}")
    logging.info(f"Config: \n{json.dumps(config.__dict__, indent=4)}")

    logging.info("Loading train dataset...")
    # train_dataset = EncoderDataset(config).load_example(mode="train", query_key="original_docstring_tokens", code_keys=code_keys)
    # torch.save(train_dataset, f"data/database/codesearch-new/train_{setting_name}.pt")
    train_dataset = torch.load(f"data/database/codesearch-new/train_{setting_name}.pt")
    train_dataloader = DataLoader(train_dataset, config.train_batch_size, shuffle=True, collate_fn=train_dataset.collate_fn)

    logging.info("Loading eval dataset...")
    # eval_dataset = EncoderDataset(config).load_example(mode="eval", query_key="original_docstring_tokens", code_keys=code_keys)
    # torch.save(eval_dataset, f"data/database/codesearch-new/valid_{setting_name}.pt")
    eval_dataset = torch.load(f"data/database/codesearch-new/valid_{setting_name}.pt")
    eval_dataloader = DataLoader(eval_dataset, config.eval_batch_size, collate_fn=eval_dataset.collate_fn)

    logging.info("Loading test dataset...")
    # test_dataset = EncoderDataset(config).load_example(mode="test", query_key="original_docstring_tokens", code_keys=code_keys)
    # torch.save(test_dataset, f"data/database/codesearch-new/test_{setting_name}.pt")
    test_dataset = torch.load(f"data/database/codesearch-new/test_{setting_name}.pt")
    test_dataloader = DataLoader(test_dataset, config.eval_batch_size, collate_fn=test_dataset.collate_fn)


    logging.info("Loading encoder...")
    encoder = BiEncoder()

    logging.info("Start training...")
    train_encoder(train_dataloader, eval_dataloader, encoder, config, setting_name)

    logging.info("Start testing...")
    eval_encoder(test_dataloader, encoder, config, test=False, ret=False)