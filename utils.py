from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple
from abc import ABC, abstractmethod

import os.path

def base_get_location(path_to_resolve: str, local_path: str, resource_id: int, user_id: int) -> str:
    """Simple get_location function, only manages "classic" absolute and relative paths"""
    if os.path.isabs(path_to_resolve):
        return path_to_resolve
    return os.path.abspath(os.path.join(local_path, path_to_resolve))


class Parser(ABC):
    """Abstract class representing a parser"""
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
    user_id: int
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