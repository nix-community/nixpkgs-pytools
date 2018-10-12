# nixpkgs-dev-tools

These are scripts that I have written to remove the tedious nature of
creating nix package derivations. The goal of these scripts is not to
create a perfect package derivation.

## python

```
python/package-init.py <pypi-name> [--version <pypi-version>]
```

Creates a `default.nix` derivation to go into
`nixpkgs/pkgs/development/python-modules/<pypi-name>/default.nix`. This
script is overly verbose so that you don't have to remember the name
of attributes. Delete the ones that you don't need.
