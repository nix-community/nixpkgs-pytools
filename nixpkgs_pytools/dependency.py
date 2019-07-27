import re
import sys
import os
import tempfile
import unittest
import ast
import glob

from .download import download_package
from .format import format_normalized_package_name


# https://docs.python.org/3/library/index.html
STDLIB_MODULES = {
    # text processing
    "string",
    "re",
    "difflib",
    "textwrap",
    "unicodedata",
    "stringprep",
    "readline",
    "rlcompleter",
    # binary data services
    "struct",
    "codecs",
    # data types
    "datetime",
    "calendar",
    "collections",
    "heapq",
    "bisect",
    "array",
    "weakref",
    "types",
    "copy",
    "pprint",
    "reprlib",
    "enum",
    # numeric and mathematical modules
    "numbers",
    "math",
    "cmath",
    "decimal",
    "fractions",
    "random",
    "statistics",
    # functional programming modules
    "itertools",
    "functools",
    "operator",
    # file and directory access
    "pathlib",
    "fileinput",
    "stat",
    "filecmp",
    "tempfile",
    "glob",
    "fnmatch",
    "linecache",
    "shutil",
    "macpath",
    # data persistence
    "pickle",
    "copyreg",
    "shelve",
    "marshal",
    "dbm",
    "sqlite3",
    # data compression and archiving
    "zlib",
    "gzip",
    "bz2",
    "lzma",
    "zipfile",
    "tarfile",
    # file formats
    "csv",
    "configparser",
    "netrc",
    "xdrlib",
    "plistlib",
    # crypographic services
    "hashlib",
    "hmac",
    "secrets",
    # generic operating system services
    "os",
    "io",
    "time",
    "argparse",
    "getopt",
    "logging",
    "getpass",
    "curses",
    "platform",
    "errno",
    "ctypes",
    # concurrent execution
    "threading",
    "multiprocessing",
    "concurrent",
    "subprocess",
    "sched",
    "queue",
    "_thread",
    "_dummy_thread",
    "dummy_threading",
    # contextvars
    "contextvars",
    # networking and interprocess communication
    "asyncio",
    "socket",
    "ssl",
    "select",
    "selectors",
    "asyncore",
    "asynchat",
    "signal",
    "mmap",
    # internet data handling
    "email",
    "json",
    "mailcap",
    "mailbox",
    "mimetypes",
    "base64",
    "binhex",
    "binascii",
    "quopri",
    "uu",
    # structured markup processing tools
    "html",
    "xml",
    # internet protocols and support
    "webbrowser",
    "cgi",
    "cgitb",
    "wsgiref",
    "urllib",
    "ftplib",
    "poplib",
    "imaplib",
    "nntplib",
    "smtplib",
    "smtpd",
    "telnetlib",
    "uuid",
    "socketserver",
    "xmlrpc",
    "ipaddress",
    # multimedia
    "audioop",
    "aifc",
    "sunau",
    "wave",
    "chunk",
    "colorsys",
    "imghdr",
    "sndhdr",
    "ossaudiodev",
    # internationalization
    "gettext",
    "locale",
    # program frameworks
    "turtle",
    "cmd",
    "shlex",
    # graphical user interfaces with tk
    "tkinter",
    # development tools
    "typing",
    "pydoc",
    "doctest",
    "unittest",
    "lib2to3",
    "test",
    # debugging and profiling
    "bdb",
    "faulthandler",
    "pdb",
    "timeit",
    "trace",
    "tracemalloc",
    # software packaging and distribution
    "distutils",
    "ensurepip",
    "venv",
    "zipapp",
    # python runtime services
    "sys",
    "sysconfig",
    "builtins",
    "warnings",
    "dataclasses",
    "contextlib",
    "abc",
    "atexit",
    "traceback",
    "__future__",
    "gc",
    "inspect",
    "site",
    # custom python interpreters
    "code",
    "codeop",
    # importing modules
    "zipimport",
    "pkgutil",
    "modulefinder",
    "runpy",
    "importlib",
    # python language services
    "parser",
    "ast",
    "symtable",
    "symbol",
    "token",
    "keyword",
    "tokenize",
    "tabnanny",
    "pyclbr",
    "py_compile",
    "compileall",
    "dis",
    "pickletools",
    # miscellaneous services
    "formatter",
    # ms windows specific services
    "msilib",
    "msvcrt",
    "winreg",
    "winsound",
    # unix specific services
    "posix",
    "pwd",
    "spwd",
    "grp",
    "crypt",
    "termios",
    "tty",
    "pty",
    "fcntl",
    "pipes",
    "resource",
    "nis",
    "syslog",
    # superseded modules
    "optparse",
    "imp",
    # undocumented modules
    "posixpath",
    "ntpath",
}


def determine_package_dependencies(package_json, url):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            extracted_directory = download_package(url, tempdir)
            package_directory = os.path.join(tempdir, extracted_directory)

            ## should wait since a lot of false positives
            # determine_dependencies_from_python_ast(package_directory)

            dependencies = determine_dependencies_from_mock_setup(package_directory)
    except Exception as e:
        dependencies = {
            "extraInputs": [],
            "buildInputs": [],
            "checkInputs": [],
            "propagatedBuildInputs": [],
        }

        # default to using metadata is setup mock failed
        if package_json["info"]["requires_dist"]:
            extraInputs = []
            propagatedBuildInputs = []
            for package in package_json["info"]["requires_dist"]:
                if re.search("extra\s*==\s*", package):
                    extraInputs.append(package)
                else:
                    propagatedBuildInputs.append(package)
            dependencies["extraInputs"] = extraInputs
            dependencies["propagatedBuildInputs"] = propagatedBuildInputs

    return sanitize_dependencies(dependencies)


def determine_dependencies_from_mock_setup(directory):
    try:
        current_directory = os.getcwd()
        os.chdir(directory)

        sys.path.insert(0, directory)

        with open("setup.py") as f:
            setup_contents = f.read()

        if re.search("setuptools", setup_contents):
            mock_path = "setuptools.setup"
        else:
            mock_path = "distutils.core.setup"

        with unittest.mock.patch(mock_path) as mock_setup:
            exec(setup_contents)

        args, kwargs = mock_setup.call_args
    except Exception as e:
        print(
            "mocking setup.py::setup(...) failed thus dependency information is likely incomplete"
        )
        print(f'mocking error: "{e}"')
        raise e
    finally:
        sys.path = sys.path[1:]
        os.chdir(current_directory)

    extraInputs = []
    for k, v in kwargs.get("extras_require", {}).items():
        if isinstance(v, list):
            for p in v:
                extraInputs.append(f"{p} # {k}")
        else:
            extraInputs.append(f"{p} # {k}")

    return {
        "extraInputs": extraInputs,
        "buildInputs": kwargs.get("setup_requires", []),
        "checkInputs": kwargs.get("tests_require", []),
        "propagatedBuildInputs": kwargs.get("install_requires", []),
    }


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for name in node.names:
            namespace = tuple(name.name.split("."))
            self.imports.add(namespace[0])

    def visit_ImportFrom(self, node):
        if node.module is None:  # relative import
            return

        partial_namespace = tuple(node.module.split("."))
        self.imports.add(partial_namespace[0])


def determine_dependencies_from_python_ast(directory):
    dependencies = {
        "extraInputs": set(),
        "buildInputs": set(),
        "checkInputs": set(),
        "propagatedBuildInputs": set(),
    }

    filenames = list(
        glob.glob(os.path.join(directory, "**", "*.py"), recursive=True)
    ) + list(glob.glob(os.path.join(directory, "*.py"), recursive=True))
    for filename in filenames:
        try:
            with open(filename) as f:
                tree = ast.parse(f.read())
        except SyntaxError:
            continue

        import_visitor = ImportVisitor()
        import_visitor.visit(tree)

        namespaces = import_visitor.imports - STDLIB_MODULES

        if "setup.py" in filename:
            dependencies["buildInputs"] = dependencies["buildInputs"] | namespaces
        elif "test" in filename:
            dependencies["checkInputs"] = dependencies["buildInputs"] | namespaces
        elif "doc" in filename:
            dependencies["extraInputs"] = dependencies["extraInputs"] | namespaces
        else:
            dependencies["propagatedBuildInputs"] = (
                dependencies["propagatedBuildInputs"] | namespaces
            )

    dependencies["buildInputs"] = (
        dependencies["buildInputs"] - dependencies["propagatedBuildInputs"]
    )
    dependencies["checkInputs"] = (
        dependencies["checkInputs"] - dependencies["propagatedBuildInputs"]
    )

    import pprint

    pprint.pprint(dependencies)


def sanitize_dependencies(packages):
    def sanitize_dependency(package):
        has_condition = None

        match = re.search("[><=;]", package)
        if match:
            has_condition = True

        match = re.search(
            "^([A-Za-z][A-Za-z\-_0-9]+)", format_normalized_package_name(package)
        )
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
