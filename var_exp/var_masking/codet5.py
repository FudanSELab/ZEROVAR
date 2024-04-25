import torch
from transformers import T5ForConditionalGeneration, RobertaTokenizer

from var_exp.var_masking.abstract_var_explainer import AbstractVarExplainer

class CodeT5VarExplainer(AbstractVarExplainer):
	def __init__(self, device="cpu"):
		super(CodeT5VarExplainer, self).__init__()
		device = torch.device(device)
		self.multi_sum_model =  T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base-multi-sum')
		self.base_model = T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base')
		self.tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
		self.multi_sum_model.to(device)
		self.base_model.to(device)

	def explain_for_var(self, method: str, var: str, var_pos: list, cand_num=10) -> list:
		all_predictions = list()
		for idx,pos in enumerate(var_pos,1):
			inpt = method[0:pos] + "<extra_id_0>" + method[pos+len(var):]
			input_ids = self.tokenizer(inpt, return_tensors="pt").input_ids
			generated_ids = self.base_model.generate(input_ids, max_length=8, num_beams=cand_num, num_return_sequences=cand_num)
			predictions = [self.tokenizer.decode(x, skip_special_tokens=True) for x in generated_ids]
			res = dict()
			res["index"] = idx
			res["start_pos"] = pos
			res["predictions"] = predictions
			all_predictions.append(res)
		return all_predictions