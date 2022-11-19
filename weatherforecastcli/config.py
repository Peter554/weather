import json
import pathlib
import typing as t

import pydantic


class ConfigError(Exception):
    ...


class MissingConfigError(ConfigError):
    ...


class CorruptedConfigError(ConfigError):
    ...


class Config(pydantic.BaseModel):
    positionstack_access_key: str

    @classmethod
    def _path(cls) -> pathlib.Path:
        return pathlib.Path(pathlib.Path.home(), ".weather/config.json")

    def save(self) -> None:
        self._path().parent.mkdir(parents=True, exist_ok=True)
        with open(self._path(), "w") as f:
            json.dump(self.dict(), f, indent=2)

    @classmethod
    def load(cls) -> "Config":
        if not cls._path().exists():
            raise MissingConfigError
        with open(cls._path()) as f:
            try:
                return cls.parse_obj(json.load(f))
            except pydantic.ValidationError as e:
                raise CorruptedConfigError from e
