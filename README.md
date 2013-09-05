isort
=====

isort your python imports for you so you don't have to.

isort is a Python utility / library to sort imports alphabetically, and automatically separated into sections.
It provides a command line utility, Python library, and Kate plugin to quickly sort all your imports.

Before isort:

    from my_lib import Object

    print("Hey")

    import os

    from my_lib import Object2

    import sys

    from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, lib10, lib11, lib12, lib13, lib14, lib15

    import sys

    from __future__ import absolute_import

    from third_party import lib3

    print("yo")

After isort:

    from __future__ import absolute_import

    import os
    import sys

    from third_party import (lib1,
                             lib2,
                             lib3,
                             lib4,
                             lib5,
                             lib6,
                             lib7,
                             lib8,
                             lib9,
                             lib10,
                             lib11,
                             lib12,
                             lib13,
                             lib14,
                             lib15)

    from my_lib import Object, Object2

    print("Hey")
    print("yo")

Installing isort
===================
Installing isort is as simple as:

    pip install isort

or if you prefer

    easy_install isort

Using isort
===================

from the command line:

    isort mypythonfile.py mypythonfile2.py

from within Python:

    from isort import SortImports

    SortImports("pythonfile.py")

or

    from isort import SortImports

    new_contents = SortImports(file_contents=old_contents).output

from within Kate:

    ctrl+[

or

    menu > Python > Sort Imports

Installing isort's Kate plugin
===================
To install the kate plugin you must either have pate installed or the very latest version of Kate:

    wget https://raw.github.com/timothycrosley/isort/master/kate_plugin.py --output-document ~/.kde/share/apps/kate/pate/isort_plugin.py

You will then need to restart kate and enable Python Plugins as well as the isort plugin itself.

Plugins for other text editors
===================

I use Kate, and Kate provides a very nice Python plugin API so I wrote a Kate plugin.
That said I will enthusiastically accept pull requests that include plugins for other text editors
and add documentation for them as I am notified.

How does isort work?
====================

isort parses specified files for global level import lines (imports outside of try / excepts blocks, functions, etc..)
and puts them all at the top of the file grouped together by the type of import:

- Future
- Python Standard Library
- Third Party
- Current Python Project

Inside of each section the imports are sorted alphabetically. isort automatically removes duplicate python imports,
and wraps long from imports to the specified line length (defaults to 80).

When will isort not work?
======================

If you ever have the situation where you need to have a try / except block in the middle of top-level imports or if
your import order is directly linked to precedence.

For example: a common practice in Django settings files is importing * from various settings files to form
a new settings file. In this case if any of the imports change order you are changing the settings definition itself.

However, you can configure isort to skip over just these files - or even to force certain imports to the top.

Configuring isort
======================

If you find the default isort settings do not work well for your project, isort provides several ways to adjust
the behavior.

To configure isort for a single user create a ~/.isort.cfg file:

    [settings]
    line_length=120
    force_to_top=file1.py,file2.py
    skip=file3.py,file4.py
    known_standard_libary=std,std2
    known_third_party=randomthirdparty
    known_first_party=mylib1,mylib2

You can then override any of these settings by using command line arguments, or by passing in override values to the
SortImports class.

Why isort?
======================

isort simply stands for import sort. It was originally called "sortImports" however I got tired of typing the extra
characters and came to the realization camelCase is not pythonic.

I wrote isort because in an organization I used to work in the manager came in one day and decided all code must
have alphabetically sorted imports. The code base was huge - and he meant for us to do it by hand. However, being a
programmer - I'm too lazy to spend 8 hours mindlessly performing a function, but not too lazy to spend 16
hours automating it. I was giving permission to open source sortImports and here we are :)
