from transformers.models.roberta import RobertaModel, RobertaForSequenceClassification
from transformers.models.bert import BertModel
import torch
import torch.nn as nn


class BiEncoder(nn.Module):
    def __init__(self):
        super(BiEncoder, self).__init__()
        self.nl_encoder: RobertaModel = RobertaModel.from_pretrained("microsoft/codebert-base")
        # self.pl_encoder: RobertaModel = RobertaModel.from_pretrained("microsoft/codebert-base")
        self.pl_encoder: RobertaModel = self.nl_encoder

    def forward(self, nl_inputs=None, pl_inputs=None, ty_inputs=None):
        if nl_inputs is not None:
            nl_vecs = self.nl_encoder(nl_inputs, attention_mask=nl_inputs.ne(1)).pooler_output
            if pl_inputs is None:
                return nl_vecs

        if pl_inputs is not None:
            pl_vecs = self.pl_encoder(pl_inputs, token_type_ids=None, attention_mask=pl_inputs.ne(1)).pooler_output
            if nl_inputs is None:
                return pl_vecs

        return nl_vecs, pl_vecs


# 根据原论文的描述所实现的慢速编码器部分，需要涉及NL-PL对，同时还要拼接它们的按位相减的结果，按位相乘的结果
class CasClassifier(nn.Module):
        def __init__(self):
                super(CasClassifier, self).__init__()
                self.classifier: RobertaForSequenceClassification = RobertaForSequenceClassification.from_pretrained("microsoft/codebert-base")

        def forward(self, input_feats):
                outputs = self.classifier.forward(
                         input_ids=input_feats[0],
                         attention_mask=input_feats[0].ne(1),
                        #  token_type_ids=input_feats[1],
                         token_type_ids=None,
                         labels=input_feats[2],
                         return_dict=True
                )
                return outputs.logits, outputs.loss