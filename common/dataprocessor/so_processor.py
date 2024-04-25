'''
    对SO数据进行预处理
'''

from typing import List

from common.dataprocessor.abstract_data_processor import AbstractDataProcessor
from common.example import Example


class SOProcessor(AbstractDataProcessor):

    def preprocess(self, src_path: str) -> List[Example]:
        return super().preprocess(src_path)
