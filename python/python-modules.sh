#!/usr/bin/env bash
# print modules that are still in python-packages.nix

grep -n "[A-Z0-9a-z\_\-]\+ = buildPythonPackage" $1/pkgs/top-level/python-packages.nix
