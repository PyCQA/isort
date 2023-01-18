"""Defines all sections isort uses by default"""
from typing import Tuple

FUTURE: str = "FUTURE"
DUNDER: str = "DUNDER"
STDLIB: str = "STDLIB"
THIRDPARTY: str = "THIRDPARTY"
FIRSTPARTY: str = "FIRSTPARTY"
LOCALFOLDER: str = "LOCALFOLDER"
DEFAULT: Tuple[str, ...] = (FUTURE, DUNDER, STDLIB, THIRDPARTY, FIRSTPARTY, LOCALFOLDER)
