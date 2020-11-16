from pathlib import Path

from gp2gp.mesh.inbox import MeshInboxScanner
from gp2gp.mesh.file import MeshFile


def test_finds_dat_file_in_directory(fs):
    dat_file_path = Path("/IN/20201025030139_abc.dat")
    fs.create_dir("/IN")
    fs.create_file(dat_file_path, contents="I, am, data")

    expected = [MeshFile(dat_file_path)]

    scanner = MeshInboxScanner("/IN")

    result = list(scanner.scan())

    assert result == expected


def test_ignores_non_dat_files_in_directory(fs):
    txt_file_path = Path("/IN/a_file.txt")
    fs.create_dir("/IN")
    fs.create_file(txt_file_path, contents="I, am, data")

    expected = []

    scanner = MeshInboxScanner("/IN")

    result = list(scanner.scan())

    assert result == expected


def test_finds_multiple_dat_files_in_directory(fs):
    dat_file_path_one = Path("/IN/20201025030139_abc.dat")
    dat_file_path_two = Path("/IN/2020102504423_xyz.dat")
    fs.create_dir("/IN")
    fs.create_file(dat_file_path_one, contents="I, am, data")
    fs.create_file(dat_file_path_two, contents="More data")

    expected = [MeshFile(dat_file_path_one), MeshFile(dat_file_path_two)]

    scanner = MeshInboxScanner("/IN")

    result = list(scanner.scan())

    assert result == expected
