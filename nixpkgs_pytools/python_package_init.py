import urllib.request
import json
import argparse
import subprocess
import re
import sys
import os
from unittest import mock
from distutils.dir_util import copy_tree
import tempfile
import textwrap
from string import punctuation

import jinja2

from .format import (
    format_description,
    format_homepage,
    format_license,
    format_normalized_package_name,
)
from .dependency import determine_package_dependencies
from .download import download_package_json
from .utils import determine_filename_extension
from .output import write_nix_file, write_nixpkgs_package


def main():
    args = cli(sys.argv)
    content = initialize_package(
        args.package,
        args.version,
        args.filename,
        args.force,
        args.stdout,
        args.nixpkgs_root,
    )


def cli(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("package", help="pypi package name")
    parser.add_argument(
        "--version", help="pypi package version (stable if not specified)"
    )
    parser.add_argument(
        "--filename", default="default.nix", help="filename for nix derivation"
    )
    parser.add_argument(
        "--stdout", action="store_true", help="Print the nix derivation to stdout"
    )
    parser.add_argument("--nixpkgs-root", help="Root directory of nixpkgs")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force creation of file, overwriting when it already exists",
    )
    args = parser.parse_args()
    print(f'Fetching package="{args.package}" version="{args.version or "stable"}"')
    return args


def initialize_package(
    package_name, version, filename, force=False, to_stdout=False, nixpkgs_root=None
):
    data = download_package_json(package_name)
    metadata = package_json_to_metadata(data, package_name, version)
    content = metadata_to_nix(metadata)
    if to_stdout:
        print(content)
    elif nixpkgs_root is not None:
        write_nixpkgs_package(content, package_name, nixpkgs_root, force)
    else:
        write_nix_file(content, filename, force)
        print(f'Package "{package_name}" succesfully written to "{filename}"')


def determine_check_phase(metadata):
    if "pytest" in metadata["checkInputs"]:
        return "pytest"
    elif "nose" in metadata["checkInputs"]:
        return "nosetests"
    return None


def package_json_to_metadata(package_json, package_name, package_version):
    package_version = package_version or package_json["info"]["version"]

    if package_version not in package_json["releases"]:
        raise ValueError(f'package version "{package_version}" does not exist on pypi')

    package_release_json = None
    for release in package_json["releases"][package_version]:
        if release["packagetype"] == "sdist":
            package_release_json = release
            break
    else:
        raise ValueError(
            f"no source distribution (sdist) found for {package_name}:{package_version}"
        )

    metadata = {
        "pname": format_normalized_package_name(package_json["info"]["name"]),
        "downloadname": package_json["info"]["name"],
        "version": package_version,
        "python_version": package_json["info"]["requires_python"],
        "sha256": package_release_json["digests"]["sha256"],
        "url": package_release_json["url"],
        "extension": determine_filename_extension(
            package_release_json["filename"],
            package_json["info"]["name"],
            package_version,
        ),
        "description": format_description(package_json["info"]["summary"]),
        "homepage": format_homepage(package_json["info"]["home_page"]),
        "license": format_license(package_json["info"]["license"]),
    }

    metadata.update(determine_package_dependencies(package_json, metadata["url"]))
    metadata["checkPhase"] = determine_check_phase(metadata)
    return metadata


def metadata_to_nix(metadata):
    template = jinja2.Template(
        textwrap.dedent(
            """\
        { lib
        , buildPythonPackage
        , fetchPypi
        {% for p in (metadata.buildInputs + metadata.checkInputs + metadata.propagatedBuildInputs) %}, {{ p }}
        {% endfor %}}:

        buildPythonPackage rec {
          pname = "{{ metadata.pname }}";
          version = "{{ metadata.version }}";
        {% if metadata.python_version %}
          disabled = ; # requires python version {{ metadata.python_version }}
        {% endif %}
          src = fetchPypi {
        {%- if metadata.pname != metadata.downloadname %}
            pname = "{{ metadata.downloadname }}";
            inherit version;
        {%- else %}
            inherit pname version;
        {%- endif %}
        {%- if metadata.extension != "tar.gz" %}
            extension = "{{ metadata.extension }}";
        {%- endif %}
            sha256 = "{{ metadata["sha256"] }}";
          };
        {% if metadata.packageConditions %}
          # # Package conditions to handle
          # # might have to sed setup.py and egg.info in patchPhase
          # # sed -i "s/<package>.../<package>/"
        {%- for condition in metadata.packageConditions %}
          # {{ condition -}}
        {% endfor %}{% endif %}{% if metadata.extraInputs %}
          # # Extra packages (may not be necessary)
        {%- for p in metadata.extraInputs %}
          # {{ p -}}
        {% endfor %}{% endif %}
        {%- if metadata.buildInputs %}
          buildInputs = [
        {%- for p in metadata.buildInputs %}
            {{ p -}}
        {% endfor %}
          ];
        {% endif %}
        {%- if metadata.checkInputs %}
          checkInputs = [
        {%- for p in metadata.checkInputs %}
            {{ p -}}
        {% endfor %}
          ];
        {% endif %}
        {%- if metadata.propagatedBuildInputs %}
          propagatedBuildInputs = [
        {%- for p in metadata.propagatedBuildInputs %}
            {{ p -}}
        {% endfor %}
          ];
        {% endif %}
        {%- if metadata.checkPhase %}
          checkPhase = ''
            {{metadata.checkPhase|indent(width=6)}}
          '';
        {% endif %}
          meta = with lib; {
            description = "{{ metadata.description }}";
            homepage = {{ metadata.homepage }};
            license = licenses.{{ metadata.license }};
            # maintainers = [ maintainers. ];
          };
        }
    """
        )
    )
    return template.render(metadata=metadata)


if __name__ == "__main__":
    main()
