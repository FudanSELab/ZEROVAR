#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from abc import ABCMeta, abstractmethod
from collections import defaultdict

from codetoolkit.javalang.parse import parse
from codetoolkit.javalang.tree import *
from var_exp.common.database import Example

class AbstractVarExplainer(metaclass=ABCMeta):
    def __init__(self,):
        pass

    def search_vars_position(self, method: str, vars: list) -> dict:
        vars_pos = defaultdict(list)
        prefix = "public class Foo {"
        pure_code = prefix + method + "}"
        try:
            ast = parse(pure_code)
            for _, declaration_node in ast.filter(LocalVariableDeclaration):
                for declarator in declaration_node.declarators:
                    if declarator.name in vars:
                        pos = declarator.begin_pos.column - 1 - len(prefix)  # column从1开始计数，转索引时需要删除
                        vars_pos[declarator.name].append(pos)
            for _, mr_node in ast.filter(MemberReference):
                if mr_node.member in vars:
                    pos = mr_node.end_pos.column - len(prefix) - len(mr_node.member)
                    vars_pos[mr_node.member].append(pos)
            for _, mi_node in ast.filter(MethodInvocation):
                if mi_node.qualifier in vars:
                    pos = mi_node.begin_pos.column - 1 - len(prefix)
                    vars_pos[mi_node.qualifier].append(pos)
            # resort
            for _, pos in vars_pos.items():
                pos.sort()
        except Exception:
            return None
        return vars_pos

    @abstractmethod
    def explain_for_var(self, method: str, var: str, var_pos: list, cand_num=10) -> list:
        raise NotImplementedError

    def explain(self, example: Example, cand_num=10) -> dict:
        exp_dict = dict()
        vars_pos = self.search_vars_position(example.method, example.vars)
        for var,pos in vars_pos.items():
            predictions = self.explain_for_var(example.method, var, pos, cand_num)
            exp_dict[var] = predictions
        return exp_dict 