import logging
import logging.handlers
import sys

from formatters import JSONFormatter, SimpleFormatter

logger = logging.getLogger("my_app")

console_handler = logging.StreamHandler(stream=sys.stdout)
formatter = SimpleFormatter(fmt="%(asctime)s %(message)s")
console_handler.setFormatter(formatter)

file_handler = logging.handlers.RotatingFileHandler("app.log")
json_formatter = JSONFormatter(
    fmt_keys={"asctime": "timestamp", "message": "message"},
)
file_handler.setFormatter(json_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel(level=logging.DEBUG)

logger.info("info message without extra")
logger.info("info message", extra={"foo": "foo"})

foo = 1
bar = 0
try:
    baz = foo / bar
except ZeroDivisionError:
    logger.exception("zero division", extra={"foo": foo, "bar": bar})
    baz = 0

print(baz)
