import hashlib
import json

def read_json(file):
    with open(file, "r") as f:
        return json.load(f)

def calc_md5(text):
    m = hashlib.md5()
    m.update(text.encode("utf-8"))
    return m.hexdigest()

def inCandidates(groundtruth, candidate_list):
    for cand in candidate_list:
        cand1 = cand.lower().split(";") # [xxx#xxx, xxx]
        for cand2 in cand1:
            cand3 = cand2.split("#") # [xxx, xxx]
            for cand4 in cand3: # xxx
                if groundtruth in cand4:
                    return True
    return False

def combine_Groundtruth_and_candidate(candidate, groundtruth, res_path):
    # res = list()
    res = dict()
    local_dir = "C:\\Users\\12444\\Desktop\\ParseGitProjects_Ver8_CSV_Diction(NO Change)\\ParseGitProjects_Ver8_CSV_Diction(NO Change)\\"
    server_dir = "data/AbbExpansion/"
    for data in candidate:
        method_paths = data["path"].replace(local_dir,server_dir).replace("\\", "/")[:-1].split(";") # 去除分号
        for method_path in method_paths:
            if res_path == "enriched_res.json":
                method_path = method_path.replace("enriched", "original")
            with open(method_path, "r") as f:
                method = "".join(f.readlines()[1:-1]).strip()
                key = calc_md5(method) + "#" + data["abbr"].lower() + "#" + data["name"].lower()
                # groundtruth var path
                # middle var paths
                if key in groundtruth.keys():
                    # key在res中，但是comment为空
                    if key in res.keys() and not res[key]["comment_candidate"]:
                        res[key] = {
                            "id": key,
                            "abbr":data["abbr"].lower(),
                            "groundtruth":groundtruth[key],
                            "path": method_path,
                            "other_candidate": data["other_candidate"],
                            "comment_candidate": data["comment_candidate"]
                        }
                    else:
                        res[key]= {
                            "id": key,
                            "abbr":data["abbr"].lower(),
                            "groundtruth":groundtruth[key],
                            "path": method_path,
                            "other_candidate": data["other_candidate"],
                            "comment_candidate": data["comment_candidate"]
                        }

    res = list(res.values())
    with open(res_path, "w+") as f:
        json.dump(res, f, indent=4)
    return res

if __name__ == "__main__":
    original_candidate_path = "data/AbbExpansion/original_candidate1.json"
    enriched_candidate_path = "data/AbbExpansion/enriched_candidate1.json"
    original_candidate = read_json(original_candidate_path)
    enriched_candidate = read_json(enriched_candidate_path)
    groundtruth = read_json("data/AbbExpansion/pseudo_param_abb_expansion_abbr_with_line1.json")

    # get groundtruth
    # [method => hash] + var作为id
    abbr2expansion = dict()
    for data in groundtruth:
        key = calc_md5(data["method"].strip()) + "#" + data["var"].lower() + "#" + data["name"].lower()
        abbr2expansion[key] = data["expansion"]

    print("groundtruth", len(abbr2expansion.keys()))
    print("original_candidate", len(original_candidate))
    print("enriched_candidate", len(enriched_candidate))

    # for key, item in abbr2expansion.items():
    #     print("An Example of groundtruth: ", key, item)
    #     break


    # original_res = combine_Groundtruth_and_candidate(original_candidate, abbr2expansion, "original_res.json")
    # ids = []
    # for d in original_res:
    #     if d["id"] in abbr2expansion.keys():
    #         abbr2expansion.pop(d["id"])
    # print(len(abbr2expansion))
    # print(abbr2expansion)
    # import os
    # os._exit(0)

    original_res = combine_Groundtruth_and_candidate(original_candidate, abbr2expansion, "original_res.json")
    enriched_res = combine_Groundtruth_and_candidate(enriched_candidate, abbr2expansion, "enriched_res.json")

print("[original]")
# original comment
hit = 0
for data in original_res:
    candidate_list = data["comment_candidate"]
    if inCandidates(data["groundtruth"], candidate_list):
        hit += 1
print("In comment", f"{hit}/{len(original_res)}", "Precision: ", f"{round(hit/len(original_res), 3)}")
# print("Precision", f"{hit/len(original_res)}")

hit = 0
for data in original_res:
    candidate_list = data["other_candidate"]
    if inCandidates(data["groundtruth"], candidate_list):
        hit += 1
print("In others", f"{hit}/{len(original_res)}")

hit = 0
for data in original_res:
    candidate_list = data["other_candidate"]+data["comment_candidate"]
    if not inCandidates(data["groundtruth"], candidate_list):
        hit += 1
print("neither", f"{hit}/{len(original_res)}")
print("coverage", f"{round((len(original_res)-hit)/len(original_res), 3)}")

print("[enriched]")
hit = 0
for data in enriched_res:
    candidate_list = data["comment_candidate"]
    if inCandidates(data["groundtruth"], candidate_list):
        hit += 1
print("In comment", f"{hit}/{len(enriched_res)}", "Precision: ", f"{round(hit/len(enriched_res), 3)}")

hit = 0
for data in enriched_res:
    candidate_list = data["other_candidate"]
    if inCandidates(data["groundtruth"], candidate_list):
        hit += 1
print("In others", f"{hit}/{len(enriched_res)}")

hit = 0
for data in enriched_res:
    candidate_list = data["other_candidate"]+data["comment_candidate"]
    if not inCandidates(data["groundtruth"], candidate_list):
        hit += 1
print("neither", f"{hit}/{len(enriched_res)}")
print("coverage", f"{round((len(enriched_res)-hit)/len(enriched_res), 3)}")
