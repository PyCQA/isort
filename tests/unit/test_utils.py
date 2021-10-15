from isort.utils import Trie


def test_trie():
    trie_root = Trie("default", {"line_length": 70})

    trie_root.insert("/temp/config1/.isort.cfg", {"line_length": 71})
    trie_root.insert("/temp/config2/setup.cfg", {"line_length": 72})
    trie_root.insert("/temp/config3/pyproject.toml", {"line_length": 73})

    # Ensure that appropriate configs are resolved for files in different directories
    config1 = trie_root.search("/temp/config1/subdir/file1.py")
    assert config1[0] == "/temp/config1/.isort.cfg"
    assert config1[1] == {"line_length": 71}

    config1_2 = trie_root.search("/temp/config1/file1_2.py")
    assert config1_2[0] == "/temp/config1/.isort.cfg"
    assert config1_2[1] == {"line_length": 71}

    config2 = trie_root.search("/temp/config2/subdir/subsubdir/file2.py")
    assert config2[0] == "/temp/config2/setup.cfg"
    assert config2[1] == {"line_length": 72}

    config2_2 = trie_root.search("/temp/config2/subdir/file2_2.py")
    assert config2_2[0] == "/temp/config2/setup.cfg"
    assert config2_2[1] == {"line_length": 72}

    config3 = trie_root.search("/temp/config3/subdir/subsubdir/subsubsubdir/file3.py")
    assert config3[0] == "/temp/config3/pyproject.toml"
    assert config3[1] == {"line_length": 73}

    config3_2 = trie_root.search("/temp/config3/file3.py")
    assert config3_2[0] == "/temp/config3/pyproject.toml"
    assert config3_2[1] == {"line_length": 73}

    config_outside = trie_root.search("/temp/file.py")
    assert config_outside[0] == "default"
    assert config_outside[1] == {"line_length": 70}
