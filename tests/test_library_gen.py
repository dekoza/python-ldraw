import os
import shutil
import tempfile
from os.path import join

import mock
import pytest

from ldraw import CustomImporter, generate
from ldraw.colour import Colour


@pytest.fixture
def mocked_library_path():
    part_lst_path = os.path.join("tests", "test_ldraw", "parts.lst")
    library_path = tempfile.mkdtemp()
    generate(part_lst_path, library_path)
    with mock.patch(
        "ldraw.get_config",
        side_effect=lambda: {"parts.lst": part_lst_path, "library": library_path},
    ):
        yield library_path


def test_library_gen_files(mocked_library_path):
    """ generated library contains the right files """
    content = {
        os.path.relpath(os.path.join(dp, f), mocked_library_path)
        for dp, dn, fn in os.walk(mocked_library_path)
        for f in fn
    }

    library = {
        "__init__.py",
        "colours.py",
        "license.txt",
        "__hash__",
        join("parts", "__init__.py"),
        join("parts", "others.py"),
    }

    assert content == {join("library", el) for el in library}


def test_library_gen_import(mocked_library_path):
    """ generated library is importable """
    from ldraw import library

    assert library.__all__ == ["colours"]

    from ldraw.library.parts import others

    assert library.parts.__all__ == ["others"]

    from ldraw.library.parts.others import Brick2X4

    assert Brick2X4 == "3001"

    from ldraw.library.colours import ColoursByCode, ColoursByName, Reddish_Gold

    expected_color = Colour(189, "Reddish_Gold", "#AC8247", 255, ["PEARLESCENT"])

    assert ColoursByCode == {expected_color.code: expected_color}
    assert ColoursByName == {expected_color.name: expected_color}

    assert Reddish_Gold == expected_color
