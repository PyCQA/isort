from isort.pylama_isort import Linter


class TestLinter:
    instance = Linter()

    def test_allow(self):
        assert not self.instance.allow("test_case.pyc")
        assert not self.instance.allow("test_case.c")
        assert self.instance.allow("test_case.py")

    def test_run(self, tmpdir):
        correct = tmpdir.join("incorrect.py")
        correct.write("import a\nimport b\n")
        assert not self.instance.run(str(correct))

        incorrect = tmpdir.join("incorrect.py")
        incorrect.write("import b\nimport a\n")
        assert self.instance.run(str(incorrect))

    def test_skip(self, tmpdir):
        incorrect = tmpdir.join("incorrect.py")
        incorrect.write("# isort: skip_file\nimport b\nimport a\n")
        assert not self.instance.run(str(incorrect))
