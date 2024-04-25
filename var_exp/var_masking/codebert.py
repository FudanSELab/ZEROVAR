import torch
from transformers import RobertaTokenizer, RobertaForMaskedLM, pipeline

from var_exp.var_masking.abstract_var_explainer import AbstractVarExplainer

class CodeBERTVarExplainer(AbstractVarExplainer):
	def __init__(self, device="cpu"):
		super(CodeBERTVarExplainer, self).__init__()
		device = torch.device(device)
		self.model = RobertaForMaskedLM.from_pretrained("microsoft/codebert-base-mlm")
		self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base-mlm")
		self.model.to(device)

	def explain_for_var(self, method: str, var: str, var_pos: list, cand_num=10) -> list:
		fill_mask = pipeline('fill-mask', model=self.model, tokenizer=self.tokenizer)
		all_predictions = list()
		for idx,pos in enumerate(var_pos,1):
			inpt = method[0:pos] + "<mask>" + method[pos+len(var):]
			outputs = fill_mask(inpt, top_k=cand_num)
			predictions = [x["token_str"] for x in outputs]
			res = dict()
			res["index"] = idx
			res["start_pos"] = pos
			res["predictions"] = predictions
			all_predictions.append(res)
		return all_predictions
		