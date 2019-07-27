import re
import string
import urllib.request


def format_normalized_package_name(package_name: str) -> str:
    """Normalize a package name"""
    return package_name.replace(".", "-").replace("_", "-").lower()


def format_description(description: str) -> str:
    """Normalize whitespace, remove punctuation, and capitalize first letter"""
    if len(description) == 0:
        return ""

    description = re.sub("\s+", description.strip(string.punctuation), " ")
    return description[0].upper() + description[1:]


def format_homepage(homepage: str) -> str:
    """Use https url if possible"""
    if re.match("https://", homepage):
        return homepage

    https_homepage = homepage.replace("http://", "https://")
    try:
        response = urllib.request.urlopen(https_homepage)
        return https_homepage
    except:
        return ""


def format_license(license: str) -> str:
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
