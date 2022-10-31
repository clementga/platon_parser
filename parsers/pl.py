# Trick to allow import of python modules in parent directoryn useful if running this file directly
if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Actual imports begin here
import re
import json
import os.path
from typing import NoReturn, List, Tuple
from ast import literal_eval
from unicodedata import name

import exceptions as excp
from baseparser import Parser
from parser_output import ParserOutput


BAD_CHAR = r''.join(['/', ' ', '\t', '\n', ';', '#', '+', '&'])

 # .pl grammar
KEY = r'^(?P<key>[a-zA-Z_][a-zA-Z0-9_\.]*)\s*'
COMMENT = r'(?P<comment>#.*)'
VALUE = r'(?P<value>[^=@%#][^#]*?)\s*'
FILE = r'(?P<file>([a-zA-Z0-9_]*:)?((\/)?[^' + \
    BAD_CHAR + r']+)(\/[^' + BAD_CHAR + r']+)*)\s*'
ALIAS = r'((\[\s*(?P<alias>[a-zA-Z_.][a-zA-Z0-9_.]*)\s*\])\s*?)?'

COMPONENT_LINE = re.compile(
    KEY + r'\s*(?P<operator>=:)\s*(?P<component>\w+)\s*' + COMMENT + r'?$')
URL_LINE = re.compile(
    KEY + r'(?P<operator>=\$)\s*' + FILE + COMMENT + r'?$')
ONE_LINE = re.compile(
    KEY + r'(?P<operator>=|\%|\+|\-)\s*' + VALUE + COMMENT + r'?$')
FROM_FILE_LINE = re.compile(
    KEY + r'(?P<operator>=@|\+=@|\-=@)\s*' + FILE + COMMENT + r'?$')
EXTENDS_LINE = re.compile(
    r'(extends|template)\s*=\s*' + FILE + COMMENT + r'?$')
MULTI_LINE = re.compile(
    KEY + r'(?P<operator>==|\+=|\-=|\%=)\s*' + COMMENT + r'?$')
SANDBOX_FILE_LINE = re.compile(r'@\s*' + FILE + ALIAS + COMMENT + r'?$')
END_MULTI_LINE = re.compile(r'==\s*$')
COMMENT_LINE = re.compile(r'\s*' + COMMENT + r'$')
EMPTY_LINE = re.compile(r'\s*$')

class PLParser(Parser):
    """Parser for .pl files"""

    def __init__(self, path: str, resource_id: int):
        self.path = path
        self.resource_id = resource_id
        self.output = ParserOutput(path, resource_id, 'pl')

        self.__current_line = ''
        self.__line_number = 1
        self.__in_multiline = False

    def parse(self) -> ParserOutput:
        """Parses the file and returns the corresponding output"""

        with open(self.path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines:
            self.__current_line = line
            self.parse_line(line)
            self.__line_number += 1

        return self.output

    def parse_line(self, line: str) -> NoReturn:
        """ Parse the given line by calling the appropriate method according to regex matches.

            Raises exceptions.ParserSyntaxError if the line wasn't match by any regex."""
        if self.__in_multiline:
            self.in_multi_line(line)
        elif ONE_LINE.match(line):
            self.one_line_match(ONE_LINE.match(line))
        elif MULTI_LINE.match(line):
            self.multi_line_match(MULTI_LINE.match(line))
        elif EXTENDS_LINE.match(line):
            self.extends_line_match(EXTENDS_LINE.match(line))
        elif FROM_FILE_LINE.match(line):
            self.from_file_line_match(FROM_FILE_LINE.match(line))
        elif URL_LINE.match(line):
            self.url_line_match(URL_LINE.match(line))
        elif COMPONENT_LINE.match(line):
            self.component_line_match(COMPONENT_LINE.match(line))
        elif SANDBOX_FILE_LINE.match(line):
            self.sandbox_file_line_match(
                self.SANDBOX_FILE_LINE.match(line))
        elif COMMENT_LINE.match(line):
            self.output.comments.append(COMMENT_LINE.match(line).group('comment'))
        elif EMPTY_LINE.match(line):
            return
        else:
            raise excp.ParserSyntaxError(self.path, line, self.__line_number, 'Line does not correspond to any defined pattern')
        
    def one_line_match(self, match: re.Match) -> NoReturn:
        """ Maps value to key if operator is '=',
            appends on existing key is operator is '+',
            prepends on existing key is operator is '-',
            Maps json.loads(value) if operator is '%'

            Raise exceptions.ParserSyntaxError:
                if no group 'value', 'key' or 'operator' was found
                if operator is '%' and value isn't a well formated json
        """
        value = match.group('value')
        key = match.group('key')
        op = match.group('operator')

        if op == '=':
            self.map_expression_to_key(key, value)
        elif op == '%':
            pass
        elif op == '+':
            pass
        elif op == '-':
            pass
        else:
            raise AssertionError

    def multi_line_match(self, match: re.Match, line: str) -> NoReturn:
        pass

    def in_multi_line(self, line: str) -> NoReturn:
        pass
    
    def extends_line_match(self, match: re.Match, line: str) -> NoReturn:
        pass

    def from_file_line_match(self, match: re.Match, line: str) -> NoReturn:
        pass

    def url_line_match(self, match: re.Match, line: str) -> NoReturn:
        pass
    
    def component_line_match(self, match: re.Match, line: str) -> NoReturn:
        pass

    def sandbox_file_line_match(self, match: re.Match, line: str) -> NoReturn:
        pass

    def map_expression_to_key(self, key: str, expr: str) -> NoReturn:
        """Evaluates expr like a Python expression and maps it to the corresponding key
        in the data section of the output. If the expression is invalid, it is mapped
        as a string directly"""
        try:
            namespace, nkey = get_namespace(self.output.data, key.split('.'))
        except TypeError as e:
            raise excp.ParserSemanticError(self.path, self.__current_line, self.__line_number, f'{key} does not correspond to a valid namespace')
        if nkey in namespace:
            self.output.warnings.append(f'Overwriting existing value {namespace[nkey]} at key {nkey}')
        try:
            namespace[nkey] = literal_eval(expr)
        except (ValueError, TypeError, SyntaxError):
            namespace[nkey] = expr
        

def get_namespace(d: dict, keys: List[str]) -> Tuple[dict, str]:
    """Navigates, and creates if necessary, subdictionaries in the order of
    the list of keys given and returns a tuple the last subdictionary found/created
    and the last key
    
    Raises TypeError if one of the namespaces is not a dictionary
    """
    for key in keys[:-1]:
        if type(d) != dict: raise TypeError(f'{d} is not a dictionary')
        if key not in d: d[key] = {}
        d = d[key]
    return d, keys[-1]