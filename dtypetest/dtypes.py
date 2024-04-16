import pathlib
from typing import get_origin, get_args
from types import UnionType
import ast
from typing import Any
from dtypetest.type_checker import TypeChecker

class DTypes:
    """
    This is the main class of the package. It is used to get the AST of the entry file, assign function parameter types and then run the type checker.
    """
    def __init__(self, entry_file: str) -> None:
        """
        __init__ Gets and stores the AST of the entry file written in Python.

        :param entry_file: Path to the entry python file.
        :type entry_file: str
        """
        self.entry_file = entry_file
        # path to the entry file directory to parse other imported local python files
        self.entry_file_dir = pathlib.Path(entry_file).parent
        
        # get the AST of the entry file
        with open(entry_file, 'r') as f:
            self.ast = ast.parse(f.read())
            
        # go through all the local imports and get the AST of the imported files
        for node in ast.walk(self.ast):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_file = self.entry_file_dir / f"{alias.name}.py"
                    with open(imported_file, 'r') as f:
                        imported_ast = ast.parse(f.read())
                    self.ast.body.extend(imported_ast.body)
            elif isinstance(node, ast.ImportFrom):
                imported_file = self.entry_file_dir / f"{node.module}.py"
                with open(imported_file, 'r') as f:
                    imported_ast = ast.parse(f.read())
                self.ast.body.extend(imported_ast.body)
        
        # dictionary to store the type assignments of the functions
        self.type_assignments = {}

    def given(self, func_name: str, param_types: dict[str, Any], return_type: Any) -> None:
        """
        given Assigns the parameter types and return type to the function.

        :param func_name: Name of the function to assign types to.
        :type func_name: str
        :param param_types: Dictionary containing the parameter names and their types.
        :type param_types: dict[str, any]
        :param return_type: The return type of the function.
        :type return_type: any
        """
        # get the function node
        func_node = None
        for node in ast.walk(self.ast):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                func_node = node
                break
            
        if func_node is None:
            raise ValueError(f"Function {func_name} not found in the AST.")
        
        # check if the number of parameters match and their names match
        if len(func_node.args.args) != len(param_types):
            raise ValueError(f"Number of parameters in the function {func_name} do not match.")
        
        for arg_name, arg_type in param_types.items():
            if not any(arg.arg == arg_name for arg in func_node.args.args):
                raise ValueError(f"Parameter {arg_name} not found in the function {func_name}.")
            param_types[arg_name] = self._parse_arg_types(arg_type)
        
        # save the types of that function to the type_assignments dictionary
        self.type_assignments[func_name] = {
            'param_types': param_types,
            'return_type': self._parse_arg_types(return_type)
        }
        
    def _parse_arg_types(self, arg_types: set | list | str) -> set[str]:
        """
        _parse_arg_types Parses the argument types.

        :param arg_types: The argument types.
        :type arg_types: Any
        :return: The parsed argument types.
        :rtype: set[str]
        """
        arg_to_str = {
            int: 'int',
            str: 'str',
            float: 'float',
            bool: 'bool',
            None: 'None'
        }
        
        if isinstance(arg_types, str):
            return {arg_types}

        elif isinstance(arg_types, set) or isinstance(arg_types, list):
            arg_types = set(arg_types)
            for arg_type in arg_types:
                if arg_type not in arg_to_str and not isinstance(arg_type, str):
                    raise ValueError(f"Unsupported argument type: {arg_type}")
                if arg_type in arg_to_str:
                    arg_types.remove(arg_type)
                    arg_types.add(arg_to_str[arg_type]) # type: ignore

        elif arg_types in arg_to_str:
            return {arg_to_str[arg_types]}
        
        elif get_origin(arg_types) is UnionType:
            new_arg_types = set()
            for arg in get_args(arg_types):
                new_arg_types.update(self._parse_arg_types(arg))
            arg_types = new_arg_types
            
        else:
            raise ValueError(f"Unsupported argument type: {arg_types}")
                
        return arg_types
        
    def run(self) -> None:
        """
        run Runs the type checker on the entry file.
        """
        TypeChecker(self.ast, self.entry_file_dir, self.type_assignments).check_types()
        