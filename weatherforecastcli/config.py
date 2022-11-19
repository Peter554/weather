import json
import pathlib

import pydantic

import weatherforecastcli.errors as errors


APP_DIR = pathlib.Path(pathlib.Path.home(), ".weather")


class Config(pydantic.BaseModel):
    positionstack_access_key: str

    @classmethod
    def _path(cls) -> pathlib.Path:
        return pathlib.Path(APP_DIR, "config.json")

    def save(self) -> None:
        self._path().parent.mkdir(parents=True, exist_ok=True)
        with open(self._path(), "w") as f:
            json.dump(self.dict(), f, indent=2)

    @classmethod
    def load(cls) -> "Config":
        if not cls._path().exists():
            raise errors.MissingConfigError
        with open(cls._path()) as f:
            try:
                return cls.parse_obj(json.load(f))
            except pydantic.ValidationError as e:
                raise errors.CorruptedConfigError from e
