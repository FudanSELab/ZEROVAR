#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pickle
import re
from tqdm import tqdm
from typing import List

import codetoolkit
from codetoolkit.javalang.parse import parse
from codetoolkit.javalang.tokenizer import Position
from codetoolkit.javalang.tree import *

class Example:
    def __init__(self, so_id:int, method:str, text:str="", vars:List[str]=None):
        self.so_id = so_id
        self.method = method
        self.text = text
        self.vars = vars

# 适配当前系统，暂时选择不继承Example
class CSNExample():
    def __init__(self, method:str, docstring:str, explanation:str):
        self.method = method
        self.docstring = docstring
        self.explanation = explanation

    def __repr__(self):
        return f"{{'method':{self.method}, 'docstring': {self.docstring}, 'explanation': {self.explanation}}}"


class Database:
    def __init__(self):
        self.examples: List[Example] = []

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

    @staticmethod
    def load_from_rawdata_json(processed_data_path):
        """
        读入使用abbr_expansion.data_collection.preprocess.py处理后的json文件，例如位于CodeLM-Prompt/data/processed_data/processed_java_0_36251080.json
        返回一个已经组装好examples的db
        """
        db = Database()
        with open(processed_data_path, 'r') as f:
            lines = f.readlines()
            print("loading and preprocess origin json data:")
            for line in tqdm(lines):
                idx_text_code = eval(line[:-1])
                idx = list(idx_text_code.keys())[0]
                text = idx_text_code[idx]["text"]
                codes = idx_text_code[idx]["code"]  #codes是同一个帖子内多个代码块的代码构成的list
                clear_code_list, clear_text = Database.clear_data(codes, text)    #清洗数据并抽取方法代码

                for clear_code in clear_code_list:
                    variables:List[str] = Database.get_all_variables(clear_code)
                    if variables:   #只保存解析出来里面有变量存在的方法代码
                        db.examples.append(Example(idx, clear_code, clear_text, variables))
        return db

    @staticmethod
    def clear_data(codes:List[str], text:str):
        """
        Args:
            codes (list[str]): 由字符串代码片段构成的列表
            text(str)：So帖子的文本

        Returns:
            clear_code_list, clear_text: 返回处理好的代码字符串列表，和处理好的文本字符串
        """

        char_need_del_list = ['&gt','&lt','&quot','&amp','<sub>','<sup>','&frasl','&nbsp','&mdash']
        clear_code_list = []
        for ch in char_need_del_list:
            text = text.replace(f"{ch};", '')
            text = text.replace(ch, '')
        clear_text = re.sub(r'(\s\s*)', ' ', text)
        for code in codes:
            #清洗特殊字符
            for ch in char_need_del_list:
                code = code.replace(f"{ch};", '')
                code = code.replace(ch, '')
            #获得干净的代码列表
            clear_code_list_temp = Database.get_so_snippet_method_list(code)
            if clear_code_list_temp:  #去除无法解析返回None的情况
                clear_code_list.extend(clear_code_list_temp)
        return clear_code_list, clear_text

    @staticmethod
    def get_all_variables(pure_code):
        """
            传入方法代码，返回局部变量和变量引用的名字合并的列表
        """
        var_set = set()
        pure_code = f"public class Foo {{{pure_code}}}"
        try:
            ast = parse(pure_code)
            for _, declaration_node in ast.filter(LocalVariableDeclaration):
                for declarator in declaration_node.declarators:
                    var_set.add(declarator.name)  #使用set去重得到不重复的完整变量集合
            # 就是局部变量的名字
            for _, mf in ast.filter(MemberReference):
                # 就是变量引用的名字
                var_set.add(mf.member)
        except:
            return None
        return list(var_set)

    @staticmethod
    def extract_method_from_code(code:str, begin_pos:Position, end_pos:Position) -> str:
        """
        从给出的代码中，按照给出的指定起始和终止位置，截取出完整方法体
        输入：Position类型的元组，例如：
            Position(line=2, column=1)
            Position(line=6, column=26)
        返回：完整的方法代码
        """
        begin_line = begin_pos[0]   #有多少个line就说明有多少个\n
        begin_column = begin_pos[1]
        begin_index = begin_pos[1]

        end_line = end_pos[0]
        end_column = end_pos[1]
        end_index = end_pos[1]
        count = 1
        pos = code.find('\n')
        while pos != -1:
            count += 1
            if count == begin_line:
                begin_index = pos + begin_column
            if count == end_line:
                end_index = pos + end_column
                break
            pos = (code.find('\n',pos+1))
        return code[begin_index - 1: end_index]

    @staticmethod
    def get_so_snippet_method_list(method:str) -> List[str]:    #从数据集筛选可用的method代码，必须是纯method，外层不能包有类
        '''
        输入：So代码块内代码
        返回：代码块内可被解析的方法体的代码的列表
        '''
        #如果存在一个类包含多个方法，则会记录一个类里面存在的多个方法
        method_code_list = []
        try:
            ast = parse(method)
            for _, node in ast.filter(codetoolkit.javalang.tree.MethodDeclaration):
                #如果本身已经是方法了，则抽取出方法的源代码，加入方法代码列表返回
                if isinstance(node, codetoolkit.javalang.tree.MethodDeclaration):
                    method_code_list.append(Database.extract_method_from_code(code=method, begin_pos=node.begin_pos, end_pos=node.end_pos))
            return method_code_list
        except Exception:
            try:
                ast = parse(f"public class Foo {{{method}}}")
                for _, node in ast.filter(codetoolkit.javalang.tree.MethodDeclaration):
                    #如果本身已经是方法了，则抽取出方法的源代码，加入方法代码列表返回
                    if isinstance(node, codetoolkit.javalang.tree.MethodDeclaration):
                        method_code_list.append(Database.extract_method_from_code(code=method, begin_pos=node.begin_pos, end_pos=node.end_pos))
                    return method_code_list
            except:
            #只要无法解析都返回None
                return None



# Running Example:
# db = Database()
# db = Database.load_from_rawdata_json("/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/var_exp/test.json")
# # db.save("/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/var_exp/test.pkl")
# # db.load("/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/var_exp/test.pkl")
# for i in db:
#     print(i.so_id)
#     print(i.vars)
#     print(i.method)
#     print(i.text)