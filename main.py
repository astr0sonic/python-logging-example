import logging
import sys

from formatters import SimpleFormatter

logger = logging.getLogger("my_app")

console_handler = logging.StreamHandler(stream=sys.stdout)
formatter = SimpleFormatter(fmt="%(asctime)s %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.setLevel(level=logging.DEBUG)

logger.info("info message", extra={"foo": "foo"})

foo = 1
bar = 0
try:
    baz = foo / bar
except ZeroDivisionError:
    logger.exception("zero division", extra={"foo": foo, "bar": bar})
    baz = 0

print(baz)
