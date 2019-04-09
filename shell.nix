with import <nixpkgs> {};
python3.pkgs.buildPythonPackage {
  name = "env";
  src = ./.;
  propagatedBuildInputs = with python3.pkgs;[
    jinja2 setuptools
  ];
  checkInputs = [ python3.pkgs.black ];
}
