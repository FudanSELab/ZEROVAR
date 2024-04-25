'''
    封装的数据库类

    使用不同的data_processor将不同来源的数据封装成Database类,并提供用于预训练和模型预测的
    数据。
'''

import pickle
from typing import List

from common.dataprocessor.abstract_data_processor import AbstractDataProcessor
from common.example import Example, CSNExample, MethodVariableExample

class Database:
    def __init__(self, preprocessor: AbstractDataProcessor=None):
        self.examples: List[Example] = []
        self.preprocessor = preprocessor

    def __iter__(self):
        return iter(self.examples)

    def __getitem__(self, i):
        return self.examples[i]

    def __len__(self) -> int:
        return len(self.examples)

    def save(self, path_name):
        """
        输入保存的路径和文件名，保存database为pickle文件。
        """
        with open(path_name, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path_name):
        """
        第一次用json加载保存之后，后续读取都从这里来加载pickle格式的对象文件
        """
        with open(path_name, 'rb') as f:
            return pickle.load(f)

    def generate_database(self, src_path: str, output_path: str):
        '''
            处理源数据，封装成Database数据库并保存到output_path中

            Args:
                src_path: 源数据文件路径，json格式
                output_path: 保存database的文件路径，pkl格式
        '''
        self.examples = self.preprocessor.preprocess(src_path)
        self.save(output_path)