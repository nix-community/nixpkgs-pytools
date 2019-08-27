import urllib
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

import shutil
import os
import json


def download_package_json(package_name):
    url = "https://pypi.org/pypi/{package_name}/json".format(package_name=package_name)
    try:
        response = urlopen(url)
        return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError('package "{package_name}" does not exist on pypi'.format(package_name=package_name))
        else:
            raise ValueError(
                'error fetching pypi package "{package_name}" information'.format(package_name=package_name)
            )


def download_package(url, directory):
    base_filename = os.path.join(directory, os.path.basename(url))

    with urlopen(url) as response:
        with open(base_filename, "wb") as f:
            f.write(response.read())

    previous_directory_state = set(os.listdir(directory))
    shutil.unpack_archive(base_filename, directory)
    current_directory_state = set(os.listdir(directory))

    changed_filenames = current_directory_state - previous_directory_state
    if len(changed_filenames) > 1:
        raise ValueError(
            "expected that extracting sdist archive only produces one directory: {changed_filenames}".format(changed_filenames=changed_filenames)
        )

    return list(changed_filenames)[0]
