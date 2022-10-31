class ParserException(Exception):
    """Abstract exception used to subtype all parser exceptions"""
    pass

class ParserExceptionLine(ParserException):
    """Exception indicating the file, line and line number where the parsing exception happened"""
    def __init__(self, path: str, line: str, line_number: int, message: str):
        self.path = path
        self.line = line
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return f'{self.path} (line {self.line_number}): {self.message} in "{self.line}"'

class ParserSyntaxError(ParserExceptionLine):
    """Exception repreesnting a syntax error in the parsed file"""
    def __init__(self, path: str, line: str, line_number: int, message: str = 'Syntax error'):
        super().__init__(path, line, line_number, message)

class ParserSemanticError(ParserExceptionLine):
    """Exception repreesnting a semantic error in the parsed file"""
    def __init__(self, path: str, line: str, line_number: int, message: str = 'Semantic error'):
        super().__init__(path, line, line_number, message)