import datetime
import json
import logging
import sys
from collections import OrderedDict
from typing import Any, Dict, List, Literal, MutableMapping, Tuple, TypeAlias
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger("root")

DEFAULT_LOG_RECORD_ATTRS = logging.LogRecord(
    name="", level=0, pathname="", lineno=0, msg="", args=None, exc_info=None
).__dict__
DEFAULT_LOG_RECORD_ATTRS.update(
    {
        "asctime": "",
        "message": "",
    }
)

TimeSpecType: TypeAlias = (
    Literal["auto"]
    | Literal["hours"]
    | Literal["minutes"]
    | Literal["seconds"]
    | Literal["milliseconds"]
    | Literal["microseconds"]
)
LogDataType: TypeAlias = MutableMapping[str, Any]


class SimpleFormatter(logging.Formatter):
    DEFAULT_FMT = "%(asctime)s %(message)s"

    def __init__(
        self,
        fmt: str = DEFAULT_FMT,
        timespec: TimeSpecType = "milliseconds",
        log_timezone: str | None = None,
    ):
        super().__init__()
        self.fmt = fmt
        self._fmt_keys = self._parse_fmt_keys()
        self.timespec = timespec
        try:
            timezone = (
                ZoneInfo(log_timezone) if log_timezone is not None else ZoneInfo("UTC")
            )
        except ZoneInfoNotFoundError:
            logger.exception("Wrong timezone: %s", log_timezone)
            sys.exit(1)
        self.log_timezone = timezone

    def _parse_fmt_keys(self) -> List[str]:
        keys = [
            key[2:-2]
            for key in self.fmt.split(" ")
            if key[2:-2] not in ["msg", "exc_info", "stack_info"]
        ]
        for key in keys:
            if key not in DEFAULT_LOG_RECORD_ATTRS:
                raise ValueError(f"Unknown format key: {key}")
        return keys

    def format(self, record: logging.LogRecord) -> str:
        log_entry = ""
        log_entry = self._set_main_keys(record, log_entry)
        log_entry, was_exception = self._set_exception_keys(record, log_entry)
        log_entry = self._set_extra_keys(record, log_entry, was_exception)
        return log_entry

    def _set_main_keys(self, record: logging.LogRecord, formatted: str) -> str:
        for key in self._fmt_keys:
            if key == "asctime":
                value = self._format_time(record)
            elif key == "message":
                value = record.getMessage()
            else:
                value = str(getattr(record, key))
            formatted += f"{value} "
        formatted = formatted[:-1]
        return formatted

    def _format_time(self, record: logging.LogRecord) -> str:
        d = datetime.datetime.fromtimestamp(record.created, tz=self.log_timezone)
        formatted_time = d.isoformat(timespec=self.timespec)
        return formatted_time

    def _set_exception_keys(
        self, record: logging.LogRecord, formatted: str
    ) -> Tuple[str, bool]:
        was_exception = False
        exc_info = record.exc_info
        if exc_info:
            if not was_exception:
                was_exception = True
            formatted += f"\n{self.formatException(exc_info)}"
        stack_info = record.stack_info
        if stack_info:
            if not was_exception:
                was_exception = True
            formatted += f"\n{self.formatStack(stack_info)}"
        return formatted, was_exception

    def _set_extra_keys(
        self, record: logging.LogRecord, formatted: str, was_exception: bool
    ) -> str:
        was_extra = False
        is_first = True
        for key, value in record.__dict__.items():
            if key not in DEFAULT_LOG_RECORD_ATTRS:
                if not was_extra:
                    was_extra = True
                if is_first:
                    if was_exception:
                        delimeter = "\n"
                    else:
                        delimeter = " "
                    formatted += delimeter
                    is_first = False
                formatted += f"{key}={str(value)} "
        if was_extra:
            formatted = formatted[:-1]
        return formatted


class JSONFormatter(logging.Formatter):
    DEFAULT_FMT_KEYS = {
        "asctime": "timestamp",
        "message": "message",
    }

    def __init__(
        self,
        fmt_keys: Dict[str, str] | None = None,
        timespec: TimeSpecType = "milliseconds",
        log_timezone: str | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else self.DEFAULT_FMT_KEYS
        self._check_fmt_keys()
        self.timespec = timespec
        try:
            timezone = (
                ZoneInfo(log_timezone) if log_timezone is not None else ZoneInfo("UTC")
            )
        except ZoneInfoNotFoundError:
            logger.exception("Wrong timezone: %s", log_timezone)
            sys.exit(1)
        self.log_timezone = timezone

    def _check_fmt_keys(self) -> None:
        for key, _ in self.fmt_keys.items():
            if key not in DEFAULT_LOG_RECORD_ATTRS:
                raise ValueError(f"Unknown format key: {key}")

    def format(self, record: logging.LogRecord) -> str:
        log_data: LogDataType = OrderedDict()
        log_data = self._set_main_keys(record, log_data)
        log_data = self._set_exception_keys(record, log_data)
        log_data = self._set_extra_keys(record, log_data)
        log_entry = json.dumps(log_data)
        return log_entry

    def _set_main_keys(
        self, record: logging.LogRecord, log_data: LogDataType
    ) -> LogDataType:
        for key, new_key in self.fmt_keys.items():
            if key in ["msg", "exc_info", "stack_info"]:
                continue
            if key == "asctime":
                value = self._format_time(record)
            elif key == "message":
                value = record.getMessage()
            else:
                value = str(getattr(record, key))
            log_data[new_key] = value
        return log_data

    def _format_time(self, record: logging.LogRecord) -> str:
        d = datetime.datetime.fromtimestamp(record.created, tz=self.log_timezone)
        formatted_time = d.isoformat(timespec=self.timespec)
        return formatted_time

    def _set_exception_keys(
        self, record: logging.LogRecord, log_data: LogDataType
    ) -> LogDataType:
        exc_info = record.exc_info
        if exc_info:
            new_key = self.fmt_keys.get("exc_info", None)
            new_key = new_key if new_key is not None else "excInfo"
            log_data[new_key] = self.formatException(exc_info)
        stack_info = record.stack_info
        if stack_info:
            new_key = self.fmt_keys.get("stack_info", None)
            new_key = new_key if new_key is not None else "stackInfo"
            log_data[new_key] = self.formatStack(stack_info)
        return log_data

    def _set_extra_keys(
        self, record: logging.LogRecord, log_data: LogDataType
    ) -> LogDataType:
        extra = OrderedDict()
        for key, value in record.__dict__.items():
            if key not in DEFAULT_LOG_RECORD_ATTRS:
                extra[key] = str(value)

        extra_key = "extra"
        log_data[extra_key] = extra
        return log_data
