import pytest

try:
    from unittest import mock
except ImportError:
    import mock

import os
import tempfile

from nixpkgs_pytools.python_package_init import initialize_package


# packages are added to tests when I run into
# a new issue with auto packaging
@pytest.mark.parametrize(
    "package_name",
    [
        "flask",  # setuptools
        "Flask",  # ensure package name not case sensitive
        "six",  # setuptools
        "dask",  # setuptools
        "pyxl3",  # distutils
        "numpy",  # mocking setup fails
        "capnpy",  # empty description
        "pytest",  # cannot unpack non-iterable NoneType object
    ],
)
def test_packages(tmpdir, package_name):
    filename = str(tmpdir.join("{package_name}.nix".format(package_name=package_name)))

    initialize_package(package_name=package_name, version=None, filename=filename)

    print(open(filename).read())



@pytest.mark.parametrize(
    "package_name, dependencies",
    [
        (
            "nixpkgs-pytools",
            {
                "checkInputs": {"pytest"},
                "buildInputs": set(),
                "propagatedBuildInputs": {"setuptools", "jinja2", "rope"},
            },
        )
    ],
)
@pytest.mark.xfail
def test_package_dependencies(tmpdir, package_name, dependencies):
    filename = str(tmpdir.join("{package_name}.nix".format(package_name=package_name)))

    with mock.patch(
            "nixpkgs_pytools.python_package_init.metadata_to_nix"
    ) as mock_func:
        mock_func.return_value = ""
        initialize_package(package_name=package_name, version=None, filename=filename)

    args, kwargs = mock_func.call_args
    assert set(args[0]["buildInputs"]) == dependencies["buildInputs"]
    assert set(args[0]["checkInputs"]) == dependencies["checkInputs"]
    assert (
        set(args[0]["propagatedBuildInputs"]) == dependencies["propagatedBuildInputs"]
    )
