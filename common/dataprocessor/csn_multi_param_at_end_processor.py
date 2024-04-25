'''
    将CodeSearchNet的数据处理成含多个参数，但是将预测的参数挪至尾部的形式
'''

import re
from typing import List

from datasets import load_dataset

from common.config import PARAM_EXP_PATTERN,PLACEHOLDER
from common.dataprocessor.abstract_data_processor import AbstractDataProcessor
from common.example import Example, CSNExample


class CSNMultiparamAtEndProcessor(AbstractDataProcessor):
    def generate_new_docstring(self, prefix: str, suffix: str, param: str):
        return "".join([prefix, "\n", suffix, "\n@param ", param, " ", PLACEHOLDER])