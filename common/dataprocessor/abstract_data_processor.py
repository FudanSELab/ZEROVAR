'''
    对不同来源的源数据进行预处理的抽象类
'''

from abc import ABC, abstractmethod
from datasets import load_dataset
import regex as re
from typing import List

from common.config import PARAM_EXP_PATTERN, PLACEHOLDER
from common.example import Example, CSNExample


class AbstractDataProcessor(ABC):

    @abstractmethod
    def generate_new_docstring(self, prefix: str, suffix: str, param: str):
        raise NotImplementedError

    def preprocess(self, src_path: str) -> List[Example]:
        '''
            对不同数据源进行不同的预处理操作，封装成list(Example)返回
        '''
        data_files = {"train":src_path+"/*.jsonl"}
        ds = load_dataset("json", data_files = data_files)
        ds = ds.remove_columns(["original_string", "language", "url", "sha",
            "docstring_tokens", "code_tokens", "func_name", "path", "repo",
            "partition"])

        examples = []
        for idx,data in enumerate(ds["train"]):
            doc = data["docstring"]
            f = re.finditer(PARAM_EXP_PATTERN, doc)
            for match in f:
                start, end = match.span()
                var = match.group(1)
                exp = match.group(2)
                exp = re.sub(r"\n", " ", exp).strip()

                # 1. var和exp都不为空
                # 2. exp不能以@开头（过滤掉@param/@return）
                if var and exp and not exp.startswith("@"):
                    new_docstring = self.generate_new_docstring(
                        doc[:start].strip(),
                        doc[end:].strip(),
                        var)
                    example :CSNExample = CSNExample(method=data["code"],
                                                        docstring=new_docstring,
                                                        var=var,
                                                        explanation=exp)
                    examples.append(example)
        return examples

    def __repr__(self):
        return self.__class__.__name__