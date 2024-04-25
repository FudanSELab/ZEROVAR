'''
    对SO帖子提取的代码进行预测
'''
from var_exp.pseudo_param.codet5 import CodeT5VarExplainer
from script.var_exp.predict import predict

SRC_FILE = "data/var_exp/database_samples.pkl"
OUTPUT_FILE = "data/output/var_exp/pseudo_param/codet5.jsonl"
LOG_FILE = "log/var_exp/pseudo_param/codet5.log"

if __name__ == "__main__":
	explainer = CodeT5VarExplainer()
	predict(explainer, OUTPUT_FILE, LOG_FILE, SRC_FILE)