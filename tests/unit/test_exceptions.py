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


class TestLiteralParsingFailure(TestISortError):
    def setup_class(self):
        self.instance = exceptions.LiteralParsingFailure("x = [", SyntaxError)

    def test_variables(self):
        assert self.instance.code == "x = ["
        assert self.instance.original_error == SyntaxError


class TestLiteralSortTypeMismatch(TestISortError):
    def setup_class(self):
        self.instance = exceptions.LiteralSortTypeMismatch(tuple, list)

    def test_variables(self):
        assert self.instance.kind == tuple
        assert self.instance.expected_kind == list


class TestAssignmentsFormatMismatch(TestISortError):
    def setup_class(self):
        self.instance = exceptions.AssignmentsFormatMismatch("print x")

    def test_variables(self):
        assert self.instance.code == "print x"


class TestUnsupportedSettings(TestISortError):
    def setup_class(self):
        self.instance = exceptions.UnsupportedSettings({"apply": {"value": "true", "source": "/"}})

    def test_variables(self):
        assert self.instance.unsupported_settings == {"apply": {"value": "true", "source": "/"}}


class TestUnsupportedEncoding(TestISortError):
    def setup_class(self):
        self.instance = exceptions.UnsupportedEncoding("file.py")

    def test_variables(self):
        assert self.instance.filename == "file.py"
