import ast
import pathlib
from typing import Any

class TypeChecker:
    """
    This is the class that is responsible for type inference for each variable and function call in the AST.
    """
    def __init__(self, code_ast: ast.AST, entry_file_dir: pathlib.Path, type_assignments: dict[str, dict[str, Any]]) -> None:
        """
        __init__ The constructor of the TypeChecker class.

        :param code_ast: The parsed AST of the entry file. This can be obtained using the ast.parse() function or from dtypes.DTypes.ast.
        :type code_ast: ast.AST
        :param entry_file_dir: The directory of the entry file. This is used to parse other local imported files.
        :type entry_file_dir: pathlib.Path
        :param type_assignments: The types assigned for different functions to test. This is the same as dtypes.DTypes.type_assignments.
        :type type_assignments: dict[str, dict[str, Any]]
        """
        self.ast = code_ast
        self.entry_file_dir = entry_file_dir
        self.type_assignments = type_assignments
        
        for node in ast.walk(self.ast):
            node.parent = None
        self._assign_parents(self.ast)
        
    def _assign_parents(self, node: ast.AST, parent: ast.AST = None) -> None:
        """
        _assign_parents Usually ast nodes do not have a parent attribute. This function assigns the parent attribute to each node in the AST. This helps in traversing the AST and finding parent nodes (e.g. which function I am currently in, etc.).

        :param node: The current ast node to assign the parent to.
        :type node: ast.AST
        :param parent: The parent of this node, defaults to None (root node).
        :type parent: ast.AST, optional
        """
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self._assign_parents(child, node)
    
    def _lookup_function_calls(self, func_name: str) -> list[ast.Call]:
        """
        _lookup_function_calls Identifies all the function calls in the AST with the given function name.

        :param func_name: The name of the function to look for in the AST.
        :type func_name: str
        :return: List of all the function calls in the AST with the given function name.
        :rtype: list[ast.Call]
        """
        calls: list[ast.Call] = []
        for node in ast.walk(self.ast):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func_name:
                calls.append(node)
        return calls
    
    def _lookup_function_def(self, func_name: str) -> ast.FunctionDef:
        """
        _lookup_function_def Finds the function definition node in the AST with the given function name.

        :param func_name: The name of the function to look for in the AST.
        :type func_name: str
        :raises ValueError: If the function is not found in the AST.
        :return: The function definition node in the AST with the given function name.
        :rtype: ast.FunctionDef
        """
        for node in ast.walk(self.ast):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return node
        raise ValueError(f"Function {func_name} not found in the AST.")

    def check_types(self) -> None:
        """
        check_types Run the whole type checking process. This function checks if the function calls are made with the correct arguments and if the return types are correct. Internally this function calls other functions (e.g. _evaluate_arg, _find_var_types, etc.) to do the type checking.
        """
        for func_name in self.type_assignments:
            func_calls = self._lookup_function_calls(func_name)
            for call in func_calls:
                # get the calling function node
                parent_func = None
                call_i = call
                while call_i and not isinstance(call_i, ast.FunctionDef):
                    call_i = call_i.parent
                parent_func = call_i

                func_def = self._lookup_function_def(func_name)
                args = {arg_def.arg: self._evaluate_arg(arg, parent_func) for arg, arg_def in zip(call.args, func_def.args.args)}
                
                for arg_name, arg_type in args.items():
                    # print(arg_type)
                    # print(self.type_assignments[func_name]['param_types'][arg_name])
                    assert 'any' in arg_type or arg_type.issubset(self.type_assignments[func_name]['param_types'][arg_name]), f"In line {call.lineno}, function {func_name} called with wrong arguments., expected {self.type_assignments[func_name]['param_types'][arg_name]}, got {arg_type}"

                # print(self._get_func_return_type(func_name))
                # print(self.type_assignments[func_name]['return_type'])
                assert 'any' in arg_type or self._get_func_return_type(func_name).issubset(self.type_assignments[func_name]['return_type']), f"In line {call.lineno}, function {func_name} returned wrong type, expected {self.type_assignments[func_name]['return_type']}, got {self._get_func_return_type(func_name)}"


    def _evaluate_arg(self, arg: ast.expr, parent_func: ast.FunctionDef | None) -> set[str]:
        """
        _evaluate_arg Tries to find the type of an expression in the AST.

        :param arg: The expression to find the type of.
        :type arg: ast.expr
        :param parent_func: The parent function of the expression. This is used to find the type of the variables in the function.
        :type parent_func: ast.FunctionDef | None
        :raises ValueError: If the type of the expression is not supported.
        :return: The inferred type of the expression.
        :rtype: set[str]
        """
        if isinstance(arg, ast.Constant):
            return {self._get_constant_type(arg.value)}
        elif isinstance(arg, ast.Name):
            return self._find_var_type(arg.id, arg.lineno, parent_func)
        elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
            return self._get_func_return_type(arg.func.id)
        else:
            raise ValueError(f"Unsupported variable type: {type(arg)}")
    

    def _get_constant_type(self, value: Any) -> str:
        """
        _get_constant_type Returns the type of the constant value. All python build-in types are supported and custom class objects are also supported.

        :param value: The constant value to find the type of. This is usually the value attribute of the ast.Constant node.
        :type value: Any
        :raises ValueError: If the type of the constant is not supported.
        :return: The type of the constant value.
        :rtype: str
        """
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, bool):
            return 'bool'
        elif value is None:
            return 'None'
        elif isinstance(value, bytes):
            return 'bytes'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, tuple):
            return 'tuple'
        elif isinstance(value, dict):
            return 'dict'
        elif isinstance(value, set):
            return 'set'
        elif isinstance(value, frozenset):
            return 'frozenset'
        elif isinstance(value, complex):
            return 'complex'
        elif isinstance(value, range):
            return 'range'
        elif isinstance(value, slice):
            return 'slice'
        elif isinstance(value, memoryview):
            return 'memoryview'
        elif isinstance(value, type):
            return 'type'
        elif isinstance(value, object):
            return 'object'
        elif isinstance(value, type(None)):
            return 'NoneType'
        else:
            raise ValueError(f"Unsupported constant type: {type(value)}")
        
    def _get_func_return_type(self, func_name: str) -> set[str]:
        """
        _get_func_return_type Returns the possible return types of a function.

        :param func_name: The name of the function to find the return types of.
        :type func_name: str
        :raises ValueError: If the function is not found in the AST.
        :return: The possible return types of the function.
        :rtype: set[str]
        """
        func_node = None
        for node in ast.walk(self.ast):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                func_node = node
                break
        
        if not func_node:
            # check if the function is a constructor of a class
            for node in ast.walk(self.ast):
                if isinstance(node, ast.ClassDef) and node.name == func_name:
                    return {func_name}

        if not func_node:
            raise ValueError(f"Function {func_name} not found in the AST.")
        
        # get all the return statements in the function
        return_stmts = [stmt for stmt in func_node.body if isinstance(stmt, ast.Return)]
        if not return_stmts:
            return {'None'}
        
        possible_returns = set()
        # get the return types of the function
        for stmt in return_stmts:
            if isinstance(stmt.value, ast.Constant):
                possible_returns.add(self._get_constant_type(stmt.value.value))
            elif isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                called_func_name = stmt.value.func.id
                possible_returns.add(self._get_func_return_type(called_func_name))
        
        # check if the function ends without a return statement
        if len(func_node.body) > return_stmts[-1].lineno:
            if len(func_node.body) > return_stmts[-1].lineno:
                possible_returns.add('None')
            
        return possible_returns


    def _find_var_type(self, var_name: str, start_line: int, func_node: ast.FunctionDef | None) -> set[str]:
        """
        _find_var_type Finds the type of a variable in the AST. As python is a dynamically typed language, this function tries to infer the type of the variable by looking at the assignments and function calls.

        :param var_name: The name of the variable to find the type of.
        :type var_name: str
        :param start_line: The line number where the variable's type is to be inferred. This is required as the same variable's type can change in different parts of the code. This function starts from the start_line and goes up to find the type of the variable from its assignments. However, the type can often not be possible to infer. For example, if the variable is assigned in a loop (both as an iterator or inside the loop), the type of the variable cannot be inferred. Or if the variables type is totally determined at runtime. The library never infers variable types from annotations. It only infers from the code itself.
        :type start_line: int
        :param func_node: The function ast node where the variable is used. None if the line is not inside a function.
        :type func_node: ast.FunctionDef | None
        :raises ValueError: If the variable or the parent function is not found in the AST.
        :return: The inferred type of the variable.
        :rtype: set[str]
        """
        for stmt in reversed(func_node.body if func_node else self.ast.body):
            if stmt.lineno > start_line:
                continue
            if isinstance(stmt, ast.Assign) and any(isinstance(target, ast.Name) and target.id == var_name for target in stmt.targets):
                if isinstance(stmt.value, ast.Constant):
                    return {self._get_constant_type(stmt.value.value)}
                elif isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                    called_func_name = stmt.value.func.id
                    return self._get_func_return_type(called_func_name)
            # see if variable is coming as iterator of loop
            elif isinstance(stmt, ast.For) and (isinstance(stmt.iter, ast.List) or isinstance(stmt.iter, ast.Tuple) or isinstance(stmt.iter, ast.Set)):
                return set(['any'])

        # var_name could not be inferred from function body, check if it is a parameter
        possible_types = set()
        if func_node is not None:
            param_pos = None
            for i, arg in enumerate(func_node.args.args):
                if arg.arg == var_name:
                    param_pos = i
                    break
            if param_pos is not None:
                parent_calls = self._lookup_function_calls(func_node.name)
                for call in parent_calls:
                    parent_parent = None
                    call_i = call
                    while not isinstance(call_i, ast.FunctionDef):
                        call_i = call_i.parent
                    parent_parent = call_i
                    
                    if len(call.args) > param_pos:
                        possible_types |= self._evaluate_arg(call.args[param_pos], parent_parent)
                    else:
                        raise ValueError(f"Parameter {var_name} not found in parent function call {parent_parent.name}")

        if func_node is None or param_pos is None:
            possible_types |= self._find_global_var_type(var_name, start_line)
        
        if possible_types:
            return possible_types
        else:
            raise ValueError(f"Parameter {var_name} could not be inferred from function {func_node.name}")
        
        
    def _find_global_var_type(self, var_name: str, start_line: int) -> set[str]:
        """
        _find_global_var_type Finds the type of a global variable in the AST. This is called if the variable assignment is not found in any function scope. That means that the variable is initialized at the global scope (outside any function).

        :param var_name: The name of the variable to find the type of.
        :type var_name: str
        :param start_line: The line number where the variable is used. This is similar to the start_line parameter in :meth:`dtypetests.type_checker.TypeChecker._find_var_type`.
        :type start_line: int
        :raises ValueError: If the variable is not found in the AST.
        :return: The inferred type of the variable.
        :rtype: set[str]
        """
        for stmt in reversed(self.ast.body):
            if stmt.lineno > start_line:
                continue
            if isinstance(stmt, ast.Assign) and any(isinstance(target, ast.Name) and target.id == var_name for target in stmt.targets):
                if isinstance(stmt.value, ast.Constant):
                    return {type(stmt.value.value).__name__}
                elif isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                    return self._evaluate_arg(stmt.value, None)
                
        raise ValueError(f"Variable {var_name} not found in the AST.")


