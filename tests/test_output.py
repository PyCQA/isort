from hypothesis_auto import auto_pytest_magic

from isort import output

auto_pytest_magic(output.grid, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.vertical, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.hanging_indent, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.vertical_hanging_indent, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.vertical_grid_common, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.vertical_grid, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.vertical_grid_grouped, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.vertical_grid_grouped_no_comma, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.noqa, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(output.with_comments, auto_allow_exceptions_=(ValueError,))
