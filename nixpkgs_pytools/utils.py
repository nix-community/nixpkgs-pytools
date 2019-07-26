import os
import re


def determine_filename_extension(filename: str, package_name: str, version: str) -> str:
    base_filename = os.path.basename(filename)
    match = re.match(f"{package_name}-{version}\.(.+)", base_filename)
    if match is None:
        raise ValueError(f"could not determine extension of package: {filename}")
    return match.group(1)
