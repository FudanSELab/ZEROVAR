'''
    初步过滤提取到的变量及解释
'''
import json
import spacy
from tqdm import tqdm
from codetoolkit import Delimiter

VAR_COMMENT_PATH = "data/ExtractVarComment/csn_var_comment.json"
LEN_LIMIT = 8
STORE_PATH = "data/ExtractVarComment/auto_filtered_csn_var_comment.json"

def is_english(doc):
    ''' 过滤非英文文本 '''
    for token in doc:
        if not (token.is_alpha and all(c.isalpha() and c.isascii() for c in token.text)):
            return False
    return True

def is_possible_abbr(a, b):
    '''判断a是否可能是b的一个缩写'''
    idx = 0
    c1 = a[idx]
    for c2 in b:
        if c1 == c2:
            idx+=1
            if idx == len(a):
                return True
            c1 = a[idx]
    return False

def is_possible_related(part_list, b):
    ''' 判断part_list是否和b相关：part_list分词后的结果是否可能在b中找到扩展形式 '''
    flag = False
    for part in part_list:
        flag = flag or is_possible_abbr(part, b) # 只要有一个扩展可能成立即可
    return flag



if __name__ == "__main__" :
    filter_res = []
    nlp = spacy.load("en_core_web_sm")
    with open(VAR_COMMENT_PATH, "r") as f:
        data = json.load(f)

    for d in tqdm(data):
    # for d in data:
        d["exp"] = d["exp"][2:].strip()
        var_lower = d["var"].lower()
        exp_lower = d['exp'].lower() # 预处理：去除//，转小写

        # 1. 过滤var
        # 过滤单字符变量：往往歧义较大
        if len(var_lower) == 1:
            continue

        # 过滤不合适的var
        var_black_list = ["tmp", "obj","this", "that", "ok", "data", "sb", "ad", "uuuuu",]
        if var_lower in var_black_list:
            # print(var_lower)
            # print(exp_lower)
            # print()
            continue
        # 过滤t0这种混杂的
        if not var_lower.isalpha():
            continue


        ## 2. 过滤exp
        doc = nlp(exp_lower)

        # 过滤大于字数限制的exp
        if len(doc) > LEN_LIMIT:
            continue

        # exp只有一个单词但和var无关
        if len(doc) == 1 and not is_possible_abbr(var_lower, doc[0].text):
            continue

        # 过滤var分割后和exp一样，或比exp还长的
        var_parts_str = Delimiter.split_camel(d["var"])
        if var_parts_str == exp_lower:
            continue
        var_parts_list = var_parts_str.split(" ")
        if len(var_parts_list) > len(doc) and not is_possible_abbr(var_lower, doc[0].text):
            continue

        # 过滤分割后的var和exp几乎无关的
        if not is_possible_related(var_parts_list, exp_lower):
            continue


        # 过滤注解
        if doc[0].text.startswith('@'):
            continue
        # 过滤不合适的exp
        exp_black_list = ["todo","fixme","grab", "this", "that", "go", "gotta"]
        if doc[0].text in exp_black_list:
            continue
        # # 过滤动词开头的注释
        # if doc[0].pos_=="VERB":
        #     continue
        # 过滤非英文
        if not is_english(doc):
            continue

        # 过滤var和exp一样的
        if var_lower == exp_lower:
            continue
        # 过滤exp在var里的
        if exp_lower in var_lower:
            continue

        filter_res.append({
            "id": d["id"],
            "comment_line":d["comment_line"],
            "code":d["code"],
            "var": d["var"],
            "exp": d["exp"]
        })

    print(f"Data amount: {len(filter_res)}")

    with open(STORE_PATH, "w+") as f:
        json.dump(filter_res, f, indent=4)