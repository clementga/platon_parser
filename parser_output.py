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