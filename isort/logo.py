from ._version import __version__

ASCII_ART = r"""
/#######################################################################\

     `sMMy`
     .yyyy-                                                      `
    ##soos##                                                    ./o.
          `     ``..-..`         ``...`.``         `   ```` ``-ssso```
     .s:-y-   .+osssssso/.     ./ossss+:so+:`    :+o-`/osso:+sssssssso/
     .s::y-   osss+.``.``     -ssss+-.`-ossso`   ssssso/::..::+ssss:::.
     .s::y-   /ssss+//:-.`   `ssss+     `ssss+   sssso`       :ssss`
     .s::y-   `-/+oossssso/  `ssss/      sssso   ssss/        :ssss`
     .y-/y-       ````:ssss`  ossso.    :ssss:   ssss/        :ssss.
     `/so:`    `-//::/osss+   `+ssss+-/ossso:    /sso-        `osssso/.
       \/      `-/oooo++/-      .:/++:/++/-`      ..           `://++/.


         isort your Python imports for you so you don't have to

                            VERSION {}

\########################################################################/
""".format(
    __version__
)

__doc__ = """
```python
{}
```
""".format(ASCII_ART)
