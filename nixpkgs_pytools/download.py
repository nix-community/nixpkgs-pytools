import urllib.request
import shutil
import os
import json


def download_package_json(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError('package "{package_name}" does not exist on pypi')
        else:
            raise ValueError(
                f'error fetching pypi package "{package_name}" information'
            )


def download_package(url, directory):
    base_filename = os.path.join(directory, os.path.basename(url))

    with urllib.request.urlopen(url) as response:
        with open(base_filename, "wb") as f:
            f.write(response.read())

    previous_directory_state = set(os.listdir(directory))
    shutil.unpack_archive(base_filename, directory)
    current_directory_state = set(os.listdir(directory))

    changed_filenames = current_directory_state - previous_directory_state
    if len(changed_filenames) > 1:
        raise ValueError(
            f"expected that extracting sdist archive only produces one directory: {changed_filenames}"
        )

    return list(changed_filenames)[0]
