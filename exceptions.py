class ParserException(Exception):
    """Abstract exception used to subtype all parser exceptions"""
    pass

class ParserExceptionLine(ParserException):
    """Exception indicating the file, line and line number where the parsing exception happened"""
    def __init__(self, path: str, line: str, line_number: int, message: str):
        self.path = path
        self.line = line.strip()
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return f'{self.path} (line {self.line_number}): {self.message} in "{self.line}"'

class ParserSyntaxError(ParserExceptionLine):
    """Represents a syntax error in the parsed file"""
    def __init__(self, path: str, line: str, line_number: int, message: str = 'Syntax error'):
        super().__init__(path, line, line_number, message)

class ParserSemanticError(ParserExceptionLine):
    """Represents a semantic error in the parsed file"""
    def __init__(self, path: str, line: str, line_number: int, message: str = 'Semantic error'):
        super().__init__(path, line, line_number, message)

class ParserNotImplementedError(ParserExceptionLine):
    """Represents a non implemented feature in a parsed file"""
    def __init__(self, path: str, line: str, line_number: int, message: str = 'Not implemented error'):
        super().__init__(path, line, line_number, message)

class ParserFileNotFound(ParserExceptionLine):
    """Represents failure to resolve to a file path in a parsed file"""
    def __init__(self, path: str, line: str, line_number: int, message: str = 'File not found'):
        super().__init__(path, line, line_number, message)

class ParserComponentNotFound(ParserExceptionLine):
    """Represents failure to find a component"""
    def __init__(self, path: str, line: str, line_number: int, message: str = 'Component not found'):
        super().__init__(path, line, line_number, message)
