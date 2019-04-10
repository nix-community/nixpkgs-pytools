import urllib.request
import json
import argparse
import subprocess
import re
import sys
import os
from unittest import mock
import setuptools
from distutils.dir_util import copy_tree
import tempfile
import textwrap
from string import punctuation

import jinja2


def main():
    args = cli(sys.argv)
    initialize_package(args.package, args.version, args.filename, args.force)


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
        "-f",
        "--force",
        action="store_true",
        help="Force creation of file, overwriting when it already exists",
    )
    args = parser.parse_args()
    print(args.package, args.version)
    return args


def initialize_package(package, version, filename, force=False):
    data = download_package_json(package)
    metadata = package_json_to_metadata(data, package, version)

    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)
    mode = "w" if force else "x"
    with open(filename, mode) as f:
        f.write(metadata_to_nix(metadata))


def download_package_json(package_name):
    url = "https://pypi.org/pypi/%s/json" % package_name
    with urllib.request.urlopen(url) as response:
        if response.getcode() != 200:
            raise ValueError(
                'error fetching pypi package "%s" information' % package_name
            )
        return json.loads(response.read().decode())


def python_to_nix_license(license):
    """Convert python setup.py license to nix license

    These licenses account for about 95% of all licenses. The
    following snippet gathers licenses of top 5,000 packages.

    .. code-block:: python

       import urllib.request
       import json
       from collections import defaultdict

       projects = {r['project'] for r in requests.get("https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.json").json()['rows']}
       licenses = defaultdict(lambda:0)
       for p in projects:
           try:
               data = requests.get('https://pypi.org/pypi/%s/json' % p).json()
               license = data.get('info', {}).get('license')
               licenses[license] += 1
           except:
               pass
       sorted([(k, v) for k, v in licenses.items()], key=lambda t: -t[1])
    """
    case_sensitive_license_nix_map = {
        "3-clause BSD": "bsd3",
        "AGPL": "agpl3",
        "Apache": "asl20",
        "Apache 2": "asl20",
        "Apache2": "asl20",
        "Apache-2": "asl20",
        "Apache 2.0": "asl20",
        "Apache-2.0": "asl20",
        "Apache License": "asl20",
        "Apache License (2.0)": "asl20",
        "Apache License 2.0": "asl20",
        "Apache License, Version 2.0": "asl20",
        "Apache License Version 2.0": "asl20",
        "Apache Software License": "asl20",
        "Apache Software License 2.0": "asl20",
        "BSD license": " # lookup BSD license being used: bsd0, bsd2, bsd3, or bsdOriginal ",
        "BSD": " # lookup BSD license being used: bsd0, bsd2, bsd3, or bsdOriginal ",
        "BSD-3": "bsd3",
        "BSD 3-clause": "bsd3",
        "BSD 3-Clause License": "bsd3",
        "GNU GPL": "gpl1",
        "GNU LGPL": "lgpl2Plus",
        "GNU GPLv2 or any later version": "gpl2Plus",
        "GNU General Public License (GPL)": "gpl1",
        "GNU General Public License v2 or later (GPLv2+)": "gpl2Plus",
        "GPL": "gpl1",
        "GPLv2 or later": "gpl2Plus",
        "GPLv2": "gpl2",
        "GPLv2+": "gpl2Plus",
        "GPLv3": "gpl3",
        "GPL v3": "gpl3",
        "GPLv3+": "gpl3Plus",
        "ISC": "isc",
        "ISC License": "isc",
        "LGPL": "lgpl2Plus",
        "LGPLv2+": "lgpl2Plus",
        "LGPLv2.1 or later": "lgpl21Plus",
        "LGPLv3": "lgpl3",
        "LGPLv3+": "lgpl3Plus",
        "License :: OSI Approved :: MIT License": "mit",
        "MIT": "mit",
        "MIT License": "mit",
        "The MIT License: http://www.opensource.org/licenses/mit-license.php": "mit",
        "Mozilla Public License 2.0 (MPL 2.0)": "mpl20",
        "MPL": "mpl10",
        "MPL2": "mpl20",
        "MPL 2.0": "mpl20",
        "New BSD": "bsd3",
        "New BSD License": "bsd3",
        "PSF License": "psfl",
        "PSF": "psfl",
        "Python Software Foundation License": "psfl",
        "Python style": "psfl",
        "Public Domain": "publicDomain",
        "Two-clause BSD license": "bsd2",
        "Unlicense": "unlicense",
        "ZPL 2.1": "zpl21",
        "ZPL": "zpl21",
        "Zope Public License": "zpl21",
    }
    license_nix_map = {
        name.lower(): nix_attr
        for name, nix_attr in case_sensitive_license_nix_map.items()
    }
    return license_nix_map.get(license.lower(), license)


def package_json_to_metadata(package_json, package_name, package_version):
    package_version = package_version or package_json["info"]["version"]

    if package_version not in package_json["releases"]:
        raise ValueError(
            'package version "%s" does not exist on pypi' % package_version
        )

    package_release_json = None
    for release in package_json["releases"][package_version]:
        if release["packagetype"] == "sdist":
            package_release_json = release
            break
    else:
        raise ValueError(
            "no source distribution found for %s:%s" % (package_name, package_version)
        )

    metadata = {
        "pname": normalize_name(package_json["info"]["name"]),
        "downloadname": package_json["info"]["name"],
        "version": package_version,
        "python_version": package_json["info"]["requires_python"],
        "sha256": package_release_json["digests"]["sha256"],
        "url": package_release_json["url"],
        "description": package_json["info"]["summary"].strip(punctuation),
        "homepage": package_json["info"]["home_page"],
        "license": python_to_nix_license(package_json["info"]["license"]),
    }

    metadata.update(determine_package_dependencies(package_json, metadata["url"]))
    return metadata


def normalize_name(name: str) -> str:
    """Normalize a package name."""
    return name.replace(".", "-").replace("_", "-").lower()


def sanitize_dependencies(packages):
    def sanitize_dependency(package):
        has_condition = None

        match = re.search("[><=;]", package)
        if match:
            has_condition = True

        match = re.search("^([A-Za-z][A-Za-z\-_0-9]+)", normalize_name(package))
        return match.group(1), has_condition

    packageConditions = []
    buildInputs = []
    checkInputs = []
    propagatedBuildInputs = []

    for package in packages["buildInputs"]:
        sanitized_name, has_condition = sanitize_dependency(package)
        if has_condition:
            packageConditions.append(package)
        buildInputs.append(sanitized_name)

    for package in packages["checkInputs"]:
        sanitized_name, has_condition = sanitize_dependency(package)
        if has_condition:
            packageConditions.append(package)
        checkInputs.append(sanitized_name)

    for package in packages["propagatedBuildInputs"]:
        sanitized_name, has_condition = sanitize_dependency(package)
        if has_condition:
            packageConditions.append(package)
        propagatedBuildInputs.append(sanitized_name)

    return {
        "packageConditions": packageConditions,
        "extraInputs": packages["extraInputs"],
        "buildInputs": buildInputs,
        "checkInputs": checkInputs,
        "propagatedBuildInputs": propagatedBuildInputs,
    }


def determine_package_dependencies(package_json, url):
    # initially use requires_dist
    if package_json["info"]["requires_dist"]:
        extraInputs = []
        propagatedBuildInputs = []
        for package in package_json["info"]["requires_dist"]:
            if re.search("extra\s*==\s*", package):
                extraInputs.append(package)
            else:
                propagatedBuildInputs.append(package)
        dependencies = {
            "extraInputs": extraInputs,
            "buildInputs": [],
            "checkInputs": [],
            "propagatedBuildInputs": propagatedBuildInputs,
        }
    else:
        # fallover if requires_dist not populated
        dependencies = determine_dependencies_from_package(url)
    return sanitize_dependencies(dependencies)


def determine_dependencies_from_package(url):
    stdout = subprocess.check_output(
        ["nix-prefetch-url", "--unpack", url], stderr=subprocess.STDOUT
    )
    nix_store_path = re.search(b"^unpacking...\npath is '(.*)'\n(.*)\n$", stdout).group(
        1
    )

    sys.path.append(".")

    with tempfile.TemporaryDirectory() as tempdir:
        try:
            current_directory = os.getcwd()
            copy_tree(
                nix_store_path.decode("utf-8"),
                tempdir,
                preserve_mode=False,
                preserve_times=False,
            )
            os.chdir(tempdir)
            sys.path.insert(0, tempdir)
            with mock.patch.object(setuptools, "setup") as mock_setup:
                import setup  # This is setup.py which calls setuptools.setup
        finally:
            sys.path = sys.path[1:]
            os.chdir(current_directory)

    args, kwargs = mock_setup.call_args

    extraInputs = []
    for k, v in kwargs.get("extras_require", {}).items():
        if isinstance(v, list):
            for p in v:
                extraInputs.append("%s # %s" % (p, k))
        else:
            extraInputs.append("%s # %s" % (p, k))

    return {
        "extraInputs": extraInputs,
        "buildInputs": kwargs.get("setup_requires", []),
        "checkInputs": kwargs.get("tests_require", []),
        "propagatedBuildInputs": kwargs.get("install_requires", []),
    }


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
