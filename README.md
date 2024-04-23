# dtypetest

## Description

This project introduces a Python library designed to enforce strict type annotations in Python codebases, including legacy systems where code modification is not feasible. Utilizing abstract syntax tree (AST) parsing, the library statically analyzes and infers types, aiming to enhance type safety and reduce runtime errors without altering original source codes. The approach supports external annotation of function parameters and return types, leveraging type inference to enforce type consistency across various Python versions. Initial testing indicates the library's effectiveness in identifying type mismatches, with future work focused on extending capabilities to handle more complex and undefined types. 


## Installation

We are working on uploading the project to PyPI. In the meantime, you can install the library by cloning the repository and running the following command:

```bash
git clone https://github.com/Prapti-044/dtypetest.git
cd dtypetest
pip install .
```

If you have poetry, you can also install the library using the following command:

poetry add git+https://github.com/Prapti-044/dtypetest.git

## Usage

To use the library, you can import the dtypetest module and use the class DType to parse the source code and provide type annotations. The following example demonstrates how to use the library to enforce type annotations in a Python script:

```python
# A sample python code
a = 10
b = 'hello'

def fun1(x: int):
  print(x)
  
def fun2(y):
  hello = 5
  fun1(y)
  y = 10
  
def main():
  a = 20
  fun2(a)
  fun2(b)
  fun1(10)
  fun1(fun2(10))
```
```python
# tests with dtypetest module
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
```