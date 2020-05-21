from isort import exceptions


class TestISortError:
    def setup_class(self):
        self.instance = exceptions.ISortError()

    def test_init(self):
        assert isinstance(self.instance, exceptions.ISortError)


class TestExistingSyntaxErrors(TestISortError):
    def setup_class(self):
        self.instance = exceptions.ExistingSyntaxErrors("file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestIntroducedSyntaxErrors(TestISortError):
    def setup_class(self):
        self.instance = exceptions.IntroducedSyntaxErrors("file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestFileSkipped(TestISortError):
    def setup_class(self):
        self.instance = exceptions.FileSkipped("message", "file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"
        assert str(self.instance) == "message"


class TestFileSkipComment(TestISortError):
    def setup_class(self):
        self.instance = exceptions.FileSkipComment("file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestFileSkipSetting(TestISortError):
    def setup_class(self):
        self.instance = exceptions.FileSkipSetting("file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestProfileDoesNotExist(TestISortError):
    def setup_class(self):
        self.instance = exceptions.ProfileDoesNotExist("profile")

    def test_variables(self):
        assert self.instance.profile == "profile"
