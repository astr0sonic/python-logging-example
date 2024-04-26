import logging
import sys

logger = logging.getLogger("my_app")

console_handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    fmt="%(asctime)s %(message)s", datefmt="%Y.%m.%dT%H:%M:%S%z"
)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.setLevel(level=logging.DEBUG)

logger.info("info message", extra={"foo": "foo"})

foo = 1
bar = 0
try:
    baz = foo / bar
except ZeroDivisionError as e:
    logger.exception("zero division", extra={"foo": foo, "bar": bar})
    baz = 0

print(baz)
