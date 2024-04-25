import random
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer
import json
import torch
from typing import List
from more_itertools import chunked
from config_class import Config

class InputExample(object):
    def __init__(self, nl_ids, pl_ids, label):
        self.nl_ids = nl_ids
        self.pl_ids = pl_ids
        self.label = label

# 训练encoder的数据集与一般使用时的数据集
class EncoderDataset(Dataset):
    def __init__(self, config: Config, cls_id=0, pad_id=1, sep_id=2):
        super(Dataset, self).__init__()
        self.config = config
        self.examples: List[InputExample] = []
        self.cls_id = cls_id
        self.pad_id = pad_id
        self.sep_id = sep_id

    def __getitem__(self, idx):
        #return (torch.tensor(self.data[idx].pl_ids), torch.tensor(self.data[idx].nl_ids))
        return self.examples[idx]

    def __len__(self):
        return len(self.examples)

    def collate_fn(self, batch: List[InputExample]):
        nl_batch = []
        pl_batch = []
        ty_batch = []
        for example in batch:
            nl_batch.append([self.cls_id] + example.nl_ids[:self.config.max_nl_len-2] + [self.sep_id])
            pl_tokens = [self.cls_id] + example.pl_ids[:self.config.max_pl_len-2] + [self.sep_id]
            pl_batch.append(pl_tokens)
            first_sep_idx = pl_tokens.index(self.sep_id)
            if first_sep_idx < len(pl_tokens) - 1:
                token_types = [0] * (first_sep_idx + 1) + [1] * (len(pl_tokens) - first_sep_idx - 1)
            else:
                token_types = [0] * len(pl_tokens)
            ty_batch.append(token_types)
        max_nl = max([len(nl_ids) for nl_ids in nl_batch])
        max_pl = max([len(pl_ids) for pl_ids in pl_batch])
        nl_batch = [
            nl_ids + [self.pad_id] * (max_nl - len(nl_ids)) for nl_ids in nl_batch
        ]
        pl_batch = [
            pl_ids + [self.pad_id] * (max_pl - len(pl_ids)) for pl_ids in pl_batch
        ]
        ty_batch = [
            ty_ids + [0] * (max_pl - len(ty_ids)) for ty_ids in ty_batch
        ]
        return torch.LongTensor(nl_batch), torch.LongTensor(pl_batch), torch.LongTensor(ty_batch)

    def load_example(
            self,
            mode,
            tokenizer:RobertaTokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base"),
            query_key="docstring_tokens",
            code_keys=["enriched_code"]
        ):
        self.cls_id = tokenizer.cls_token_id
        self.pad_id = tokenizer.pad_token_id
        tokenizer.pad_token_type_id
        self.sep_id = tokenizer.sep_token_id
        if mode == 'test':
            path = f"{self.config.data_path}/test.json"
        elif mode == 'eval':
            path = f"{self.config.data_path}/valid.json"
        else:
            path = f"{self.config.data_path}/train.json"
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Dataset size: {len(data)}")
            for js in data:
                nl = " ".join(js[query_key])
                pl = "\n".join(js[k] for k in code_keys)
                nl_tokens = tokenizer.tokenize(nl)
                pl_tokens = tokenizer.tokenize(pl)
                nl_ids = tokenizer.convert_tokens_to_ids(nl_tokens)
                pl_ids = tokenizer.convert_tokens_to_ids(pl_tokens)
                self.examples.append(InputExample(nl_ids, pl_ids, label=1))
        print(len(self))
        return self
        
# 训练encoder的数据集与一般使用时的数据集
class ClassifierDataset(Dataset):
    def __init__(self, config: Config, cls_id=0, pad_id=1, sep_id=2):
        super(Dataset, self).__init__()
        self.config = config
        self.examples: List[InputExample] = []
        self.cls_id = cls_id
        self.pad_id = pad_id
        self.sep_id = sep_id

    def __getitem__(self, idx):
        #return (torch.tensor(self.data[idx].pl_ids), torch.tensor(self.data[idx].nl_ids))
        return self.examples[idx]

    def __len__(self):
        return len(self.examples)

    def collate_fn(self, batch: List[InputExample]):
        token_batch = []
        type_batch = []
        label_batch = []
        for example in batch:
            token_ids = [self.cls_id]+ example.nl_ids[:self.config.max_nl_len-3] + [self.sep_id] + example.pl_ids[:self.config.max_pl_len-3] + [self.sep_id]
            type_ids = [0] * (len(example.nl_ids[:self.config.max_nl_len-3]) + 2) + [1] * (len(example.pl_ids[:self.config.max_pl_len-3]) + 1)
            token_batch.append(token_ids)
            type_batch.append(type_ids)
            label_batch.append(example.label)
        max_len = max([len(token_ids) for token_ids in token_batch])
        token_batch = [
            token_ids + [self.pad_id] * (max_len - len(token_ids)) for token_ids in token_batch
        ]
        type_batch = [
            type_ids + [0] * (max_len - len(type_ids)) for type_ids in type_batch
        ]
        
        return torch.LongTensor(token_batch), torch.LongTensor(type_batch), torch.LongTensor(label_batch)


    def load_example(
            self,
            mode,
            tokenizer:RobertaTokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base"),
            query_key="docstring_tokens",
            code_keys=["enriched_code"]
        ):
        self.cls_id = tokenizer.cls_token_id
        self.pad_id = tokenizer.pad_token_id
        tokenizer.pad_token_type_id
        self.sep_id = tokenizer.sep_token_id
        if mode == 'test':
            path = f"{self.config.data_path}/test.json"
        elif mode == 'eval':
            path = f"{self.config.data_path}/valid.json"
        else:
            path = f"{self.config.data_path}/train.json"
        with open(path, 'r', encoding='utf-8') as f:
            for js in json.load(f):
                nl = " ".join(js[query_key])
                pl = "\n".join(js[k] for k in code_keys)
                nl_tokens = tokenizer.tokenize(nl)
                pl_tokens = tokenizer.tokenize(pl)
                nl_ids = tokenizer.convert_tokens_to_ids(nl_tokens)
                pl_ids = tokenizer.convert_tokens_to_ids(pl_tokens)
                self.examples.append(InputExample(nl_ids, pl_ids, label=1))
        if mode == "train" or mode == "eval":
            size = len(self.examples)
            for idx in range(size):
                neg_idx = random.randint(0, size-1)
                while neg_idx == idx:
                    neg_idx = random.randint(0, size-1)
                nl_ids = self.examples[idx].nl_ids
                pl_ids = self.examples[neg_idx].pl_ids
                self.examples.append(InputExample(nl_ids, pl_ids, label=0))
        else:
            new_examples = []
            chunk_size = 1000  # 参考codebert论文
            for chunk in chunked(self.examples, chunk_size):
                if len(chunk) < chunk_size:
                    break
                for e in chunk:
                    nl_ids = e.nl_ids
                    for ee in chunk:
                        pl_ids = ee.pl_ids
                        new_examples.append(InputExample(nl_ids, pl_ids, label=1 if ee is e else 0))
            self.examples = new_examples
        return self

if __name__ == "__main__":
    config = Config()
    dataset = EncoderDataset(config,'test')
    dataloader = DataLoader(dataset, batch_size=4, collate_fn=dataset.collate_fn)
    for batch in dataloader:
        print(batch)


