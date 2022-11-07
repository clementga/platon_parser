from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

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