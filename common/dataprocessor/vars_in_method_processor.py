from codetoolkit.javalang.parse import parse
from codetoolkit.javalang.tree import *
from datasets import load_dataset
from tqdm import tqdm

from common.config import PLACEHOLDER
from common.example import MethodVariableExample

from common.dataprocessor.abstract_data_processor import AbstractDataProcessor

class VarsInMethodProcessor(AbstractDataProcessor):
    def __init__(self) -> None:
        super(VarsInMethodProcessor, self).__init__()

    def get_all_variables(self, pure_code):
        """
            传入方法代码，返回局部变量和变量引用的名字合并的列表
        """
        vars = dict()
        pure_code = f"public class Foo {{{pure_code}}}"
        try:
            ast = parse(pure_code)
            for _, declaration_node in ast.filter(LocalVariableDeclaration):
                for declarator in declaration_node.declarators:
                    if not declarator.name in vars:
                        vars[declarator.name] = declarator.begin_pos.line
            for _, mf in ast.filter(MemberReference):
                if not mf.member in vars:
                    vars[mf.member] = mf.begin_pos.line
        except:
            return None
        return vars

    def preprocess(self, src_path: str):
        # 目录
        if not src_path.endswith(".jsonl"):
            data_files = {"train":src_path+"/*.jsonl"}
        else: # 文件
            data_files = {"train":src_path}
        ds = load_dataset("json", data_files = data_files)
        # ds = ds.remove_columns(["original_string", "language", "url", "sha",
        #     "docstring_tokens", "code_tokens", "func_name", "path", "repo",
        #     "partition"])
        examples = []
        for idx, data in enumerate(tqdm(ds["train"])):
            vars = self.get_all_variables(data["code"])
            example :MethodVariableExample = MethodVariableExample(
                                                method_id=idx,
                                                method=data["code"],
                                                docstring=data["docstring"],
                                                vars=vars
                                            )
            examples.append(example)
        return examples

    def generate_new_docstring(self, prefix: str, suffix: str, param: str):
        return super().generate_new_docstring(prefix, suffix, param)