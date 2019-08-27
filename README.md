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

## python-rewrite-imports

```
usage: python-rewrite-imports [-h] --path PATH [--replace REPLACE REPLACE]

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           path to refactor imports
  --replace REPLACE REPLACE
                        module import to replace
```

example rewriting airflow imports

```shell
nix-shell -p nixpkgs-pytools

cd /tmp
wget https://github.com/apache/airflow/archive/master.tar.gz
tar -xf master.tar.gz

python-rewrite-imports --path /tmp/airflow-master \
                       --replace flask_appbuilder flask_appbuilder_1_13_6237336a2b92fa6ba5f7f14dda56c08af6c0a76a \
                       --replace pendulum pendulum_1_4_4_55011d302b80c60360e2cc9f3a5ace7336c727c7

grep -R pendulum /tmp/airflow-master
```

You'll notice that all imports have been rewritten. Rewrites are done
via [rope](https://github.com/python-rope/rope) a robust refactoring
library used by many text editors.


## Hacking on these tools

`nix-shell` will load the correct environment for your usage:

```
nix-shell
```
