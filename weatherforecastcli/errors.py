class AppError(Exception):
    ...


class ConfigError(AppError):
    ...


class MissingConfigError(ConfigError):
    ...


class CorruptedConfigError(ConfigError):
    ...


class GeocodingError(AppError):
    ...


class PositionstackError(GeocodingError):
    ...


class OpenmeteoError(AppError):
    ...
