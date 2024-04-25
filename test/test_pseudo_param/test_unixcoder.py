from var_exp.common.database import Example, Database
from var_exp.pseudo_param.unixcoder import UniXcoderVarExplainer

if __name__ == '__main__':
    db: Database = Database.load("data/var_exp/database.pkl")
    example: Example = db[1]

    print("[Method]\n", example.method, "\n")
    print("[Vars]\n", example.vars, "\n")

    print("[Predictions]")
    explainer = UniXcoderVarExplainer()
    for var, exps in explainer.explain(example).items():
        print(var)
        for template, predictions in exps.items():
            print(repr(template), "\n", predictions,)
        print()
    