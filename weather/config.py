import dataclasses
import json
import pathlib
import typing as t


@dataclasses.dataclass(kw_only=True, frozen=True)
class Config:
    meteomatics_username: str
    meteomatics_password: str
    positionstack_access_key: str

    @classmethod
    def _path(cls) -> pathlib.Path:
        return pathlib.Path(pathlib.Path.home(), ".weather/config.json")

    def save(self) -> None:
        self._path().parent.mkdir(parents=True, exist_ok=True)
        with open(self._path(), "w") as f:
            json.dump(dataclasses.asdict(self), f, indent=2)

    @classmethod
    def load(cls) -> t.Optional["Config"]:
        if not cls._path().exists():
            return None
        with open(cls._path()) as f:
            return cls(**json.load(f))
