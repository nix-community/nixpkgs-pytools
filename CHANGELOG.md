# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.2] - 2019-07-27

### Added
 - support for directly adding package to `nixpkgs` via `--nixpkgs-root`
 - `--stdout` option to print derivation instead of writing to file
 - more complete unit tests
 - detect `pytest` and `nose` as `checkInputs` and automatically set `checkPhase`
 - automatic `http://` -> `https://` urls if they exist
 - `fetchPypi` now includes the `extension` if not `tar.gz`

### Changed
 - removed dependency on `nix-prefetch-url`
 - mocking `setup(...)` is now the default

## [1.0.1] - 2019-04-10
### Added
- adds a changelog

### Changed
- add unit tests via pytest

## [1.0.0] - 2019-04-09
### Added
- setup.py support
- package is released to pypi, automatic publishing of the package to pypi via travis

### Changed
- move files to subfolder for setup.py packaging support

### Removed
- remove support for direct calling of `python-package-init.py`, install the
  package and run `python-package-init` instead
