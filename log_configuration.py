import json
import logging.config
import os
from pathlib import Path
from typing import Dict


def configure_logging() -> None:
    log_dir = Path("logs")
    create_log_dir(log_dir)

    log_config_path = Path("log_config.json")
    log_config = get_log_config(log_config_path)
    logging.config.dictConfig(log_config)


def create_log_dir(log_dir: Path) -> None:
    if not log_dir.exists():
        os.makedirs(log_dir)


def get_log_config(log_config_path: Path) -> Dict[str, str]:
    with open(log_config_path, mode="r", encoding="utf-8") as f:
        log_config = json.load(f)
    return log_config
