import pytest
from dtypetest.dtypes import DTypes

@pytest.fixture
def simple_ast_obj():
    return DTypes('tests/simple.py')

def test_simple_fun1(simple_ast_obj: DTypes):
    simple_ast_obj.given('fun1', {'x': int}, None)
    with pytest.raises(AssertionError) as e_info:
        simple_ast_obj.run()

def test_simple_fun2(simple_ast_obj: DTypes):
    simple_ast_obj.given('fun2', {'y': [int, str]}, None)
    simple_ast_obj.given('fun2', {'y': int | str}, [None])
    simple_ast_obj.given('fun2', {'y': ['int', 'str']}, 'None')
    simple_ast_obj.run()
    
def test_simple_fun2_wrong_argname(simple_ast_obj: DTypes):
    with pytest.raises(ValueError) as e_info:
        simple_ast_obj.given('fun2', {'a': 'int'}, 'int')
        simple_ast_obj.run()

@pytest.fixture
def class_ast_obj():
    return DTypes('tests/class.py')

def test_class_fun1(class_ast_obj: DTypes):
    class_ast_obj.given('fun1', {'x': ['A', 'C', int]}, None)
    class_ast_obj.run()

def test_class_fun2(class_ast_obj: DTypes):
    class_ast_obj.given('fun2', {'x': ['B', 'C']}, ['B', 'C'])
    class_ast_obj.run()


def test_dynamic_for_fun1():
    d = DTypes('tests/dynamic_for_types.py')
    d.given('fun1', {'x': [int, str, float]}, None)
    d.run()