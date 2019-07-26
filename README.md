# python nixpkgs tools

[![Build Status](https://travis-ci.org/nix-community/nixpkgs-pytools.svg?branch=master)](https://travis-ci.org/nix-community/nixpkgs-pytools)

These are scripts written to remove the tedious nature of creating nix
package derivations for nixpkgs. The goal of these scripts is not to
create a perfect package derivation but complete as much as possible
and guide the user on necessary changes.

## python-package-init

```
usage: python-package-init [-h] [--version VERSION] [--filename FILENAME]
                           [--stdout] [-f]
                           package

positional arguments:
  package              pypi package name

optional arguments:
  -h, --help           show this help message and exit
  --version VERSION    pypi package version (stable if not specified)
  --filename FILENAME  filename for nix derivation
  --stdout             Print the nix derivation to stdout
  -f, --force          Force creation of file, overwriting when it already exists
```

Creates a `default.nix` derivation to go into
`nixpkgs/pkgs/development/python-modules/<pypi-name>/default.nix`. This
script is overly verbose so that you don't have to remember the name
of attributes. Delete the ones that you don't need.


## Hacking on these tools

`nix-shell` will load the correct environment for your usage:

```
nix-shell
```
