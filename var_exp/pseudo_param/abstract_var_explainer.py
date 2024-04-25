#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from abc import ABCMeta, abstractmethod

class AbstractVarExplainer(metaclass=ABCMeta):
    def __init__(self,):
        pass

    @abstractmethod
    def generate_prompt_templates(self, method: str) -> list:
        raise NotImplementedError

    @abstractmethod
    def explain_for_var(self, method: str, prompt_templates: list, cand_num=10) -> dict:
        raise NotImplementedError

    def explain(self, example, cand_num=10) -> dict:
        '''
            给不带注释的数据生成参数解释
        '''
        prompt_templates = self.generate_prompt_templates(example.method)

        exp_dict = dict()
        for var in example.vars:
            prompt_templates = [t%var for t in prompt_templates]
        predictions = self.explain_for_var(example.method, prompt_templates, var, cand_num)
        exp_dict[var] = predictions
        return exp_dict

    def explain_with_doc(self, method: str, prompt: str, cand_num=10):
        '''
            给自带注释的数据生成参数解释，并返回结果
        '''
        prompt_template = [prompt]
        predictions = self.explain_for_var(method, prompt_template, cand_num)
        return predictions

    def add_exp_to_code(self, method: str, vars: list[dict]) -> str:
        '''
            将生成的方法注释以行间注释的形式加入到源代码中，并返回生成的代码
        '''
        split_method = method.split("\n")
        commented_method = []
        for idx, line in enumerate(split_method,1):
            for var in vars:
                if var["line"] == idx and len(var['exp'])>0:
                    commented_method.append(f"// {var['name']}: {var['exp'][0]}\n")
            commented_method.append(line+"\n")
        return "".join(commented_method)