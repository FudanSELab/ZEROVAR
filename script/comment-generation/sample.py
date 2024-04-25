'''
抽样进行人工检测
'''
import json
import random

hybird_data_path = "data/ExtractVarComment/hybird_generated_comment.json"
codet5_data_path = "data/ExtractVarComment/artifial_filtered_codet5_generated_csn_var_comment.json"
store_data_path = "data/ExtractVarComment/samples.json"

if __name__ == "__main__": 
    with open(hybird_data_path, "r") as f:
        hybird_data = json.load(f)
    with open(codet5_data_path, "r") as f:
        codet5_data = json.load(f)    


    size = len(hybird_data)
    cnt = 0
    samples = []
    while True:
        try:
            idx = random.randint(0, size)
            sample = hybird_data[idx]
            print(sample["method"])
            print(sample["var"])
            print("[truth]", sample["truth"])
            print("[our model]", sample["predictions"][0])
            print("[codet5]", codet5_data[idx]["predictions"][0])
            ans = input("Do you want this?")
            if ans == 'n':
                continue
            else:
                samples.append(sample)
                print(f"current sample count: {len(samples)}")
            if (len(samples) == 30): 
                break
        except:
            with open(store_data_path, "w+") as f:
                json.dump(samples, f, indent=4)
    
    with open(store_data_path, "w+") as f:
        json.dump(samples, f, indent=4)