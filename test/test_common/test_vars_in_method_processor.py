'''
    Use "pytest -q [filename] to execute
'''

from common.dataprocessor.vars_in_method_processor import VarsInMethodProcessor
def test_get_all_variables():
    method = "public void test(){\nint a = 1;\nint b = c.d;\n}"
    processor = VarsInMethodProcessor()
    vars = processor.get_all_variables(method)
    assert(len(vars.items())==3)
    assert(vars["a"]==2)
    assert(vars["b"]==3)
    assert(vars["d"]==3)