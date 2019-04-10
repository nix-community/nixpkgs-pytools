# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2019-04-10
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
