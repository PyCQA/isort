import os
import sys
from typing import Any, Dict, List

from pylama.lint import Linter as BaseLinter

from . import SortImports


class Linter(BaseLinter):

    def allow(self, path: str) -> bool:
        """Determine if this path should be linted."""
        return path.endswith('.py')

    def run(self, path: str, **meta: Any) -> List[Dict[str, Any]]:
        """Lint the file. Return an array of error dicts if appropriate."""
        with open(os.devnull, 'w') as devnull:
            # Suppress isort messages
            sys.stdout = devnull

            if SortImports(path, check=True).incorrectly_sorted:
                return [{
                    'lnum': 0,
                    'col': 0,
                    'text': 'Incorrectly sorted imports.',
                    'type': 'ISORT'
                }]
            else:
                return []
