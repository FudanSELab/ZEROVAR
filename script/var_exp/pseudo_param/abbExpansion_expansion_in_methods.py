"""
    计算AbbExpansion的数据中，expansion在方法体中存在的比例
"""
import json
import re

from codetoolkit.javalang.parse import parse
from codetoolkit.javalang.tree import *
from codetoolkit.delimiter import *
from codetoolkit.javalang.tokenizer import Identifier, String
from tqdm import tqdm

def tokenize_method(code, reserve_comment=False):
    '''
        将方法处理为token序列
    '''
    code_tokens = list()
    try:
        cu = parse(code)
    except:
        return None 
    for _, node in cu.filter(MethodDeclaration):
        if reserve_comment and node.documentation is not None:
            for line in node.documentation.strip('/*\n. ').split("\n"):
                line = line.strip('/*\n. ')
                line = " ".join(Delimiter.split_camel(w) for w in line.split() if w not in NLTK_STOPWORDS and not re.match(r'\W+$', w))
                code_tokens.append(line)
    for token in node.tokens(type=(String, Identifier)):
        code_tokens.extend(ronin.split(token.value.strip('\"\'')))
    return code_tokens

src_file = "data/AbbExpansion/pseudo_param_abb_expansion_abbr.json"
with open(src_file, "r") as f:
    db = json.load(f)

cnt0,cnt1,cnt2 = 0,0,0
for idx, data in enumerate(tqdm(db)):
    code = f"class Foo{{\n {data['method']} \n}}"
    tokens = " ".join(tokenize_method(code)).lower()
    explanation_tokens = ""
    for exp in data["explanation"]:
        explanation_tokens += " ".join(Delimiter.split_camel(w) for w in exp.split()) + "\n"

    pattern = fr"\b{data['expansion']}\b"
    in_method = len(re.findall(pattern, tokens))>0
    in_explanation = len(re.findall(pattern, explanation_tokens)) > 0
    # in_method = data["expansion"] in " ".join(tokens).lower()
    # in_explanation = data["expansion"] in explanation_tokens
    if in_method:
        cnt0 += 1 
    if in_explanation:
        cnt1 += 1
    if in_method or in_explanation:
        cnt2 += 1

print("在方法里：",cnt0/len(db))
print("在注释里：", cnt1/len(db))
print("在两者任一：", cnt2/len(db))
