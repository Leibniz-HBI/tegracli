"""Tegracli
Philipp Kessling, Leibniz-HBI, 2022
"""

from typing import Dict, List

import yaml


class Group(yaml.YAMLObject):
    """Manage group settings and members"""

    yaml_tag = "!tegracli.group.Group"

    def __init__(self, members: List[str], name: str, params: Dict) -> None:
        super().__init__()

        self.members = members or []
        self.name = name or "new_group"
        self.params = params or {}
