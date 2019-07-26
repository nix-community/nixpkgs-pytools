# python nixpkgs tools

[![Build Status](https://travis-ci.org/nix-community/nixpkgs-pytools.svg?branch=master)](https://travis-ci.org/nix-community/nixpkgs-pytools)

These are scripts written to remove the tedious nature of creating nix
package derivations for nixpkgs. The goal of these scripts is not to
create a perfect package derivation but complete as much as possible
and guide the user on necessary changes.

## python-package-init

```
usage: python-package-init [-h] [--version VERSION] [--filename FILENAME] [--stdout] [--nixpkgs-root NIXPKGS_ROOT] [-f] package

positional arguments:
  package               pypi package name

optional arguments:
  -h, --help            show this help message and exit
  --version VERSION     pypi package version (stable if not specified)
  --filename FILENAME   filename for nix derivation
  --stdout              Print the nix derivation to stdout
  --nixpkgs-root NIXPKGS_ROOT
                        Root directory of nixpkgs
  -f, --force           Force creation of file, overwriting when it already exists
```

`python-package-init` now has the ability to create a `<package-name>
= callPackages ../...<package-name> { };` in
`pkgs/top-level/python-modules.nix` and write the `default.nix` to
`pkgs/development/python-modules/<package-name>/default.nix` with a
nearly complete derivation.

Example lets add `nixpkgs-pytools` to nixpkgs. It is already in
nixpkgs so you would need to provide the `-f` (force) option to force
it to be written to nixpkgs.

```shell
nix-shell -p nixpkgs-pytools
python-package-init nixpkgs-pytools --nixpkgs-root=<path to nixpkgs>
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
