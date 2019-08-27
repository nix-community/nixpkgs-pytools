{ pkgs ? import <nixpkgs> { }, pythonPackages ? pkgs.python3Packages }:

pythonPackages.buildPythonPackage {
  name = "env";
  src = ./.;

  propagatedBuildInputs = with pythonPackages; [
    jinja2 setuptools rope
  ] ++ pkgs.stdenv.lib.optionals pythonPackages.isPy27 [ pythonPackages.mock ];

  checkInputs = [ pythonPackages.pytest ]
    ++ pkgs.stdenv.lib.optionals pythonPackages.isPy3k [ pythonPackages.black ];
}
