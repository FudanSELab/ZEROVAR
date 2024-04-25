'''
    将CodeSearchNet数据处理为注释中只有单个变量, 并对其进行预测的形式
'''

import regex as re
from typing import List

from datasets import load_dataset

from common.dataprocessor.abstract_data_processor import AbstractDataProcessor
from common.config import PLACEHOLDER, PARAM_EXP_PATTERN
from common.example import Example,CSNExample


class CSNParamProcessor(AbstractDataProcessor):

    def generate_new_docstring(self, prefix: str, suffix: str, param: str):
        pass

    def preprocess(self, path: str) -> List[Example]:
        '''
            将CodeSearchNet方法注释处理成单变量预测的形式，如：
            some comments here.
            @param p1 [placeholder].

            Args:
                path: CodeSearchNet的数据目录

            Returns:
                用Example封装的数据列表
        '''

        PURE_COMMENT_PATTERN = r'^(.*?)(?=\n@|$)'

        data_files = {"train":path+"/*.jsonl"}
        ds = load_dataset("json", data_files = data_files)
        ds = ds.remove_columns(["original_string", "language", "url", "sha",
            "docstring_tokens", "code_tokens", "func_name", "path", "repo",
            "partition"])

        examples = []
        for data in ds["train"]:
            params = re.findall(PARAM_EXP_PATTERN, data["docstring"], re.DOTALL)
            pure_comment = re.findall(PURE_COMMENT_PATTERN, data["docstring"], re.DOTALL)[0]
            for param, exp in params:
                if param and exp and not exp.startswith("@"):
                    exp = re.sub(r"\n", " ", exp).strip()
                    new_docstring = f"{pure_comment}\n@param {param} {PLACEHOLDER}"
                    example :CSNExample = CSNExample(method=data["code"],
                                                        docstring=new_docstring,
                                                        var=param,
                                                        explanation=exp)
                    examples.append(example)
        return examples