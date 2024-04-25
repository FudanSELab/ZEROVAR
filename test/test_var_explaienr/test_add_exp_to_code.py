'''
    Use ’pytest -q filename' to excute
'''
from var_exp.pseudo_param.codet5 import CodeT5VarExplainer


def test_add_exp_to_code():
    explainer = CodeT5VarExplainer()
    method = "public void test(){\nint a = 1;\nint b = c.d;\n}"
    vars = [
            {"name":"a", "line":2, "exp":["exp of a"]},
            {"name":"b", "line":3, "exp":["exp of b"]},
            {"name":"d", "line":3, "exp":["exp of d"]}
        ]
    commented_code = explainer.add_exp_to_code(method, vars)
    assert commented_code == \
        "public void test(){\n// exp of a\nint a = 1;\n// exp of b\n// exp of d\nint b = c.d;\n}\n",\
        "wrong result"


