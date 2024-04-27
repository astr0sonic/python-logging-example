import datetime
import logging
from typing import List, Literal, Tuple
from zoneinfo import ZoneInfo

DEFAULT_LOG_RECORD_ATTRS = logging.LogRecord(
    name="", level=0, pathname="", lineno=0, msg="", args=None, exc_info=None
).__dict__
DEFAULT_LOG_RECORD_ATTRS.update(
    {
        "asctime": "",
        "message": "",
    }
)

TimeSpecType = (
    Literal["auto"]
    | Literal["hours"]
    | Literal["minutes"]
    | Literal["seconds"]
    | Literal["milliseconds"]
    | Literal["microseconds"]
)


class SimpleFormatter(logging.Formatter):
    DEFAULT_FMT = "%(message)s"

    def __init__(
        self,
        fmt: str = DEFAULT_FMT,
        timespec: TimeSpecType = "milliseconds",
        log_timezone: ZoneInfo = ZoneInfo("UTC"),
    ):
        super().__init__()
        self.fmt = fmt
        self._fmt_keys = self._parse_fmt_keys()
        self.timespec = timespec
        self.log_timezone = log_timezone

    def _parse_fmt_keys(self) -> List[str]:
        keys = [key[2:-2] for key in self.fmt.split(" ")]
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
            elif key in ["message", "msg"]:
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
            was_exception = True
            formatted += f"\n{self.formatException(exc_info)}"
        stack_info = record.stack_info
        if stack_info:
            was_exception = True
            formatted += f"\n{self.formatStack(stack_info)}"
        return formatted, was_exception

    def _set_extra_keys(
        self, record: logging.LogRecord, formatted: str, was_exception: bool
    ) -> str:
        is_first = True
        for key, value in record.__dict__.items():
            if key not in DEFAULT_LOG_RECORD_ATTRS:
                if is_first:
                    if was_exception:
                        delimeter = "\n"
                    else:
                        delimeter = " "
                    formatted += delimeter
                    is_first = False
                formatted += f"{key}={str(value)} "
        formatted = formatted[:-1]
        return formatted
