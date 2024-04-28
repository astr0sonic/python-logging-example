import logging
from collections import OrderedDict
from typing import Any, MutableMapping, Tuple


class CustomLoggerAdapter(logging.LoggerAdapter):
    def __init__(
        self, logger: logging.Logger, extra: MutableMapping[str, Any] | None = None
    ):
        super().__init__(logger, extra)

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        updated_extra: MutableMapping[str, Any] = OrderedDict()
        if self.extra is not None:
            updated_extra.update(self.extra)
        if kwargs.get("extra", None) is not None:
            updated_extra.update(kwargs["extra"])
        kwargs.update({"extra": updated_extra})
        return msg, kwargs
