import torch
from transformers import T5ForConditionalGeneration, RobertaTokenizer

from common.config import PLACEHOLDER
from var_exp.pseudo_param.abstract_var_explainer import AbstractVarExplainer

class CodeT5VarExplainer(AbstractVarExplainer):
    def __init__(self, device="cpu", checkpoint=None):
        super(CodeT5VarExplainer, self).__init__()
        self.device = torch.device(device)
        self.base_model = T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base')
        if checkpoint:
            self.base_model.load_state_dict(torch.load(checkpoint, map_location=self.device))
        self.tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
        self.base_model.to(self.device)


    def generate_prompt_templates(self, method: str) -> list:
        self.multi_sum_model =  T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base-multi-sum')
        self.multi_sum_model.to(self.device)

        input_ids = self.tokenizer(method, return_tensors="pt").input_ids
        input_ids = input_ids.to(self.device)
        generated_ids = self.multi_sum_model.generate(input_ids, max_length=128, num_beams=1, num_return_sequences=1)
        predictions = [self.tokenizer.decode(x, skip_special_tokens=True) for x in generated_ids]
        # 暂时去掉供生成纯注释用
        # remove the meta character '%' in templates
        # predictions = [x.replace("%", "%%").strip() for x in predictions]
        # predictions = [x+"\n@param %s <extra_id_0>.\n" for x in predictions]
        return predictions

    def explain_for_var(self, method: str, prompt_templates: list, cand_num=10) -> dict:
        all_predictions = dict()
        for template in prompt_templates:
            template = template.replace(PLACEHOLDER, "<extra_id_0>")
            inpt = template + "\n" + method
            input_ids = self.tokenizer(inpt, return_tensors="pt").input_ids
            input_ids = input_ids.to(self.device)
            generated_ids = self.base_model.generate(input_ids, max_new_tokens=128, num_beams=cand_num, num_return_sequences=cand_num)
            predictions = []
            for generated_id in generated_ids:
                output = self.tokenizer.decode(generated_id, skip_special_tokens=True)
                predictions.append(output)
            all_predictions[template] = predictions
        return all_predictions