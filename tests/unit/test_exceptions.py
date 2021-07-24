import pickle

from isort import exceptions


class TestISortError:
    def setup_class(self):
        self.instance = exceptions.ISortError()

    def test_init(self):
        assert isinstance(self.instance, exceptions.ISortError)

    def test_pickleable(self):
        assert isinstance(pickle.loads(pickle.dumps(self.instance)), exceptions.ISortError)


class TestExistingSyntaxErrors(TestISortError):
    def setup_class(self):
        self.instance: exceptions.ExistingSyntaxErrors = exceptions.ExistingSyntaxErrors(
            "file_path"
        )

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestIntroducedSyntaxErrors(TestISortError):
    def setup_class(self):
        self.instance: exceptions.IntroducedSyntaxErrors = exceptions.IntroducedSyntaxErrors(
            "file_path"
        )

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestFileSkipped(TestISortError):
    def setup_class(self):
        self.instance: exceptions.FileSkipped = exceptions.FileSkipped("message", "file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"
        assert str(self.instance) == "message"


class TestFileSkipComment(TestISortError):
    def setup_class(self):
        self.instance: exceptions.FileSkipComment = exceptions.FileSkipComment("file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestFileSkipSetting(TestISortError):
    def setup_class(self):
        self.instance: exceptions.FileSkipSetting = exceptions.FileSkipSetting("file_path")

    def test_variables(self):
        assert self.instance.file_path == "file_path"


class TestProfileDoesNotExist(TestISortError):
    def setup_class(self):
        self.instance: exceptions.ProfileDoesNotExist = exceptions.ProfileDoesNotExist("profile")

    def test_variables(self):
        assert self.instance.profile == "profile"


class TestSortingFunctionDoesNotExist(TestISortError):
    def setup_class(self):
        self.instance: exceptions.SortingFunctionDoesNotExist = (
            exceptions.SortingFunctionDoesNotExist("round", ["square", "peg"])
        )

    def test_variables(self):
        assert self.instance.sort_order == "round"
        assert self.instance.available_sort_orders == ["square", "peg"]


class TestLiteralParsingFailure(TestISortError):
    def setup_class(self):
        self.instance: exceptions.LiteralParsingFailure = exceptions.LiteralParsingFailure(
            "x = [", SyntaxError
        )

    def test_variables(self):
        assert self.instance.code == "x = ["
        assert self.instance.original_error == SyntaxError


class TestLiteralSortTypeMismatch(TestISortError):
    def setup_class(self):
        self.instance: exceptions.LiteralSortTypeMismatch = exceptions.LiteralSortTypeMismatch(
            tuple, list
        )

    def test_variables(self):
        assert self.instance.kind == tuple
        assert self.instance.expected_kind == list


class TestAssignmentsFormatMismatch(TestISortError):
    def setup_class(self):
        self.instance: exceptions.AssignmentsFormatMismatch = exceptions.AssignmentsFormatMismatch(
            "print x"
        )

    def test_variables(self):
        assert self.instance.code == "print x"


class TestUnsupportedSettings(TestISortError):
    def setup_class(self):
        self.instance: exceptions.UnsupportedSettings = exceptions.UnsupportedSettings(
            {"apply": {"value": "true", "source": "/"}}
        )

    def test_variables(self):
        assert self.instance.unsupported_settings == {"apply": {"value": "true", "source": "/"}}


class TestUnsupportedEncoding(TestISortError):
    def setup_class(self):
        self.instance: exceptions.UnsupportedEncoding = exceptions.UnsupportedEncoding("file.py")

    def test_variables(self):
        assert self.instance.filename == "file.py"
