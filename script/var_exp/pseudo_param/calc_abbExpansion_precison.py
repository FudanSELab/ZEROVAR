"""
    伪参数在abbExpansion上的准确率
"""
import json

from codetoolkit import Delimiter

data_file = "data/AbbExpansion/pseudo_param_abb_expansion_abbr.json"
with open(data_file, "r") as f:
    db = json.load(f)

# 记录一下没有击中的
not_hit_list = []

hit = 0
for data in db:
    isHit = False
    for explanation in data["explanation"]:
        explanation = explanation.replace("{", "")
        explanation = explanation.replace("}", "")
        explanation = explanation.replace("@", "")
        explanation = Delimiter.split_camel(explanation)
        if data["expansion"] in explanation:
            isHit = True
            break
    if isHit:
        hit += 1
    else:
        not_hit_list.append(data)


with open("data/AbbExpansion/not_hit_pure_abbr.json", "w+") as f:
    json.dump(not_hit_list, f, indent=4)

print("data total:",len(db))
print("hit count",hit)
print("hit rate:", hit/len(db))