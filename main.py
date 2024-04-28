import logging

from log_configuration import configure_logging

logger = logging.getLogger("my_app")

configure_logging(level=logging.DEBUG)

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
