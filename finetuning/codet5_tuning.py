import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration

from . abstract_lm import AbstractLM
from . config import CodeT5Config

T5_NAME = "Salesforce/codet5-base"

class CodeT5Tuning(AbstractLM):
    def __init__(self, config=CodeT5Config()):
        super(CodeT5Tuning, self).__init__(config)
        self.config.name = "t5-tuning"

    def init_model(self, checkpoint=None):
        self.tokenizer = RobertaTokenizer.from_pretrained(T5_NAME)
        self.model = T5ForConditionalGeneration.from_pretrained(T5_NAME)
        if checkpoint:
            self.model.load_state_dict(torch.load(checkpoint, map_location=self.config.device))
        self.model.to(self.config.device)
