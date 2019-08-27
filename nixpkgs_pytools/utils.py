import os
import re


def determine_filename_extension(filename, package_name, version):
    # type: (str, str, str) -> str
    base_filename = os.path.basename(filename)
    match = re.match("{package_name}-{version}\.(.+)".format(package_name=package_name, version=version), base_filename)
    if match is None:
        raise ValueError("could not determine extension of package: {filename}".format(filename=filename))
    return match.group(1)
