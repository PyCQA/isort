from subprocess import check_call

from isort.main import main


def test_django(tmpdir):
    check_call(["git", "clone", "https://github.com/django/django", str(tmpdir)])
    isort_target_dirs = [
        str(target_dir) for target_dir in (tmpdir / "django", tmpdir / "tests", tmpdir / "scripts")
    ]
    main(["--check-only", "--diff", *isort_target_dirs])
