'''
从CSN的测试集中，通过规则抽取变量注释
'''
import re
import json

from codetoolkit.javalang.parser import Parser
from codetoolkit.javalang.tokenizer import tokenize
from codetoolkit.javalang.tree import *
import jsonlines
# from wordsegment import load, segment
# from nltk.corpus import words as nltk_words
from tqdm import tqdm

CSN_TEST_PATH = "/home/fdse/Data/CodeSearchNet/resources/data/java/final/jsonl/test/java_test_0.jsonl"
COMMENT_PATTERN = r"//.*"
BLACK_LIST = [";", "{", "}", "(", ")", "[", "]", "/"] # 过滤代码注释

VAR_COMMENT_PATH = "data/ExtractVarComment/csn_var_comment.json"

if __name__ == "__main__":
    data = [d for d in jsonlines.open(CSN_TEST_PATH, "r")]

    var_comment_data = []
    d_idx = 1
    for entry in tqdm(data):
        code = f"public class Foo {{{entry['code']}}}"
        lines = code.split("\n")
        for idx in range(len(lines)):
            line = lines[idx]
            m = re.fullmatch(COMMENT_PATTERN, line.strip())
            if(m and not m.group()[-1] in BLACK_LIST):
                # 如果上一行也是注释，可能是块级注释，舍弃
                if idx > 1 and re.fullmatch(COMMENT_PATTERN, lines[idx-1].strip()):
                    continue

                if idx + 1 < len(lines):
                    try:
                        # 判断下一行是否是变量声明语句
                        tokens  = tokenize(lines[idx + 1])
                        parser  = Parser(tokens)
                        lvds = parser.parse_local_variable_declaration_statement()
                        var = lvds.declarators[0].name
                        var_comment_data.append({
                            "id": d_idx,
                            "comment_line": idx,
                            "code": entry['code'],
                            "var": var,
                            "exp": line.strip()
                        })
                        d_idx += 1

                        # 只保留缩写变量
                        # load()
                        # words = segment(var)
                        # for word in words:
                        #     if not word in nltk_words.words():
                        #         var_comment_data.append({
                        #             "code": entry['code'],
                        #             "var": var,
                        #             "exp": line.strip()
                        #         })
                        #         break
                    except:
                        # 下一行不是变量声明
                        continue

    print(f"Data amount: {len(var_comment_data)}")

    with open(VAR_COMMENT_PATH, "w+") as f:
        json.dump(var_comment_data, f, indent=4)


