from typing import Dict, Callable, Union
import os
import importlib
import logging
from functools import lru_cache
from os.path import splitext

from utils import ParserImport, ParserOutput, base_get_location
from parser_exceptions import *

logger = logging.getLogger(__name__)

PARSERS_ROOT = os.path.join(os.path.dirname(__file__), 'parsers')

def load_parser_from_module(filename: str, modulename: str):
    """Loads a parser from a given file in a given module
    Calls the get_parser() function in the module to so"""
    modfilename = modulename + '.' + splitext(filename)[0]
    module = importlib.import_module(modfilename)
    try:
        parser_import = module.get_parser()
        if type(parser_import) != ParserImport:
            logger.error(f'get_parser() function from file {filename} returned {type(parser_import)} object instead of expected ParserImport')
            return None
        return parser_import
    except AttributeError:
        logger.error(f'get_parser() function from file {filename} is not defined')
    except Exception as e:
        logger.exception(f'Could not import parser {filename}: {e}')


@lru_cache
def get_parsers(parsers_root: str) -> Dict[str, ParserImport]:
    """Loads parsers contained inside a given folder"""
    parsers = {}
    filenames = [filename for filename in os.listdir(parsers_root) if filename.endswith('.py') and '__' not in filename]
    for filename in filenames:
        parser_import = load_parser_from_module(filename, os.path.basename(parsers_root))
        if parser_import is not None:
            for ext in parser_import.extensions:
                if ext in parsers:
                    logger.warn(f'Conflict detected for {ext} extension. A parser was already declared for that extension, but was overwritten by {filename}')
                parsers[ext] = parser_import   
    return parsers


def parse_file(path: str, resource_id: int, user_id: int, get_location: Callable[[str, str, int, int], str]) -> Union[ParserOutput, None]:
    """Parses a file and returns the output"""
    parsers = get_parsers(PARSERS_ROOT)
    extension = os.path.basename(path).split('.')[-1]
    if extension not in parsers:
        raise NoParserError(path, extension)
    parser = parsers[extension].parser(path, resource_id, user_id, get_location)
    output = parser.parse()
    return output


if __name__ == '__main__':
    print(parse_file('test/test.pl', 0, 0, base_get_location))