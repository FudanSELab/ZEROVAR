from typing import List

class Example:
    def __init__(self, so_id:int, method:str, text:str="", vars:List[str]=None):
        self.so_id = so_id
        self.method = method
        self.text = text
        self.vars = vars

# 适配当前系统，暂时选择不继承Example
class CSNExample():
    def __init__(self, method:str, docstring:str, var:str, explanation:str):
        self.method = method
        self.docstring = docstring
        self.explanation = explanation
        self.var = var

    def __repr__(self):
        return f"{{'method':{self.method}, 'docstring': {self.docstring}, 'var': {self.var}, 'explanation': {self.explanation}}}"

class MethodVariableExample():
    '''
        保存从方法中提取出的变量相关属性
    '''
    def __init__(self, method_id: int, method: str, docstring: str, vars: dict):
        self.idx = method_id
        self.method = method
        self.docstring = docstring
        self.vars = vars

    def __repr__(self):
        return f'{{"method":{self.method}, "docstring":{self.docstring}, "vars":{self.vars}}}'