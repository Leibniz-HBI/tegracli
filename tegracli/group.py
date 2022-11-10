"""Tegracli
Philipp Kessling, Leibniz-HBI, 2022
"""
from datetime import datetime, timedelta
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
        self.unreachable_members: List[Dict[str, str]] = []
        self.name = name or "new_group"
        self.params = params or {}
        self.error_state = {}

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

    def get_error_state(self, slot: str) -> bool:
        """get the error state for a API method"""
        if not self.error_state:
            self.error_state = {}
        state = self.error_state.get(slot)
        if state:
            endtime = state.get("endtime")
            if endtime:
                return datetime.now() <= datetime.fromtimestamp(endtime)
        return False

    def set_error_state(self, slot: str, period: int) -> None:
        """set the error state for the specified API method"""
        error_period_end = datetime.now() + timedelta(seconds=period)
        if not self.error_state:
            self.error_state = {}
        self.error_state[slot] = {"endtime": error_period_end.timestamp()}
        self.dump()

    def get_member_profile(self, member: str) -> Optional[Dict[str, str]]:
        """loads a user profile from disk

        Parameters
        ----------

        member : str : id or handle to load

        Returns
        -------
        Dict or None : user profile. if none is found returns None
        """
        _member = (
            int(member) if str.isnumeric(member) else member
        )  # cast id to int, so telethon
        # retrieves it from it's DB rather then bothering telegram's API.
        with self._profiles_path.open("r") as profiles:
            for line in profiles:
                record: Dict[str, str] = ujson.loads(
                    line
                )  # pylint: disable=c-extension-no-member
                if record.get("id") == _member or record.get("username") == _member:
                    return record
        return None

    def update_member(self, member: str, new_value: str):
        """update the entry for a member

        params:
          member: str:
            the member to update
          new_value: str:
            the new value

        returns:
          Nothing, nada, nope.
        """
        try:
            index = self.members.index(member)
        except ValueError:
            # nothing to do, just quit
            return
        self.members[index] = new_value

    def get_params(self, **kwargs) -> Dict:
        """return an pimped params dict"""
        return dict(self.params, **kwargs)

    def get_last_message_for(self, member: str) -> Optional[int]:
        """retrieves the last message for a member"""
        member_path = self._group_dir / (member + ".jsonl")
        if member_path.exists():
            with member_path.open("r") as file:
                ids = [
                    int(
                        ujson.loads(line)["id"]
                    )  # pylint: disable=c-extension-no-member
                    for line in file
                ]
                if len(ids) != 0:
                    return max(ids)
        return None

    def retry_all_unreachable(self):
        """put all unreachable accounts back into the active members"""
        self.members = [*self.members, *self.unreachable_members]
        self.unreachable_members = []

    def mark_member_unreachable(self, member: str, reason: str) -> None:
        """move a member to the unreachable list"""
        if member in self.members:
            self.members.remove(member)
            self.unreachable_members.append({"member": member, "reason": reason})

    def dump(self):
        """dump the configuration to disk"""
        with self._conf_path.open("w") as conf_file:
            yaml.dump(self, conf_file)
