'''
    将CodeSearchNet数据处理为注释中有多个变量, 并在原地对其进行预测的形式
'''

import re
from typing import List

from datasets import load_dataset

from common.dataprocessor.abstract_data_processor import AbstractDataProcessor
from common.example import Example,CSNExample
from common.config import PLACEHOLDER


class CSNMultiparamInplaceProcessor(AbstractDataProcessor):
    def __init__(self) -> None:
        super(CSNMultiparamInplaceProcessor, self).__init__()

    def generate_new_docstring(self, prefix: str, suffix: str, param: str):
        return "".join([prefix, "\n", "@param ", param, " ", PLACEHOLDER, "\n", suffix])