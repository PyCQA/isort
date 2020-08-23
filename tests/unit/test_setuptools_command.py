from isort import setuptools_commands


def test_isort_command_smoke(src_dir):
    """A basic smoke test for the setuptools_commands command"""
    from distutils.dist import Distribution

    command = setuptools_commands.ISortCommand(Distribution())
    command.distribution.packages = ["isort"]
    command.distribution.package_dir = {"isort": src_dir}
    command.initialize_options()
    command.finalize_options()
    try:
        command.run()
    except BaseException:
        pass

    command.distribution.package_dir = {"": "isort"}
    command.distribution.py_modules = ["one", "two"]
    command.initialize_options()
    command.finalize_options()
    command.run()

    command.distribution.packages = ["not_a_file"]
    command.distribution.package_dir = {"not_a_file": src_dir}
    command.initialize_options()
    command.finalize_options()
    try:
        command.run()
    except BaseException:
        pass
