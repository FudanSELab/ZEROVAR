'''
    Using "pytest -q test_re_pattern.py" to excute
'''
import regex as re

from common.config import PARAM_EXP_PATTERN

def test_normal():
    doc = "xxxx.\n@param a explanation of a\n@param b explanation of b"
    res = re.findall(PARAM_EXP_PATTERN, doc)
    assert len(res) == 2
    assert res[0][0] == 'a'
    assert res[0][1] == 'explanation of a'
    assert res[1][0] == 'b'
    assert res[1][1] == 'explanation of b'

def test_newline_between_var_and_exp():
    doc = "xxxx\n@param a\nexplanation of a\n@param b explanation of b"
    res = re.findall(PARAM_EXP_PATTERN, doc)
    assert len(res) == 2
    assert res[0][0] == 'a'
    assert res[0][1] == 'explanation of a'
    assert res[1][0] == 'b'
    assert res[1][1] == 'explanation of b'

def test_no_exp_with_blank():
    doc = "xxxx\n@param a \n@param b "
    res = re.findall(PARAM_EXP_PATTERN, doc)
    assert len(res) == 2
    assert res[0][0] == 'a'
    assert res[0][1] == ''
    assert res[1][0] == 'b'
    assert res[1][1] == ''

# def test_no_exp_without_blank():
#     doc = "xxxx\n@param a\n@param b"
#     res = re.findall(PARAM_EXP_PATTERN, doc|re.ASCII)
#     assert len(res) == 2
#     assert res[0][0] == 'a'
#     assert res[0][1] == ''
#     assert res[1][0] == 'b'
#     assert res[1][1] == ''

def test_exp_with_newline():
    doc = "xxxx\n@param a explanation \nof a\n@param b explanation of b"
    res = re.findall(PARAM_EXP_PATTERN, doc)
    assert len(res) == 2
    assert res[0][0] == 'a'
    assert res[0][1] == 'explanation \nof a'
    assert res[1][0] == 'b'
    assert res[1][1] == 'explanation of b'

def test_exp_in_other_language():
    doc = "xxxx.\n@param a 参数a\n@param b の"
    res = re.findall(PARAM_EXP_PATTERN, doc)
    assert len(res) == 0

def test_exp_with_punc():
    doc = "xxxx.\n@param a ~`!@#$%^&*()_+-={[}]|\\\"\':;<>,.?/"
    res = re.findall(PARAM_EXP_PATTERN, doc)
    assert len(res) == 1
    assert res[0][0] == 'a'
    assert res[0][1] == '~`!@#$%^&*()_+-={[}]|\\\"\':;<>,.?/'

