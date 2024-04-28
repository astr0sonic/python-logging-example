import atexit
import json
import logging.config
import logging.handlers
import os
from pathlib import Path
from queue import Queue
from typing import Dict


def configure_logging(level: int) -> None:
    log_dir = Path("logs")
    create_log_dir(log_dir)

    log_config_path = Path("log_config.json")
    log_config = get_log_config(log_config_path)
    logging.config.dictConfig(log_config)

    register_queue_handler(level)


def create_log_dir(log_dir: Path) -> None:
    if not log_dir.exists():
        os.makedirs(log_dir)


def get_log_config(log_config_path: Path) -> Dict[str, str]:
    with open(log_config_path, mode="r", encoding="utf-8") as f:
        log_config = json.load(f)
    return log_config


def register_queue_handler(level: int) -> None:
    root = logging.getLogger("root")
    handlers = root.handlers

    log_queue: Queue = Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.setLevel(level)

    root.handlers = [queue_handler]

    queue_listener = logging.handlers.QueueListener(
        log_queue, *handlers, respect_handler_level=True
    )
    queue_listener.start()
    atexit.register(queue_listener.stop)
