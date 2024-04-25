import json

def insert_as_inner_comment(method: str, exp_dicts: list) -> str:
    '''
        将生成的方法注释以行间注释的形式加入到源代码中，并返回生成的代码
    '''
    split_method = method.split("\n")
    commented_method = []
    for idx, line in enumerate(split_method,1):
        for exp_dict in exp_dicts:
            if exp_dict["line"] == idx and len(exp_dict['exp'])>0:
                commented_method.append(f"// {exp_dict['var']}: {exp_dict['exp'][0]}\n")
        commented_method.append(line+"\n")
    return "".join(commented_method)

def insert_as_outer_comment(method: str, exp_dicts: list) -> str:
    '''
        将生成的方法注释以方法注释的形式加入到源代码中，并返回生成的代码
    '''
    comment_lines = []
    for exp_dict in exp_dicts:
        if len(exp_dict['exp']) > 0:
            comment_lines.append(f"@var {exp_dict['var']} {exp_dict['exp'][0]}")
    if len(comment_lines) == 0:
        return method
    return "\n".join(comment_lines) + "\n\n</s>" + method

def get_outer_comments(exp_dicts:list) -> str:
    '''
        将生成的变量注释按行拼接返回
    '''
    comment_lines = []
    for exp_dict in exp_dicts:
        if len(exp_dict['exp']) > 0:
            comment_lines.append(f"{exp_dict['exp'][0]}")
    return "\n".join(comment_lines)

if __name__ == "__main__":
    # with open("data/database/codesearch-new/train.jsonl", "r") as f:
    #     str_data = "[" + ",\n".join(line.strip() for line in f if line.startswith('{')) + "]"
    # json.dump(json.loads(str_data), open("data/database/codesearch-new/train.json", "w"), indent=4)
    # with open("data/database/codesearch-new/valid.jsonl", "r") as f:
    #     str_data = "[" + ",\n".join(line.strip() for line in f if line.startswith('{')) + "]"
    # json.dump(json.loads(str_data), open("data/database/codesearch-new/valid.json", "w"), indent=4)
    # with open("data/database/codesearch-new/test.jsonl", "r") as f:
    #     str_data = "[" + ",\n".join(line.strip() for line in f if line.startswith('{')) + "]"
    # json.dump(json.loads(str_data), open("data/database/codesearch-new/test.json", "w"), indent=4)


    ## 将变量解释插入到代码上方，并添加分隔符
    # train_js = json.load(open("data/database/codesearch/train.json", "r"))
    # for item in train_js:
    #     item["enriched_code_outer"] = insert_as_outer_comment(
    #                                         item["original_code"],
    #                                         item["exp_dicts"]
    #                                 )
    # json.dump(train_js, open("data/database/codesearch/train.json", "w"), indent=4)

    # valid_js = json.load(open("data/database/codesearch/valid.json", "r"))
    # for item in valid_js:
    #     item["enriched_code_outer"] = insert_as_outer_comment(
    #                                         item["original_code"],
    #                                         item["exp_dicts"]
    #                                 )
    # json.dump(valid_js, open("data/database/codesearch/valid.json", "w"), indent=4)

    # test_js = json.load(open("data/database/codesearch/test.json", "r"))
    # for item in test_js:
    #     item["enriched_code_outer"] = insert_as_outer_comment(
    #                                         item["original_code"],
    #                                         item["exp_dicts"]
    #                                 )
    # json.dump(test_js, open("data/database/codesearch/test.json", "w"), indent=4)


    ## 将方法注释按行拼接存入数据库，供IR搜索使用
    train_js = json.load(open("data/database/codesearch/train.json", "r"))
    for item in train_js:
        item["var_comments"] = get_outer_comments(
                                            item["exp_dicts"]
                                    )
    json.dump(train_js, open("data/database/codesearch/train.json", "w"), indent=4)

    valid_js = json.load(open("data/database/codesearch/valid.json", "r"))
    for item in valid_js:
        item["var_comments"] = get_outer_comments(
                                            item["exp_dicts"]
                                    )
    json.dump(valid_js, open("data/database/codesearch/valid.json", "w"), indent=4)

    test_js = json.load(open("data/database/codesearch/test.json", "r"))
    for item in test_js:
        item["var_comments"] = get_outer_comments(
                                            item["exp_dicts"]
                                    )
    json.dump(test_js, open("data/database/codesearch/test.json", "w"), indent=4)