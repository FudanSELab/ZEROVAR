from var_exp.var_masking.codebert import CodeBERTVarExplainer
from script.var_exp.predict import predict

SRC_FILE = "data/var_exp/database_samples.pkl"
OUTPUT_FILE = "data/output/var_exp/var_masking/codebert.jsonl"
LOG_FILE = "log/var_exp/var_masking/codebert.log"

if __name__ == "__main__":
	explainer = CodeBERTVarExplainer()
	predict(explainer, SRC_FILE, OUTPUT_FILE, LOG_FILE)