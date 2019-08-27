import os
import re
import string

from .format import format_normalized_package_name


def write_nix_file(content, filename, force=False):
    directory = os.path.dirname(filename)
    if directory:
        if not os.path.isdir(directory):
            os.makedirs(directory)

    if os.path.isfile(filename) and not force:
        raise ValueError('file {filename} already exists'.format(filename=filename))

    with open(filename, 'w') as f:
        f.write(content)


def write_nixpkgs_package(content, package_name, nixpkgs_root, force=False):
    # check if is nixpkgs directory
    if not (
        {"default.nix", "doc", "lib", "maintainers", "README.md", "nixos", "pkgs"}
        <= set(os.listdir(nixpkgs_root))
    ):
        raise ValueError("directory {nixpkgs_root} is not a nixpkgs root directory".format(nixpkgs_root=nixpkgs_root))

    normalized_package_name = format_normalized_package_name(package_name)
    python_modules_directory = os.path.join(
        nixpkgs_root, "pkgs", "development", "python-modules"
    )
    package_directory = os.path.join(python_modules_directory, normalized_package_name)
    python_packages_filename = os.path.join(
        nixpkgs_root, "pkgs", "top-level", "python-packages.nix"
    )
    package_regex = "\n[ ]+([A-Za-z0-9\-_]+)\s+=\s+callPackage"
    inserted_text = "\n  {normalized_package_name} = callPackage ../development/python-modules/{normalized_package_name} {{ }};\n".format(normalized_package_name=normalized_package_name)

    # adhoc method of getting all python packages
    normalized_package_names = {
        format_normalized_package_name(_) for _ in os.listdir(python_modules_directory)
    }

    # check that package does not already exist
    if normalized_package_name in normalized_package_names and not force:
        raise ValueError(
            'cannot overrite existing package derivation {package_directory} without force "-f" option'.format(package_directory=package_directory)
        )

    # write file to pkgs/development/python-modules/<package_name>/default.nix
    write_nix_file(content, os.path.join(package_directory, "default.nix"), force)

    # now insert package in `pkgs/top-level/python-packages.nix`
    # this doesn't capture all package names but it doesn't need
    # to in order to find a place to insert a package name
    with open(python_packages_filename) as f:
        python_packages_content = f.read()

    content_offset = python_packages_content.find("phonenumbers = callPackage")

    for i, match in enumerate(
        re.finditer(package_regex, python_packages_content[content_offset:])
    ):
        python_packages_package_name = format_normalized_package_name(match.group(1))

        # ensure that package is put in a reasonable place
        # that first letter of package is at most one letter away
        left_letter_index = string.ascii_lowercase.find(normalized_package_name[0])
        right_letter_index = string.ascii_lowercase.find(
            python_packages_package_name[0]
        )
        letter_distance = abs(left_letter_index - right_letter_index)

        if (
            normalized_package_name < python_packages_package_name
            and letter_distance <= 1
        ):
            print("inserting package before {package} in python-modules.nix".format(package=match.group(1)))
            insertion_location = content_offset + match.start()

            with open(python_packages_filename, "w") as f:
                f.write(
                    python_packages_content[:insertion_location]
                    + inserted_text
                    + python_packages_content[insertion_location:]
                )

            break
