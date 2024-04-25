'''
人工筛选artifical_filter.py的脚本
'''
import json
import jsonlines
import os

VAR_COMMENT_PATH = "data/ExtractVarComment/csn_var_comment.json"
FILTER_COMMENT_PATH = "data/ExtractVarComment/filtered_csn_var_comment.jsonl"
PROGRESS_RECORD = "data/ExtractVarComment/progress.txt"

def is_contains_chinese(strs):
    ''' 去除注释里含中文的 '''
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


if __name__ == "__main__":
    data = []
    with open(VAR_COMMENT_PATH, "r") as f:
        data = json.load(f)
    
    start = 0
    if os.path.exists(PROGRESS_RECORD):
        with open(PROGRESS_RECORD, "r") as f:
            start = int(f.read())

    size = len(data)
    try:
        for i in range(start, size):
            idx = i + 1
            entry = data[i]
            if is_contains_chinese(entry):
                continue
            print(f"[progress: {idx} / {size}]")
            print(entry['var'])
            print(entry['exp'])
            ipt = input("Save this entry?")
            if ipt == 'Y' or ipt == 'y':
                entry["original_idx"] = i
                with jsonlines.open(FILTER_COMMENT_PATH, "a+") as w:
                    w.write(entry)
            if ipt == 'Q' or ipt == 'q':
                with open(PROGRESS_RECORD, "w+") as f:
                    f.write(str(i))
    except:
        with open(PROGRESS_RECORD, "w+") as f:
            f.write(str(i))