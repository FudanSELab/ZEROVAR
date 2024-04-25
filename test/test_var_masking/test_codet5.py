from var_exp.common.database import Example, Database
from var_exp.var_masking.codet5 import CodeT5VarExplainer

if __name__ == '__main__':
    db: Database = Database.load("data/var_exp/database.pkl")
    example: Example = db[0]
    print("[Method]\n", example.method, "\n")
    print("[Vars]\n", example.vars, "\n")

    print("[Predictions]")
    explainer = CodeT5VarExplainer()
    for var, exps in explainer.explain(example).items():
        print(var) 
        for predictions in exps:
            print(predictions)
        print()