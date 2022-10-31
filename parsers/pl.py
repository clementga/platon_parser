# Trick to allow import of python modules in parent directory, useful if running this file directly
if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Actual imports begin here
import re
import json
import os.path
from typing import NoReturn, List, Tuple, Callable
from ast import literal_eval
from dataclasses import dataclass

import exceptions as excp
from baseparser import Parser
from parser_output import ParserOutput


from components import COMPONENT_SELECTORS


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
    KEY + r'(?P<operator>=@|\+=@|\-=@|\%=@)\s*' + FILE + COMMENT + r'?$')
EXTENDS_LINE = re.compile(
    r'(extends|template)\s*=\s*' + FILE + COMMENT + r'?$')
MULTI_LINE = re.compile(
    KEY + r'(?P<operator>==|\+=|\-=|\%=)\s*' + COMMENT + r'?$')
DEPENDENCY_FILE_LINE = re.compile(r'@\s*' + FILE + ALIAS + COMMENT + r'?$')
END_MULTI_LINE = re.compile(r'==\s*$')
COMMENT_LINE = re.compile(r'\s*' + COMMENT + r'$')
EMPTY_LINE = re.compile(r'\s*$')

class PLParser(Parser):
    """Parser for .pl files"""
    @dataclass
    class Multiline():
        """Used to keep information about multiline parsing status"""
        ongoing: bool = False
        current_key: str = None
        current_op: str = None
        current_value: any = None
        starting_line: str = None
        starting_line_number: int = 0


    def __init__(self, path: str, resource_id: int, user_id: int, get_location: Callable[[str, str, int, int], str]):
        self.path = path
        self.dir, self.filename = os.path.split(path)
        self.resource_id = resource_id
        self.user_id = user_id
        self.get_location = get_location
        self.output = ParserOutput(path, resource_id, user_id, 'pl')

        self.__current_line = ''
        self.__line_number = 1
        self.__multiline = PLParser.Multiline()


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
        """
        Parse the given line by calling the appropriate method according to regex matches.

        Raises exceptions.ParserSyntaxError if the line wasn't match by any regex.
        """
        if self.__multiline.ongoing:
            if END_MULTI_LINE.match(line):
                self.end_multi_line()
            else:
                self.__multiline.current_value += line[:-1]
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
        elif DEPENDENCY_FILE_LINE.match(line):
            self.dependency_line_match(DEPENDENCY_FILE_LINE.match(line))
        elif COMMENT_LINE.match(line):
            self.output.comments.append(COMMENT_LINE.match(line).group('comment'))
        elif EMPTY_LINE.match(line):
            return
        else:
            raise excp.ParserSyntaxError(self.path, line, self.__line_number, 'Line does not correspond to any defined pattern')
        

    def one_line_match(self, match: re.Match) -> NoReturn:
        """ 
        Maps value to key if operator is '=',
            appends on existing key is operator is '+',
            prepends on existing key is operator is '-',
            Maps json.loads(value) if operator is '%'

        Raise exceptions.ParserSyntaxError:
            if no group 'value', 'key' or 'operator' was found
            if operator is '%' and value isn't a well formated json
        """
        def map_value(n, k, v): n[k] = v
        def append_value(n, k, v): n[k] += v
        def prepend_value(n, k, v): n[k] = v + n[k]

        value = match.group('value')
        key = match.group('key')
        op = match.group('operator')

        if op == '=':
            self.apply_expression_to_key(key, value, map_value)
        elif op == '%':
            try:
                self.apply_expression_to_key(key, json.loads(value), map_value)
            except json.decoder.JSONDecodeError:
                raise excp.ParserSyntaxError(self.path, self.__current_line, self.__line_number, 'Line does not correspond to a valid JSON format.')
        elif op == '+':
            self.apply_expression_to_key(key, value, append_value, key_must_exist=True)
        elif op == '-':
            self.apply_expression_to_key(key, value, prepend_value, key_must_exist=True)
        else:
            raise AssertionError


    def multi_line_match(self, match: re.Match) -> NoReturn:
        """
        Starts the proecss for matching a whole multiline block
        """
        key = match.group('key')
        op = match.group('operator')

        self.__multiline.ongoing = True
        self.__multiline.current_key = key
        self.__multiline.current_op = op
        self.__multiline.current_value = ''
        self.__multiline.starting_line_number = self.__line_number
        self.__multiline.starting_line = self.__current_line


    def end_multi_line(self) -> NoReturn:
        """
        Evaluates the complete multiline value and does the action given by the operator:
            == : maps value to key
            += : appends value to key
            -= : prepends value to key
            %= : interprets value as JSON and maps to key
        """
        def map_value(n, k, v): n[k] = v
        def append_value(n, k, v): n[k] += v
        def prepend_value(n, k, v): n[k] = v + n[k]

        op = self.__multiline.current_op
        key = self.__multiline.current_key
        value = self.__multiline.current_value

        if op == '==':
            self.apply_expression_to_key(key, value, map_value)
        elif op == '%=':
            try:
                self.apply_expression_to_key(key, json.loads(value), map_value)
            except json.decoder.JSONDecodeError:
                raise excp.ParserSyntaxError(self.path, value, self.__multiline.starting_line_number, 'Multiline does not correspond to a valid JSON format.')
        elif op == '+=':
            self.apply_expression_to_key(key, value, append_value, key_must_exist=True)
        elif op == '-=':
            self.apply_expression_to_key(key, value, prepend_value, key_must_exist=True)
        else:
            raise AssertionError
        
        self.__multiline.ongoing = False

    
    def extends_line_match(self, match: re.Match) -> NoReturn:
        """
        Inheritance
        """
        pass


    def from_file_line_match(self, match: re.Match) -> NoReturn:
        """
        Loads file content into key
        """
        def map_value(n, k, v): n[k] = v
        def append_value(n, k, v): n[k] += v
        def prepend_value(n, k, v): n[k] = v + n[k]

        key = match.group('key')
        op = match.group('operator')
        path = self.get_path(match.group('file'))

        with open(path, 'r') as file:
            value = file.read()
            if op == '=@':
                self.apply_expression_to_key(key, value, map_value)
            elif op == '%=@':
                try:
                    self.apply_expression_to_key(key, json.loads(value), map_value)
                except json.decoder.JSONDecodeError:
                    raise excp.ParserSyntaxError(self.path, self.__current_line, self.__line_number, 'File does not correspond to a valid JSON format.')
            elif op == '+=@':
                self.apply_expression_to_key(key, value, append_value, key_must_exist=True)
            elif op == '-=@':
                self.apply_expression_to_key(key, value, prepend_value, key_must_exist=True)
            else:
                raise AssertionError


    def url_line_match(self, match: re.Match) -> NoReturn:
        """Not implemented"""
        raise excp.ParserNotImplementedError('Import from URL is not implemented currently')
    

    def component_line_match(self, match: re.Match) -> NoReturn:
        pass


    def dependency_line_match(self, match: re.Match) -> NoReturn:
        """
        Adds a file to the dependencies to load in the sandbox environnement
        """
        path = self.get_path(match.group('file'))

        alias = match.group('alias') or os.path.basename(path)
        self.output.dependencies.add((path, alias))


    def apply_expression_to_key(self, key: str, expr: str, apply: Callable[[str, str, any], NoReturn], key_must_exist:bool=False) -> NoReturn:
        """Evaluates expr like a Python expression and applies it to the corresponding key
        in the data section of the output using the given callable. If the expression is invalid, it is evaluated
        as a string directly
        
        Raises exceptions.ParserSemanticError if the key is expected to already exist and it doesn't
        """
        line_number = self.__line_number if not self.__multiline.ongoing else self.__multiline.starting_line_number
        current_line = self.__current_line if not self.__multiline.ongoing else self.__multiline.starting_line

        try:
            namespace, nkey = get_namespace(self.output.data, key.split('.'))
        except TypeError:
            raise excp.ParserSemanticError(self.path, current_line, line_number, f'{key} does not correspond to a valid namespace')
        if nkey in namespace:
            self.output.warnings.append(f'Overwriting existing value {namespace[nkey]} at key {nkey}')
        if key_must_exist and key not in namespace: 
            raise excp.ParserSemanticError(self.path, current_line, line_number, f'{key} does not already exist')
        try:
            value = literal_eval(expr)
        except (ValueError, TypeError, SyntaxError):
            value = expr
        apply(namespace, nkey, value)

    def get_path(self, path: str):
        """Finds real path to a file given pl path"""
        path = self.get_location(path, self.dir, self.resource_id, self.user_id)
        if not path: raise excp.ParserFileNotFound(self.path, self.__current_line, self.__line_number, 'File path could not be resolved')
        return path
  

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
    if type(d) != dict: raise TypeError(f'{d} is not a dictionary')
    return d, keys[-1]


if __name__ == '__main__':
    pass