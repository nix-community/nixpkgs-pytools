import pytest

from nixpkgs_pytools.python_package_init import initialize_package


# packages are added to tests when I run into
# a new issue with auto packaging
@pytest.mark.parametrize("package_name", [
    'flask', # setuptools
    'Flask', # ensure package name not case sensitive
    'six',   # setuptools
    'dask',  # setuptools
    'pyxl3', # distutils
    'numpy'  # mocking setup fails
])
def test_packages(tmp_path, package_name):
    filename = tmp_path / f"{package_name}.nix"

    initialize_package(package_name=package_name, version=None, filename=filename)

    print(open(filename).read())
