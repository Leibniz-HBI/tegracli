"""Tegracli
Philipp Kessling, Leibniz-HBI, 2022
"""
from pathlib import Path
from typing import Dict, List, Optional

import ujson
import yaml

CONF_FILE_NAME = "tegracli_group.conf.yml"
PROF_FILE_NAME = "profiles.jsonl"


class Group(yaml.YAMLObject):
    """Manage group settings and members"""

    yaml_tag = "!tegracli.group.Group"

    def __init__(self, members: List[str], name: str, params: Dict) -> None:
        super().__init__()

        self.members = members or []
        self.unreachable_members = []
        self.name = name or "new_group"
        self.params = params or {}

        if not self._group_dir.exists():
            self._group_dir.mkdir()
        if not self._profiles_path.exists():
            self._profiles_path.touch()

    @property
    def _group_dir(self) -> Path:
        return Path(self.name)

    @property
    def _profiles_path(self) -> Path:
        return self._group_dir / PROF_FILE_NAME

    @property
    def _conf_path(self) -> Path:
        return self._group_dir / CONF_FILE_NAME

    def get_member_profile(self, member: str) -> Optional[Dict[str, str]]:
        """loads a user profile from disk

        Parameters
        ----------

        member : str : id or handle to load

        Returns
        -------
        Dict or None : user profile. if none is found returns None
        """
        with self._profiles_path.open("r") as profiles:
            for line in profiles.readlines():
                record = ujson.loads(line)  # pylint: disable=c-extension-no-member
                if record.get("id") == member or record.get("username") == member:
                    return record
        return None

    def get_params(self, **kwargs) -> Dict:
        """return an pimped params dict"""
        return dict(self.params, **kwargs)

    def get_last_message_for(self, member: str) -> int:
        """retrieves the last message for a member"""
        member_path = self._group_dir / (member + ".jsonl")
        if member_path.exists():
            with member_path.open("r") as file:
                ids = [
                    int(
                        ujson.loads(line)["id"]
                    )  # pylint: disable=c-extension-no-member
                    for line in file.readlines()
                ]
                if len(ids) != 0:
                    return max(ids)
        return 1

    def dump(self):
        """dump the configuration to disk"""
        with self._conf_path.open("w") as conf_file:
            yaml.dump(self, conf_file)