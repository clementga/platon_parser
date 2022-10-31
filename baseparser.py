from abc import ABC, abstractmethod
from parser_output import ParserOutput

class Parser(ABC):
    """Abstract class representing a parser"""
    @abstractmethod
    def parse(self) -> ParserOutput:
        """Parses the file and returns the output of that parse"""
        pass