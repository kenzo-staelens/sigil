#!/usr/bin/env python3
from pathlib import Path

from sigil import run_from_config

if __name__ == "__main__":
    run_from_config(Path(__file__).parent)
