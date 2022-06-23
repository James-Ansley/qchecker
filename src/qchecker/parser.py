import ast

import libcst


class CodeModule:
    __slots__ = ['ast', 'cst', 'code']

    def __init__(self, code):
        """
        Parses the code to be used by Substructures

        :raises SyntaxError: If the given code cannot be parsed.
        """
        self.code = code
        self.ast = ast.parse(code)
        try:
            self.cst = libcst.MetadataWrapper(libcst.parse_module(code))
        except libcst.ParserSyntaxError as e:
            raise SyntaxError from e
