from var_exp.pseudo_param.unixcoder import UniXcoderVarExplainer
from script.var_exp.predict import predict

SRC_FILE = "data/var_exp/database_samples.pkl"
OUTPUT_FILE = "data/output/var_exp/pseudo_param/unixcoder.jsonl"
LOG_FILE = "log/var_exp/pseudo_param/unixcoder.log"

if __name__ == "__main__":
	explainer = UniXcoderVarExplainer()
	predict(explainer, SRC_FILE, OUTPUT_FILE, LOG_FILE)