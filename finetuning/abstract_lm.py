import logging
import math
import random
import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from tqdm import tqdm

import torch
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

from . config import CodeT5Config
from common.config import PLACEHOLDER
from common.database import Database

class AbstractLM(metaclass=ABCMeta):
    def __init__(self, config: CodeT5Config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.model_checkpoint = None

    @abstractmethod
    def init_model(self, checkpoint=None):
        raise NotImplementedError

    def train( self, train_database: Database, valid_database: Database, database_type: str):
        timestamp = time.strftime("%m%d-%H%M", time.localtime())
        log_file = f"log/fine-tuning/{database_type}-{timestamp}.log"
        logging.basicConfig(filename=log_file, level=logging.INFO, filemode="w")

        # 新建模型存放的文件夹
        if self.config.save_dir is not None:
            Path(self.config.save_dir).mkdir(parents=True, exist_ok=True)

        # 模型初始化
        if self.model is None:
            self.init_model()

        logging.info(f"learning_rate: {self.config.learning_rate}")
        logging.info(f"train_batch_size: {self.config.train_batch_size}")
        logging.info(f"valid_batch_size: {self.config.valid_batch_size}")
        logging.info(f"epochs: {self.config.epochs}")
        logging.info(f"adam_epsilon: {self.config.adam_epsilon}")
        logging.info(f"weight_decay: {self.config.weight_decay}")
        logging.info(f"warmup_steps: {self.config.warmup_steps}")
        logging.info(f"max_grad_norm: {self.config.max_grad_norm}")
        logging.info(f"train_sampling: {self.config.train_sampling}")
        logging.info(f"valid_sampling: {self.config.valid_sampling}")
        logging.info(f"save_dir: {self.config.save_dir}")
        logging.info(f"log_step: {self.config.log_step}")

        logging.info("")
        logging.info("")

        train_examples = train_database.examples
        valid_examples = valid_database.examples

        if self.config.train_sampling is not None and self.config.train_sampling < len(train_examples):
            train_examples = random.sample(train_examples, self.config.train_sampling)
        if self.config.valid_sampling is not None and self.config.valid_sampling < len(valid_examples):
            valid_examples = random.sample(valid_examples, self.config.valid_sampling)

        num_train_optimization_steps = self.config.epochs * math.ceil(len(train_examples) / self.config.train_batch_size)
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
                'weight_decay': self.config.weight_decay},
            {'params': [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]

        optimizer = AdamW(optimizer_grouped_parameters, lr=self.config.learning_rate, eps=self.config.adam_epsilon)

        if self.config.warmup_steps < 1:
            warmup_steps = num_train_optimization_steps * self.config.warmup_steps
        else:
            warmup_steps = int(self.config.warmup_steps)
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=num_train_optimization_steps
        )

        # Start training
        logging.info("***** Running training *****")
        logging.info("  Training examples = %d", len(train_examples))
        logging.info("  Validation examples = %d", len(valid_examples))
        logging.info("  Training Batch size = %d", self.config.train_batch_size)
        logging.info("  Training Batch num = %d", math.ceil(len(train_examples) / self.config.train_batch_size))
        logging.info("  Validation Batch size = %d", self.config.valid_batch_size)
        logging.info("  Validation Batch num = %d", math.ceil(len(valid_examples) / self.config.valid_batch_size))
        logging.info("  Epoch = %d", self.config.epochs)

        for cur_epoch in range(self.config.epochs):
            self.model.train()
            random.shuffle(train_examples)
            train_steps, train_loss = 0, 0
            valid_train_steps = 0
            batch_ranges = list(
                zip(
                    range(0, len(train_examples), self.config.train_batch_size),
                    range(
                        self.config.train_batch_size,
                        len(train_examples)+self.config.train_batch_size,
                        self.config.train_batch_size)
                   )
                )
            total_batch = len(batch_ranges)
            for beg, end in batch_ranges:
                train_steps += 1
                batch = train_examples[beg:end]

                def split_code_and_label(data):
                    codes = []
                    labels = []
                    for d in data:
                        codes.append(d.docstring + "\n" + d.method)
                        labels.append(d.explanation)
                    return codes,labels

                masked_inpts, targets = split_code_and_label(batch)

                # 占位符替换成mask_token
                inputs_x = [c.replace(PLACEHOLDER, self.config.mask_token) for c in masked_inpts]
                source_ids = self.tokenizer(inputs_x, add_special_tokens=True, padding=True, truncation=True, return_tensors="pt").input_ids
                source_ids = source_ids.to(self.config.device)
                target_ids = self.tokenizer(targets, add_special_tokens=True, padding=True, truncation=True, return_tensors="pt").input_ids
                target_ids = target_ids.to(self.config.device)

                # 把pad_token_id排除
                attention_mask = source_ids.ne(self.tokenizer.pad_token_id)
                decoder_attention_mask = target_ids.ne(self.tokenizer.pad_token_id)
                outputs = self.model(
                    input_ids=source_ids,
                    attention_mask=attention_mask,
                    labels=target_ids,
                    decoder_attention_mask=decoder_attention_mask,
                    output_hidden_states=True
                )

                loss = outputs.loss
                train_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                optimizer.step()
                optimizer.zero_grad()
                scheduler.step()

                valid_train_steps += 1
                if train_steps % self.config.log_step == 0 or train_steps == total_batch:
                    logging.info(f"Epoch {cur_epoch+1}/{self.config.epochs}, Batch {train_steps}/{len(batch_ranges)},  Train loss {round(train_loss / valid_train_steps, 6)}")

            valid_loss = self.evaluate(valid_examples)
            logging.info(f"vaild_loss@ {valid_loss}")

            if self.config.save_dir is not None:
                timestamp = time.strftime("%m%d-%H%M", time.localtime())
                self.model_checkpoint = f"{self.config.save_dir}/{database_type}-epoch{cur_epoch+1}-{timestamp}.bin"
                model_to_save = self.model.module if hasattr(self.model, 'module') else self.model
                torch.save(model_to_save.state_dict(), self.model_checkpoint)
                # torch.save(model_to_save.state_dict(), f"{self.config.save_dir}/model-latest.bin")
                logging.info("Save the latest model into %s", self.model_checkpoint)

        del self.model

    def evaluate(self, eval_set):
        self.model.eval()
        batch_ranges = list(
            zip(
                range(0, len(eval_set), self.config.valid_batch_size),
                range(self.config.valid_batch_size, len(eval_set)+self.config.valid_batch_size, self.config.valid_batch_size)
            )
        )
        valid_loss = 0
        with torch.no_grad():
            for beg, end in tqdm(batch_ranges, ascii=True, desc="Validation"):
                batch = eval_set[beg:end]

                def split_code_and_label(data):
                    codes = []
                    labels = []
                    for d in data:
                        codes.append(d.docstring + "\n" + d.method)
                        labels.append(d.explanation)
                    return codes,labels
                masked_inpts, targets = split_code_and_label(batch)

                inputs_x = [c.replace(PLACEHOLDER, self.config.mask_token) for c in masked_inpts]

                source_ids = self.tokenizer(inputs_x, add_special_tokens=True, padding=True, truncation=True, return_tensors="pt").input_ids
                source_ids = source_ids.to(self.config.device)
                target_ids = self.tokenizer(targets, add_special_tokens=True, padding=True, truncation=True, return_tensors="pt").input_ids
                target_ids = target_ids.to(self.config.device)


                attention_mask = source_ids.ne(self.tokenizer.pad_token_id)
                decoder_attention_mask = target_ids.ne(self.tokenizer.pad_token_id)
                outputs = self.model(
                    input_ids=source_ids,
                    attention_mask=attention_mask,
                    labels=target_ids,
                    decoder_attention_mask=decoder_attention_mask,
                    output_hidden_states=True
                )

                loss = outputs.loss
                valid_loss += loss.item()
        return valid_loss / len(batch_ranges)

    # 目前没有调用
    def generate(self, sources):
        sources = [code.replace(PLACEHOLDER, self.config.mask_token) for code in sources]
        source_ids = self.tokenizer(sources, add_special_tokens=True, padding=True, truncation=True, return_tensors="pt").input_ids
        source_ids = source_ids.to(self.config.device)
        outputs = self.model.generate(source_ids, num_beams=self.config.cand_num, num_return_sequences=self.config.cand_num, max_length=self.config.max_len)
        beams = outputs.view(len(sources), self.config.cand_num, -1).cpu()
        cands = []
        for beam in beams:
            cands.append([self.tokenizer.decode(cand, skip_special_tokens=True).replace(self.config.mask_token, "").strip() for cand in beam])
        return cands