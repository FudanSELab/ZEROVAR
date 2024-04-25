file = "data/AbbExpansion/pseudo_param_abb_expansion_abbr_with_line.json"
import json
with open(file, "r") as f:
    db = json.load(f)
print(len(db))