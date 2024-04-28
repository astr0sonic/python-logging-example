import logging
from pathlib import Path

from adapters import CustomLoggerAdapter
from log_configuration import configure_logging

logger = logging.getLogger("my_app")

base_dir = Path().absolute()
configure_logging(base_dir=base_dir, level=logging.DEBUG)

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

adapter = CustomLoggerAdapter(logger, extra={"foo": "bar", "bar": "baz"})
adapter.debug("logger adapter testing", extra={"key1": "value2"})
