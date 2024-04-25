from var_exp.common.database import Database,Example
from var_exp.var_masking.unixcoder import UniXcoderVarExplainer

if __name__ == "__main__":
	db: Database = Database.load("data/var_exp/database.pkl")
	example: Example = db[102]

	print("[Method]\n", example.method, "\n")
	print("[Vars]\n", example.vars, "\n")

	print("[Predictions]")
	explainer = UniXcoderVarExplainer()
	for var, exps in explainer.explain(example).items():
		print(var)
		for method, predictions in exps.items():
			print(method)
			print(predictions)
			print()