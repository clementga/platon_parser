from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple, Callable
from abc import ABC, abstractmethod
from io import StringIO
import os.path

def base_get_location(uri: str, working_directory: str, resource_id: int, circle_id: int) -> LocationResult:
    """Simple get_location function, URIs are simple file paths, nothing else"""
    result = LocationResult()
    if os.path.isabs(uri):
        result.path = uri
    else:
        result.path = os.path.abspath(os.path.join(working_directory, uri))
    if not os.path.exists(result.path): return None
    result.file_handle = open(result.path, 'r')
    return result

class Parser(ABC):
    """Abstract class representing a parser"""
    @abstractmethod
    def __init__(self, file_handle: StringIO, path: str, resource_id: int, circle_id: int, get_location: Callable[[str, str, int, int], str], 
                 inherited=tuple(), check_mandatory_keys=True):
        """
        file_handle: TextIO object for reading the file
        path: path to the file, used as a unique identifier for things such as logging, or inheritance loop detection
        resource_id: id of the resource the file is in
        circle_id: id of the circle the file is in
        get_location: method used to obtain the file corresponding to an URI
        inherited: tuple containing the chain of inheritance that lead here
        check_mandatory_keys: boolean indicating if the keys that must be defined in a final PL file should be checked for or not
        """
        pass

    @abstractmethod
    def parse(self) -> ParserOutput:
        """Parses the file and returns the output of that parse"""
        pass


@dataclass
class ParserOutput:
    """Represents the output of a parser"""
    # Metadata
    path: str
    resource_id: int
    circle_id: int
    format: str
    dependencies: Set[Tuple[str, str]] = field(default_factory=set) # Tuples (path, alias)
    comments: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)


    def merge_output(self, output: ParserOutput):
        """Merge an output into current output"""
        self.dependencies |= output.dependencies
        self.comments.extend(output.comments)
        self.warnings.extend(output.warnings)
        recursive_update(self.data, output.data)

@dataclass
class LocationResult:
    """Represents the output of a get_location function"""
    file_handle: StringIO = None
    path: str = None
    resource_id: int = -1
    circle_id: int = -1


def recursive_update(curr_dict: dict, merge_dict: dict):
    """Recursively updates a nested dictionary with another"""
    for key, value in merge_dict.items():
        if key not in curr_dict:
            curr_dict[key] = value
        else:
            if type(value) == dict and type(curr_dict[key]) == dict:
                recursive_update(curr_dict[key], value)
            else:
                curr_dict[key] = value


@dataclass
class ParserImport:
    """Used to import a parser from a file"""
    parser: type[Parser]
    file_type: str
    extensions: Tuple[str]