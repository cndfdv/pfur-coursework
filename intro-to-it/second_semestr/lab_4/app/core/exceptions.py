class BaseAppError(Exception):
    """Базовое исключение приложения."""


class DataFormatError(BaseAppError):
    """Ошибка структуры или формата входного файла."""


class ValidationError(BaseAppError):
    """Запись не прошла бизнес-валидацию."""


class CurrencyMismatchError(BaseAppError):
    """В одном отчёте встречены разные валюты без конвертации."""
