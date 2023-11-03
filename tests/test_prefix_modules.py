import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from subprocess import check_output

import pytest
from rope.base.fscommands import subprocess

from nixpkgs_pytools.prefix_modules import prefix_modules, rename_external


@contextmanager
def temp_tree():
    path = tempfile.mkdtemp()
    try:
        yield Path(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)


@contextmanager
def extended_sys_path(path):
    sys.path.append(path)
    try:
        yield
    finally:
        # May remove from the wrong index, but close enough
        sys.path.remove(path)


@contextmanager
def remember_sys_path():
    path = list(sys.path)
    try:
        yield
    finally:
        sys.path.clear()
        sys.path.extend(path)


@pytest.fixture(scope="function")
def some_package():
    with temp_tree() as path:
        (path / "utils").mkdir()
        (path / "utils" / "__init__.py").touch()
        (path / "models.py").write_text("import utils")

        env = {
            "PYTHONPATH": ":".join([path.as_posix(), *sys.path]),
        }

        with remember_sys_path():
            prefix_modules(
                path,
                "some_project",
                mode="first-error",
                verbose=True,
                exclude_globs=[],
            )

        yield (path, env)


def test_package_moved(some_package):
    _, env = some_package

    subprocess.run(
        [sys.executable, "-c", "import some_project.utils"],
        env=env,
        check=True,
    )


def test_module_moved(some_package):
    path, _ = some_package

    assert (path / "some_project" / "models.py").exists()


def test_imports_rewritten(some_package):
    _, env = some_package

    subprocess.run(
        [sys.executable, "-c", "import some_project.models"],
        env=env,
        check=True,
    )


def test_old_module_doesnt_exist(some_package):
    _, env = some_package
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            [sys.executable, "-c", "import utils"],
            env=env,
            check=True,
        )


def test_rename_external(some_package):
    path, _ = some_package

    (path / "thing.py").write_text("import non_existence")
    rename_external(
        project_root=path,
        old_name="non_existence",
        new_name="other_project.non_existence",
        pattern="**",
        mode="first-error",
        quiet=False,
        exclude_globs=[],
    )

    with open(path / "thing.py", "r") as f:
        assert f.read().strip() == "import other_project.non_existence"
