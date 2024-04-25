from distutils.command.config import config
import json
import random
import os
import re
import string

"""
本文件对CodeSearchNet的源数据进行一定的处理：
1、用来构建为慢速分类器训练的分类数据
2、对一些质量不好的数据进行一定的处理（如过滤掉等）
3、对源数据中的一些本项目用不到的属性进行过滤
"""

class TrainData:
    def __init__(self,code_tokens,nl_tokens,code,docstring,func_name,repo) -> None:
        self.code_tokens = code_tokens
        self.nl_tokens = nl_tokens
        self.code = code
        self.docstring = docstring
        self.func_name = func_name
        self.repo = repo


class DataFilterer:
    def __init__(self,data_path=None,data=None):
        if data is None:
            self.data_path = data_path
            self.data = self.load_data(self.data_path)
        else:
            self.data = data
        self.filter_table = ['<p','()','=','<br','>','/','<ul','<li','<ol','{','{@','}','\n','(',')','*','@','--']

    @staticmethod
    def filter(self,data):
        result = []
        for i in range(len(data)):
            if self.too_short(data[i]):
                continue
            elif self.has_chinese(data[i]):
                continue
            elif self.has_java(data[i]):
                continue
            else:
                data[i].nl_tokens = self.detach_punctuation(data[i])
                data[i].nl_tokens = self.too_long(data[i])
                result.append(data[i])
        return result

    def load_data(self,data_path):
        data = []
        with open(data_path,'r') as f:
            for line in f.readlines():
                js = json.loads(line)
                data.append(TrainData(js['code_tokens'],js['docstring_tokens'],js['code'],js['docstring'],js['func_name'],js['repo']))
        return data

    # 一些过滤规则，True则应该过滤，False则不应该过滤
    # 第一条过滤规则：nl_tokens长度过小的数据需要被过滤.注意，判断nl_tokens的长度是在去除标点符号后判断的
    def too_short(self,example):
        punc = string.punctuation
        nl_tokens = example.nl_tokens
        length = 0
        for token in nl_tokens:
            if token not in punc:
                length += 1
        return True if length<=4 else False

    # 第二条过滤规则：将中文的NL过滤出去，因为它们在数据集中是以unicode的形式存储的，这在模型中无法提供有用的语义信息
    def has_chinese(self,example):
        nl = example.docstring
        for str in nl:
            if u'\u4e00' <= str <= u'\u9fff':
                return True
        return False

    # 第三条规则：考虑将一些过长的nl_tokens截断(考虑截断tokens长度大于20的，从第一个句号前截断)
    def too_long(self,example):
        if len(example.nl_tokens) > 20:
            nl_tokens = example.nl_tokens
            loc = len(nl_tokens)-1
            for index in range(len(nl_tokens)):
                if nl_tokens[index] == ".":
                    loc = index
                    break
            return nl_tokens[:loc+1]
        else:
            return example.nl_tokens

    # 第四条规则：考虑将第一句中含有javadoc标识符的注释过滤掉
    def has_java(self,example):
        nl = example.docstring
        nl = nl.split('.')
        if '@' in nl[0]:
            return True
        return False

    # 第五条规则：将docstring_tokens中含有黑名单中符号的部分拿掉
    def detach_punctuation(self,example):
        nl_tokens = []
        for i in range(len(example.nl_tokens)):
            flag = False
            for p in self.filter_table:
                if p in example.nl_tokens[i]:
                    flag = True
                    break
            if flag == False:
                nl_tokens.append(example.nl_tokens[i])
        return nl_tokens

from common.config import CSN_DATA_DIR
if __name__ == "__main__":
    src_file = CSN_DATA_DIR + "train"
    filter = DataFilterer()
