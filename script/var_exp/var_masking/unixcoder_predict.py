from script.var_exp.predict import predict
from var_exp.var_masking.unixcoder import UniXcoderVarExplainer

SRC_FILE = "data/var_exp/database_samples.pkl"
OUTPUT_FILE = "data/output/var_exp/var_masking/unixcoder.jsonl"
LOG_FILE = "log/var_exp/var_masking/unixcoder.log"

if __name__ == "__main__":
	explainer = UniXcoderVarExplainer()
	predict(explainer, SRC_FILE, OUTPUT_FILE, LOG_FILE)