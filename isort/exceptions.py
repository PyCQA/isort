"""All isort specific exception classes should be defined here"""
from .profiles import profiles


class ISortError(Exception):
    """Base isort exception object from which all isort sourced exceptions should inherit"""


class InvalidSettingsPath(ISortError):
    """Raised when a settings path is provided that is neither a valid file or directory"""

    def __init__(self, settings_path: str):
        super().__init__(
            f"isort was told to use the settings_path: {settings_path} as the base directory or "
            "file that represents the starting point of config file discovery, but it does not "
            "exist."
        )
        self.settings_path = settings_path


class ExistingSyntaxErrors(ISortError):
    """Raised when isort is told to sort imports within code that has existing syntax errors"""

    def __init__(self, file_path: str):
        super().__init__(
            f"isort was told to sort imports within code that contains syntax errors: "
            f"{file_path}."
        )
        self.file_path = file_path


class IntroducedSyntaxErrors(ISortError):
    """Raised when isort has introduced a syntax error in the process of sorting imports"""

    def __init__(self, file_path: str):
        super().__init__(
            f"isort introduced syntax errors when attempting to sort the imports contained within "
            f"{file_path}."
        )
        self.file_path = file_path


class FileSkipped(ISortError):
    """Should be raised when a file is skipped for any reason"""

    def __init__(self, message: str, file_path: str):
        super().__init__(message)
        self.file_path = file_path


class FileSkipComment(FileSkipped):
    """Raised when an entire file is skipped due to a isort skip file comment"""

    def __init__(self, file_path: str):
        super().__init__(
            f"{file_path} contains an file skip comment and was skipped.", file_path=file_path
        )


class FileSkipSetting(FileSkipped):
    """Raised when an entire file is skipped due to provided isort settings"""

    def __init__(self, file_path: str):
        super().__init__(
            f"{file_path} was skipped as it's listed in 'skip' setting"
            " or matches a glob in 'skip_glob' setting",
            file_path=file_path,
        )


class ProfileDoesNotExist(ISortError):
    """Raised when a profile is set by the user that doesn't exist"""

    def __init__(self, profile: str):
        super().__init__(
            f"Specified profile of {profile} does not exist. "
            f"Available profiles: {','.join(profiles)}."
        )
        self.profile = profile


class FormattingPluginDoesNotExist(ISortError):
    """Raised when a formatting plugin is set by the user that doesn't exist"""

    def __init__(self, formatter: str):
        super().__init__(f"Specified formatting plugin of {formatter} does not exist. ")
        self.formatter = formatter
