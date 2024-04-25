from var_exp.var_masking.codet5 import CodeT5VarExplainer
from script.var_exp.predict import predict

SRC_FILE = "data/var_exp/database_samples.pkl"
OUTPUT_FILE = "data/output/var_exp/var_masking/codet5.jsonl"
LOG_FILE = "log/var_exp/var_masking/codet5.log"

if __name__ == "__main__":
	explainer = CodeT5VarExplainer()
	predict(explainer, SRC_FILE, OUTPUT_FILE, LOG_FILE)