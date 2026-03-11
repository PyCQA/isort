# isort

*isort your imports, so you don't have to.*

isort is a Python utility / library to sort imports alphabetically, and automatically separated into sections and by type.
It provides a command line utility, Python library, and [plugins for various editors](https://github.com/PyCQA/isort/wiki)
to quickly sort all your imports. It requires Python 3.10+ to run, but supports formatting Python 2 code too.

**Before isort:**

```python
from my_lib import Object

import os

from my_lib import Object3

from my_lib import Object2

import sys

from third_party import lib15, lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, lib10, lib11, lib12, lib13, lib14

import sys

from __future__ import absolute_import

from third_party import lib3

print("Hey")
print("yo")
```

**After isort:**

```python
from __future__ import absolute_import

import os
import sys

from third_party import (lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8,
                         lib9, lib10, lib11, lib12, lib13, lib14, lib15)

from my_lib import Object, Object2, Object3

print("Hey")
print("yo")
```

```{toctree}
:maxdepth: 2
:caption: Quick Start
:hidden:

quick_start/1.-install
quick_start/2.-cli
quick_start/3.-api
```

```{toctree}
:maxdepth: 2
:caption: Configuration
:hidden:

configuration/options
configuration/profiles
configuration/config_files
configuration/multi_line_output_modes
configuration/black_compatibility
configuration/pre-commit
configuration/git_hook
configuration/github_action
configuration/action_comments
configuration/custom_sections_and_ordering
configuration/add_or_remove_imports
```

```{toctree}
:maxdepth: 2
:caption: How-To Guides
:hidden:

howto/shared_profiles
```

```{toctree}
:maxdepth: 2
:caption: Major Releases
:hidden:

major_releases/introducing_isort_5
major_releases/release_policy
```

```{toctree}
:maxdepth: 2
:caption: Upgrade Guides
:hidden:

upgrade_guides/5.0.0
```

```{toctree}
:maxdepth: 2
:caption: Warning and Error Codes
:hidden:

warning_and_error_codes/W0500
```

```{toctree}
:maxdepth: 2
:caption: Contributing
:hidden:

contributing/1.-contributing-guide
contributing/2.-coding-standard
contributing/3.-code-of-conduct
contributing/4.-acknowledgements
```
