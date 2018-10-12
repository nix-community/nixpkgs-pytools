# nixpkgs-dev-tools

These are scripts that I have written to remove the tedious nature of
creating nix package derivations. The goal of these scripts is not to
create a perfect package derivation.

## usefull development commands

Build Package in sandbox

```
nix-build <path-to-nixpkgs> -A <package> --option sandbox true
```

## general

```
nix-build -I nixpkgs=<path-to-nixpkgs> check-meta.nix -A [ maintainers, license, homepage, broken ]
```

List are packages that have given meta attribute
  - maintainers :: checks that maintainer is defined
  - license :: checks that a license is defined
  - homepage :: checks that a homepage is defined
  - broken :: checks for all packages marked broken

## python

```
python/package-init.py <pypi-name> [--version <pypi-version>]
```

Creates a `default.nix` derivation to go into
`nixpkgs/pkgs/development/python-modules/<pypi-name>/default.nix`. This
script is overly verbose so that you don't have to remember the name
of attributes. Delete the ones that you don't need.

```
python/needs-license.py <nixpkgs-archive-url>
```

Lists all python packages that do not have a license. Checks PyPi if a
license is provided for that package.


