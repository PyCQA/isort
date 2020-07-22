import os

from isort.pylama_isort import Linter


class TestLinter:
    instance = Linter()

    def test_allow(self):
        assert not self.instance.allow("test_case.pyc")
        assert not self.instance.allow("test_case.c")
        assert self.instance.allow("test_case.py")

    def test_run(self, src_dir, tmpdir):
        assert not self.instance.run(os.path.join(src_dir, "api.py"))

        incorrect = tmpdir.join("incorrect.py")
        incorrect.write("import b\nimport a\n")
        assert self.instance.run(str(incorrect))
